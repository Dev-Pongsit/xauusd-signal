# ==========================================
# 🧪 คู่มือทดสอบบน Local (Windows)
# XAUUSD AI Signal System
# ==========================================

## ⚡ Quick Start — 5 นาทีก็ทดสอบได้

### Step 1: เปิด Command Prompt หรือ PowerShell
กด `Win + R` → พิมพ์ `cmd` → Enter
(หรือค้นหา "PowerShell" ใน Start Menu)


### Step 2: เช็ค Python
```
python --version
```
ต้องได้ Python 3.9+ (ถ้าไม่ได้ลอง `python3 --version`)


### Step 3: สร้างโฟลเดอร์โปรเจกต์
```
mkdir C:\xauusd-signal
cd C:\xauusd-signal
```


### Step 4: สร้าง Virtual Environment
```
python -m venv venv
venv\Scripts\activate
```
จะเห็น `(venv)` ข้างหน้า prompt แสดงว่าสำเร็จ


### Step 5: วางไฟล์โปรเจกต์
คัดลอกไฟล์ทั้งหมดจากที่ดาวน์โหลดมาวางใน `C:\xauusd-signal\`

โครงสร้างต้องเป็นแบบนี้:
```
C:\xauusd-signal\
├── server.py
├── requirements.txt
├── .env
├── app\
│   ├── __init__.py
│   ├── config.py
│   ├── runner.py
│   ├── data\
│   │   ├── __init__.py
│   │   └── fetcher.py
│   ├── strategies\
│   │   ├── __init__.py
│   │   └── trend_following.py
│   ├── ai\
│   │   ├── __init__.py
│   │   └── analysis.py
│   └── utils\
│       ├── __init__.py
│       ├── notify.py
│       └── store.py
└── web\
    └── templates\
        └── dashboard.html
```


### Step 6: ติดตั้ง packages
```
pip install -r requirements.txt
```
รอสักครู่ (~1-2 นาที)


### Step 7: สร้างไฟล์ .env
```
copy .env.example .env
```
เปิดแก้ไข:
```
notepad .env
```
ใส่ ANTHROPIC_API_KEY (ถ้ามี) — ถ้ายังไม่มีก็ข้ามได้ ระบบทำงานได้โดยไม่มี AI


### Step 8: ทดสอบ!
```
python test_local.py
```
(ดูไฟล์ test_local.py ที่แนบมา)


### Step 9: เปิด Dashboard
```
python server.py
```
เปิด browser → http://localhost:5000

---

## 🔧 แก้ปัญหาที่พบบ่อย

### ❌ "python ไม่ใช่คำสั่งภายใน"
→ ใช้ `python3` แทน หรือติดตั้ง Python จาก python.org แล้วติ๊ก "Add to PATH"

### ❌ "pip install ล้มเหลว"
→ ลอง: `python -m pip install -r requirements.txt`

### ❌ "ModuleNotFoundError"
→ ตรวจสอบว่า activate venv แล้ว: `venv\Scripts\activate`

### ❌ "yfinance ไม่ได้ข้อมูล"
→ ตลาดอาจปิด (วันเสาร์-อาทิตย์) — ระบบจะใช้ข้อมูลล่าสุดที่มี

### ❌ "Address already in use"
→ เปลี่ยน port: แก้ FLASK_PORT=5001 ใน .env
