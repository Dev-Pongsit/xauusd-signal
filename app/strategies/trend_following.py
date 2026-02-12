"""
Trend Following Strategy — XAUUSD Optimized
=============================================
EMA Crossover + MACD + RSI + ATR-based SL/TP

ปรับค่าเฉพาะสำหรับทองคำ:
- ทองคำมี volatility สูงกว่า forex ปกติ
- ATR multiplier ใหญ่ขึ้นเพื่อไม่โดน SL บ่อย
- Pip value ของทองคำ = 0.01 (1 pip = $0.01)
"""

import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

# ============================
# Default Parameters (XAUUSD tuned)
# ============================
DEFAULT_PARAMS = {
    "ema_fast": 9,
    "ema_slow": 21,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "rsi_period": 14,
    "atr_period": 14,
    "atr_sl_mult": 1.5,    # SL = ATR × 1.5
    "atr_tp1_mult": 2.0,   # TP1 = ATR × 2.0
    "atr_tp2_mult": 3.0,   # TP2 = ATR × 3.0
    "rsi_overbought": 70,
    "rsi_oversold": 30,
}


def calculate_indicators(df: pd.DataFrame, params: dict = None) -> pd.DataFrame:
    """คำนวณ indicators ทั้งหมด"""
    p = {**DEFAULT_PARAMS, **(params or {})}

    df = df.copy()

    # EMA
    df["ema_fast"] = EMAIndicator(df["close"], window=p["ema_fast"]).ema_indicator()
    df["ema_slow"] = EMAIndicator(df["close"], window=p["ema_slow"]).ema_indicator()

    # MACD
    macd = MACD(df["close"], window_slow=p["macd_slow"],
                window_fast=p["macd_fast"], window_sign=p["macd_signal"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_hist"] = macd.macd_diff()

    # RSI
    df["rsi"] = RSIIndicator(df["close"], window=p["rsi_period"]).rsi()

    # ATR
    df["atr"] = AverageTrueRange(df["high"], df["low"], df["close"],
                                  window=p["atr_period"]).average_true_range()

    return df


def generate_signal(df: pd.DataFrame, params: dict = None) -> dict | None:
    """
    วิเคราะห์ข้อมูลและสร้าง signal

    Returns:
        dict with signal info or None if no signal
    """
    p = {**DEFAULT_PARAMS, **(params or {})}

    # คำนวณ indicators
    df = calculate_indicators(df, p)

    # ต้องมีข้อมูลเพียงพอ
    if len(df) < p["macd_slow"] + p["macd_signal"] + 5:
        return None

    # ดึงค่าล่าสุด
    now = df.iloc[-1]
    prev = df.iloc[-2]

    ema_fast_now = now["ema_fast"]
    ema_slow_now = now["ema_slow"]
    ema_fast_prev = prev["ema_fast"]
    ema_slow_prev = prev["ema_slow"]

    macd_hist_now = now["macd_hist"]
    macd_hist_prev = prev["macd_hist"]
    macd_now = now["macd"]
    macd_signal_now = now["macd_signal"]

    rsi_now = now["rsi"]
    atr_now = now["atr"]
    price = now["close"]

    # ============================
    # เงื่อนไข BUY
    # ============================
    ema_bull_cross = (ema_fast_prev <= ema_slow_prev) and (ema_fast_now > ema_slow_now)
    ema_bull_trend = ema_fast_now > ema_slow_now
    macd_bull_flip = (macd_hist_now > 0) and (macd_hist_prev <= 0)
    macd_bull_trend = macd_now > macd_signal_now
    rsi_not_ob = rsi_now < p["rsi_overbought"]

    # ============================
    # เงื่อนไข SELL
    # ============================
    ema_bear_cross = (ema_fast_prev >= ema_slow_prev) and (ema_fast_now < ema_slow_now)
    ema_bear_trend = ema_fast_now < ema_slow_now
    macd_bear_flip = (macd_hist_now < 0) and (macd_hist_prev >= 0)
    macd_bear_trend = macd_now < macd_signal_now
    rsi_not_os = rsi_now > p["rsi_oversold"]

    # ============================
    # ตัดสินใจ
    # ============================
    direction = None
    strength = "WEAK"
    confidence = 0
    reasoning = ""

    # --- STRONG BUY ---
    if ema_bull_cross and macd_bull_flip and rsi_not_ob:
        direction = "BUY"
        strength = "STRONG"
        confidence = 85
        reasoning = "EMA Golden Cross + MACD flipped bullish + RSI supports"

    # --- MODERATE BUY ---
    elif ema_bull_trend and macd_bull_trend and rsi_not_ob:
        direction = "BUY"
        strength = "MODERATE"
        confidence = 65
        reasoning = "EMA bullish trend + MACD above signal + RSI has room"

    # --- STRONG SELL ---
    elif ema_bear_cross and macd_bear_flip and rsi_not_os:
        direction = "SELL"
        strength = "STRONG"
        confidence = 85
        reasoning = "EMA Death Cross + MACD flipped bearish + RSI supports"

    # --- MODERATE SELL ---
    elif ema_bear_trend and macd_bear_trend and rsi_not_os:
        direction = "SELL"
        strength = "MODERATE"
        confidence = 65
        reasoning = "EMA bearish trend + MACD below signal + RSI has room"

    if direction is None:
        return None

    # ============================
    # คำนวณ SL / TP (ATR-based)
    # ============================
    sl_dist = atr_now * p["atr_sl_mult"]
    tp1_dist = atr_now * p["atr_tp1_mult"]
    tp2_dist = atr_now * p["atr_tp2_mult"]

    if direction == "BUY":
        sl = price - sl_dist
        tp1 = price + tp1_dist
        tp2 = price + tp2_dist
    else:
        sl = price + sl_dist
        tp1 = price - tp1_dist
        tp2 = price - tp2_dist

    rr_ratio = tp1_dist / sl_dist if sl_dist > 0 else 0

    signal = {
        "id": f"SIG-{uuid.uuid4().hex[:8].upper()}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": "XAUUSD",
        "direction": direction,
        "strength": strength,
        "confidence": confidence,
        "entry": round(price, 2),
        "sl": round(sl, 2),
        "tp1": round(tp1, 2),
        "tp2": round(tp2, 2),
        "rr_ratio": round(rr_ratio, 2),
        "reasoning": reasoning,
        "indicators": {
            "ema_fast": round(ema_fast_now, 2),
            "ema_slow": round(ema_slow_now, 2),
            "macd": round(macd_now, 2),
            "macd_signal": round(macd_signal_now, 2),
            "macd_hist": round(macd_hist_now, 2),
            "rsi": round(rsi_now, 1),
            "atr": round(atr_now, 2),
        },
        "ai_analysis": None,  # จะถูกเติมภายหลัง
    }

    logger.info(f"Signal: {direction} {strength} @ {price:.2f} | conf={confidence}%")
    return signal
