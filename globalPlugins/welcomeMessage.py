# welcomeMessage.py
# NVDA Startup Announcer Global Plugin with Settings Panel
#
# Update log (kept in-file so development can resume from the source alone):
#
# - 2026.08.09 (session 1): Modernized settings panel registration. `SettingsPanel` and
#   `NVDASettingsDialog` are now imported from `gui.settingsDialogs` instead
#   of the deprecated top-level `gui` re-export. Importing `SettingsPanel`
#   from `gui` directly triggers a deprecation warning in current NVDA
#   (see gui/__init__.py `__getattr__`), which add-on testers/reviewers see
#   as a stack-trace warning. `gui.settingsDialogs` is the supported,
#   non-deprecated location for both symbols.
#
# - 2026.08.09 (session 3): Redesigned how/when the greeting is spoken, to fix two
#   real bugs the user reported: (a) the greeting was sometimes not heard at all,
#   and (b) it could be causing NVDA to feel laggy right at startup.
#
#   Root causes found by reading NVDA's own source (source/core.py, source/speech):
#
#   1) The old code scheduled the announcement with a blind `wx.CallLater(300, ...)`
#      fired from `GlobalPlugin.__init__`, which runs *while NVDA is still starting*
#      (global plugins are constructed before speech/GUI/focus have settled).
#      300ms is not a promise of anything - on a slower machine, or with more
#      add-ons loaded, NVDA might still be mid-startup when this fires, or the
#      timing might coincide with NVDA announcing the initial focused object,
#      and whichever call NVDA processes first can cancel the other's speech.
#      This is exactly the "reads sometimes, not others" symptom.
#      Fix: hook NVDA's own `core.postNvdaStartup` extension point instead. NVDA
#      fires this exactly once, from its core queue, only after config, speech,
#      the GUI and the initial focus report have all been set up - it is the
#      documented, supported way for an add-on to know "NVDA has fully finished
#      starting". No arbitrary timer race is needed.
#
#   2) The old code called `speech.waitUntilDone()` inside a try/except. That
#      method does not exist anywhere in NVDA's public speech API (confirmed
#      against the current source), so it always raised `AttributeError` and
#      always fell through to `time.sleep(len(message) / 17.0)` - executed on
#      NVDA's main GUI thread, since that's the thread `wx.CallLater` callbacks
#      run on. That froze all of NVDA's UI/input handling for up to a few
#      seconds on *every single startup*. This has been removed entirely: there
#      is no need to block anything, `speech.speakMessage` is asynchronous and
#      returns immediately once the message is queued.
#
#   3) The old code used NVDA's default (NORMAL) speech priority, which can be
#      silently wiped by another `speech.cancelSpeech()` call happening around
#      the same time (e.g. when NVDA reports the initially focused object).
#      Fix: speak with `speech.Spri.NOW`, NVDA's built-in priority level for
#      "this is important, must be heard now". It interrupts whatever
#      lower-priority speech is already in progress and guarantees our greeting
#      is heard first every time; the interrupted speech (e.g. the focus
#      report) automatically resumes right after ours finishes, so nothing
#      else is permanently lost either.
#
#   Net effect: the greeting is now spoken exactly once per real NVDA startup,
#   always heard first, and never blocks or delays NVDA in any way.
#
# - 2026.08.09 (session 4, diagnostic build): The user reported hearing nothing at
#   all after installing and enabling the session-3 build (confirmed via a real
#   NVDA log: no trace of this add-on at all, success or failure - our code
#   previously never logged anything of its own on success, so a silent failure
#   and a silent success were indistinguishable from the log alone).
#   Added explicit `log.info`/`log.error` calls at every step (module load,
#   __init__, settings panel registration, postNvdaStartup registration,
#   _announce being called, and immediately before/after speakMessage), all
#   prefixed "NVDA Startup Greeter:" so they are easy to find with Ctrl+F in
#   nvda.log regardless of the configured log level. Also wrapped the body of
#   __init__ and _announce in try/except so that any exception is guaranteed to
#   produce a clearly labelled ERROR entry with a full traceback, instead of
#   relying only on NVDA's generic per-handler exception logging. This build is
#   purely for diagnosis; once the real cause is confirmed the noisier logging
#   can be trimmed back to just the essentials.
#
# - 2026.08.09 (session 5): The session-4 diagnostic log came back completely clean -
#   module imported, __init__ ran, settings panel registered, postNvdaStartup fired,
#   `speech.speakMessage(..., priority=Spri.NOW)` was called and returned with no
#   error - and the user *still* heard nothing. So the bug is not in this add-on's
#   logic at all; NVDA's speech API accepted the message with no complaint, but no
#   audio came out. Looking at the user's log, right around the same moment
#   (within about a second of our _announce firing) the synth driver ("MultiLang",
#   a non-default synth) gets reloaded a second time and the user's audioManager /
#   audioDuckingEnabler add-ons are actively touching the audio device at startup.
#   This is a known class of real-world screen-reader issue: the very first speech
#   utterance sent right as a synthesizer/audio device is being (re)initialized can
#   be silently swallowed by the audio backend, even though NVDA's own software
#   queue accepts it without any error - there is nothing this add-on's code can
#   detect or catch about that, since it happens below NVDA's speech API.
#   Mitigation: instead of speaking the instant postNvdaStartup fires, we now wait
#   a short, fixed grace period (1.5s) after that event before actually speaking.
#   This still guarantees the announcement is tied to a genuine NVDA startup (not
#   an arbitrary race against NVDA's own boot sequence, as in the session-1 bug),
#   it just also gives other add-ons' own audio-device/synth setup on this
#   particular machine time to finish before we send our first utterance to it.
#
# - 2026.08.09 (session 6): The 1.5s delay from session 5 fixed the silence, but
#   introduced a new, reported problem: NVDA's own announcement of the initial
#   focused object (e.g. the desktop) is now consistently heard *before* our
#   greeting, because 1.5s is long enough for that announcement to fully finish
#   before we ever call speakMessage - so Spri.NOW has nothing left in progress
#   to interrupt; it only affects speech that is actively playing *at the moment
#   we speak*, it cannot retroactively reorder speech that already finished.
#
#   Re-examining the session-5 log: the "silence" symptom is very likely not
#   really about the audio device warming up, but about `speech.cancelSpeech()`.
#   NVDA typically cancels current speech and starts fresh whenever the focused
#   object changes (which happens right at startup, for the initial focus). If
#   that cancellation lands after our Spri.NOW message has been queued but
#   before the synthesizer has actually started producing audio for it, our
#   whole utterance is wiped - Spri.NOW protects against being interrupted by
#   *lower priority* speech, but a hard `cancelSpeech()` clears everything
#   regardless of priority. That matches both observations at once: instant
#   speaking (session 4) = silently wiped by the startup focus announcement's
#   own cancel-then-speak cycle; 1.5s delayed speaking (session 5) = survives,
#   but only because the focus announcement's cancel-then-speak cycle is long
#   over by the time we speak, so we end up going second instead of first.
#
#   Fix: speak almost immediately again (small fixed buffer, not 1.5s), but now
#   verify shortly afterwards whether the message is actually still playing
#   (`speech.isSpeaking()`). If it isn't - meaning it was most likely wiped by a
#   `cancelSpeech()` racing against us - speak it again with Spri.NOW straight
#   away, up to a handful of times. Because Spri.NOW always takes precedence
#   over whatever lower-priority speech (like a focus report) is playing at
#   that exact instant, whichever attempt finally "sticks" ends up heard first,
#   with any interrupted speech resuming afterwards as normal. This keeps
#   things fast (each retry is ~200ms apart) while being resilient to the
#   startup cancelSpeech() race, instead of trading reliability for ordering
#   (or vice versa) with a single fixed delay.
#
# - 2026.08.09 (session 8): Session 6's fix worked well: only the very start of the
#   interrupted focus announcement (e.g. "de-" of "Desktop") is now audible before
#   our greeting cuts in and plays in full. The user asked to try shrinking that
#   leftover fragment further, accepting a little more risk in exchange.
#   Read NVDA's own SpeechManager implementation (source/speech/manager.py) to
#   understand exactly what a Spri.NOW speak call does: it calls the synthesizer's
#   own `cancel()` immediately and starts pushing the new utterance - i.e. the
#   fragment that leaks through is audio that had already been sent to the
#   synth/sound device before our interrupt landed. The only way to shrink it is to
#   call speakMessage() sooner after postNvdaStartup fires, i.e. interrupt earlier.
#   Also found that `speech.isSpeaking()` was throwing on this NVDA build (2026.1.1),
#   silently disabling the retry-on-failure safety net from session 6 without
#   anyone knowing (now logged at info level so this is visible). Added a fallback
#   check via `speech._manager` (NVDA's internal speech queue object, also publicly
#   re-exported from the `speech` package) for systems where `isSpeaking()` itself
#   is unreliable, so the retry safety net still has a chance to function.
#   Reduced the initial delay from 200ms to 100ms as a moderate, evidence-based step
#   (0ms previously produced total silence for our own message; 200ms produced a
#   small leaked fragment and success) to shrink the leaked fragment further while
#   staying on the safe side of the point where our own message got lost entirely.
#
# - 2026.08.09 (session 9): 100ms still let a small fragment leak through. The user
#   understood this is a hardware/driver-buffering limit (audio already sent to the
#   sound device cannot be un-played) and asked to push a little further anyway.
#   Reduced the initial delay from 100ms to 60ms. This increases the chance of
#   landing back in the "our own message gets wiped" scenario seen at 0ms delay
#   (session 4/r2), which is exactly what the retry safety net (_speakAttempt /
#   _checkSpokenOrRetry / _isSpeechActive, session 6 and 8) exists to catch and
#   recover from automatically. If 60ms turns out to be too aggressive on this
#   machine, the fix is simply to raise POST_STARTUP_INITIAL_DELAY_MS back up again -
#   there is no single "correct" value here, only a trade-off between how much of
#   the previous utterance leaks through and how much margin there is against the
#   startup speech race, and that trade-off point can vary by machine/synth/add-ons.
#   Also shortened RETRY_CHECK_INTERVAL_MS from 200ms to 100ms, so that if the more
#   aggressive 60ms initial delay does cause a wipe, the retry-on-failure check fires
#   sooner and the recovery speech attempt follows with less of a silent gap.
#
# - 2026.09.09 (session 13): Added support for a *list* of custom messages instead of
#   a single one. If two or more messages are configured, one is picked at random each
#   time NVDA starts, deliberately excluding whichever message was picked last time
#   (persisted in config as lastSpokenCustomMessage) so the same message never plays
#   twice in a row. If the list is empty, behaviour is unchanged: the default
#   time-of-day greeting is spoken, exactly as before.
#   The settings panel's single text field was replaced with a list box plus
#   Add/Edit/Remove buttons (matching the pattern NVDA's own speech dictionary
#   dialogs use), since editing several short messages one at a time is clearer than
#   trying to parse them out of a single multi-line/delimited text field.
#   The old single "customMessage" config key is kept in the config spec purely for
#   one-time migration: if a user upgrades from an earlier version with a custom
#   message already set and no message list yet, it is automatically copied into the
#   new list on first load, so nothing is lost across the upgrade.
#
# - 2026.09.09 (session 14): The message-list feature tested well, but a small leaked
#   fragment of NVDA's own initial focus announcement was still audible just before the
#   greeting, same trade-off documented in sessions 6-9. At the user's request, pushed
#   the initial delay down again: 60ms -> 35ms. Also shortened the retry-check interval
#   (100ms -> 60ms) so the retry safety net reacts faster if this more aggressive delay
#   ever causes the message to be wiped outright (as happened at 0ms back in session 4).
#   As before, there is no single "correct" value, only a trade-off between how much of
#   the previous utterance leaks through and how much margin remains against the startup
#   speech race; raising POST_STARTUP_INITIAL_DELAY_MS back up is the fix if 35ms proves
#   too aggressive on this machine.
#
# - 2026.08.19 (session 17): A real nvda.log from the user (running NVDA 2026.1) confirmed
#   something session 8's comment had only suspected: `speech.isSpeaking()` genuinely does
#   not exist on current NVDA (it raises AttributeError every single time), it is not just
#   "unreliable on some builds". The existing try/except fallback to
#   `speech._manager._hasNoMoreSpeech()` already handled this correctly and the add-on kept
#   working exactly as designed - nothing was broken for the user. But logging a full
#   AttributeError traceback on *every* NVDA startup for a call that is now known to always
#   fail is just log noise. _isSpeechActive() now tries the `speech._manager` check first
#   (confirmed working via direct NVDA source inspection in an earlier session) and only
#   falls back to the legacy `speech.isSpeaking()` name for older NVDA builds that might
#   still have it, keeping the same "return None means unknown" behaviour either way.

import addonHandler
addonHandler.initTranslation()

import globalPluginHandler
import speech
import datetime
import random
import config
import core
import braille
import gui
import wx
from gui.settingsDialogs import NVDASettingsDialog, SettingsPanel
from logHandler import log

_LOG_PREFIX = "NVDA Startup Greeter:"
log.info(f"{_LOG_PREFIX} module is being imported")

#: Small buffer (ms) to wait after core.postNvdaStartup fires before the first
#: attempt to speak. Kept short on purpose: the retry logic in _checkSpokenOrRetry
#: is what actually protects against the message being silently cancelled, not
#: this delay - a long delay here would just make us reliably lose the race to
#: be heard first against NVDA's own initial focus announcement.
POST_STARTUP_INITIAL_DELAY_MS = 35

#: How many times to retry speaking (with Spri.NOW) if a check shortly after
#: speaking suggests the message did not actually end up playing (most likely
#: wiped by a `speech.cancelSpeech()` call racing against us, e.g. from NVDA's
#: own initial focus announcement).
MAX_SPEAK_ATTEMPTS = 5

#: How long (ms) to wait after each speak attempt before checking whether it
#: actually stuck, via speech.isSpeaking(). Shortened alongside the initial
#: delay above (sessions 9 and 14) so that, if the more aggressive initial
#: delay does cause a wipe, the retry fires again quickly instead of leaving a
#: longer silent gap before recovering.
RETRY_CHECK_INTERVAL_MS = 60

# Config spec for persistent settings
confspec = {
	"enabled": "boolean(default=True)",
	# Kept only for one-time migration from versions before 2026.09.09, which
	# supported a single custom message. See _migrateLegacyCustomMessage.
	"customMessage": "string(default='')",
	# The list of user-configured custom messages. If non-empty, one is chosen
	# at random (excluding lastSpokenCustomMessage) each time NVDA starts,
	# instead of the default time-of-day greeting.
	"customMessages": "string_list(default=list())",
	# Remembers whichever message (from customMessages) was spoken most
	# recently, purely so the next startup can avoid repeating it immediately.
	"lastSpokenCustomMessage": "string(default='')",
}
config.conf.spec["startupAnnouncer"] = confspec


class StartupAnnouncerPanel(SettingsPanel):
	"""Settings panel shown in NVDA Preferences > Settings > NVDA Startup Greeter."""

	# Translators: title of this add-on's category in NVDA's Settings dialog.
	title = _("NVDA Startup Greeter")

	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

		self.enabledCheckbox = sHelper.addItem(
			# Translators: label of a checkbox in the NVDA Startup Greeter settings panel.
			wx.CheckBox(self, label=_("&Enable startup announcement")),
		)
		self.enabledCheckbox.SetValue(config.conf["startupAnnouncer"]["enabled"])
		self.enabledCheckbox.Bind(wx.EVT_CHECKBOX, self.onToggleEnabled)

		self.messagesLabel = sHelper.addItem(
			wx.StaticText(
				self,
				# Translators: label of the list of custom messages in the settings panel.
				label=_(
					"&Custom messages (spoken instead of the default greeting; "
					"if more than one, a different one is chosen each startup; "
					"leave empty to use the default greeting):",
				),
			),
		)
		self.messagesListBox = sHelper.addItem(
			wx.ListBox(self, choices=list(config.conf["startupAnnouncer"]["customMessages"])),
		)

		buttonHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		self.addButton = buttonHelper.addButton(
			self,
			# Translators: label of a button in the NVDA Startup Greeter settings panel.
			label=_("&Add..."),
		)
		self.addButton.Bind(wx.EVT_BUTTON, self.onAddMessage)
		self.editButton = buttonHelper.addButton(
			self,
			# Translators: label of a button in the NVDA Startup Greeter settings panel.
			label=_("&Edit..."),
		)
		self.editButton.Bind(wx.EVT_BUTTON, self.onEditMessage)
		self.removeButton = buttonHelper.addButton(
			self,
			# Translators: label of a button in the NVDA Startup Greeter settings panel.
			label=_("&Remove"),
		)
		self.removeButton.Bind(wx.EVT_BUTTON, self.onRemoveMessage)
		sHelper.addItem(buttonHelper)

		self._updateFieldState()

	def onToggleEnabled(self, evt):
		self._updateFieldState()

	def _updateFieldState(self):
		enabled = self.enabledCheckbox.GetValue()
		self.messagesLabel.Enable(enabled)
		self.messagesListBox.Enable(enabled)
		self.addButton.Enable(enabled)
		self.editButton.Enable(enabled)
		self.removeButton.Enable(enabled)

	def onAddMessage(self, evt):
		with wx.TextEntryDialog(
			self,
			# Translators: prompt of a dialog to add a custom startup message.
			_("Message to speak"),
			# Translators: title of a dialog to add a custom startup message.
			_("Add custom message"),
		) as entryDialog:
			if entryDialog.ShowModal() == wx.ID_OK:
				text = entryDialog.GetValue().strip()
				if text:
					self.messagesListBox.Append(text)
		self.messagesListBox.SetFocus()

	def onEditMessage(self, evt):
		index = self.messagesListBox.GetSelection()
		if index == wx.NOT_FOUND:
			return
		with wx.TextEntryDialog(
			self,
			# Translators: prompt of a dialog to edit a custom startup message.
			_("Message to speak"),
			# Translators: title of a dialog to edit a custom startup message.
			_("Edit custom message"),
			value=self.messagesListBox.GetString(index),
		) as entryDialog:
			if entryDialog.ShowModal() == wx.ID_OK:
				text = entryDialog.GetValue().strip()
				if text:
					self.messagesListBox.SetString(index, text)
		self.messagesListBox.SetFocus()

	def onRemoveMessage(self, evt):
		index = self.messagesListBox.GetSelection()
		if index == wx.NOT_FOUND:
			return
		self.messagesListBox.Delete(index)
		newCount = self.messagesListBox.GetCount()
		if newCount:
			self.messagesListBox.SetSelection(min(index, newCount - 1))
		self.messagesListBox.SetFocus()

	def onSave(self):
		config.conf["startupAnnouncer"]["enabled"] = self.enabledCheckbox.GetValue()
		config.conf["startupAnnouncer"]["customMessages"] = list(self.messagesListBox.GetStrings())
		# The single legacy field is no longer edited from the UI; clear it so
		# it doesn't get re-migrated on a future load. See _migrateLegacyCustomMessage.
		config.conf["startupAnnouncer"]["customMessage"] = ""
		config.conf.save()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Global plugin that reliably announces NVDA's readiness once startup has
	fully completed, with configurable settings.
	"""

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		log.info(f"{_LOG_PREFIX} GlobalPlugin.__init__ starting")
		try:
			self._migrateLegacyCustomMessage()
			NVDASettingsDialog.categoryClasses.append(StartupAnnouncerPanel)
			log.info(f"{_LOG_PREFIX} settings panel registered")
			# Speak once NVDA has *completely* finished starting up (config, speech,
			# GUI and initial focus reporting are already initialized by the time
			# this fires). This is NVDA's own documented extension point for this
			# exact purpose, so we never race NVDA's startup sequence with a timer.
			core.postNvdaStartup.register(self._onPostNvdaStartup)
			log.info(f"{_LOG_PREFIX} registered with core.postNvdaStartup")
		except Exception:
			log.error(f"{_LOG_PREFIX} error during __init__", exc_info=True)
			raise

	def _migrateLegacyCustomMessage(self):
		"""One-time migration for users upgrading from a version before 2026.09.09,
		which only supported a single "customMessage" string. If that field still
		has a value and the new "customMessages" list hasn't been set up yet,
		copy it across so the user's existing message keeps working, then clear
		the legacy field so this only ever runs once.
		"""
		legacy = config.conf["startupAnnouncer"]["customMessage"].strip()
		messages = list(config.conf["startupAnnouncer"]["customMessages"])
		if legacy and not messages:
			log.info(f"{_LOG_PREFIX} migrating legacy single customMessage into customMessages list")
			config.conf["startupAnnouncer"]["customMessages"] = [legacy]
			config.conf["startupAnnouncer"]["customMessage"] = ""
			config.conf.save()

	def _chooseCustomMessage(self):
		"""Picks one message from the configured list, avoiding an immediate
		repeat of whichever message was spoken last time (if there's more than
		one to choose from). Returns None if the list is empty.
		"""
		messages = list(config.conf["startupAnnouncer"]["customMessages"])
		if not messages:
			return None
		lastSpoken = config.conf["startupAnnouncer"]["lastSpokenCustomMessage"]
		candidates = [m for m in messages if m != lastSpoken] or messages
		chosen = random.choice(candidates)
		config.conf["startupAnnouncer"]["lastSpokenCustomMessage"] = chosen
		config.conf.save()
		return chosen

	def _onPostNvdaStartup(self):
		log.info(f"{_LOG_PREFIX} postNvdaStartup fired")
		wx.CallLater(POST_STARTUP_INITIAL_DELAY_MS, self._prepareAndSpeak)

	def _prepareAndSpeak(self):
		try:
			enabled = config.conf["startupAnnouncer"]["enabled"]
			log.info(f"{_LOG_PREFIX} enabled setting = {enabled!r}")
			if not enabled:
				log.info(f"{_LOG_PREFIX} announcement disabled in settings, not speaking")
				return

			custom = self._chooseCustomMessage()
			if custom:
				log.info(f"{_LOG_PREFIX} chosen custom message: {custom!r}")
				message = custom
			else:
				currentHour = datetime.datetime.now().hour
				if 5 <= currentHour < 12:
					# Translators: default startup greeting, spoken in the morning.
					greeting = _("Good morning")
				elif 12 <= currentHour < 18:
					# Translators: default startup greeting, spoken in the afternoon.
					greeting = _("Good afternoon")
				else:
					# Translators: default startup greeting, spoken in the evening.
					greeting = _("Good evening")
				# Translators: spoken once NVDA has finished starting up.
				# {greeting} is replaced with a time-of-day greeting such as "Good morning".
				message = _("{greeting}, NVDA is ready").format(greeting=greeting)

			try:
				# Also show the greeting on a connected braille display, matching
				# how NVDA's own core reports "NVDA started" on startup. Sent once
				# up front, regardless of how many speech attempts it takes below.
				braille.handler.message(message)
			except Exception:
				log.error(f"{_LOG_PREFIX} error sending message to braille", exc_info=True)

			self._speakAttempt(message, MAX_SPEAK_ATTEMPTS)
		except Exception:
			log.error(f"{_LOG_PREFIX} error while preparing to announce", exc_info=True)

	def _speakAttempt(self, message, attemptsLeft):
		log.info(f"{_LOG_PREFIX} speaking (attempts remaining after this: {attemptsLeft}): {message!r}")
		try:
			# Spri.NOW takes precedence over whatever lower-priority speech is
			# playing at this exact instant (e.g. NVDA reporting the initially
			# focused object), interrupting it; that speech automatically
			# resumes once ours finishes. This is non-blocking and returns as
			# soon as the message has been queued for speech.
			speech.speakMessage(message, priority=speech.Spri.NOW)
			log.info(f"{_LOG_PREFIX} speakMessage call returned without error")
		except Exception:
			log.error(f"{_LOG_PREFIX} error calling speakMessage", exc_info=True)
			return
		if attemptsLeft > 0:
			wx.CallLater(RETRY_CHECK_INTERVAL_MS, self._checkSpokenOrRetry, message, attemptsLeft - 1)

	def _isSpeechActive(self):
		"""Best-effort check for whether NVDA currently considers itself to be
		speaking. Tries `speech._manager` first - NVDA's internal speech queue
		object, also re-exported at the top of the `speech` package - since a
		real nvda.log (session 17) confirmed `speech.isSpeaking()` no longer
		exists on current NVDA (2026.1) and always raises AttributeError there.
		Falls back to the legacy `speech.isSpeaking()` name in case it is still
		present on an older NVDA build. Returns None if neither approach works,
		meaning "unknown" rather than a guess.
		"""
		try:
			return not speech._manager._hasNoMoreSpeech()
		except Exception:
			log.info(
				f"{_LOG_PREFIX} speech._manager check failed; trying legacy speech.isSpeaking() fallback",
				exc_info=True,
			)
		try:
			return bool(speech.isSpeaking())
		except Exception:
			log.info(f"{_LOG_PREFIX} speech.isSpeaking() fallback also failed", exc_info=True)
			return None

	def _checkSpokenOrRetry(self, message, attemptsLeft):
		stillSpeaking = self._isSpeechActive()
		log.info(f"{_LOG_PREFIX} speech still active = {stillSpeaking!r}")
		if stillSpeaking is None:
			# Couldn't determine either way; assume it stuck rather than risk
			# repeating it indefinitely.
			return
		if stillSpeaking:
			# Something is speaking (almost certainly our own message, since we
			# just spoke it with the highest priority); nothing more to do.
			return
		if attemptsLeft <= 0:
			log.info(f"{_LOG_PREFIX} no speech detected and no attempts left; giving up for this startup")
			return
		log.info(
			f"{_LOG_PREFIX} no speech detected shortly after speaking - it was most likely "
			"cancelled by another event (e.g. the initial focus announcement); retrying",
		)
		self._speakAttempt(message, attemptsLeft)

	def terminate(self):
		core.postNvdaStartup.unregister(self._onPostNvdaStartup)
		try:
			NVDASettingsDialog.categoryClasses.remove(StartupAnnouncerPanel)
		except ValueError:
			pass
		super(GlobalPlugin, self).terminate()
  
