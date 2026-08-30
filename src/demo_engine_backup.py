import csv
import time

from strategy import generate_signal
from risk_manager import calculate_trade
from trade_manager import TradeManager


CSV_FILE = "data/EURUSD_H1.csv"
LOG_FILE = "data/demo_trade_log.csv"

def load_prices(filename):
    prices = []

    with open(filename, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            prices.append(float(row["close"]))

    return prices


print("===== FOREX BOT DEMO ENGINE =====")
print("Strategy: MA 5/30/75 + RSI 14")
print("Mode: PAPER TRADING")
print("=================================")


prices = load_prices(CSV_FILE)

manager = TradeManager()
trade_log = []
print(f"Loaded candles: {len(prices)}")

history = []


for price in prices:

    history.append(price)

    if len(history) < 100:
        continue

    print()
    print(f"EUR/USD close: {price}")

    manager.update_trade(price)

    if not manager.has_open_trade():

        signal = generate_signal(history)

        print(f"Signal: {signal}")

        if signal in ("BUY", "SELL"):

            trade = calculate_trade(
                price,
                signal
            )

            manager.record_trade(
                trade["signal"],
                trade["entry"],
                trade["stop_loss"],
                trade["take_profit"]
            )
            trade_log.append({
                "signal": trade["signal"],
                "entry": trade["entry"],
                "stop_loss": trade["stop_loss"],
                "take_profit": trade["take_profit"]
            })
            print("PAPER TRADE OPENED")
            print(f"Direction: {trade['signal']}")
            print(f"Entry: {trade['entry']}")
            print(f"SL: {trade['stop_loss']}")
            print(f"TP: {trade['take_profit']}")

    time.sleep(0.1)


print()
print("===== DEMO COMPLETE =====")

manager.show_summary()
import csv

with open("data/demo_trade_log.csv", "w", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "signal",
            "entry",
            "stop_loss",
            "take_profit"
        ]
    )

    writer.writeheader()
    writer.writerows(trade_log)

print("Trade log saved: data/demo_trade_log.csv")
