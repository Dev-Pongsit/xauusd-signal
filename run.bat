@echo off
chcp 65001 >nul
title XAUUSD AI Signal — Dashboard

echo.
echo  🥇 XAUUSD AI Signal — Starting Dashboard...
echo.

call venv\Scripts\activate.bat
python server.py

pause
