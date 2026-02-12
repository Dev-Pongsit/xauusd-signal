"""
Configuration for XAUUSD AI Signal System
Loads environment variables from .env file
"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Claude AI
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "claude-3-5-sonnet-20241022")

# Telegram Notification
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Web Dashboard
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-12345")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))

# Signal Settings
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL_MINUTES", 60))
SIGNAL_MIN_CONFIDENCE = int(os.getenv("SIGNAL_MIN_CONFIDENCE", 55))
MIN_CONFIDENCE = SIGNAL_MIN_CONFIDENCE  # Alias for compatibility
TIMEFRAME = os.getenv("TIMEFRAME", "1h")

# Timezone
TIMEZONE = os.getenv("TIMEZONE", "Asia/Bangkok")
