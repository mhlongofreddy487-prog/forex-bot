import csv

from strategy import generate_signal
from risk_manager import calculate_trade


CSV_FILE = "data/EURUSD_H1.csv"

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


def run_replay(candles):

    balance = STARTING_BALANCE
    peak_balance = STARTING_BALANCE
    max_drawdown = 0.0

    wins = 0
    losses = 0
    trades = 0

    total_profit = 0.0
    total_loss = 0.0

    trade = None
    pending_signal = None

    print("\n===== H1 PAPER REPLAY =====")
    print("Mode: PAPER TRADING")
    print(f"Starting balance: ${balance:.2f}")
    print(f"Candles: {len(candles)}")
    print("============================")

    for i in range(50, len(candles)):

        candle = candles[i]

        # Enter at current candle OPEN using
        # the signal from the previous candle.
        if trade is None and pending_signal in ("BUY", "SELL"):

            signal = pending_signal

            if signal == "BUY":
                entry = candle["open"] + (SPREAD / 2) + SLIPPAGE
            else:
                entry = candle["open"] - (SPREAD / 2) - SLIPPAGE

            trade = calculate_trade(
                entry,
                signal,
                account_balance=balance,
                risk_percent=RISK_PERCENT,
                stop_distance=STOP_DISTANCE
            )

            trades += 1

            print(
                f"\n{candle['time']} | {signal} "
                f"| Entry: {trade['entry']:.5f} "
                f"| SL: {trade['stop_loss']:.5f} "
                f"| TP: {trade['take_profit']:.5f}"
            )

            pending_signal = None

        # Manage open trade using candle high/low.
        if trade is not None:

            if trade["signal"] == "BUY":

                stop_hit = candle["low"] <= trade["stop_loss"]
                target_hit = candle["high"] >= trade["take_profit"]

                if stop_hit:
                    loss = trade["risk_amount"]
                    balance -= loss
                    total_loss += loss
                    losses += 1
                    trade = None

                    print(
                        f"   LOSS | Balance: ${balance:.2f}"
                    )

                elif target_hit:
                    profit = (
                        trade["risk_amount"]
                        * REWARD_MULTIPLIER
                    )

                    balance += profit
                    total_profit += profit
                    wins += 1
                    trade = None

                    print(
                        f"   WIN  | Balance: ${balance:.2f}"
                    )

            elif trade["signal"] == "SELL":

                stop_hit = candle["high"] >= trade["stop_loss"]
                target_hit = candle["low"] <= trade["take_profit"]

                if stop_hit:
                    loss = trade["risk_amount"]
                    balance -= loss
                    total_loss += loss
                    losses += 1
                    trade = None

                    print(
                        f"   LOSS | Balance: ${balance:.2f}"
                    )

                elif target_hit:
                    profit = (
                        trade["risk_amount"]
                        * REWARD_MULTIPLIER
                    )

                    balance += profit
                    total_profit += profit
                    wins += 1
                    trade = None

                    print(
                        f"   WIN  | Balance: ${balance:.2f}"
                    )

        # Track drawdown.
        if balance > peak_balance:
            peak_balance = balance

        drawdown = peak_balance - balance

        if drawdown > max_drawdown:
            max_drawdown = drawdown

        # Generate signal for the next candle.
        if trade is None and i + 1 < len(candles):

            closes = [
                c["close"]
                for c in candles[:i + 1]
            ]

            pending_signal = generate_signal(closes)

    closed_trades = wins + losses

    win_rate = (
        wins / closed_trades * 100
        if closed_trades
        else 0.0
    )

    profit_factor = (
        total_profit / total_loss
        if total_loss > 0
        else 0.0
    )

    print("\n========== PAPER REPLAY SUMMARY ==========")
    print(f"Starting balance: ${STARTING_BALANCE:.2f}")
    print(f"Final balance:    ${balance:.2f}")
    print(f"Net profit:       ${balance - STARTING_BALANCE:.2f}")
    print(f"Total trades:     {trades}")
    print(f"Wins:             {wins}")
    print(f"Losses:           {losses}")
    print(f"Win rate:         {win_rate:.1f}%")
    print(f"Profit factor:    {profit_factor:.2f}")
    print(f"Max drawdown:     ${max_drawdown:.2f}")
    print("===========================================")


if __name__ == "__main__":

    candles = load_candles(CSV_FILE)

    print(f"Loaded candles: {len(candles)}")

    run_replay(candles)
