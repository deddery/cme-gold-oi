# CME Gold Options Dashboard

แดชบอร์ดส่วนตัวสำหรับติดตาม Open Interest ของ **COMEX Gold Options on Futures** และโพสิชันของกลุ่มเทรดเดอร์ต่างๆ เพื่อใช้ประกอบการวิเคราะห์ XAUUSD ส่งสรุปผ่าน Telegram

## สองแหล่งข้อมูล สองจังหวะเวลา

### 1) CME Daily Bulletin (PG64) — อัปโหลดด้วยมือ

CME ป้องกันการดึง PDF อัตโนมัติด้วย Akamai Bot Manager: การเรียก `CME_PG64_URL` (ดู `app/config.py`) แบบ script จะได้ HTTP 403 พร้อมข้อความว่าเป็นการ scrape ที่ขัดกับ Data Terms of Use ของ CME และ IP ที่โดนตรวจพบจะถูกบล็อก ระบบนี้จึงไม่ดาวน์โหลดอัตโนมัติอีกต่อไป

**ขั้นตอน:**

1. เปิด `CME_PG64_URL` ในเบราว์เซอร์แล้วดาวน์โหลด PDF ด้วยตัวเอง (ถ้า IP ของคุณโดนบล็อกอยู่ ให้ลองเครือข่ายอื่น หรือรอ/ติดต่อ CME GCC ที่ gcc@cmegroup.com)
2. นำไฟล์ไปวางไว้ที่ `data/raw/` (ใช้ชื่อไฟล์เดิมก็ได้ ไม่ต้องเปลี่ยน)
3. Commit และ push — workflow `Update CME Gold Options` จะทำงานอัตโนมัติเมื่อมีการ push ไฟล์ `.pdf` ใหม่ใต้ `data/raw/`
4. ระบบจะ: อ่าน trade date จากตัว PDF เอง → เปลี่ยนชื่อไฟล์เป็น `<trade_date>.pdf` → parse Call/Put OI ตาม strike/expiry → validate → เขียน `docs/index.html` → แจ้งเตือน Telegram

ตัวแปลง PDF จะหยุดและ **ไม่ส่งสัญญาณ** หากอ่านข้อมูลไม่ได้หรือผลตรวจสอบผิดปกติ (ดู `ParseError` ใน `app/cme.py`)

### 2) CFTC Commitments of Traders — ดึงอัตโนมัติทุกวันศุกร์

ข้อมูล COT (Disaggregated, Futures + Options Combined) ของ COMEX Gold จาก [publicreporting.cftc.gov](https://publicreporting.cftc.gov) เป็น public API ของหน่วยงานรัฐสหรัฐฯ ไม่มีการบล็อกบอต จึงดึงอัตโนมัติได้ปกติ

- Workflow `Update CFTC COT Gold` รันทุกวันศุกร์ ~21:00 UTC (หลัง CFTC เผยแพร่รายงานราว 15:30 เวลาตะวันออกของสหรัฐฯ)
- สรุปโพสิชัน long/short/net ของ Producer/Merchant, Swap Dealers, Managed Money, Other Reportables พร้อมการเปลี่ยนแปลงรายสัปดาห์
- เขียนหน้า `docs/cot/index.html` และแจ้งเตือน Telegram แยกจากฝั่ง CME

> ข้อมูลทั้งสองแหล่งเป็นข้อมูล end-of-day/รายสัปดาห์ ไม่ใช่สัญญาณซื้อขายโดยลำพัง โปรดตรวจสอบข้อมูลต้นฉบับก่อนใช้ตัดสินใจเทรดเสมอ

## ตั้งค่า GitHub

1. สร้าง repository จากโฟลเดอร์นี้ แล้ว push ขึ้น GitHub (แนะนำให้ตั้งเป็น **private repo** เนื่องจาก CME จำกัดการเผยแพร่ข้อมูลจาก Daily Bulletin ต่อ — ดูรายละเอียดใน Data Terms of Use ของ CME)
2. ที่ **Settings → Secrets and variables → Actions** เพิ่ม secrets:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
3. ไปที่ **Settings → Pages** แล้วเลือก source เป็น **GitHub Actions**
4. เปิดแท็บ Actions และรัน workflow `Update CFTC COT Gold` ครั้งแรกด้วยปุ่ม **Run workflow** เพื่อทดสอบ (ไม่ต้องรอวันศุกร์)
5. อัปโหลด PDF แรกตามขั้นตอนด้านบนเพื่อทดสอบฝั่ง CME

## ทำงานบนเครื่อง

ต้องมี Python 3.11+, Poppler (`pdftotext`) และติดตั้งไลบรารี (ใช้แค่ standard library):

```powershell
py -m pip install -r requirements.txt
py -m app.run        # parse ไฟล์ PDF ที่วางไว้ใน data/raw/
py -m app.run_cot     # ดึงข้อมูล CFTC COT ล่าสุด
```

ตั้ง `TELEGRAM_BOT_TOKEN` และ `TELEGRAM_CHAT_ID` เป็น environment variables หากต้องการทดสอบการแจ้งเตือน

## ข้อสำคัญเรื่องตัวแปลง PDF

CME เปลี่ยนรูปแบบรายงานได้เป็นครั้งคราว ตัวแปลงจะหยุดและ **ไม่ส่งสัญญาณ** หากอ่านข้อมูลไม่ได้หรือผลตรวจสอบผิดปกติ ไฟล์ PDF ทุกวันถูกเก็บไว้ใน `data/raw/` เพื่อให้ตรวจสอบย้อนกลับได้
