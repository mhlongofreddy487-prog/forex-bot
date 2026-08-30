import csv
import time
import requests
from datetime import datetime, timezone

from strategy import generate_signal
from risk_manager import calculate_trade


SYMBOL = "EURUSD=X"
INTERVAL = "1h"

RISK_PERCENT = 1.0
STOP_DISTANCE = 0.0010
REWARD_MULTIPLIER = 2.0

STARTING_BALANCE = 10000.0
LOG_FILE = "data/live_paper_log.csv"

YAHOO_URL = (
    "https://query1.finance.yahoo.com/v8/finance/chart/"
    f"{SYMBOL}?range=5d&interval={INTERVAL}"
)


def get_candles():
    response = requests.get(YAHOO_URL, timeout=15)
    response.raise_for_status()

    data = response.json()["chart"]["result"][0]

    timestamps = data["timestamp"]
    quote = data["indicators"]["quote"][0]

    candles = []

    for i, timestamp in enumerate(timestamps):
        if (
            quote["open"][i] is None
            or quote["high"][i] is None
            or quote["low"][i] is None
            or quote["close"][i] is None
        ):
            continue

        candles.append({
            "time": datetime.fromtimestamp(
                timestamp, tz=timezone.utc
            ).isoformat(),
            "open": float(quote["open"][i]),
            "high": float(quote["high"][i]),
            "low": float(quote["low"][i]),
            "close": float(quote["close"][i]),
        })

    return candles


def save_signal(candle, signal, trade=None):
    file_exists = False

    try:
        with open(LOG_FILE, "r"):
            file_exists = True
    except FileNotFoundError:
        pass

    with open(LOG_FILE, "a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "time",
                "close",
                "signal",
                "entry",
                "stop_loss",
                "take_profit"
            ])

        writer.writerow([
            candle["time"],
            f"{candle['close']:.5f}",
            signal,
            f"{trade['entry']:.5f}" if trade else "",
            f"{trade['stop_loss']:.5f}" if trade else "",
            f"{trade['take_profit']:.5f}" if trade else "",
        ])


def main():
    print("===== EUR/USD H1 LIVE PAPER ENGINE =====")
    print("Strategy: MA 5/40/75 + RSI 14")
    print("Risk: 1%")
    print("SL: 10 pips")
    print("TP: 20 pips")
    print("Mode: PAPER ONLY")
    print("=========================================")

    last_candle_time = None
    balance = STARTING_BALANCE
    open_trade = None

    while True:
        try:
            candles = get_candles()

            if len(candles) < 76:
                print("Waiting for enough H1 candles...")
                time.sleep(60)
                continue

            # Ignore the currently forming candle.
            closed_candles = candles[:-1]

            latest = closed_candles[-1]

            if latest["time"] == last_candle_time:
                time.sleep(60)
                continue

            last_candle_time = latest["time"]

            closes = [c["close"] for c in closed_candles]

            signal = generate_signal(closes)

            print()
            print("===== NEW CLOSED H1 CANDLE =====")
            print(f"Time:   {latest['time']}")
            print(f"Close:  {latest['close']:.5f}")
            print(f"Signal: {signal}")

            if open_trade is None and signal in ("BUY", "SELL"):
                trade = calculate_trade(
                    latest["close"],
                    signal,
                    account_balance=balance,
                    risk_percent=RISK_PERCENT,
                    stop_distance=STOP_DISTANCE
                )

                trade["reward_multiplier"] = REWARD_MULTIPLIER

                open_trade = trade

                print()
                print("PAPER TRADE OPENED")
                print(f"Direction: {trade['signal']}")
                print(f"Entry:     {trade['entry']:.5f}")
                print(f"SL:        {trade['stop_loss']:.5f}")
                print(f"TP:        {trade['take_profit']:.5f}")
                print(f"Risk:      ${trade['risk_amount']:.2f}")

                save_signal(latest, signal, trade)

            else:
                save_signal(latest, signal)

            print(f"Balance: ${balance:.2f}")

        except Exception as error:
            print(f"Data error: {error}")

        time.sleep(60)


if __name__ == "__main__":
    main()
