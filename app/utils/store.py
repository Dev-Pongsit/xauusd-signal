"""
Signal Store — เก็บประวัติ signal เป็น JSON
ไม่ต้องติดตั้ง database — ทำงานบน VPS ได้ทันที
"""

import json
import os
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

STORE_DIR = Path(__file__).parent.parent.parent / "data"
STORE_FILE = STORE_DIR / "signals.json"


def _ensure_store():
    STORE_DIR.mkdir(exist_ok=True)
    if not STORE_FILE.exists():
        STORE_FILE.write_text("[]")


def save_signal(signal: dict):
    """บันทึก signal ลง JSON file"""
    _ensure_store()
    try:
        signals = json.loads(STORE_FILE.read_text())
        signals.append(signal)
        # เก็บแค่ 500 signals ล่าสุด
        if len(signals) > 500:
            signals = signals[-500:]
        STORE_FILE.write_text(json.dumps(signals, indent=2, default=str))
        logger.info(f"Signal saved: {signal['id']}")
    except Exception as e:
        logger.error(f"Save failed: {e}")


def get_signals(limit: int = 50) -> list:
    """ดึง signals ล่าสุด"""
    _ensure_store()
    try:
        signals = json.loads(STORE_FILE.read_text())
        return signals[-limit:][::-1]  # newest first
    except Exception:
        return []


def get_stats() -> dict:
    """สถิติ signals"""
    signals = get_signals(limit=500)
    if not signals:
        return {"total": 0, "buy": 0, "sell": 0, "strong": 0, "avg_confidence": 0}

    buy = sum(1 for s in signals if s["direction"] == "BUY")
    sell = sum(1 for s in signals if s["direction"] == "SELL")
    strong = sum(1 for s in signals if s["strength"] == "STRONG")
    avg_conf = sum(s["confidence"] for s in signals) / len(signals)

    return {
        "total": len(signals),
        "buy": buy,
        "sell": sell,
        "strong": strong,
        "avg_confidence": round(avg_conf, 1),
    }
