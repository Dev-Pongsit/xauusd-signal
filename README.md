# 🥇 XAUUSD AI Signal System

> ระบบ AI วิเคราะห์ทองคำ (XAUUSD) ส่ง Signal พร้อม Web Dashboard
> สร้างจากแนวคิด Michael Ionita / OpenClaw — ปรับใช้กับ Forex + ทองคำ

---

## ✅ แก้ปัญหาทุกจุดที่คุณต้องการ

| ปัญหา | วิธีแก้ |
|--------|---------|
| ❌ TypeScript ยาก | ✅ **Python** ทั้งโปรเจกต์ |
| ❌ ไม่มี server/คอม | ✅ รันบน **Hostinger VPS** ($5/เดือน) |
| ❌ MT5 ต้องจ่ายเงิน bridge | ✅ ใช้ **yfinance** ดึงข้อมูลฟรี 100% |
| ❌ UI ไม่ชัดว่าคู่เงินอะไร | ✅ Dashboard แสดง **🥇 XAUUSD ทองคำ** ชัดเจนทุกจุด |

---

## 💰 ค่าใช้จ่ายรวม

| รายการ | ราคา | หมายเหตุ |
|--------|-------|----------|
| Hostinger VPS (KVM1) | **~$5/เดือน** | 1 vCPU, 4GB RAM — เหลือเฟือ |
| ข้อมูลราคาทองคำ | **ฟรี** | yfinance (Yahoo Finance) |
| Claude API | **~$1-5/เดือน** | จ่ายตามใช้, ~$0.003/signal |
| Telegram Bot | **ฟรี** | แจ้งเตือน signal |
| **รวม** | **~$6-10/เดือน** | |

---

## 🏗️ สถาปัตยกรรม

```
┌─────────────────────────────────────────────────────────────┐
│                    Hostinger VPS ($5/mo)                     │
│                                                             │
│  ┌──────────┐  ┌────────────────┐  ┌──────────────────┐    │
│  │ yfinance │→│ Trend Strategy  │→│ Claude AI         │    │
│  │ (ฟรี)    │  │ EMA+MACD+RSI   │  │ วิเคราะห์เสริม     │    │
│  └──────────┘  └────────────────┘  └──────────────────┘    │
│                        │                                    │
│                        ▼                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Flask Dashboard (port 5000)                          │  │
│  │ 🥇 XAUUSD ราคา + Signal + AI Analysis              │  │
│  └──────────────────────────────────────────────────────┘  │
│                        │                                    │
│              ┌─────────▼─────────┐                          │
│              │ Telegram แจ้งเตือน │                          │
│              └───────────────────┘                          │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
              คุณเปิด MT5 เทรดเอง
```

---

## ⚡ Quick Start (local test)

```bash
# 1. Clone
git clone <your-repo>
cd xauusd-ai-signal

# 2. Install
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Config
cp .env.example .env
# แก้ไข .env → ใส่ ANTHROPIC_API_KEY

# 4. Run
python server.py

# 5. เปิด browser → http://localhost:5000
```

---

## 📁 โครงสร้างโปรเจกต์

```
xauusd-ai-signal/
├── server.py                 # 🚀 Flask server + scheduler
├── deploy-hostinger.sh       # 📦 คู่มือ deploy Hostinger VPS
├── requirements.txt
├── .env.example
│
├── app/
│   ├── config.py             # ⚙️ Config จาก .env
│   ├── runner.py             # 🎯 Signal pipeline หลัก
│   │
│   ├── data/
│   │   └── fetcher.py        # 📊 ดึงราคา XAUUSD ฟรี (yfinance)
│   │
│   ├── strategies/
│   │   └── trend_following.py # 📈 EMA+MACD+RSI strategy
│   │
│   ├── ai/
│   │   └── analysis.py       # 🤖 Claude AI วิเคราะห์ตลาด
│   │
│   └── utils/
│       ├── notify.py          # 📱 Telegram + console notification
│       └── store.py           # 💾 บันทึก signal (JSON)
│
├── web/
│   └── templates/
│       └── dashboard.html     # 🖥️ Dashboard UI
│
└── data/
    └── signals.json           # 📋 Signal history (auto-created)
```

---

## 🎯 วิธีดู Signal บน Dashboard

Dashboard แสดงชัดเจนทุกจุด:

1. **🥇 XAUUSD badge** — ด้านบนสุด แสดงว่าเป็นคู่เงินทองคำ
2. **ราคา real-time** — อัพเดททุก 60 วินาที
3. **Signal Card** — แต่ละ signal แสดง:
   - 🟢 BUY / 🔴 SELL + ความแรง (STRONG/MODERATE/WEAK)
   - Entry, SL, TP1, TP2 ชัดเจน
   - Indicators: EMA, MACD, RSI, ATR
   - Confidence bar
   - 🤖 AI Analysis (ถ้าเปิด Claude)
   - Timestamp + Signal ID

---

## 🔌 ทำไมไม่ใช้ MT5 Python API ตรงๆ?

Library `MetaTrader5` (official) **ทำงานได้แค่บน Windows** เท่านั้น
— ไม่สามารถรันบน Hostinger VPS (Linux) ได้

**ทางเลือกที่เราเลือก: yfinance**
- ✅ ฟรี 100%
- ✅ ทำงานบน Linux
- ✅ ข้อมูล XAUUSD (GC=F) แม่นยำ
- ✅ ไม่ต้องสมัคร API key
- ⚠️ delay ประมาณ 15 นาที (ไม่ใช่ real-time)

> **สำหรับ Signal-based trading ที่ใช้ H1 timeframe
> delay 15 นาทีไม่มีผลกระทบ เพราะ signal มี SL/TP ที่คำนวณจาก ATR อยู่แล้ว**

---

## 📱 ตั้งค่า Telegram Bot (ฟรี)

1. เปิด Telegram → ค้นหา `@BotFather`
2. ส่ง `/newbot` → ตั้งชื่อ → ได้ **Bot Token**
3. ส่ง `/start` ให้ bot ของคุณ
4. ค้นหา `@userinfobot` → ส่งข้อความ → ได้ **Chat ID**
5. ใส่ใน `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your_token
   TELEGRAM_CHAT_ID=your_id
   ```

---

## 🚀 Deploy บน Hostinger VPS

### แนะนำ: KVM 1 Plan ($4.99/mo)
- 1 vCPU + 4GB RAM — **เหลือเฟือสำหรับระบบนี้**
- OS: Ubuntu 22.04
- Location: **Singapore** (ใกล้ไทย, latency ต่ำ)

ดูขั้นตอน deploy ทั้งหมดใน `deploy-hostinger.sh`

---

## ⚠️ Disclaimer

ระบบนี้เป็น **เครื่องมือช่วยวิเคราะห์** ไม่ใช่คำแนะนำการลงทุน
- ทุกการเทรดมีความเสี่ยง
- ทดสอบบน demo account ก่อนเสมอ
- ใช้ risk management ที่เหมาะสม (แนะนำ 1-2% ต่อ trade)
