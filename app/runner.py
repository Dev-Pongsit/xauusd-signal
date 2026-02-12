"""
Signal Runner — Pipeline หลัก
==============================
1. ดึงข้อมูล XAUUSD (ฟรี via yfinance)
2. รัน Strategy → Technical Signal
3. ส่งให้ AI วิเคราะห์เสริม (Claude)
4. Filter → บันทึก + ส่ง Notification
"""

import logging
from app.data.fetcher import fetch_xauusd
from app.strategies.trend_following import generate_signal
from app.ai.analysis import analyze_signal, apply_ai_override
from app.utils.notify import notify_signal
from app.utils.store import save_signal
from app.config import MIN_CONFIDENCE, ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)


def run_scan() -> dict | None:
    """
    รัน signal scan ครั้งเดียว

    Returns:
        signal dict or None
    """
    logger.info("=== Starting XAUUSD Scan ===")

    # Step 1: ดึงข้อมูล
    try:
        df = fetch_xauusd(period="60d", interval="1h")
    except Exception as e:
        logger.error(f"Data fetch failed: {e}")
        return None

    # Step 2: รัน Strategy
    signal = generate_signal(df)
    if signal is None:
        logger.info("No signal detected")
        return None

    logger.info(f"Technical Signal: {signal['direction']} "
                f"({signal['strength']}, {signal['confidence']}%)")

    # Step 3: AI Analysis
    if ANTHROPIC_API_KEY:
        logger.info("Requesting AI analysis...")
        last_10 = df.tail(10)
        candles_text = "\n".join(
            f"{row['time']} | O:{row['open']:.2f} H:{row['high']:.2f} "
            f"L:{row['low']:.2f} C:{row['close']:.2f}"
            for _, row in last_10.iterrows()
        )

        ai_result = analyze_signal(signal, candles_text)
        if ai_result:
            signal = apply_ai_override(signal, ai_result)
            logger.info(f"After AI: confidence={signal['confidence']}%")

    # Step 4: Filter
    if signal["confidence"] < MIN_CONFIDENCE:
        logger.info(f"Filtered: confidence {signal['confidence']}% < {MIN_CONFIDENCE}%")
        return None

    # Step 5: Save + Notify
    save_signal(signal)
    notify_signal(signal)

    logger.info(f"=== Signal Published: {signal['id']} ===")
    return signal
