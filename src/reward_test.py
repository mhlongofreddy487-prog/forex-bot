import csv

from strategy import generate_signal
from risk_manager import calculate_trade

CSV_FILE = "data/EURUSD_H1.csv"

STARTING_BALANCE = 10000.0
RISK_PERCENT = 1.0

SPREAD = 0.00010
SLIPPAGE = 0.00002
STOP_DISTANCE = 0.0010


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


def test(candles, reward_ratio):

    balance = STARTING_BALANCE
    peak = balance
    max_drawdown = 0.0

    wins = 0
    losses = 0
    trades = 0

    profit_total = 0.0
    loss_total = 0.0

    trade = None
    pending_signal = None

    for i in range(100, len(candles)):

        candle = candles[i]

        # Enter at next candle open
        if trade is None and pending_signal in ("BUY", "SELL"):

            if pending_signal == "BUY":
                entry = candle["open"] + SPREAD / 2 + SLIPPAGE
            else:
                entry = candle["open"] - SPREAD / 2 - SLIPPAGE

            trade = calculate_trade(
                entry,
                pending_signal,
                account_balance=balance,
                risk_percent=RISK_PERCENT,
                stop_distance=STOP_DISTANCE
            )

            # Adjust target to the ratio being tested
            if pending_signal == "BUY":
                trade["take_profit"] = round(
                    entry + STOP_DISTANCE * reward_ratio,
                    5
                )
            else:
                trade["take_profit"] = round(
                    entry - STOP_DISTANCE * reward_ratio,
                    5
                )

            trades += 1
            pending_signal = None

        # Manage trade
        if trade is not None:

            if trade["signal"] == "BUY":

                stop_hit = candle["low"] <= trade["stop_loss"]
                target_hit = candle["high"] >= trade["take_profit"]

                if stop_hit:
                    loss = trade["risk_amount"]
                    balance -= loss
                    loss_total += loss
                    losses += 1
                    trade = None

                elif target_hit:
                    profit = trade["risk_amount"] * reward_ratio
                    balance += profit
                    profit_total += profit
                    wins += 1
                    trade = None

            else:

                stop_hit = candle["high"] >= trade["stop_loss"]
                target_hit = candle["low"] <= trade["take_profit"]

                if stop_hit:
                    loss = trade["risk_amount"]
                    balance -= loss
                    loss_total += loss
                    losses += 1
                    trade = None

                elif target_hit:
                    profit = trade["risk_amount"] * reward_ratio
                    balance += profit
                    profit_total += profit
                    wins += 1
                    trade = None

        if balance > peak:
            peak = balance

        drawdown = peak - balance

        if drawdown > max_drawdown:
            max_drawdown = drawdown

        closes = [c["close"] for c in candles[:i + 1]]

        if trade is None:
            pending_signal = generate_signal(closes)

    closed = wins + losses

    win_rate = wins / closed * 100 if closed else 0.0

    profit_factor = (
        profit_total / loss_total
        if loss_total > 0
        else 0.0
    )

    return (
        balance,
        balance - STARTING_BALANCE,
        trades,
        wins,
        losses,
        win_rate,
        profit_factor,
        max_drawdown
    )


if __name__ == "__main__":

    candles = load_candles(CSV_FILE)

    ratios = [1.0, 1.5, 2.0, 2.5, 3.0]

    print("\n===== REWARD/RISK TEST =====")
    print(f"Candles: {len(candles)}")
    print()

    for ratio in ratios:

        (
            balance,
            profit,
            trades,
            wins,
            losses,
            win_rate,
            pf,
            drawdown
        ) = test(candles, ratio)

        print(
            f"R:R 1:{ratio:<3} | "
            f"Final ${balance:8.2f} | "
            f"Profit ${profit:8.2f} | "
            f"Trades {trades:3d} | "
            f"Win {win_rate:5.1f}% | "
            f"PF {pf:.2f} | "
            f"DD ${drawdown:7.2f}"
        )

    print("============================")
