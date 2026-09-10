# ทดสอบ
"""
==========================================
🧪 Local Test Script — ทดสอบระบบทั้งหมด
==========================================
รันด้วย: python test_local.py

ทดสอบทีละขั้นตอน:
  [1] ดึงข้อมูลราคาทองคำ (yfinance)
  [2] คำนวณ Indicators (EMA, MACD, RSI, ATR)
  [3] สร้าง Signal
  [4] AI วิเคราะห์ (ถ้ามี API key)
  [5] บันทึก Signal
  [6] แสดงผลบน Console
  [7] เปิด Dashboard

ไม่ต้องมี API key ก็ทดสอบได้ (ข้าม AI step)
"""

import sys
import os
import time
import io

# ============================
# Fix Windows Console Encoding
# ============================
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ============================
# สีสำหรับ Windows Console
# ============================
os.system("")  # Enable ANSI colors on Windows

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
GOLD = "\033[33m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"


def print_header():
    print(f"""
{GOLD}{BOLD}
  ╔══════════════════════════════════════════════╗
  ║  🥇  XAUUSD AI Signal — Local Test          ║
  ║      ทดสอบระบบบน Windows                      ║
  ╚══════════════════════════════════════════════╝
{RESET}""")


def print_step(num, title):
    print(f"\n{CYAN}{BOLD}{'='*50}")
    print(f"  [{num}/7] {title}")
    print(f"{'='*50}{RESET}\n")


def print_pass(msg):
    print(f"  {GREEN}✅ PASS:{RESET} {msg}")


def print_fail(msg):
    print(f"  {RED}❌ FAIL:{RESET} {msg}")


def print_warn(msg):
    print(f"  {YELLOW}⚠️  WARN:{RESET} {msg}")


def print_info(msg):
    print(f"  {DIM}ℹ️  {msg}{RESET}")


# ============================
# Test 1: ดึงข้อมูลราคาทองคำ
# ============================
def test_data_fetch():
    print_step(1, "ดึงข้อมูลราคา XAUUSD (ทองคำ)")

    try:
        from app.data.fetcher import fetch_xauusd, get_current_price

        # ดึง historical data
        print_info("กำลังดึงข้อมูลจาก Yahoo Finance...")
        df = fetch_xauusd(period="30d", interval="1h")

        print_pass(f"ดึงข้อมูลสำเร็จ: {len(df)} แท่งเทียน")
        print_info(f"ช่วงเวลา: {df['time'].iloc[0]} → {df['time'].iloc[-1]}")
        print_info(f"ราคาล่าสุด: ${df['close'].iloc[-1]:.2f}")
        print_info(f"สูงสุด: ${df['high'].max():.2f} | ต่ำสุด: ${df['low'].min():.2f}")

        # ดึงราคาปัจจุบัน
        price = get_current_price()
        if price["price"] > 0:
            chg = "+" if price["change"] >= 0 else ""
            print_pass(f"ราคาปัจจุบัน: ${price['price']} ({chg}{price['change']})")
        else:
            print_warn("ราคาปัจจุบัน = 0 (ตลาดอาจปิดอยู่)")

        print()
        print(f"  {GOLD}📊 ตัวอย่างข้อมูล 5 แท่งเทียนล่าสุด:{RESET}")
        for _, row in df.tail(5).iterrows():
            t = str(row["time"])[:16]
            print(f"     {t} | O:{row['open']:>8.2f} H:{row['high']:>8.2f} "
                  f"L:{row['low']:>8.2f} C:{row['close']:>8.2f}")

        return df

    except Exception as e:
        print_fail(f"ดึงข้อมูลล้มเหลว: {e}")
        print_warn("อาจเป็นเพราะ: ไม่มี internet / ตลาดปิด / yfinance มีปัญหา")
        return None


# ============================
# Test 2: คำนวณ Indicators
# ============================
def test_indicators(df):
    print_step(2, "คำนวณ Technical Indicators")

    try:
        from app.strategies.trend_following import calculate_indicators

        df_ind = calculate_indicators(df)

        last = df_ind.iloc[-1]
        print_pass("คำนวณ Indicators สำเร็จ")
        print()
        print(f"  {GOLD}📈 ค่า Indicators ล่าสุด:{RESET}")
        print(f"     EMA  9:  {last['ema_fast']:.2f}")
        print(f"     EMA 21:  {last['ema_slow']:.2f}")
        print(f"     MACD:    {last['macd']:.2f}")
        print(f"     Signal:  {last['macd_signal']:.2f}")
        print(f"     Hist:    {last['macd_hist']:.2f}")
        print(f"     RSI:     {last['rsi']:.1f}")
        print(f"     ATR:     {last['atr']:.2f}")

        # วิเคราะห์สถานะ
        trend = "BULLISH 📈" if last["ema_fast"] > last["ema_slow"] else "BEARISH 📉"
        momentum = "POSITIVE" if last["macd_hist"] > 0 else "NEGATIVE"
        rsi_status = ("OVERBOUGHT ⚠️" if last["rsi"] > 70
                      else "OVERSOLD ⚠️" if last["rsi"] < 30
                      else "NEUTRAL ✅")

        print()
        print(f"  {CYAN}📋 สรุปสถานะ:{RESET}")
        print(f"     Trend:    {trend}")
        print(f"     Momentum: {momentum}")
        print(f"     RSI:      {rsi_status}")

        return True

    except Exception as e:
        print_fail(f"คำนวณ Indicators ล้มเหลว: {e}")
        return False


# ============================
# Test 3: สร้าง Signal
# ============================
def test_signal(df):
    print_step(3, "สร้าง Trading Signal")

    try:
        from app.strategies.trend_following import generate_signal

        signal = generate_signal(df)

        if signal is None:
            print_warn("ไม่มี Signal ในขณะนี้ (ปกติ — ตลาดอาจไม่มีสัญญาณชัด)")
            print_info("ระบบจะสร้าง signal เฉพาะเมื่อเงื่อนไขครบเท่านั้น")
            print_info("ลองรันใหม่ในชั่วโมงถัดไป หรือดู Test 3b (Force Test)")

            # Force test — สร้าง mock signal เพื่อทดสอบส่วนอื่น
            print()
            print(f"  {YELLOW}🔧 สร้าง Mock Signal เพื่อทดสอบ pipeline ต่อ...{RESET}")
            from app.strategies.trend_following import build_trade_plan

            mock_price = round(df["close"].iloc[-1], 2)
            mock_atr = round(df["high"].iloc[-1] - df["low"].iloc[-1], 2) or 5.0
            mock_plan = build_trade_plan("BUY", mock_price, mock_atr)
            signal = {
                "id": "SIG-TEST0001",
                "timestamp": "2026-02-12 16:00:00",
                "symbol": "XAUUSD",
                "direction": "BUY",
                "strength": "STRONG",
                "confidence": 85,
                "entry": mock_plan["entry"],
                "entry_zone": mock_plan["entry_zone"],
                "sl": mock_plan["sl"],
                "tp1": mock_plan["tp1"],
                "tp2": mock_plan["tp2"],
                "tp3": mock_plan["tp3"],
                "rr_ratio": mock_plan["rr_ratio"],
                "trade_plan": mock_plan,
                "reasoning": "[MOCK] Test signal for pipeline verification",
                "indicators": {
                    "ema_fast": round(df["close"].iloc[-1], 2),
                    "ema_slow": round(df["close"].iloc[-2], 2),
                    "macd": 1.25,
                    "macd_signal": 0.80,
                    "macd_hist": 0.45,
                    "rsi": 58.5,
                    "atr": round(df["high"].iloc[-1] - df["low"].iloc[-1], 2),
                },
                "ai_analysis": None,
            }
            print_pass("Mock Signal สร้างสำเร็จ")
        else:
            direction = signal["direction"]
            arrow = f"{GREEN}🟢 BUY{RESET}" if direction == "BUY" else f"{RED}🔴 SELL{RESET}"
            print_pass(f"Signal detected!")
            print()
            print(f"  {GOLD}{'━'*44}")
            print(f"  {arrow}  XAUUSD (ทองคำ)  {signal['strength']}")
            print(f"  {GOLD}{'━'*44}{RESET}")
            print(f"     📍 Entry:  ${signal['entry']}")
            print(f"     🛑 SL:     ${signal['sl']}")
            print(f"     🎯 TP1:    ${signal['tp1']}")
            print(f"     🎯 TP2:    ${signal['tp2']}")
            print(f"     🎯 TP3:    ${signal.get('tp3', 'N/A')}")
            print(f"     📊 R:R:    1:{signal['rr_ratio']}")
            if signal.get("trade_plan"):
                pos = signal["trade_plan"]["position"]
                print(f"     💰 Lot:    {pos['lot']} (เสี่ยง ${pos['risk_usd']} ≈ {pos['risk_percent']}%)")
            print(f"     💪 Conf:   {signal['confidence']}%")
            print(f"     💡 {signal['reasoning']}")

        return signal

    except Exception as e:
        print_fail(f"สร้าง Signal ล้มเหลว: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================
# Test 3b: Trade Plan ครบชุด
# ============================
def test_trade_plan():
    print_step("3b", "ตรวจแผนเทรดครบชุด (Buy/SL/TP + Lot)")

    try:
        from app.strategies.trend_following import build_trade_plan

        entry, atr = 3300.0, 20.0
        # ใช้พอร์ตใหญ่พอให้ lot ไม่ติดเพดาน min_lot (ทดสอบสูตร sizing)
        risk_cfg = {"account_balance": 100000.0, "risk_percent": 1.0}
        buy = build_trade_plan("BUY", entry, atr, risk_cfg)
        sell = build_trade_plan("SELL", entry, atr, risk_cfg)

        # BUY: SL ต่ำกว่า entry, TP ไล่ขึ้นตามลำดับ
        assert buy["sl"] < buy["entry"] < buy["tp1"] < buy["tp2"] < buy["tp3"], "ลำดับราคา BUY ผิด"
        # SELL: กลับด้าน
        assert sell["tp3"] < sell["tp2"] < sell["tp1"] < sell["entry"] < sell["sl"], "ลำดับราคา SELL ผิด"
        # partial close รวมกัน = 100%
        total_pct = sum(t["close_percent"] for t in buy["tp"])
        assert total_pct == 100, f"partial close รวม {total_pct}% ไม่ครบ 100"
        # lot อยู่ในช่วงที่ตั้ง + risk ใกล้เคียงเป้า (พอร์ตใหญ่ = ไม่ติดเพดาน)
        pos = buy["position"]
        assert 0.01 <= pos["lot"] <= 5.0, f"lot {pos['lot']} เกินขอบเขต"
        target_risk = pos["account_balance"] * pos["risk_percent"] / 100
        assert abs(pos["risk_usd"] - target_risk) <= target_risk * 0.1, "risk_usd เพี้ยนจากเป้าหมาย"
        # พอร์ตเล็ก → ติดเพดาน min_lot → ต้องตั้งธง risk_exceeds_target
        small = build_trade_plan("BUY", entry, atr, {"account_balance": 1000.0, "risk_percent": 1.0})
        assert small["position"]["risk_exceeds_target"] is True, "ควรเตือนเมื่อ risk เกินเป้า"
        # entry zone ครอบ entry
        assert buy["entry_zone"]["min"] <= buy["entry"] <= buy["entry_zone"]["max"], "entry zone ไม่ครอบ entry"

        print_pass("แผนเทรดครบชุดถูกต้อง (BUY + SELL)")
        print()
        print(f"  {GOLD}📋 ตัวอย่าง BUY @ {entry} (ATR {atr}):{RESET}")
        print(f"     Entry zone: ${buy['entry_zone']['min']} – ${buy['entry_zone']['max']}")
        print(f"     SL: ${buy['sl']}  (ระยะ {buy['sl_distance']})")
        for t in buy["tp"]:
            print(f"     TP{t['level']}: ${t['price']}  R:R 1:{t['rr']}  ปิด {t['close_percent']}%")
        print(f"     Lot: {pos['lot']}  | เสี่ยง ${pos['risk_usd']} ({pos['risk_percent']}% ของ ${pos['account_balance']})")
        print(f"     Breakeven เมื่อถึง {buy['management']['breakeven_trigger']}, "
              f"trailing {buy['management']['trailing_distance']}")

        return True

    except Exception as e:
        print_fail(f"แผนเทรดครบชุดผิดพลาด: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================
# Test 4: AI Analysis
# ============================
def test_ai(signal, df):
    print_step(4, "AI วิเคราะห์ตลาด (Claude)")

    from app.config import ANTHROPIC_API_KEY

    if not ANTHROPIC_API_KEY:
        print_warn("ไม่มี ANTHROPIC_API_KEY ใน .env")
        print_info("ข้าม AI test — ระบบยังทำงานได้ปกติโดยไม่มี AI")
        print_info("ถ้าต้องการทดสอบ AI ให้ใส่ key ใน .env แล้วรันใหม่")
        return signal

    try:
        from app.ai.analysis import analyze_signal, apply_ai_override

        print_info("กำลังส่งข้อมูลให้ Claude วิเคราะห์...")
        last_10 = df.tail(10)
        candles_text = "\n".join(
            f"{row['time']} | O:{row['open']:.2f} H:{row['high']:.2f} "
            f"L:{row['low']:.2f} C:{row['close']:.2f}"
            for _, row in last_10.iterrows()
        )

        ai_result = analyze_signal(signal, candles_text)

        if ai_result:
            print_pass("AI วิเคราะห์สำเร็จ!")
            print()
            print(f"  {CYAN}🤖 AI Analysis:{RESET}")
            print(f"     Market:    {ai_result.get('market_condition', 'N/A')}")
            print(f"     Trend:     {ai_result.get('trend', 'N/A')}")
            print(f"     AI says:   {ai_result.get('recommendation', 'N/A')}")
            print(f"     Conf:      {ai_result.get('confidence', 0)}%")
            print(f"     Reasoning: {ai_result.get('reasoning', 'N/A')}")

            if ai_result.get("risks"):
                print(f"     ⚠️ Risks:")
                for r in ai_result["risks"]:
                    print(f"        - {r}")

            # Apply override
            signal = apply_ai_override(signal, ai_result)
            print_info(f"Confidence หลัง AI: {signal['confidence']}%")
        else:
            print_warn("AI ไม่ส่งผลลัพธ์กลับมา")

        return signal

    except Exception as e:
        print_fail(f"AI วิเคราะห์ล้มเหลว: {e}")
        return signal


# ============================
# Test 5: บันทึก Signal
# ============================
def test_store(signal):
    print_step(5, "บันทึก Signal")

    try:
        from app.utils.store import save_signal, get_signals, get_stats

        save_signal(signal)
        print_pass("บันทึก signal สำเร็จ")

        # ดึงกลับมาเช็ค
        signals = get_signals(limit=5)
        stats = get_stats()

        print_info(f"Signals ในระบบ: {stats['total']} รายการ")
        print_info(f"BUY: {stats['buy']} | SELL: {stats['sell']} | "
                   f"STRONG: {stats['strong']} | Avg Conf: {stats['avg_confidence']}%")

        return True

    except Exception as e:
        print_fail(f"บันทึกล้มเหลว: {e}")
        return False


# ============================
# Test 6: Notification
# ============================
def test_notification(signal):
    print_step(6, "แสดงผล Signal (Console + Telegram)")

    try:
        from app.utils.notify import format_signal_text, send_telegram
        from app.config import TELEGRAM_BOT_TOKEN

        text = format_signal_text(signal)
        print_pass("Format signal สำเร็จ:")
        print()
        print(f"{GOLD}{text}{RESET}")

        if TELEGRAM_BOT_TOKEN:
            print()
            print_info("กำลังส่ง Telegram...")
            ok = send_telegram(text)
            if ok:
                print_pass("ส่ง Telegram สำเร็จ! เช็คมือถือ")
            else:
                print_warn("ส่ง Telegram ไม่สำเร็จ — เช็ค Token/Chat ID")
        else:
            print_warn("ไม่ได้ตั้งค่า Telegram — ข้าม")
            print_info("ใส่ TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID ใน .env ถ้าต้องการ")

        return True

    except Exception as e:
        print_fail(f"Notification ล้มเหลว: {e}")
        return False


# ============================
# Test 7: Dashboard
# ============================
def test_ema_ribbon():
    """ทดสอบตัวจำแนกสีเส้น EMA (แถบสีบน dashboard card)"""
    print(f"\n{CYAN}{BOLD}{'='*50}")
    print(f"  [EMA Ribbon] เช็คสีเส้น EMA")
    print(f"{'='*50}{RESET}\n")

    from app.strategies.trend_following import classify_ema_ribbon

    cases = [
        # (ema_fast, ema_slow, atr, expected_state)
        (2050.0, 2040.0, 5.0, "bullish"),   # เร็ว > ช้า ชัดเจน
        (2040.0, 2050.0, 5.0, "bearish"),   # เร็ว < ช้า ชัดเจน
        (2050.10, 2050.0, 8.0, "neutral"),  # ห่างกัน 0.1 < 5% ของ ATR (0.4)
        (2050.0, 2040.0, None, "bullish"),  # ไม่มี ATR ก็ยังจำแนกได้
    ]

    ok = True
    for ema_fast, ema_slow, atr, expected in cases:
        result = classify_ema_ribbon(ema_fast, ema_slow, atr)
        got = result["state"]
        # โครงสร้าง dict ต้องครบสำหรับ template
        has_keys = all(k in result for k in ("state", "gap", "color", "icon", "label"))
        if got == expected and has_keys:
            print_pass(f"EMA {ema_fast}/{ema_slow} atr={atr} → {got}")
        else:
            print_fail(f"EMA {ema_fast}/{ema_slow} atr={atr} → {got} (คาดว่า {expected}, keys_ok={has_keys})")
            ok = False

    return ok


def test_dashboard():
    print_step(7, "เปิด Web Dashboard")

    print_info("Dashboard พร้อมเปิดแล้ว")
    print()
    print(f"  {GOLD}{BOLD}┌────────────────────────────────────────┐")
    print(f"  │                                        │")
    print(f"  │   เปิด browser แล้วไปที่:               │")
    print(f"  │                                        │")
    print(f"  │   👉  http://localhost:5000             │")
    print(f"  │                                        │")
    print(f"  │   กด Ctrl+C เพื่อหยุด server            │")
    print(f"  └────────────────────────────────────────┘{RESET}")
    print()

    try:
        # เปิด browser อัตโนมัติ
        import webbrowser
        import threading
        threading.Timer(2.0, lambda: webbrowser.open("http://localhost:5000")).start()

        from server import app, start_scheduler
        start_scheduler()
        print_info("กำลังเปิด Dashboard... (Ctrl+C เพื่อหยุด)")
        app.run(host="0.0.0.0", port=5000, debug=False)

    except KeyboardInterrupt:
        print(f"\n{GREEN}✅ หยุด server เรียบร้อย{RESET}")
    except Exception as e:
        print_fail(f"Dashboard error: {e}")


# ============================
# Main
# ============================
def main():
    print_header()

    results = {"pass": 0, "fail": 0, "skip": 0}

    # Test 1: Data
    df = test_data_fetch()
    if df is not None:
        results["pass"] += 1
    else:
        results["fail"] += 1
        print(f"\n{RED}❌ ไม่สามารถดึงข้อมูลได้ — หยุดทดสอบ{RESET}")
        print("   ตรวจสอบ: internet connection + ลอง `pip install yfinance --upgrade`")
        sys.exit(1)

    # Test 2: Indicators
    if test_indicators(df):
        results["pass"] += 1
    else:
        results["fail"] += 1

    # Test 3: Signal
    signal = test_signal(df)
    if signal:
        results["pass"] += 1
    else:
        results["fail"] += 1

    # Test 3b: Trade Plan ครบชุด
    if test_trade_plan():
        results["pass"] += 1
    else:
        results["fail"] += 1

    # Test 4: AI
    if signal:
        signal = test_ai(signal, df)
        results["pass"] += 1

    # Test 5: Store
    if signal:
        if test_store(signal):
            results["pass"] += 1
        else:
            results["fail"] += 1

    # Test 6: Notification
    if signal:
        if test_notification(signal):
            results["pass"] += 1
        else:
            results["fail"] += 1

    # Test: EMA Ribbon color check (ไม่ต้องใช้ network)
    if test_ema_ribbon():
        results["pass"] += 1
    else:
        results["fail"] += 1

    # Summary
    print(f"""
{GOLD}{BOLD}
╔══════════════════════════════════════════════╗
║              🧪 TEST SUMMARY                ║
╠══════════════════════════════════════════════╣
║  ✅ Passed:  {results['pass']:<30} ║
║  ❌ Failed:  {results['fail']:<30} ║
╚══════════════════════════════════════════════╝
{RESET}""")

    if results["fail"] == 0:
        print(f"{GREEN}{BOLD}🎉 ทุก test ผ่าน! ระบบพร้อมใช้งาน{RESET}")
    else:
        print(f"{YELLOW}⚠️  บาง test ไม่ผ่าน — ดูรายละเอียดด้านบน{RESET}")

    # ถาม: เปิด Dashboard?
    print()
    choice = input(f"{CYAN}เปิด Dashboard หรือไม่? (y/n): {RESET}").strip().lower()
    if choice in ("y", "yes", ""):
        test_dashboard()
    else:
        print(f"\n{DIM}เปิด Dashboard ทีหลังได้ด้วย: python server.py{RESET}")


if __name__ == "__main__":
    main()
