"""
Web Dashboard — Flask
======================
UI แสดง signal ชัดเจนว่าเป็นคู่เงินอะไร
พร้อมราคาปัจจุบัน, ประวัติ signal, สถิติ
"""

from flask import Flask, render_template, jsonify
from app.config import SECRET_KEY, FLASK_PORT
from app.runner import run_scan
from app.data.fetcher import get_current_price
from app.utils.store import get_signals, get_stats
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import SCAN_INTERVAL
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = Flask(
    __name__,
    template_folder="web/templates",
    static_folder="web/static",
)
app.secret_key = SECRET_KEY


# ============================
# Routes
# ============================

@app.route("/")
def index():
    """หน้า Dashboard หลัก"""
    price_info = get_current_price()
    signals = get_signals(limit=20)
    stats = get_stats()
    return render_template("dashboard.html",
                           price=price_info,
                           signals=signals,
                           stats=stats)


@app.route("/api/scan", methods=["POST"])
def api_scan():
    """Trigger manual scan"""
    signal = run_scan()
    if signal:
        return jsonify({"status": "signal", "data": signal})
    return jsonify({"status": "no_signal", "data": None})


@app.route("/api/signals")
def api_signals():
    """ดึง signals ล่าสุด"""
    signals = get_signals(limit=50)
    return jsonify(signals)


@app.route("/api/price")
def api_price():
    """ราคาปัจจุบัน"""
    return jsonify(get_current_price())


@app.route("/api/stats")
def api_stats():
    """สถิติ"""
    return jsonify(get_stats())


# ============================
# Scheduler — auto scan
# ============================

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_scan, "interval", minutes=SCAN_INTERVAL,
                      id="signal_scan", replace_existing=True)
    scheduler.start()
    logging.info(f"Scheduler started: scan every {SCAN_INTERVAL} minutes")


if __name__ == "__main__":
    start_scheduler()
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=False)
