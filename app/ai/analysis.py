"""
AI Analysis Engine — Claude as Market Analyst
==============================================
ให้ Claude วิเคราะห์ signal เสริมก่อนส่งให้ user
- ยืนยัน/ค้าน signal จาก technical strategy
- ให้ key levels (support/resistance)
- ประเมินความเสี่ยง
- Daily briefing

ค่าใช้จ่ายประมาณ: ~$0.003-0.01 ต่อ signal (Sonnet)
"""

import json
import logging
from anthropic import Anthropic
from app.config import ANTHROPIC_API_KEY, AI_MODEL

logger = logging.getLogger(__name__)


def get_client():
    if not ANTHROPIC_API_KEY:
        return None
    return Anthropic(api_key=ANTHROPIC_API_KEY)


def analyze_signal(signal: dict, candles_summary: str) -> dict | None:
    """
    ให้ AI วิเคราะห์ signal เสริม

    Returns:
        dict with AI analysis or None if AI unavailable
    """
    client = get_client()
    if not client:
        logger.warning("AI unavailable — no API key")
        return None

    prompt = f"""You are a professional XAUUSD (Gold) market analyst.
Analyze this trading signal and provide your assessment.

## Signal
- Direction: {signal['direction']}
- Entry: ${signal['entry']}
- Stop Loss: ${signal['sl']}
- Take Profit 1: ${signal['tp1']}
- Take Profit 2: ${signal['tp2']}
- Take Profit 3: ${signal.get('tp3', 'N/A')}
- R:R Ratio (to TP1): 1:{signal['rr_ratio']}
- Position Size: {signal.get('trade_plan', {}).get('position', {}).get('lot', 'N/A')} lot
- Strategy Confidence: {signal['confidence']}%
- Reasoning: {signal['reasoning']}

## Current Indicators
- EMA 9: {signal['indicators']['ema_fast']}
- EMA 21: {signal['indicators']['ema_slow']}
- MACD: {signal['indicators']['macd']}
- MACD Hist: {signal['indicators']['macd_hist']}
- RSI: {signal['indicators']['rsi']}
- ATR: {signal['indicators']['atr']}

## Recent Price Action (last 10 candles)
{candles_summary}

Respond ONLY in this JSON format (no markdown):
{{
    "market_condition": "TRENDING" | "RANGING" | "VOLATILE",
    "trend": "BULLISH" | "BEARISH" | "NEUTRAL",
    "support": [number, number],
    "resistance": [number, number],
    "recommendation": "BUY" | "SELL" | "NEUTRAL",
    "confidence": number 0-100,
    "reasoning": "2-3 sentence analysis",
    "risks": ["risk1", "risk2"],
    "news_impact": "HIGH" | "MEDIUM" | "LOW"
}}"""

    try:
        response = client.messages.create(
            model=AI_MODEL,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.content[0].text
        cleaned = text.replace("```json", "").replace("```", "").strip()
        analysis = json.loads(cleaned)

        logger.info(f"AI: {analysis['recommendation']} (conf={analysis['confidence']}%)")
        return analysis

    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        return None


def apply_ai_override(signal: dict, ai: dict) -> dict:
    """
    ปรับ confidence ตาม AI opinion

    - AI เห็นด้วย → +20% confidence
    - AI neutral → -15%
    - AI ค้าน → -40% + downgrade to WEAK
    """
    signal = signal.copy()
    signal["ai_analysis"] = ai

    if ai["recommendation"] == signal["direction"]:
        boost = int(ai["confidence"] * 0.2)
        signal["confidence"] = min(100, signal["confidence"] + boost)
    elif ai["recommendation"] == "NEUTRAL":
        signal["confidence"] = int(signal["confidence"] * 0.85)
    else:
        signal["confidence"] = int(signal["confidence"] * 0.6)
        signal["strength"] = "WEAK"

    return signal
