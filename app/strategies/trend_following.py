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

from app.config import (
    ACCOUNT_BALANCE,
    RISK_PERCENT,
    XAUUSD_CONTRACT_SIZE,
    MIN_LOT,
    MAX_LOT,
)

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
    "atr_tp3_mult": 4.5,   # TP3 = ATR × 4.5
    "rsi_overbought": 70,
    "rsi_oversold": 30,
    # --- Trade plan (แผนเทรดครบชุด) ---
    "entry_zone_atr": 0.25,           # ความกว้าง entry zone = ATR × 0.25
    "tp_split": (0.4, 0.4, 0.2),      # สัดส่วนปิดไม้ที่ TP1 / TP2 / TP3
    "be_trigger": "TP1",              # เลื่อน SL → entry เมื่อราคาถึงระดับนี้
    "trail_atr_mult": 1.0,            # trailing stop = ATR × 1.0 (หลัง breakeven)
    # --- Position sizing (อ่านค่าเริ่มต้นจาก .env ผ่าน app/config.py) ---
    "account_balance": ACCOUNT_BALANCE,
    "risk_percent": RISK_PERCENT,
    "contract_size": XAUUSD_CONTRACT_SIZE,
    "min_lot": MIN_LOT,
    "max_lot": MAX_LOT,
}


def build_trade_plan(direction: str, entry: float, atr: float, params: dict = None) -> dict:
    """
    สร้างแผนเทรดครบชุดจากราคา entry + ATR

    ประกอบด้วย:
      - entry zone (ช่วงราคาเข้าที่ยอมรับได้)
      - stop loss + ระยะ SL
      - TP1 / TP2 / TP3 พร้อม R:R และสัดส่วนปิดไม้ (partial close)
      - position size (lot) คำนวณจาก account_balance × risk_percent
      - แผนบริหารไม้: breakeven + trailing stop

    Args:
        direction: "BUY" หรือ "SELL"
        entry: ราคาเข้า
        atr: ค่า ATR ปัจจุบัน
        params: override DEFAULT_PARAMS ได้

    Returns:
        dict แผนเทรดครบชุด
    """
    p = {**DEFAULT_PARAMS, **(params or {})}
    sign = 1 if direction == "BUY" else -1

    sl_dist = atr * p["atr_sl_mult"]
    tp_dists = [
        atr * p["atr_tp1_mult"],
        atr * p["atr_tp2_mult"],
        atr * p["atr_tp3_mult"],
    ]
    zone_half = atr * p["entry_zone_atr"] / 2

    sl = entry - sign * sl_dist
    zone_lo, zone_hi = sorted([entry - zone_half, entry + zone_half])

    # --- Position sizing ---
    # XAUUSD: กำไร/ขาดทุน 1 ไม้ = ระยะราคา (USD) × contract_size × lot
    risk_usd_target = p["account_balance"] * p["risk_percent"] / 100
    raw_lot = risk_usd_target / (sl_dist * p["contract_size"]) if sl_dist > 0 else 0.0
    lot = round(max(p["min_lot"], min(p["max_lot"], raw_lot)), 2)
    actual_risk_usd = round(lot * sl_dist * p["contract_size"], 2)
    risk_pct_actual = round(actual_risk_usd / p["account_balance"] * 100, 2) if p["account_balance"] > 0 else 0.0
    # min_lot ทำให้ความเสี่ยงจริงเกินเป้า หรือ max_lot ทำให้ต่ำกว่าเป้า
    risk_exceeds_target = actual_risk_usd > risk_usd_target * 1.05

    # --- TP levels + partial close ---
    tp_levels = []
    for i, (dist, part) in enumerate(zip(tp_dists, p["tp_split"]), start=1):
        tp_levels.append({
            "level": i,
            "price": round(entry + sign * dist, 2),
            "distance": round(dist, 2),
            "rr": round(dist / sl_dist, 2) if sl_dist > 0 else 0.0,
            "close_percent": int(round(part * 100)),
            "lot": round(lot * part, 2),
        })

    return {
        "direction": direction,
        "entry": round(entry, 2),
        "entry_zone": {"min": round(zone_lo, 2), "max": round(zone_hi, 2)},
        "sl": round(sl, 2),
        "sl_distance": round(sl_dist, 2),
        "tp": tp_levels,
        # --- alias เพื่อ backward compatibility ---
        "tp1": tp_levels[0]["price"],
        "tp2": tp_levels[1]["price"],
        "tp3": tp_levels[2]["price"],
        "rr_ratio": tp_levels[0]["rr"],
        "position": {
            "lot": lot,
            "risk_usd": actual_risk_usd,
            "risk_percent": p["risk_percent"],
            "risk_percent_actual": risk_pct_actual,
            "risk_exceeds_target": risk_exceeds_target,
            "account_balance": p["account_balance"],
            "contract_size": p["contract_size"],
        },
        "management": {
            "breakeven_trigger": p["be_trigger"],
            "breakeven_price": round(entry, 2),
            "trailing_atr_mult": p["trail_atr_mult"],
            "trailing_distance": round(atr * p["trail_atr_mult"], 2),
        },
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
    # คำนวณแผนเทรดครบชุด (Buy/SL/TP + lot + management)
    # ============================
    plan = build_trade_plan(direction, price, atr_now, p)

    signal = {
        "id": f"SIG-{uuid.uuid4().hex[:8].upper()}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": "XAUUSD",
        "direction": direction,
        "strength": strength,
        "confidence": confidence,
        "entry": plan["entry"],
        "entry_zone": plan["entry_zone"],
        "sl": plan["sl"],
        "tp1": plan["tp1"],
        "tp2": plan["tp2"],
        "tp3": plan["tp3"],
        "rr_ratio": plan["rr_ratio"],
        "trade_plan": plan,
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
