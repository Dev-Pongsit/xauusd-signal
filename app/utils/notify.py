"""
Notification — Telegram + Console
"""

import requests
import logging
from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)


def _format_trade_plan(plan: dict) -> str:
    """Format แผนเทรดครบชุด (entry zone, SL, TP1-3, lot, management)"""
    pos = plan["position"]
    mgmt = plan["management"]

    def _tp_line(t: dict) -> str:
        lot_txt = f" ≈ {t['lot']} lot" if t["lot"] > 0 else ""
        return f"🎯 TP{t['level']}:    ${t['price']}  (1:{t['rr']} | ปิด {t['close_percent']}%{lot_txt})"

    tp_lines = "\n".join(_tp_line(t) for t in plan["tp"])

    risk_txt = f"${pos['risk_usd']} ≈ {pos['risk_percent_actual']}%"
    if pos.get("risk_exceeds_target"):
        risk_txt += f" ⚠️ เกินเป้า {pos['risk_percent']}% (ติดเพดาน min lot)"

    return f"""
📍 Entry:  ${plan['entry']}
   Zone:   ${plan['entry_zone']['min']} – ${plan['entry_zone']['max']}
🛑 SL:     ${plan['sl']}  (ระยะ {plan['sl_distance']} | เสี่ยง {risk_txt})
{tp_lines}

💰 Position: {pos['lot']} lot  (พอร์ต ${pos['account_balance']})
🔧 บริหารไม้:
   • เลื่อน SL → กันทุน (${mgmt['breakeven_price']}) เมื่อถึง {mgmt['breakeven_trigger']}
   • Trailing stop ระยะ {mgmt['trailing_distance']} (ATR × {mgmt['trailing_atr_mult']})"""


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

    # แผนเทรดครบชุด — ถ้าไม่มี (signal เก่า) fallback เป็นรูปแบบเดิม
    if signal.get("trade_plan"):
        plan_text = _format_trade_plan(signal["trade_plan"])
    else:
        plan_text = f"""
📍 Entry:  ${signal['entry']}
🛑 SL:     ${signal['sl']}
🎯 TP1:    ${signal['tp1']}
🎯 TP2:    ${signal['tp2']}
📊 R:R = 1:{signal['rr_ratio']}"""

    return f"""
━━━━━━━━━━━━━━━━━━━━━━━
{arrow}  XAUUSD (ทองคำ)
━━━━━━━━━━━━━━━━━━━━━━━
Signal: {strength_icon} {signal['strength']} ({signal['confidence']}%)
{plan_text}

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
