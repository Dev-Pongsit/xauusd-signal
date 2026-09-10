# CLAUDE.md — คำสั่งสำหรับ AI agent

## เกี่ยวกับโปรเจกต์
ระบบ signal เทรด XAU/USD (Python + Flask) ใช้ Claude วิเคราะห์
แจ้งเตือนผ่าน Telegram

## กฎเรื่อง Git (สำคัญมาก)
- คุณกำลังทำงานอยู่ใน git worktree — อย่าสั่ง `git checkout main`
  หรือ `git checkout <branch อื่น>` เด็ดขาด เพราะจะทำให้ worktree พัง
- ทำงานเฉพาะบน branch ปัจจุบันของ worktree นี้เท่านั้น
- ถ้าต้องการ sync กับ main ให้บอกผู้ใช้ อย่าทำเอง
- commit เฉพาะไฟล์ที่เกี่ยวกับ task นี้

## Coding standards
- Python 3.9+ ใช้ type hints ทุกฟังก์ชัน
- ตั้งชื่อตัวแปร/ฟังก์ชันเป็น snake_case
- comment เป็นภาษาไทยได้ (ให้ตรงสไตล์โปรเจกต์เดิม)
- อย่า hardcode API key — อ่านจาก .env ผ่าน app/config.py เสมอ

## การทดสอบ
- รันเทสต์ด้วย: `python test_local.py`
- ต้องผ่านเทสต์ก่อน commit ทุกครั้ง
- ถ้าเพิ่ม feature ใหม่ ให้เพิ่ม test case ใน test_local.py ด้วย

## ห้ามทำ
- อย่าแตะไฟล์ .env จริง (มี secret)
- อย่าแก้ requirements.txt โดยไม่จำเป็น
- อย่าลบหรือแก้ไฟล์ที่ไม่เกี่ยวกับ task