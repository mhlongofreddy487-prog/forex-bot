import csv
import os

from strategy import generate_signal
from risk_manager import calculate_trade


CSV_FILE = "data/EURUSD_H1.csv"
LOG_FILE = "data/forward_trade_log.csv"

STARTING_BALANCE = 10000.0
RISK_PERCENT = 1.0

SPREAD = 0.00010
SLIPPAGE = 0.00002

STOP_DISTANCE = 0.0010
REWARD_MULTIPLIER = 2.0


def load_candles(filename):
    candles = []

    with open(filename, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            candles.append({
                "time": row["time"],
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"])
            })

    return candles


def initialize_log():
    if os.path.exists(LOG_FILE):
        return

    with open(LOG_FILE, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "time",
            "signal",
            "entry",
            "stop_loss",
            "take_profit",
            "result",
            "profit",
            "balance"
        ])


def save_trade(trade):
    with open(LOG_FILE, "a", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            trade["time"],
            trade["signal"],
            f'{trade["entry"]:.5f}',
            f'{trade["stop_loss"]:.5f}',
            f'{trade["take_profit"]:.5f}',
            trade["result"],
            f'{trade["profit"]:.2f}',
            f'{trade["balance"]:.2f}'
        ])


def run_forward_test(candles):

    initialize_log()

    balance = STARTING_BALANCE

    trade = None
    pending_signal = None

    wins = 0
    losses = 0

    start_index = 75

    print()
    print("===== FORWARD TEST ENGINE =====")
    print(f"Candles available: {len(candles)}")
    print(f"Starting balance:  ${STARTING_BALANCE:.2f}")
    print()

    for i in range(start_index, len(candles)):

        candle = candles[i]

        # -------------------------------------------------
        # ENTER USING PREVIOUS CANDLE'S SIGNAL
        # -------------------------------------------------

        if trade is None and pending_signal in ("BUY", "SELL"):

            signal = pending_signal

            if signal == "BUY":
                entry = (
                    candle["open"]
                    + (SPREAD / 2)
                    + SLIPPAGE
                )

            else:
                entry = (
                    candle["open"]
                    - (SPREAD / 2)
                    - SLIPPAGE
                )

            trade = calculate_trade(
                entry,
                signal,
                account_balance=balance,
                risk_percent=RISK_PERCENT,
                stop_distance=STOP_DISTANCE
            )

            trade["time"] = candle["time"]

            print(
                f"ENTRY {signal} | "
                f"{candle['time']} | "
                f"Entry: {entry:.5f} | "
                f"SL: {trade['stop_loss']:.5f} | "
                f"TP: {trade['take_profit']:.5f}"
            )

            pending_signal = None

        # -------------------------------------------------
        # MANAGE OPEN TRADE
        # -------------------------------------------------

        if trade is not None:

            if trade["signal"] == "BUY":

                stop_hit = (
                    candle["low"]
                    <= trade["stop_loss"]
                )

                target_hit = (
                    candle["high"]
                    >= trade["take_profit"]
                )

                if stop_hit:

                    risk_amount = trade["risk_amount"]

                    balance -= risk_amount

                    losses += 1

                    trade["result"] = "LOSS"
                    trade["profit"] = -risk_amount
                    trade["balance"] = balance

                    save_trade(trade)

                    print(
                        f"LOSS | "
                        f"Balance: ${balance:.2f}"
                    )

                    trade = None

                elif target_hit:

                    profit = (
                        trade["risk_amount"]
                        * REWARD_MULTIPLIER
                    )

                    balance += profit

                    wins += 1

                    trade["result"] = "WIN"
                    trade["profit"] = profit
                    trade["balance"] = balance

                    save_trade(trade)

                    print(
                        f"WIN | "
                        f"Balance: ${balance:.2f}"
                    )

                    trade = None

            elif trade["signal"] == "SELL":

                stop_hit = (
                    candle["high"]
                    >= trade["stop_loss"]
                )

                target_hit = (
                    candle["low"]
                    <= trade["take_profit"]
                )

                if stop_hit:

                    risk_amount = trade["risk_amount"]

                    balance -= risk_amount

                    losses += 1

                    trade["result"] = "LOSS"
                    trade["profit"] = -risk_amount
                    trade["balance"] = balance

                    save_trade(trade)

                    print(
                        f"LOSS | "
                        f"Balance: ${balance:.2f}"
                    )

                    trade = None

                elif target_hit:

                    profit = (
                        trade["risk_amount"]
                        * REWARD_MULTIPLIER
                    )

                    balance += profit

                    wins += 1

                    trade["result"] = "WIN"
                    trade["profit"] = profit
                    trade["balance"] = balance

                    save_trade(trade)

                    print(
                        f"WIN | "
                        f"Balance: ${balance:.2f}"
                    )

                    trade = None

        # -------------------------------------------------
        # GENERATE NEXT SIGNAL
        # -------------------------------------------------

        if trade is None and i + 1 < len(candles):

            closes = [
                c["close"]
                for c in candles[:i + 1]
            ]

            pending_signal = generate_signal(closes)

    total = wins + losses

    win_rate = (
        wins / total * 100
        if total > 0
        else 0.0
    )

    print()
    print("========== FORWARD TEST SUMMARY ==========")
    print(f"Starting balance: ${STARTING_BALANCE:.2f}")
    print(f"Final balance:    ${balance:.2f}")
    print(f"Net profit:       ${balance - STARTING_BALANCE:.2f}")
    print(f"Trades:           {total}")
    print(f"Wins:             {wins}")
    print(f"Losses:           {losses}")
    print(f"Win rate:         {win_rate:.2f}%")
    print("===========================================")


if __name__ == "__main__":

    candles = load_candles(CSV_FILE)

    run_forward_test(candles)
