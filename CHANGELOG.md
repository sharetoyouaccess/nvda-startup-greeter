# Changelog

All notable changes to **NVDA Startup Greeter** are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Version numbers follow NVDA's own `year.major[.minor]` API version
convention, matching the `version` / `minimumNVDAVersion` /
`lastTestedNVDAVersion` fields in [`manifest.ini`](manifest.ini). Internal
test builds of a version are distributed as separate files
(`...-r2.nvda-addon`, `...-r3.nvda-addon`, etc. — see
[`DEVELOPMENT_LOG.md`](DEVELOPMENT_LOG.md) for the reasoning and full
build-by-build history) but are not individually listed here; only the
cumulative, user-facing result for each version is recorded below.

## [Unreleased]

Nothing pending. `[2026.09.09]` below is the current candidate for the first
NVDA Add-on Store submission; still under multi-machine testing.

## [2026.09.09] - 2026-08-19

This is the version intended for the first NVDA Add-on Store submission.
The package's own `changelog` field (in `manifest.ini` / `doc/en/readme.html`)
is intentionally kept short for that submission ("Initial release." plus a
plain feature list); the fuller internal history below is for development
reference only.

### Added

- Support for multiple custom messages: add as many as you like from NVDA
  Settings, and a different one is spoken each time NVDA starts (never the
  same one twice in a row), instead of a single fixed custom message.
- `Add...` / `Edit...` / `Remove` buttons in the settings panel to manage
  the list of custom messages.
- Speaks a short greeting automatically as soon as NVDA finishes starting;
  no key press required.
- Time-of-day aware default greeting (good morning / afternoon / evening),
  used whenever no custom messages are configured.
- `NVDA Startup Greeter` category in NVDA Settings to enable/disable the
  greeting and manage custom messages.
- Matching message shown on a connected braille display.

### Changed

- Startup announcement is triggered via NVDA's `core.postNvdaStartup`
  extension point and spoken at `speech.Spri.NOW` priority, instead of a
  fixed `wx.CallLater` timer that could race NVDA's own startup sequence
  and cause the greeting to be skipped or cut off.
- Settings panel registration uses `SettingsPanel` /`NVDASettingsDialog`
  from `gui.settingsDialogs`, the current non-deprecated location, instead
  of the deprecated top-level `gui` re-export.
- Startup timing fine-tuned (delay before first speak attempt, and the
  retry-check interval) so the greeting is heard as early as possible.
- Speech-activity check (used by the retry safety net) no longer depends on
  `speech.isSpeaking()`, which does not exist on current NVDA (2026.1) and
  always raised `AttributeError` there; it now checks NVDA's internal
  `speech._manager` first, with the legacy call kept only as a fallback for
  older NVDA builds. Purely a log-noise/compatibility cleanup - behaviour
  for the end user is unchanged.

### Fixed

- Removed reliance on a non-existent `speech.waitUntilDone()` call that
  always fell back to a blocking `time.sleep()` on NVDA's main thread,
  freezing NVDA's interface for up to a few seconds on every startup. The
  announcement is fully asynchronous.
- `license.txt` no longer references a "known limitations" manual section
  that was removed from `readme.html` in an earlier draft.
