# NVDA Startup Greeter — บันทึกการพัฒนา (Development Log)

เอกสารนี้เก็บบันทึกการพัฒนาแบบละเอียดของ add-on นี้ทุกรอบ (root cause analysis, การตัดสินใจ,
trade-off, ผลทดสอบจริง) เพื่อให้กลับมาทำงานต่อจากจุดเดิมได้เสมอแม้ข้ามเซสชัน

สำหรับสรุปการเปลี่ยนแปลงแบบย่อที่ผู้ใช้ปลายทาง/ผู้ตรวจสอบ Add-on Store จะเห็น ดูที่
[`CHANGELOG.md`](CHANGELOG.md) แทน — ไฟล์นี้เจาะลึกกว่ามากและมีไว้สำหรับทำงานต่อภายในเท่านั้น

**กติกาการทำงานต่อ (ให้ยึดถือเสมอในทุกรอบถัดไป):**

- แก้ไข "ไฟล์นี้" ต่อเนื่องทุกครั้ง (เพิ่มหัวข้อ session ใหม่ต่อท้าย ห้ามลบของเดิม ห้ามสร้างไฟล์บันทึกแยก)
- Source ที่แก้ไขจริงอยู่ใน addon package: `manifest.ini`, `globalPlugins/welcomeMessage.py`,
  `doc/en/readme.html`, `license.txt`
- **Version** ของ `manifest.ini` คงที่ตามที่ตกลงกันไว้ล่าสุดเสมอ จนกว่าจะมีคำสั่งเปลี่ยนเป็นอย่างอื่น
  (ปัจจุบัน: `2026.09.09`)
- ทุกครั้งที่มีการพัฒนา/แก้ไขต่อ ให้ **สร้างไฟล์ `.nvda-addon` ใหม่เสมอ** (ห้ามเขียนทับไฟล์เดิม)
  โดยเปลี่ยนเฉพาะชื่อไฟล์ให้สังเกตได้ว่าเป็นคนละรอบ ใช้รูปแบบ:
  `NVDA Startup Greeter V<version>-rN.nvda-addon` โดย N คือเลขรอบที่นับเพิ่มขึ้นเรื่อยๆ
  (ไฟล์แรกสุดของแต่ละ version เช่น `NVDA Startup Greeter V2026.09.09.nvda-addon` = ไม่มีเลขรอบ
  ถือเป็นรอบฐาน/r1 โดยปริยาย) ไฟล์เก่าของทุกรอบเก็บไว้ในโฟลเดอร์เดียวกันเสมอ ไม่ลบทิ้ง
- ให้ผู้ใช้ทดสอบด้วยการ **restart NVDA จริง** เสมอ (ไม่ใช่ "Reload plugins" ซึ่งจะไม่ยิง
  `core.postNvdaStartup` ซ้ำ)

---

## คำสั่งเริ่มต้นจากผู้ใช้ (2026-08-03, บันทึกไว้เพื่ออ้างอิง)

> ให้เข้าถึงโฟลเดอร์ `I:\backup cowork\nvda\NVDA Startup Greeter` จากนั้นศึกษา code
> `NVDA Startup Greeter V17.6.26p.nvda-addon` จากนั้นให้บันทึกการ update การพัฒนาในแต่ละครั้งไว้ด้วย
> เพื่อจะได้ทำงานต่อได้ และทำไฟล์ source เพื่อเตรียม up ขึ้น addon store ด้วย โดยให้ update ในไฟล์เดิม
> ตลอดในส่วนของ source จากนั้นแล้วเตรียมปรับปรุงและพัฒนาโดยมีรายละเอียดดังนี้
>
> 1. ให้เปลี่ยนเวอร์ชั่นเป็น 2026.08.09 เมื่อมีการพัฒนาต่อไปให้เปลี่ยนแค่ชื่อไฟล์โดยไม่ต้องเปลี่ยน
>    เวอร์ชั่น และให้โครงสร้างรูปแบบไฟล์และเนื้อหาเป็นไปตามการกำหนดของ NVDA ในเกณฑ์ล่าสุดปัจจุบัน
>    เพื่อที่จะสามารถนำ up ขึ้น addon store ได้
> 2. Addon ยังใช้โค้ดการเรียกหน้าต่างตั้งค่าแบบเก่า (`gui.SettingsPanel`) ให้ปรับเป็นปัจจุบันตามรูปแบบ
>    ล่าสุดของ NVDA ด้วย
> 3. *(ผู้ใช้พิมพ์ข้อความไม่จบ — ข้อ 3 ไม่เคยมีเนื้อหา ไม่เคยถูกเติมในภายหลัง)*

---

## Session 1 — เวอร์ชัน 2026.08.09 (2026-08-03)

**ไฟล์ต้นทาง:** `NVDA Startup Greeter V17.6.26p.nvda-addon` (2 ไฟล์: `manifest.ini`,
`globalPlugins/welcomeMessage.py`)
**ไฟล์ผลลัพธ์:** `NVDA Startup Greeter V2026.08.09.nvda-addon`

### สิ่งที่ตรวจสอบก่อนแก้

อ้างอิงจาก NVDA Developer Guide + source code จริงของ `nvaccess/nvda` บน GitHub:

- `manifest.ini` ต้องมี field ตรงตาม `AddonManifest.configspec` ใน
  `source/addonHandler/__init__.py` เท่านั้น (`name`, `summary`, `description`, `author`, `version`,
  `changelog`, `minimumNVDAVersion`, `lastTestedNVDAVersion`, `url`, `docFileName`, รวมถึง
  `brailleTables`/`symbolDictionaries`/`speechDictionaries` ถ้ามี) → `license` และ `updateChannel`
  ที่มีอยู่เดิมไม่ใช่ field มาตรฐานในปัจจุบัน จึงตัดออก
- ค่าทุก field ที่เป็น string ต้องใส่เครื่องหมายคำพูดครอบ
- `version` ต้องเป็นรูปแบบ `major.minor` หรือ `major.minor.patch` (ของเดิม `17.6.26p` มีตัวอักษรต่อท้าย
  ซึ่งไม่ถูกต้องตามเกณฑ์ store)
- `minimumNVDAVersion`/`lastTestedNVDAVersion` ต้องเป็น apiVersion ที่ถูกต้อง
- `from gui import SettingsPanel` ทำให้เกิด deprecation warning ใน `gui/__init__.py` (`__getattr__`
  คอย `log.warning`) → ต้อง import จาก `gui.settingsDialogs` แทน

### การเปลี่ยนแปลงที่ทำจริง

1. **`manifest.ini`**: `version: "17.6.26p" → "2026.08.09"`, ใส่เครื่องหมายคำพูดครอบทุก string field,
   ตัด `license`/`updateChannel` ออก, เพิ่ม `changelog`, `lastTestedNVDAVersion: "2099.0" → "2026.1.1"`,
   `minimumNVDAVersion` คงเดิม `"2024.2"`. ตรวจผ่าน `configobj` + `validate` (`True`)
2. **`globalPlugins/welcomeMessage.py`**: เปลี่ยน import เป็น `from gui.settingsDialogs import
   NVDASettingsDialog, SettingsPanel`, เพิ่ม comment log การอัปเดตไว้ในไฟล์, ไม่แก้ตรรกะหลัก

### ยังไม่ได้ทำ / รอ

- ข้อ 3 ของคำสั่งผู้ใช้ยังไม่มีเนื้อหา — รอคำสั่งเพิ่มเติม (ไม่เคยถูกเติมในภายหลัง)
- ยังไม่ได้ทดสอบรันจริงบน NVDA
- ข้อควรระวัง: NVDA Add-on Store กำหนดให้ version ต้องสูงขึ้นทุกครั้งที่ submit จริง วิธี "เปลี่ยนแค่
  ชื่อไฟล์" ใช้ได้กับการทดสอบ/แจกจ่ายภายใน แต่ต้องขยับ version จริงตอน submit ขึ้น store แต่ละรอบ

---

## Session 2 — คู่มือ (readme.html) + แก้ชื่อผู้เขียน (2026-08-03)

**คำสั่งผู้ใช้:** อยากให้รูปแบบคู่มือ/description ดูดีและมีโครงสร้างเหมือนที่ NVDA ปัจจุบันกำหนด และให้
ชื่อผู้เขียนเป็น Peem Narkkhwan อีเมล `sharetoyouaccess@gmail.com`

### สิ่งที่ตรวจสอบก่อนแก้

- อ้างอิง `nvaccess/AddonTemplate` (ย้ายมาจาก `nvdaaddons/AddonTemplate` ที่ archive แล้วตั้งแต่
  1 ธ.ค. 2025) และ Developer Guide ส่วน "Add-on Documentation": คู่มือต้องอยู่ที่
  `doc/<lang>/<docFileName>` แล้วอ้างอิงผ่าน manifest field `docFileName`
- รูปแบบหน้าตาคู่มืออ้างอิงจาก `style.css` ของ template ทางการ (Verdana, h1/h2 จัดกลาง, `dl`/`dt`/`dd`)
- `author` แนะนำรูปแบบ `"Full Name <email>"`

### การเปลี่ยนแปลงที่ทำจริง

1. **`manifest.ini`**: `author → "Peem Narkkhwan <sharetoyouaccess@gmail.com>"`, ปรับ `description`
   ให้ชัดเจนขึ้น, เพิ่ม `docFileName = "readme.html"`, เพิ่ม changelog entry, ตรวจผ่านอีกครั้ง
2. เพิ่ม **`doc/en/readme.html`** ฉบับเต็ม: Introduction, Features, Settings, Changelog,
   Author and contact, License → แพ็กเข้า `NVDA Startup Greeter V2026.08.09.nvda-addon`

### หมายเหตุสำคัญ

ระหว่างรอบนี้พบว่าไฟล์ต้นฉบับ `NVDA Startup Greeter V17.6.26p.nvda-addon` หายไปจากโฟลเดอร์แล้ว
(ตรวจสอบยืนยันแล้วว่าไม่มีคำสั่งลบจากฝั่งเราในเซสชันนี้ ไม่ทราบสาเหตุแน่ชัด) เนื้อหาต้นฉบับยังอยู่ใน
บันทึกการสนทนา สร้างขึ้นใหม่ได้หากต้องการ

---

## Session 3 — ออกแบบใหม่ให้อ่านข้อความต้อนรับเสถียร 100% และไม่หน่วง NVDA (2026-08-03)

**คำสั่งผู้ใช้:** ต้องการออกแบบใหม่/ปรับปรุงให้ดีที่สุด โดยมีเงื่อนไข: (1) ห้ามทำให้ NVDA หน่วง
(2) ต้องได้ยินข้อความจาก add-on นี้ก่อนเสมอทุกครั้งที่เปิด NVDA อย่างเสถียร ห้ามอ่านบ้างไม่อ่านบ้าง

### การวิเคราะห์ (อ้างอิงซอร์สจริง: `source/core.py`, `source/speech/speech.py`,
`source/speech/priorities.py`)

พบบั๊ก/จุดอ่อน 3 จุดในโค้ดเดิม:

1. **จุดเรียก:** เดิมใช้ `wx.CallLater(300, self._announce)` ยิงจาก `GlobalPlugin.__init__` ซึ่งทำงาน
   *ระหว่าง* NVDA กำลังเริ่มระบบ (ก่อน speech/GUI/focus จะเสถียร) — สาเหตุของอาการ "อ่านบ้างไม่อ่านบ้าง"
   **แก้ไข:** เปลี่ยนไปใช้ `core.postNvdaStartup` extension point ของ NVDA เอง ซึ่งยิงเพียงครั้งเดียว
   หลังจาก config, speech, GUI และการประกาศโฟกัสเริ่มต้นเสร็จสมบูรณ์แล้วเท่านั้น
2. **จุดหน่วง (บั๊กจริง ทำให้ NVDA ค้าง):** เดิมมี `speech.waitUntilDone()` ซึ่งไม่มีอยู่จริงใน public
   API ของ speech module เลย → เข้า `except AttributeError` เสมอ → เรียก
   `time.sleep(len(message)/17.0)` บน **main thread** ของ NVDA → ค้างทั้ง UI/input นานหลายวินาที
   **แก้ไข:** ตัดโค้ดส่วนนี้ออกทั้งหมด (`speakMessage` เป็น asynchronous อยู่แล้ว)
3. **จุดความเสถียร:** เดิมพูดด้วย priority ปกติ (NORMAL) ซึ่งถูก `speech.cancelSpeech()` จากเหตุการณ์
   อื่นล้างทิ้งได้ **แก้ไข:** พูดด้วย `speech.Spri.NOW` — แทรกเสียง priority ต่ำกว่าที่กำลังเล่นอยู่ทันที
   เสียงที่ถูกแทรกจะเล่นต่ออัตโนมัติหลังจากนั้น ไม่หายไปถาวร

### การเปลี่ยนแปลงที่ทำจริง

- ลบ `import time`, เพิ่ม `import core`, `import braille`
- `__init__`: `wx.CallLater(300, self._announce)` → `core.postNvdaStartup.register(self._announce)`
- `terminate`: เพิ่ม `core.postNvdaStartup.unregister(self._announce)`
- `_announce`: ตัด waitUntilDone/sleep ออก, เรียก `speech.speakMessage(message,
  priority=speech.Spri.NOW)`, เพิ่ม `braille.handler.message(message)` (ห่อ try/except)
- รองรับการแปลภาษาด้วย `_()`
- ตรวจสอบผ่าน `python3 -m py_compile` + `ast.parse`
- แพ็กเป็น `NVDA Startup Greeter V2026.08.09.nvda-addon` (แทนที่ไฟล์เดิม เนื่องจากยังไม่เคย submit จริง)

**ผลลัพธ์ที่คาดหวัง:** พูดครั้งเดียวทุกครั้งที่ NVDA เปิดจริง, ได้ยินก่อนเสมอ, ไม่ทำให้ NVDA ค้าง

---

## Session 4 — ผู้ใช้ทดสอบแล้วไม่ได้ยินเสียงเลย: สร้างรุ่นวินิจฉัยปัญหา r2 (2026-08-03)

**รายงานจากผู้ใช้:** ติดตั้ง, enable, restart NVDA ทั้งหมดแล้ว แต่ไม่ได้ยินเสียงทักทายเลย

### การไล่หาสาเหตุ

1. สงสัยว่าทดสอบด้วย "Reload plugins" แทนการ restart จริง (`core.postNvdaStartup` ไม่ยิงซ้ำตอน
   reload) → ผู้ใช้ยืนยัน restart จริง ตัดทฤษฎีนี้ทิ้ง
2. ตรวจ `nvda.log` 2 รอบ (ก่อน/หลังติดตั้ง) → ไม่เจอคำว่า `nvdaStartupGreeter`/`welcomeMessage` เลย
   แม้แต่บรรทัดเดียว ทั้งที่ add-on อื่นของผู้ใช้ log ตอนโหลดให้เห็นหมด
3. **จุดอ่อนของการวินิจฉัย:** โค้ดของเราไม่เคย `log.info`/`log.error` อะไรเลยตอนทำงานปกติ →
   แยกไม่ออกจาก log ว่า "โหลดสำเร็จแต่เงียบ" กับ "โหลดไม่สำเร็จแบบเงียบ" อันไหนกันแน่
4. ผู้ใช้สังเกตเพิ่ม: "เหมือนอ่านข้อความไม่ทันหรือเปล่าไม่รู้" (ยังไม่ยืนยันชัดเจน ณ จุดนี้)

### การเปลี่ยนแปลงที่ทำจริง (เพื่อวินิจฉัย ไม่ใช่แก้ฟีเจอร์)

- `from logHandler import log`, prefix ข้อความ log ว่า `"NVDA Startup Greeter:"` (หาเจอง่ายด้วย Ctrl+F,
  `log.info` ขึ้นเสมอที่ log level default ของ NVDA)
- เพิ่ม `log.info` ทุกจุดสำคัญ: import module, ต้น `__init__`, หลัง register settings panel, หลัง
  register `postNvdaStartup`, ต้น `_announce`, ค่า `enabled`, ข้อความก่อนพูด, ยืนยัน `speakMessage`
  คืนค่าไม่ error
- ห่อ `__init__` และ `_announce` ด้วย `try/except` → `log.error(..., exc_info=True)` เสมอ
- แพ็กเป็น `NVDA Startup Greeter V2026.08.09-r2.nvda-addon`

**ขั้นตอนถัดไปที่รอผู้ใช้:** ติดตั้ง r2, restart จริง, ส่ง log ที่ค้นคำว่า `"NVDA Startup Greeter:"`

---

## Session 5 — โค้ดทำงานถูกต้อง 100% แต่เสียงไม่ออก: เพิ่ม delay รอ audio/synth (2026-08-03)

**ผลจาก log ของ r2:** เจอ log ครบทุกบรรทัดตามลำดับที่คาดไว้เป๊ะๆ จนถึง `speakMessage call returned
without error` — **ไม่มี exception เลยสักจุด** แต่ผู้ใช้ยังไม่ได้ยินเสียง → บั๊กไม่ได้อยู่ที่ logic ของเรา
แต่อยู่ "ปลายทาง" หลังจาก NVDA รับข้อความเข้าคิวเสียงไปแล้ว

**ข้อสังเกตจาก log:** ใกล้เวลาที่เราพูด มี `"Loaded synthDriver MultiLang"` ขึ้นซ้ำเป็นรอบที่ 2
(synth ไม่ใช่ตัว default) และ add-on อื่นของผู้ใช้ (`audioManager`, `audioDuckingEnabler`) กำลังยุ่งกับ
อุปกรณ์เสียงตอน startup พอดี — รูปแบบบั๊กที่รู้จักกันดี: utterance แรกที่ส่งไปตอน synth/audio device
กำลัง (re)initialize อาจถูกกลืนหายไปเงียบๆ แม้ software queue จะรับคำสั่งไปแล้วโดยไม่ error

### แนวทางแก้ไข

- แยก handler เป็น `_onPostNvdaStartup` (log + ตั้งเวลา) แทนที่จะเรียก `_announce` ตรงๆ
- เพิ่ม `POST_STARTUP_SPEECH_DELAY_MS = 1500` + `wx.CallLater(1500, self._announce)` ให้เวลา
  audio/synth pipeline ตั้งตัวก่อน (ยังคงผูกกับ `postNvdaStartup` เหมือนเดิม แค่เพิ่ม buffer)
- เพิ่ม diagnostic: หลัง speakMessage 200ms เช็ค `speech.isSpeaking()` แล้ว log ผล (ห่อ try/except)
- แพ็กเป็น `NVDA Startup Greeter V2026.08.09-r3.nvda-addon`

---

## Session 6 — r3 ได้ยินแล้วแต่มาทีหลัง desktop: แก้เป็น retry แทน delay คงที่ (2026-08-03)

**ผลทดสอบ r3:** ได้ยินเสียงของ add-on แล้ว (ไม่เงียบเหมือน r2) แต่ NVDA อ่านของ desktop/focus ก่อน
แล้วค่อยอ่านของเราทีหลัง

**วิเคราะห์ log:** `postNvdaStartup` ยิงที่ 51.360 (ห่างจาก "NVDA initialized" 50.536 ~824ms, มี
watchdog freeze recovery เกิดพอดีช่วงนั้นด้วย) + delay 1500ms → พูดจริงที่ 52.870 ห่างจาก initialized
เกือบ 2.3 วินาที การอ่าน focus เริ่มต้นจบไปนานแล้วก่อนเราพูด ดังนั้น `Spri.NOW` จึงไม่มีอะไรให้ "แทรก"
(มีผลกับเสียงที่กำลังเล่นอยู่ ณ ขณะสั่งพูดเท่านั้น ย้อนแทรกเสียงที่จบไปแล้วไม่ได้)

**ทฤษฎีใหม่เรื่อง "เงียบสนิท" ใน r2:** ไม่ใช่เรื่อง audio device ไม่พร้อม แต่เป็นเพราะ
`speech.cancelSpeech()` ที่ NVDA เรียกตอนประกาศ object ที่ได้โฟกัสเริ่มต้น (pattern ปกติของ screen
reader) ไปชนกับข้อความของเราที่เพิ่งเข้าคิวด้วย `Spri.NOW` แต่ยังไม่ทันเริ่มเล่นจริง — `cancelSpeech()`
ล้างคิวทั้งหมดโดยไม่สนใจ priority เลย (`Spri.NOW` กันแค่การถูก "แทรก" จากเสียง priority ต่ำกว่า ไม่ได้
กันการถูก `cancelSpeech()` แบบเต็มรูปแบบ) — อธิบายได้ครบทั้ง 2 กรณี: พูดทันที (r2) = โดนกลืนหายเงียบ,
พูดหลังหน่วง 1.5s (r3) = รอด แต่กลายเป็นพูดทีหลัง

### แนวทางแก้ไข

- ลดดีเลย์แรกกลับมาเหลือ **200ms** (`POST_STARTUP_INITIAL_DELAY_MS`)
- เพิ่มระบบ **retry**: พูดด้วย `Spri.NOW` แล้วหลัง 200ms (`RETRY_CHECK_INTERVAL_MS`) เช็ค
  `speech.isSpeaking()` ถ้า `False` (โดนกลืนไปแล้ว) พูดซ้ำทันที วนสูงสุด 5 รอบ (`MAX_SPEAK_ATTEMPTS`)
- แยกฟังก์ชัน: `_onPostNvdaStartup` → `_prepareAndSpeak` (สร้างข้อความ+braille) → `_speakAttempt`
  (พูด+นับ retry) → `_checkSpokenOrRetry` (เช็คแล้ววนกลับ)
- แพ็กเป็น `NVDA Startup Greeter V2026.08.09-r4.nvda-addon`

---

## Session 7 — r4: เหลือแค่เศษคำ "de-" หลุดมานิดเดียว (2026-08-03)

**ผลทดสอบ r4:** ดีขึ้นมากจาก r3 — มีคำว่า "desktop" หลุดมานิดเดียว แล้วตามด้วยข้อความต้อนรับเต็มๆ ทันที

**วิเคราะห์ log:** `postNvdaStartup` ที่ 03.901, `_prepareAndSpeak` ที่ 04.100 (ตรงดีเลย์ 200ms),
`speakMessage` เรียกที่ 04.101 คืนค่าไม่ error ที่ 04.111 — **ไม่มี log ของ `_checkSpokenOrRetry`
ปรากฏเลย** ทั้งที่ควรมีหลัง 200ms → `speech.isSpeaking()` บน NVDA 2026.1.1 ของผู้ใช้ น่าจะ raise
exception (เข้า branch except ที่ตอนนั้น log แค่ระดับ debug ซึ่งไม่โชว์ปกติ) → retry safety net
"เงียบและไม่ทำงาน" ในรอบนี้ แต่บังเอิญไม่จำเป็นต้องใช้เพราะรอบแรกติดผลแล้ว

**สรุปเรื่องเศษคำที่หลุดมา:** พฤติกรรมปกติของ interrupt-based priority speech ใดๆ — เสียงที่ถูกส่งไป
เล่นที่ลำโพงแล้วบางส่วน ไม่สามารถ "ย้อนกลับ" เอาออกได้ เป็นข้อจำกัดฮาร์ดแวร์/driver ไม่ใช่บั๊กของ add-on

### การเปลี่ยนแปลงที่ทำจริง (เล็กน้อย)

- ยกระดับ log ตอน `isSpeaking()` raise exception จาก `log.debug` → `log.info` (พร้อม `exc_info=True`)
- แพ็กเป็น `NVDA Startup Greeter V2026.08.09-r5.nvda-addon`

**สถานะ:** ใช้งานได้ดีมากแล้ว รอถามผู้ใช้ว่าพอใจหรือต้องการลดเศษเสียงต่อ (แลกกับความเสี่ยงเงียบสนิท) →
**ผู้ใช้เลือก "อยากให้ลองลดเศษเสียงที่หลุดมาให้น้อยลงอีก"**

---

## Session 8 — พยายามลดเศษเสียงที่หลุดมาให้น้อยลงอีก (2026-08-03)

อ่าน `source/speech/manager.py` (`SpeechManager`) เพิ่มเติมเพื่อเข้าใจกลไกตอนพูดด้วย `Spri.NOW` จริงๆ

### สิ่งที่พบ

- ตอนเรียก `speech.speak(..., priority=Spri.NOW)` ถ้าเป็นข้อความแรกที่คิวระดับ NOW จะเรียก
  `getSynth().cancel()` ทันทีแล้วเริ่มพูดใหม่ทันที — กลไกที่ทำให้เศษเสียงเดิม (เช่น "de-") หลุดออกมา:
  เสียงที่ synth เพิ่งส่งไปเล่นที่ลำโพงไปแล้วก่อนโดนสั่ง cancel ดึงกลับไม่ได้ ทางเดียวที่ลดเศษได้คือเรียก
  `speakMessage` ให้เร็วขึ้น
- `speech.isSpeaking()` บนเครื่องผู้ใช้ (NVDA 2026.1.1) น่าจะ raise exception จริง → retry safety net
  เงียบไม่ทำงานจริงโดยไม่มีใครรู้

### การเปลี่ยนแปลงที่ทำจริง

1. ลด `POST_STARTUP_INITIAL_DELAY_MS` **200 → 100** (0ms = เงียบสนิท, 200ms = สำเร็จมีเศษหลุดนิดเดียว
   จึงเลือกจุดกึ่งกลางที่ปลอดภัยกว่าดิ่งกลับไป 0 ตรงๆ)
2. เพิ่มเมธอด `_isSpeechActive()`: ลองเช็ค `speech.isSpeaking()` ก่อน ถ้า error fallback ไปเช็ค
   `speech._manager._hasNoMoreSpeech()` (internal object ที่ export ที่ระดับ package `speech` อยู่แล้ว)
   ถ้าทั้งสองทางล้มเหลว ถือว่า "ไม่ทราบ" แล้วไม่ retry
3. ปรับ `_checkSpokenOrRetry` ให้เรียก `_isSpeechActive()` แทน `isSpeaking()` ตรงๆ
4. แพ็กเป็น `NVDA Startup Greeter V2026.08.09-r6.nvda-addon`

---

## Session 9 — r6 ยังมีเศษเสียงหลุดมานิดนึง: ลดดีเลย์เหลือ 60ms (2026-08-03)

**ผลทดสอบ r6:** "มีเสียงรั่วเข้ามานิดนึง" (ดีขึ้นกว่า r4/r5 แต่ยังไม่หมดสนิท) — ถามผู้ใช้ว่าจะหยุดที่ r6
หรือลองลดดีเลย์ต่อ (50-70ms) พร้อมแจ้งความเสี่ยงเพิ่มชัดเจน → **ผู้ใช้เลือก "ลองอีกนิด (ลดเหลือ
50-70ms)"**

### การเปลี่ยนแปลงที่ทำจริง

1. ลด `POST_STARTUP_INITIAL_DELAY_MS` **100 → 60**
2. ลด `RETRY_CHECK_INTERVAL_MS` **200 → 100** ให้ retry safety net ตรวจพบและพูดซ้ำได้เร็วขึ้น
3. เพิ่ม comment อธิบาย trade-off: ไม่มีค่าดีเลย์ที่ "ถูกต้อง" ตายตัว มีแต่จุดสมดุล
4. แพ็กเป็น `NVDA Startup Greeter V2026.08.09-r7.nvda-addon`

---

## Session 10 — ตรวจสอบความพร้อมขึ้น Add-on Store ทุกส่วน (2026-08-03)

**คำสั่งผู้ใช้:** ตรวจว่าคู่มือมีไฟล์ครบตามโครงสร้างหรือไม่ เนื้อหา update ครบถ้วนหรือยัง และตรวจสอบกับ
ข้อกำหนดปัจจุบันของ NVDA ในทุกส่วน แล้วทำไฟล์ให้พร้อมสำหรับนำขึ้น Add-on Store

### สิ่งที่ตรวจสอบ (ค้นจาก GitHub ของ nvaccess)

- **`nvaccess/addon-datastore`** `docs/submitters/submissionGuide.md` — การ submit จริงทำผ่าน GitHub
  issue form (ไม่ใช่แค่ manifest.ini) ระบบ generate JSON metadata จาก issue form + manifest แล้วเปิด
  PR อัตโนมัติ
- **`docs/submitters/jsonMetadata.md`** + **`addon-datastore-validation`**
  `_validate/addonVersion_schema.json` — field ที่ต้องกรอกตอน submit จริง (นอกเหนือจาก manifest.ini):
  `addonId`, `channel` (stable/beta/dev), `publisher`, `homepage`, `minNVDAVersion`,
  `lastTestedVersion`, `URL` (ลิงก์ดาวน์โหลด `.nvda-addon` จริง เช่น GitHub Release), `sha256`,
  `sourceURL` (ลิงก์ source code ให้ reviewer ตรวจ), `license` (ชื่อย่อ เช่น "GPL v2"), `licenseURL`
- **`addon-datastore-transform`** `nvdaAPIVersions.json` (รายการ apiVersion ที่ระบบยอมรับจริง) —
  `"2026.1.1"` (patch) ไม่มีอยู่ในรายการ มีแค่ `"2026.1"` และ `"2026.2"` (ทั้งคู่ยังมาร์ก
  `"experimental": true`) → `lastTestedNVDAVersion = "2026.1.1"` มีความเสี่ยงไม่ตรงกับรายการที่ระบบ
  validate รู้จักตอน submit จริง
- **`accessolutions/nvda-addon-template`** (fork ของ `nvdaaddons/AddonTemplate` ที่ archive แล้ว) —
  ยืนยัน field มาตรฐานของ manifest.ini ตรงกับที่มีอยู่ครบถ้วน และควรมี license file แยก (`COPYING.txt`)
  ตามธรรมเนียม

### ผลตรวจสอบคู่มือ

โครงสร้างไฟล์ (`doc/en/readme.html`) ถูกต้องครบ แต่เนื้อหา Changelog ยัง sync แค่ session 1-3 ยังไม่มี
สรุปการปรับจูนความเสถียร (session 4-9/r2-r7) และยังไม่มีหัวข้อ "Known limitations"

### การเปลี่ยนแปลงที่ทำจริง

1. **`doc/en/readme.html`**: เพิ่มหัวข้อ "Known limitations" (เศษเสียงหลุดมานิดหน่อย = ข้อจำกัดของ
   interrupt-based speech ทั่วไป ไม่ใช่บั๊ก), เพิ่ม bullet สรุปการปรับจูน r2-r7 ด้วยภาษาที่เหมาะกับ
   ผู้ใช้ทั่วไป, อัปเดต License section ให้อ้างอิง `license.txt`
2. **`manifest.ini`**: `lastTestedNVDAVersion: "2026.1.1" → "2026.1"` (ตัด patch ให้ตรงกับ
   `nvdaAPIVersions.json` จริง), เพิ่ม changelog entry, ตรวจผ่านอีกครั้ง + เขียนสคริปต์เสริมตรวจ
   `minimumNVDAVersion`/`lastTestedNVDAVersion` เทียบกับ `nvdaAPIVersions.json` โดยตรง (ผ่านทั้งคู่)
3. เพิ่มไฟล์ **`license.txt`** ที่ root ของ addon source (ตามธรรมเนียม template ทางการ) ระบุการ
   ประกาศ public domain แบบเต็ม
4. แพ็กเป็น `NVDA Startup Greeter V2026.08.09-r8.nvda-addon` (4 ไฟล์: manifest.ini,
   globalPlugins/welcomeMessage.py, doc/en/readme.html, license.txt)
   **SHA256:** `bbe34eeaba617143c54ced9ab2693e71ded5843ac12584bb7f774d2d30f9c854`

### สิ่งที่ "พร้อมแล้ว" vs "ยังไม่พร้อม"

**พร้อมแล้ว:** ตัวไฟล์ `.nvda-addon` เอง (manifest + โค้ด + คู่มือ + license) ถูกต้องตามข้อกำหนดของ
NVDA ทุกจุดที่ตรวจสอบได้

**ยังไม่พร้อม** (ต้องให้ผู้ใช้ทำเอง เพราะต้องใช้บัญชี/พื้นที่โฮสต์ของผู้ใช้):

1. ต้องมี public source code repository (แนะนำ GitHub) เพื่อใช้เป็น `sourceURL`
2. ต้อง publish ไฟล์ `.nvda-addon` จริง (เช่น GitHub Release) เพื่อให้ได้ URL ดาวน์โหลดถาวร
3. ต้องกรอกข้อมูลเพิ่มตอน submit ผ่าน GitHub issue form: `publisher`, `homepage`, `channel`
   (แนะนำพิจารณา `beta` เนื่องจาก `2026.1` ยังมาร์ก experimental), `license` (เช่น "Public Domain"),
   `licenseURL`
4. `sha256` คำนวณให้แล้วด้านบน แต่ต้องคำนวณใหม่ทุกครั้งถ้ามีการแก้ไฟล์อีก

---

## Session 11 — ตรวจทานซ้ำจากซอร์สโค้ดจริงของ NVDA (master) ทุกจุด (2026-08-03)

**คำสั่งผู้ใช้:** "ลองเช็คให้ชัวจากต้นทางของข้อกำหนดการทำ addon จาก nvda ที่เป็นข้อมูลปัจจุบันนะครับ
เพื่อที่จะไม่ให้ผิดพลาด" — ตรวจสอบทุกจุดจากซอร์สโค้ดจริงของ NVDA โดยตรง ไม่ใช่แค่เอกสาร/เทมเพลต

ดึงไฟล์ซอร์สจริงจาก `nvaccess/nvda` branch `master` มาตรวจสอบทีละจุด:

1. **`source/addonHandler/__init__.py`** — ดึง configspec จริงของ `AddonManifest` มาเทียบกับ
   `manifest.ini` แบบตรงตัวอักษร พบว่าตรงกัน 100% เขียนสคริปต์ `validate_manifest_authoritative.py`
   คัดลอก configspec และ `validate_apiVersionString` มาจากซอร์สจริงเป๊ะๆ → ผลลัพธ์ **PASS** ทุกเงื่อนไข
2. **`source/addonAPIVersion.py`** — พบข้อมูลสำคัญที่ยังไม่เคยตรวจ: `BACK_COMPAT_TO` ของ NVDA master
   ปัจจุบันคือ `(2026, 1, 0)` และ `source/addonHandler/addonVersionCheck.py` ยืนยันว่า
   `isAddonCompatible = (minimumNVDAVersion <= NVDA ปัจจุบัน) AND (lastTestedNVDAVersion >=
   BACK_COMPAT_TO)` → `lastTestedNVDAVersion` ต้อง `>= 2026.1` จริงๆ ไม่ใช่แค่เรื่อง "สวยงามตอน
   submit" แต่เป็นเงื่อนไขจริงที่ NVDA ใช้ตัดสินว่า add-on จะโหลด/enable ได้หรือไม่ การปรับใน Session 10
   เป็น `"2026.1"` (`=2026,1,0`) จึงถูกต้องพอดีที่ขอบเขตล่าง (ตรวจสอบจำลอง NVDA 2026.1.1:
   `isAddonCompatible = True`)
3. **`source/gui/__init__.py`** — ยืนยัน `gui.__getattr__` ยังคง `log.warning` "deprecated" เมื่อ import
   `SettingsPanel` จาก `gui` โดยตรง และต้อง import จาก `gui.settingsDialogs` → โค้ดเราถูกต้องแล้ว
4. **`source/gui/settingsDialogs.py`** — ตรวจ class `SettingsPanel` จริง: ยืนยัน `title`/
   `panelDescription`, `@abstractmethod makeSettings(self, sizer)`, `@abstractmethod onSave(self)`
   ตรงกับที่ `StartupAnnouncerPanel` ใช้ทุกจุด และ `NVDASettingsDialog.categoryClasses` เป็น list
   ระดับคลาสที่ append/remove ได้ตรงตามโค้ดเรา
5. **`source/core.py`** — ยืนยัน `core.postNvdaStartup = extensionPoints.Action()` ยังอยู่ และพบลำดับ
   เหตุการณ์จริงใน `core.main()`: NVDA คิว `_setInitialFocus` (การประกาศโฟกัสเริ่มต้น) ไว้ *ก่อน* คิว
   `postNvdaStartup.notify()` เสมอ (ทำหลัง watchdog/updateCheck ฯลฯ initialize เสร็จ) — ยืนยันเป๊ะๆ ว่า
   ทำไมการประกาศโฟกัสเริ่มต้นจึงมาก่อน `postNvdaStartup` ของเราเสมอโดยการออกแบบของ NVDA เอง ไม่ใช่บั๊ก
6. **`source/speech/__init__.py`**, **`priorities.py`**, **`manager.py`** — ยืนยัน `speech.Spri`,
   `speech.speakMessage`, `speech._manager`, `SpeechManager._hasNoMoreSpeech()`
   (`return self._curPriQueue is None`) ยังมีอยู่จริงและพฤติกรรมตรงตามที่วิเคราะห์ไว้ใน Session 8 ทุกจุด
   และ `braille.handler.message(...)` ที่เราใช้เป็น pattern เดียวกับที่ NVDA เองใช้พูด "NVDA started"
   ใน `core.main()` พอดี (ห่อ try/except เหมือนกัน)
   *ข้อสังเกตเล็กน้อยที่ยังไม่ฟันธง:* `speech/__init__.py` import ชื่อ `isSpeaking` จาก `.speech` แต่
   ค้นในเนื้อหาไฟล์ `speech/speech.py` ที่ดึงมาไม่พบนิยามฟังก์ชันนี้เลย — ไม่กระทบการทำงานของเรา เพราะ
   โค้ดมี try/except พร้อม fallback อยู่แล้ว แต่บันทึกไว้เป็นข้อสังเกต ไม่ใช่ข้อสรุปที่ยืนยันได้ 100%

**สรุป:** ไม่พบข้อผิดพลาดใหม่ที่ต้องแก้เพิ่มจาก r8 ทุกจุดตรงกับซอร์สโค้ดจริงปัจจุบันทั้งหมด ไม่ต้องออก
ไฟล์ใหม่รอบนี้

---

## Session 12 — ปรับ description และ changelog ให้เหมาะกับการ submit เวอร์ชันแรก (2026-08-03)

**คำสั่งผู้ใช้:** "ในส่วนของ discription ไม่ต้องพูดถึงเสียงหลุดใดๆ เพราะไม่สำคัญ แค่เน้นให้เห็นถึง
คุณสมบัติและแนวทางการใช้งานที่โดดเด่นน่าจะดีกว่า ส่วน changelog ผมอยากให้เขียนสั้นๆ เพราะอันนี้เป็น
เวอร์ชันแรกที่จะ up ขึ้น addon store"

### การเปลี่ยนแปลงที่ทำจริง

1. **`doc/en/readme.html`**: ลบหัวข้อ "Known limitations" ทั้งหมด, เขียน Introduction/Features ใหม่ให้
   เน้นจุดเด่น/ประโยชน์การใช้งาน (ไม่กล่าวถึงปัญหาทางเทคนิค), เขียน Changelog ใหม่แบบสั้น "Initial
   release" (5 บรรทัด) แทนรายการยาวที่สรุป r2-r8
2. **`manifest.ini`**: `description` เขียนใหม่เน้นจุดขาย, `changelog` แทนที่ด้วยเวอร์ชันสั้นตรงกับ
   readme.html, ตรวจผ่าน `validate_manifest_authoritative.py` อีกครั้ง (PASS รวม compatibility gate)
3. แพ็กเป็น `NVDA Startup Greeter V2026.08.09-r9.nvda-addon`
   **SHA256:** `9b88b628ebb02f39504651d5457f9dddbcf349d1e70986bd08bc1beb9d6e046c`

**หมายเหตุ:** ประวัติแบบละเอียด (r2-r8, root cause, tuning ฯลฯ) ยังคงเก็บรักษาไว้ครบในไฟล์นี้ เพียงแต่
ตัดออกจาก description/changelog สาธารณะที่ผู้ใช้ปลายทาง/ผู้ตรวจสอบ store จะเห็น

---

## Session 13 — เริ่มเวอร์ชัน 2026.09.09: ฟีเจอร์สุ่มข้อความหลายอัน (2026-08-03)

**คำสั่งผู้ใช้:** ปิดเวอร์ชัน 2026.08.09 ไว้ที่ r9 เริ่มเวอร์ชันใหม่ `2026.09.09` เป็นไฟล์ใหม่ ฟีเจอร์แรก
คือให้สุ่มอ่านข้อความจากรายการที่ผู้ใช้เขียนไว้ (ขอให้นำเสนอรูปแบบก่อนทำจริง)

### การตัดสินใจออกแบบ (ผ่าน AskUserQuestion)

1. **รูปแบบกรอกข้อความ:** เลือก **"รายการ list พร้อมปุ่มเพิ่ม/แก้ไข/ลบ"** (ไม่ใช่ multiline textbox
   หรือบรรทัดเดียวคั่นด้วยเครื่องหมาย)
2. **วิธีสุ่มแต่ละครั้งที่เปิด NVDA:** เลือก **"สุ่มแบบไม่ซ้ำอันก่อนหน้า"** (ไม่ใช่สุ่มล้วนๆ ที่อาจซ้ำ
   ติดกันได้ และไม่ใช่การวนตามลำดับที่พิมพ์ไว้)
3. **ความสัมพันธ์กับคำทักทายตามช่วงเวลาเดิม:** เลือก **"แทนที่ทั้งหมด"** (มีข้อความในรายการ = ไม่ใช้
   คำทักทายตามช่วงเวลาเลย, รายการว่าง = กลับไปใช้คำทักทายตามช่วงเวลาเหมือนเดิม)

### การเปลี่ยนแปลงที่ทำจริงใน `globalPlugins/welcomeMessage.py`

1. เพิ่ม `import random`
2. ขยาย `confspec` ของ `config["startupAnnouncer"]`:
   - `"customMessages": "string_list(default=list())"` — รายการข้อความใหม่
   - `"lastSpokenCustomMessage": "string(default='')"` — จำข้อความล่าสุดที่พูดไป กันสุ่มซ้ำติดกัน
   - `"customMessage"` (single string เดิม) ยังอยู่ใน confspec แต่ใช้เพื่อ migrate ครั้งเดียวเท่านั้น
3. เพิ่มเมธอด `_migrateLegacyCustomMessage()` ใน `GlobalPlugin.__init__`: ถ้า `customMessage` เดิมมีค่า
   และ `customMessages` ยังว่าง (เพิ่งอัปเกรดจากเวอร์ชันก่อน 2026.09.09) → copy เข้าเป็นสมาชิกแรกของ
   `customMessages` แล้วเคลียร์ `customMessage` ทิ้ง (ทำครั้งเดียว)
4. เพิ่มเมธอด `_chooseCustomMessage()`: `customMessages` ว่าง → คืน `None` (ใช้คำทักทายตามช่วงเวลา);
   มีข้อความ → สุ่มเลือกจากรายการที่ตัด `lastSpokenCustomMessage` ออกก่อน (ถ้าตัดแล้วว่างเพราะมีข้อความ
   เดียว กลับไปสุ่มจากรายการเต็ม) แล้วบันทึกข้อความที่เลือกเป็น `lastSpokenCustomMessage` ใหม่
   *ทดสอบ logic แยกต่างหาก* (จำลองด้วย Python สุ่ม 3,000 รอบ): ข้อความเดียว = ไม่มีปัญหา, สองข้อความ =
   สลับกันทุกครั้งไม่ซ้ำติดกันเลย, สามข้อความ = กระจายใกล้เคียงกันทางสถิติ (~990-1015 ครั้งต่ออัน)
5. ปรับ `StartupAnnouncerPanel.makeSettings`: แทนที่ `wx.TextCtrl` เดี่ยวด้วย `wx.ListBox` พร้อมปุ่ม
   Add.../Edit.../Remove (ใช้ `gui.guiHelper.ButtonHelper` แบบเดียวกับที่ NVDA เองใช้ในหน้า Settings
   อื่นๆ — ตรวจสอบ API จริงจากเอกสาร wxPython Phoenix ยืนยันว่า `GetStrings`/`GetString`/`SetString`/
   `Append`/`Delete`/`GetSelection`/`wx.NOT_FOUND` ถูกต้องตรงกับที่ใช้)
   - `onAddMessage`/`onEditMessage` ใช้ `wx.TextEntryDialog` แบบ context manager (`with ... as dlg:`)
     เหมือน pattern ที่ NVDA เองใช้ใน `gui/guiHelper.py`
     (`PathSelectionHelper.onBrowseForDirectory` ใช้ `wx.DirDialog` แบบเดียวกัน)
   - `onSave` เขียน `customMessages` กลับเข้า config จาก listbox ทั้งหมด และเคลียร์ `customMessage`
     เดิมทิ้ง (กันไม่ให้ migrate ซ้ำ)
6. ตรวจสอบผ่าน `python3 -m py_compile` และ `validate_manifest_authoritative.py` (PASS ทุกเงื่อนไข)

### `manifest.ini`

- `version`: `"2026.08.09" → "2026.09.09"`
- `description`: ปรับให้กล่าวถึงฟีเจอร์ข้อความหลายอันที่สุ่มไม่ซ้ำ
- `changelog`: เพิ่ม section ใหม่ `"= 2026.09.09 ="` ไว้บนสุด (เก็บ section `2026.08.09` เดิมไว้ด้านล่าง)

### `doc/en/readme.html`

ปรับ Intro/Features ให้กล่าวถึงฟีเจอร์ข้อความหลายอัน, ปรับ Settings section ให้อธิบายปุ่ม
Add/Edit/Remove, เพิ่ม h3 `"2026.09.09"` ใหม่ในหัวข้อ Changelog

แพ็กเป็นไฟล์ฐานใหม่ (ไม่มีเลขรอบต่อท้าย เพราะเป็นไฟล์แรกของเวอร์ชันนี้):
`NVDA Startup Greeter V2026.09.09.nvda-addon`
**SHA256:** `256722e40f51e966589052f55993b295a65e6616019a8248982316d25d560ad9`

### ขั้นตอนถัดไปที่รอผู้ใช้ (ณ ตอนนั้น)

1. ติดตั้งทับเวอร์ชันเดิม restart NVDA จริง
2. เปิด Settings > NVDA Startup Greeter ลอง Add ข้อความ 2-3 อัน restart หลายรอบ ฟังว่าสุ่มไม่ซ้ำจริงไหม
3. ยืนยันว่า custom message เดี่ยวเดิม (จากเวอร์ชัน 2026.08.09) ยังอยู่หลังอัปเกรด (ทดสอบ migration)
4. ถ้าเจอปัญหา ส่ง log ค้นคำว่า `"NVDA Startup Greeter:"` — จะมีบรรทัด "migrating legacy single
   customMessage..." และ "chosen custom message: ..."

---

## Session 14 — ทดสอบ 2026.09.09 ผ่านแล้ว แต่ยังมีเสียงรั่วนิดหน่อย (2026-08-06)

**ผลทดสอบจากผู้ใช้:** ฟีเจอร์สุ่มข้อความทำงานได้ดี แต่ยังได้ยินเสียงรั่วมานิดหน่อยก่อนข้อความจะเล่น
(อาการเดิมที่เคยพบและปรับจูนตั้งแต่ Session 6-9 ในเวอร์ชัน 2026.08.09 — เนื่องจากไฟล์ฐานของ 2026.09.09
สืบทอดค่า delay 60ms/retry 100ms มาจาก r7/r8/r9 เดิม)

**คำสั่งผู้ใช้:** "ลองปรับอีกนิดแล้วทำเป็นไฟล์ใหม่ ... เปลี่ยนเฉพาะชื่อไฟล์ ... เพื่อจะได้แก้ปัญหานี้ให้จบ
ก่อนจะไปเริ่มในส่วนอื่นต่อไป"

### การเปลี่ยนแปลงที่ทำจริงใน `globalPlugins/welcomeMessage.py`

- ลด `POST_STARTUP_INITIAL_DELAY_MS` **60ms → 35ms** (ยอมรับความเสี่ยงเพิ่มเรื่องอาจกลับไปเจอ "ข้อความ
  หาย" แบบที่ 0ms เคยเจอใน Session 4 — retry safety net จาก Session 6/8 มีไว้ดักจับกรณีนี้อยู่แล้ว)
- ลด `RETRY_CHECK_INTERVAL_MS` **100ms → 60ms** ให้ retry ตรวจจับและกู้คืนได้เร็วขึ้น
- เพิ่ม comment บันทึกไว้ต้นไฟล์ (session 14) พร้อมเหตุผลและ trade-off เหมือนรูปแบบเดิม
- ตรวจสอบผ่าน `python3 -m py_compile` และ `validate_manifest_authoritative.py` (PASS ทุกเงื่อนไข)

### `manifest.ini` + `doc/en/readme.html`

เพิ่ม bullet สั้นๆ ใน changelog section "2026.09.09": *"Fine-tuned startup timing so the greeting is
heard even sooner."* (เขียนแบบเน้นประโยชน์ผู้ใช้ ไม่ลงรายละเอียดทางเทคนิค ตามแนวทางที่ผู้ใช้ขอไว้ตั้งแต่
Session 12)

แพ็กเป็น `NVDA Startup Greeter V2026.09.09-r2.nvda-addon` (เปลี่ยนแค่ชื่อไฟล์ ไม่เปลี่ยน version,
ไม่ทับไฟล์ฐานเดิม)
**SHA256:** `91356f1808ec83a68b49a514aeae4594b5c5451e53593e20da31cf20148b7fba`

### ขั้นตอนถัดไปที่รอผู้ใช้ (ณ ตอนนั้น)

1. ติดตั้ง r2 ทับ, restart NVDA จริง, ฟังว่าเศษเสียงที่รั่วมาสั้นลงกว่าเดิมไหม
2. ถ้ากลับไปเงียบสนิท (ไม่ได้ยินข้อความเลย) แจ้งทันที จะปรับ `POST_STARTUP_INITIAL_DELAY_MS` ขึ้นกลับไป
3. ถ้าเสียงรั่วยังพอรับได้/หายไปแล้ว ถือว่าปิดประเด็นนี้ได้ แล้วไปต่อฟีเจอร์ถัดไป

**อัปเดตล่าสุด:** ผู้ใช้แจ้งว่าจะนำ r2 ไปทดสอบกับหลายเครื่องก่อน เพื่อให้ทราบผลที่แน่ชัด แล้วค่อยหารือ
ต่อ — **สถานะ ณ จุดนี้คือ "รอผลทดสอบข้ามเครื่อง" ยังไม่ปิดประเด็นเรื่องดีเลย์อย่างเป็นทางการ**

---

## Session 15 — ปรับรูปแบบบันทึกการพัฒนาให้เป็นมาตรฐานมืออาชีพ (2026-08-06)

**คำสั่งผู้ใช้:** ให้เปลี่ยนไฟล์บันทึกจาก `.txt` เป็นรูปแบบที่ถูกต้องตามหลักการพัฒนาซอฟต์แวร์ทั่วไป
เพื่อให้ดูเป็นมืออาชีพ

### การตัดสินใจ (ผ่าน AskUserQuestion)

1. **โครงสร้างไฟล์:** เลือก **แยกเป็น 2 ไฟล์**
   - [`CHANGELOG.md`](CHANGELOG.md) — ภาษาอังกฤษ ตามมาตรฐาน
     [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) สำหรับสรุปการเปลี่ยนแปลงแบบย่อที่ผู้ใช้
     ปลายทาง/ผู้ตรวจสอบ Add-on Store จะเห็น
   - `DEVELOPMENT_LOG.md` (ไฟล์นี้) — สำหรับบันทึกละเอียดภายใน (root cause, การตัดสินใจ, trade-off)
2. **ภาษาของ `DEVELOPMENT_LOG.md`:** เลือก **ภาษาไทย** (เหมือนเดิม) เพื่อความสะดวกในการอ่าน/ทบทวนของ
   ผู้ใช้เอง

### สิ่งที่ทำจริง

- แปลง `แผนพัฒนา addon.txt` (Session 1-14 ทั้งหมด รวมคำสั่งเริ่มต้นของผู้ใช้และกติกาการทำงาน) เป็น
  Markdown ในไฟล์นี้ (`DEVELOPMENT_LOG.md`) โดยคงเนื้อหาทางเทคนิคไว้ครบถ้วน (root cause analysis,
  การตัดสินใจ, SHA256, ขั้นตอนทดสอบ) เพียงจัดรูปแบบใหม่ให้อ่านง่ายขึ้น (หัวข้อ, code span, bold, list)
- สร้าง `CHANGELOG.md` แยกต่างหาก ตามรูปแบบ Keep a Changelog (`[Unreleased]` / `[2026.09.09]` /
  `[2026.08.09]`, แบ่งเป็น Added/Changed/Fixed) สรุปจากเนื้อหาใน `manifest.ini` changelog +
  `doc/en/readme.html` changelog
- **ไฟล์ `แผนพัฒนา addon.txt` เดิมยังคงอยู่ในโฟลเดอร์** (ไม่ได้ลบ เนื่องจากไฟล์ในโฟลเดอร์ที่เชื่อมต่อไว้
  ลบ/เปลี่ยนชื่อไม่ได้จากฝั่งนี้) ถือเป็นเอกสารฉบับเก่า/archive — **นับจากนี้ให้ใช้ `CHANGELOG.md` และ
  `DEVELOPMENT_LOG.md` เป็นแหล่งบันทึกหลักแทน**

### กติกาที่ต้องทำต่อเนื่องเสมอในทุก session ถัดไป (อัปเดต)

- **อัปเดตทั้ง 2 ไฟล์:** `CHANGELOG.md` (สรุปสั้น เมื่อมี version/ฟีเจอร์ใหม่จริงจัง) และ
  `DEVELOPMENT_LOG.md` (บันทึกละเอียดทุก session ต่อท้ายไฟล์นี้ ห้ามลบของเดิม)
- Version ของ `manifest.ini` คงที่ตามที่ตกลงกันไว้ล่าสุดเสมอ (ปัจจุบัน: `2026.09.09`)
- ทุกการแก้ไขต้องสร้างไฟล์ `.nvda-addon` ใหม่เสมอ (ห้ามทับของเดิม) ตามรูปแบบ `V<version>-rN`
- ให้ผู้ใช้ restart NVDA จริงทุกครั้งที่ทดสอบ (ไม่ใช่ reload plugins)

### สถานะ ณ จุดนี้ / รอทำในรอบถัดไป

1. **รอผลทดสอบ `NVDA Startup Greeter V2026.09.09-r2.nvda-addon` จากหลายเครื่อง** จากผู้ใช้ (เรื่องดีเลย์
   35ms/retry 60ms) ก่อนจะปิดประเด็นนี้อย่างเป็นทางการ
2. ไอเดียฟีเจอร์อื่นที่เคยเสนอไว้แต่ยังไม่ได้ทำ (เรียงตามลำดับที่แนะนำไว้): แปลเป็นภาษาไทย
   (`locale/th`), ปุ่มลัด (gesture) พูดคำทักทายซ้ำตามต้องการ, ปรับความเร็ว/โทนเสียงของคำทักทายแยกจาก
   ค่า synth ปกติ, เปิดให้ผู้ใช้ปรับค่าหน่วงเวลา (`POST_STARTUP_INITIAL_DELAY_MS`) เองได้จากหน้า
   Settings, ข้อความอำลาตอนปิด NVDA (ต้องระวังเรื่อง timing คล้ายตอนเปิดเครื่อง)
3. เรื่องชื่อ add-on: `name` (`"nvdaStartupGreeter"`) ใน manifest.ini ห้ามเปลี่ยนอีกเพราะเป็น ID ผูกกับ
   Add-on Store แล้ว (ถ้าเคย submit ไป) ส่วนชื่อที่โชว์ผู้ใช้ (`summary`) ยังคงเป็น
   "NVDA Startup Greeter" อยู่ — แนะนำเปลี่ยนเป็น "NVDA Greeter" เฉพาะถ้าจะเพิ่มฟีเจอร์ข้อความอำลาตอน
   ปิดเครื่องในอนาคต (ยังไม่ได้ตัดสินใจจากผู้ใช้)
4. ยังไม่ได้ submit ไฟล์ใดขึ้น NVDA Add-on Store จริง (ต้องมี public source repo, publish release,
   คำนวณ sha256, กรอกฟอร์ม GitHub issue submission ตามที่บันทึกไว้ใน Session 10)

---

## Session 16 — ผู้ใช้ทดสอบจริงบน NVDA 2026.1 พร้อม log: ยืนยันข้อสังเกตค้างจาก Session 11 (2026-08-19)

**ผู้ใช้รายงาน:** รัน `NVDA Startup Greeter V2026.09.09-r2.nvda-addon` บน NVDA 2026.1 จริง แล้วนำ log
มาให้ดู สรุปได้ดังนี้:

1. โหลดปลั๊กอินสำเร็จ (09:15:16), ลงทะเบียน Settings Panel และ `core.postNvdaStartup` เรียบร้อย
2. `_prepareAndSpeak` ทำงานที่ 09:15:19, `enabled = True`, สุ่มเลือกข้อความ custom message ได้ (ตัวอย่าง
   ในรอบนี้: `'วันนี้หน้าตาคุณสดใสและดูดีมากเลยค่ะ'`)
3. `speakMessage` เรียกสำเร็จไม่มี error, เข้าสู่ retry loop (เหลือโควตา 5 ครั้ง)
4. **พบ `AttributeError: module 'speech' has no attribute 'isSpeaking'`** ตรงจุด `_isSpeechActive()`
   ที่ลองเรียก `speech.isSpeaking()` เป็นทางเลือกแรก
5. Fallback ที่เขียนไว้ตั้งแต่ Session 8 (`speech._manager._hasNoMoreSpeech()`) ทำงานแทนได้ทันที
   ผลลัพธ์ `speech still active = True` ระบบไม่ crash และทำงานต่อได้ปกติ

### ความหมายของผลทดสอบนี้

ยืนยัน**ข้อสังเกตที่ค้างไว้ตั้งแต่ Session 11** ("พบว่า `speech/__init__.py` import ชื่อ `isSpeaking`
จาก `.speech` แต่ค้นในซอร์สที่ดึงมาไม่พบนิยามฟังก์ชันนี้ — ไม่ฟันธง") ว่าเป็นเรื่องจริง: บน NVDA 2026.1
ที่ผู้ใช้รันอยู่จริง **`speech.isSpeaking()` ไม่มีอยู่แล้ว** (ถูกปรับโครงสร้าง API ออกไป)

**นี่ไม่ใช่บั๊กที่กระทบการทำงาน** — เป็นไปตามที่ออกแบบไว้ตั้งแต่ Session 8 พอดี: โค้ดมี try/except
ครอบการเรียก `speech.isSpeaking()` ไว้อยู่แล้ว และ fallback ไปที่ `speech._manager._hasNoMoreSpeech()`
ซึ่งเป็น API ภายในที่ตรวจสอบยืนยันจากซอร์สจริงแล้วว่ายังใช้งานได้ (Session 11) ผลคือ retry safety net
ยังทำงานถูกต้องสมบูรณ์ ไม่มีผลกระทบต่อผู้ใช้ปลายทางเลย

**สิ่งที่ควรพิจารณาปรับปรุง (เป็นเรื่อง cosmetic เท่านั้น ไม่กระทบการทำงาน):** ทุกครั้งที่ NVDA เริ่มระบบ
ตอนนี้จะเกิด `AttributeError` จริงและถูก log ไว้ (ระดับ `log.info` พร้อม `exc_info=True` ตั้งแต่ Session
7) ทำให้ log มี traceback โผล่ทุกรอบทั้งที่รู้สาเหตุแน่ชัดแล้วว่าเกิดกับ NVDA 2026.1 เสมอ ถ้าต้องการลด log
ที่ไม่จำเป็นและข้ามการเรียก `isSpeaking()` ที่รู้แล้วว่าจะ error เสมอบนเวอร์ชันนี้ สามารถแก้
`_isSpeechActive()` ให้เรียก `speech._manager._hasNoMoreSpeech()` เป็นค่าเริ่มต้นแทนได้ในรอบพัฒนาถัดไป
— ยังไม่ทำตอนนี้เพราะผู้ใช้ขอให้หยุดการเปลี่ยนโค้ดไว้ก่อนจนกว่าจะทดสอบครบหลายเครื่อง

### สถานะ

ไม่มีการแก้โค้ด/ออกไฟล์ใหม่ในรอบนี้ (บันทึกผลตรวจสอบ log และข้อสรุปไว้ในเอกสารเท่านั้น) รอผลทดสอบจาก
เครื่องอื่นๆ เพิ่มเติมตามที่ผู้ใช้แจ้งไว้ก่อนหน้า

---

## Session 17 — แก้จุด log รกจาก `speech.isSpeaking()` ที่ error ทุกครั้ง (2026-08-19)

**คำสั่งผู้ใช้:** "ปรับแก้ได้เลยครับ แต่ทำเป็นไฟล์ใหม่เวอร์ชั่นเดิมให้ผม" — ให้แก้จุด cosmetic ที่บันทึกไว้
ใน Session 16 (log รกจาก `AttributeError` ของ `speech.isSpeaking()` ทุกครั้งที่ NVDA เริ่มระบบ) โดยยังคง
version `2026.09.09` เดิม เปลี่ยนแค่ชื่อไฟล์

### การเปลี่ยนแปลงที่ทำจริงใน `globalPlugins/welcomeMessage.py`

- สลับลำดับการเช็คใน `_isSpeechActive()`: เดิมลอง `speech.isSpeaking()` ก่อนเสมอ (ซึ่งยืนยันแล้วจาก log
  จริงว่า error แน่นอนทุกครั้งบน NVDA 2026.1) แล้วค่อย fallback ไป `speech._manager._hasNoMoreSpeech()`
  → **สลับเป็นลอง `speech._manager._hasNoMoreSpeech()` ก่อน** (ยืนยันแล้วว่าใช้งานได้จริงจากทั้งการตรวจ
  ซอร์สจริงใน Session 11 และผลทดสอบจริงใน Session 16) แล้วเหลือ `speech.isSpeaking()` เป็น fallback
  สำรองไว้เผื่อ NVDA รุ่นเก่ากว่าที่อาจยังมีฟังก์ชันนี้อยู่
- ผลคือ `nvda.log` จะไม่มี `AttributeError` traceback โผล่ทุกครั้งที่เปิด NVDA อีกต่อไป (บน NVDA ปัจจุบัน
  ที่ไม่มี `speech.isSpeaking()`) ในขณะที่ retry safety net ยังทำงานเหมือนเดิมทุกประการ ไม่กระทบพฤติกรรม
  ที่ผู้ใช้ได้ยินเลย
- เพิ่ม comment session 17 อธิบายเหตุผลและอ้างอิงถึงผลทดสอบจริงใน Session 16
- เพิ่ม bullet ใน `manifest.ini` changelog (section `2026.09.09`) และ `doc/en/readme.html`:
  "Improved compatibility with the latest NVDA versions." (เขียนแบบผู้ใช้ทั่วไปเข้าใจได้ ไม่ลงรายละเอียด
  ทางเทคนิค)
- ตรวจสอบผ่าน `python3 -m py_compile` และ `validate_manifest_authoritative.py` (PASS ทุกเงื่อนไข)

แพ็กเป็น `NVDA Startup Greeter V2026.09.09-r3.nvda-addon` (version คงเดิมตามกติกา เปลี่ยนแค่ชื่อไฟล์)
**SHA256:** `020eabd825b54e4b274fa7c7a5d08b568487a01bc94f742724cb4835e1e9b8d0`

### ขั้นตอนถัดไปที่รอผู้ใช้

1. ติดตั้ง r3 ทับ (หรือทดสอบคู่กับ r2 บนเครื่องต่างๆ ตามที่วางแผนไว้), restart NVDA จริง
2. ตรวจ log ว่าไม่มี `AttributeError` ของ `speech.isSpeaking()` โผล่มาอีก (ควรเห็นแค่
   `speech still active = ...` ตรงๆ โดยไม่มี traceback ก่อนหน้า)
3. ยังคงรอผลทดสอบเรื่องเศษเสียงรั่ว (delay 35ms/60ms) จากหลายเครื่องตามที่ผู้ใช้แจ้งไว้ก่อนหน้า — ไม่ได้
   แตะค่า `POST_STARTUP_INITIAL_DELAY_MS`/`RETRY_CHECK_INTERVAL_MS` ในรอบนี้

### อัปเดต (จัดการไฟล์โดยผู้ใช้เอง)

ผู้ใช้ลบไฟล์ `.nvda-addon` รุ่นเก่าที่ไม่ได้ใช้ออกจากโฟลเดอร์ทั้งหมด (ไฟล์ฐาน `V2026.09.09.nvda-addon`
เดิมและ `V2026.09.09-r2.nvda-addon`) แล้วเปลี่ยนชื่อไฟล์ล่าสุด (`-r3`, เนื้อหาแก้ไข `_isSpeechActive`)
เป็น `NVDA Startup Greeter V2026.09.09.nvda-addon` (ไม่มีเลขรอบต่อท้าย) — ตรวจสอบแล้วด้วย SHA256
(`020eabd825b54e4b274fa7c7a5d08b568487a01bc94f742724cb4835e1e9b8d0`) ตรงกับเนื้อหาของ r3 ทุกประการ
เพียงเปลี่ยนชื่อไฟล์เท่านั้น ไม่ได้แก้เนื้อหาใดๆ เพิ่มเติม

**ผลต่อกติกาการตั้งชื่อไฟล์ต่อจากนี้:** ตอนนี้ `NVDA Startup Greeter V2026.09.09.nvda-addon` (ไม่มีเลข
รอบ) คือไฟล์ปัจจุบันที่ใช้งานอยู่จริงของเวอร์ชันนี้ ถ้ามีการแก้ไขเพิ่มเติมในเวอร์ชัน `2026.09.09` ต่อไป
ให้เริ่มนับ **`-r2`** ใหม่อีกครั้ง (เหมือนรูปแบบที่เคยเกิดกับเวอร์ชัน `2026.08.09`: ไฟล์ฐานไม่มีเลขรอบ →
ตามด้วย r2, r3, ...) ไม่ใช่ต่อจาก r3 เดิม เนื่องจากไฟล์ r2/r3 เดิมถูกลบไปแล้วและไฟล์ปัจจุบันถูกนับเป็น
"ฐานใหม่" ของสถานะล่าสุดนี้แทน

---

## Session 18 — ตรวจสอบความสมบูรณ์ของไฟล์ล่าสุดทั้งหมด + ย่อ changelog ให้สั้นสำหรับ Store เวอร์ชันแรก
(2026-08-19)

**คำสั่งผู้ใช้:** "เช็ค addon ล่าสุดให้ผมอีกรอบว่าสมบูรณ์ และ update เป็นปัจจุบันทุกส่วนแล้วหรือยัง
รวมถึงส่วนของ changelog ไม่ต้องใส่ข้อมูลเยอะ เพราะอันนี้เป็นเวอร์ชั่นแรกที่จะ up ขึ้น nvda store"

### สิ่งที่ตรวจสอบ

ตรวจไฟล์ทั้งหมดใน draft source (`manifest.ini`, `globalPlugins/welcomeMessage.py`, `doc/en/readme.html`,
`license.txt`) ทีละไฟล์เทียบกับเนื้อหาที่แพ็กเป็นไฟล์ล่าสุด (ยืนยันตรงกับ r3 เดิมที่ผู้ใช้เปลี่ยนชื่อเป็น
`V2026.09.09.nvda-addon` ผ่าน SHA256 ก่อนหน้านี้แล้ว):

1. `manifest.ini` — field ครบตาม configspec, `minimumNVDAVersion`/`lastTestedNVDAVersion` ถูกต้อง,
   `docFileName` ตรงกับไฟล์จริง
2. `globalPlugins/welcomeMessage.py` — ตรงกับเนื้อหาที่แก้ไขล่าสุดใน Session 17 (สลับลำดับ
   `_isSpeechActive`) ครบถ้วน
3. `doc/en/readme.html` — เนื้อหาฟีเจอร์ตรงกับโค้ดปัจจุบันทุกจุด
4. `license.txt` — **พบจุดที่ไม่ตรงกัน (stale):** บรรทัดสุดท้ายยังอ้างอิงถึงหัวข้อ "known limitations"
   ในคู่มือ ทั้งที่หัวข้อนี้ถูกลบออกจาก `readme.html` ไปแล้วตั้งแต่ Session 12 → **แก้ไขแล้ว** ตัดคำว่า
   "and known limitations" ออก

### การเปลี่ยนแปลงที่ทำจริง (ย่อ changelog สำหรับการ submit ครั้งแรก)

เนื่องจากผู้ใช้ยืนยันว่า `2026.09.09` คือเวอร์ชันแรกที่จะ submit ขึ้น NVDA Add-on Store จริง (เวอร์ชัน
`2026.08.09` ไม่เคย submit จริง) จึงรวม changelog ที่จะแพ็กไปกับ addon (ซึ่งผู้ใช้ปลายทาง/ผู้ตรวจสอบเห็น)
ให้เหลือ section เดียวแบบ "Initial release" สั้นๆ (ตัดรายละเอียดภายใน เช่น การ migrate ข้อความเดี่ยว,
การปรับจูน timing, การแก้ `isSpeaking` ออกทั้งหมด — ยังคงบันทึกรายละเอียดพวกนี้ไว้ครบใน
`DEVELOPMENT_LOG.md`/`CHANGELOG.md` ภายในตามเดิม):

1. **`manifest.ini`**: `changelog` เหลือ section เดียว `= 2026.09.09 =` แบบสั้น (Initial release +
   รายการฟีเจอร์หลัก 5 บรรทัด) ตัด section `= 2026.08.09 =` เดิมออกทั้งหมด
2. **`doc/en/readme.html`**: หัวข้อ Changelog เหลือ `<h3>2026.09.09</h3>` เดียว เนื้อหาเดียวกับ
   `manifest.ini`, ตัด `<h3>2026.08.09</h3>` เดิมออก
3. **`license.txt`**: แก้บรรทัดอ้างอิง "known limitations" ที่ล้าสมัยตามที่ตรวจพบด้านบน
4. ตรวจสอบผ่าน `python3 -m py_compile` และ `validate_manifest_authoritative.py` (PASS ทุกเงื่อนไข)

แพ็กเป็น `NVDA Startup Greeter V2026.09.09-r2.nvda-addon` (ต่อจากไฟล์ฐานที่ผู้ใช้เปลี่ยนชื่อไว้ ตามกติกา
ใหม่ที่บันทึกไว้ด้านบน)
**SHA256:** `a929734aa5d986a80abd12eba2e4779ec7a710d0ba5d5ac88381d819f64621df`

### สรุปผลตรวจสอบ

ไฟล์ทั้งหมด**สมบูรณ์และอัปเดตตรงกันทุกส่วนแล้ว** ยกเว้นจุดเดียวที่พบและแก้ไขแล้ว (`license.txt` อ้างอิง
เนื้อหาที่ถูกลบไปแล้ว) การตรวจสอบตาม `validate_manifest_authoritative.py` (อ้างอิงจากซอร์สจริงของ NVDA)
ยังคงผ่านครบทุกเงื่อนไขเหมือนทุกรอบก่อนหน้า

### ขั้นตอนถัดไปที่รอผู้ใช้

1. ติดตั้ง r2 ทับ, restart NVDA จริง, ตรวจว่าทุกฟีเจอร์ยังทำงานปกติเหมือนไฟล์ก่อนหน้า (ไม่มีการแก้โค้ด
   เชิงพฤติกรรมในรอบนี้ มีแค่แก้เอกสาร/changelog)
2. เมื่อพร้อม submit จริง ยังต้องทำตามขั้นตอนที่บันทึกไว้ใน Session 10: มี public source repo, publish
   release (เพื่อได้ URL ดาวน์โหลด), คำนวณ sha256 ใหม่จากไฟล์สุดท้ายที่จะ submit จริง, กรอกฟอร์ม GitHub
   issue submission (addonId, channel, publisher, homepage, license, licenseURL ฯลฯ)

### อัปเดต (จัดการไฟล์โดยผู้ใช้เอง อีกครั้ง)

ผู้ใช้เปลี่ยนชื่อไฟล์ `-r2` (เนื้อหา: changelog สั้นแบบ Initial release + แก้ `license.txt`) เป็น
`NVDA Startup Greeter V2026.09.09.nvda-addon` (ไม่มีเลขรอบ) อีกครั้ง โดยให้เหตุผลว่าชื่อไฟล์ที่มีเลขรอบ
ต่อท้ายเป็นเพียงชื่อทดลองระหว่างพัฒนาเท่านั้น ไม่ต้องการเก็บไว้ในโฟลเดอร์จริง — ตรวจสอบแล้วด้วย SHA256
(`a929734aa5d986a80abd12eba2e4779ec7a710d0ba5d5ac88381d819f64621df`) ตรงกับเนื้อหา r2 ทุกประการ

**สรุปแนวทางที่ผู้ใช้ต้องการ (ยืนยันชัดเจนแล้วจาก 2 ครั้งที่ทำแบบนี้ติดกัน):** ผู้ใช้ต้องการเก็บไฟล์
`.nvda-addon` ไว้แค่ไฟล์เดียวในโฟลเดอร์เสมอ คือ `NVDA Startup Greeter V2026.09.09.nvda-addon` (ไม่มีเลข
รอบ) เป็นตัวแทนสถานะล่าสุด ส่วนไฟล์ที่เราส่งมอบให้ในแต่ละรอบพัฒนาจะยังคงใช้เลขรอบ (`-r2`, `-r3`, ...) ตาม
กติกาเดิม (เพื่อให้ทดสอบเทียบกับไฟล์ก่อนหน้าได้ก่อนตัดสินใจ) แต่ผู้ใช้จะเป็นคนจัดการเปลี่ยนชื่อ/ลบไฟล์เก่า
เองในโฟลเดอร์จริงหลังจากพอใจกับไฟล์ล่าสุดแล้ว — ไม่ต้องกังวลหรือแก้ไขอะไรเพิ่มเติมฝั่งเรา แค่รับทราบว่า
ไฟล์ฐาน (ไม่มีเลขรอบ) ในโฟลเดอร์คือของล่าสุดเสมอ และไฟล์ถัดไปที่จะสร้างยังคงเริ่มนับที่ `-r2` ตามเดิม
