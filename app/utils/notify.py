"""
Notification — Telegram + Console
"""

import requests
import logging
from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)


def format_signal_text(signal: dict) -> str:
    """Format signal เป็นข้อความสวยๆ"""
    d = signal["direction"]
    arrow = "🟢 BUY" if d == "BUY" else "🔴 SELL"

    s = signal["strength"]
    strength_icon = "💪" if s == "STRONG" else "👍" if s == "MODERATE" else "🤏"

    ai_text = ""
    if signal.get("ai_analysis"):
        ai = signal["ai_analysis"]
        ai_text = f"""
🤖 AI Analysis:
   {ai.get('reasoning', 'N/A')}
   Support: {ai.get('support', 'N/A')}
   Resistance: {ai.get('resistance', 'N/A')}"""

    return f"""
━━━━━━━━━━━━━━━━━━━━━━━
{arrow}  XAUUSD (ทองคำ)
━━━━━━━━━━━━━━━━━━━━━━━
Signal: {strength_icon} {signal['strength']} ({signal['confidence']}%)

📍 Entry:  ${signal['entry']}
🛑 SL:     ${signal['sl']}
🎯 TP1:    ${signal['tp1']}
🎯 TP2:    ${signal['tp2']}
📊 R:R = 1:{signal['rr_ratio']}

📈 Indicators:
   EMA {signal['indicators']['ema_fast']} / {signal['indicators']['ema_slow']}
   MACD Hist: {signal['indicators']['macd_hist']}
   RSI: {signal['indicators']['rsi']}
   ATR: {signal['indicators']['atr']}

💡 {signal['reasoning']}
{ai_text}
━━━━━━━━━━━━━━━━━━━━━━━
⏰ {signal['timestamp']}
ID: {signal['id']}
""".strip()


def send_telegram(text: str) -> bool:
    """ส่งข้อความไป Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.debug("Telegram not configured — skipping")
        return False

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        resp = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
        }, timeout=10)
        resp.raise_for_status()
        logger.info("Telegram notification sent")
        return True
    except Exception as e:
        logger.error(f"Telegram failed: {e}")
        return False


def notify_signal(signal: dict):
    """ส่ง signal ทุกช่องทาง"""
    text = format_signal_text(signal)
    print("\n" + text + "\n")  # console
    send_telegram(text)
