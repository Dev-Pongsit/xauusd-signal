@echo off
chcp 65001 >nul
title XAUUSD AI Signal — Setup

echo.
echo  ╔══════════════════════════════════════╗
echo  ║  🥇 XAUUSD AI Signal — Setup        ║
echo  ║  ติดตั้งอัตโนมัติสำหรับ Windows        ║
echo  ╚══════════════════════════════════════╝
echo.

:: Check Python
echo [1/4] เช็ค Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ไม่พบ Python! กรุณาติดตั้งจาก python.org
    pause
    exit /b 1
)
python --version
echo ✅ Python พร้อม
echo.

:: Create venv
echo [2/4] สร้าง Virtual Environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ สร้าง venv สำเร็จ
) else (
    echo ✅ venv มีอยู่แล้ว
)
echo.

:: Activate + Install
echo [3/4] ติดตั้ง packages...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
echo ✅ ติดตั้ง packages สำเร็จ
echo.

:: Create .env if not exists
echo [4/4] เช็คไฟล์ .env...
if not exist ".env" (
    copy .env.example .env >nul
    echo ✅ สร้าง .env สำเร็จ
    echo ⚠️  อย่าลืมแก้ไข .env ใส่ ANTHROPIC_API_KEY
) else (
    echo ✅ .env มีอยู่แล้ว
)
echo.

:: Create data directory
if not exist "data" mkdir data

echo ══════════════════════════════════════
echo  ✅ Setup เสร็จสิ้น!
echo ══════════════════════════════════════
echo.
echo  คำสั่งถัดไป:
echo.
echo    ทดสอบระบบ:     python test_local.py
echo    เปิด Dashboard:  python server.py
echo.
echo  (ต้อง activate venv ก่อน: venv\Scripts\activate)
echo.
pause
