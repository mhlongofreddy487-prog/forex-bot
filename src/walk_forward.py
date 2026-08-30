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


def test_period(candles, start, end):

    balance = STARTING_BALANCE
    peak_balance = STARTING_BALANCE
    max_drawdown = 0.0

    wins = 0
    losses = 0
    trades = 0

    total_profit = 0.0
    total_loss = 0.0

    trade = None
    closes = []

    period = candles[start:end]

    for candle in period:

        closes.append(candle["close"])

        if len(closes) < 75:
            continue

        # Manage existing trade
        if trade is not None:

            if trade["signal"] == "BUY":

                if candle["low"] <= trade["stop_loss"]:
                    pnl = -trade["risk_amount"]

                    balance += pnl
                    losses += 1
                    total_loss += abs(pnl)

                    trade = None

                elif candle["high"] >= trade["take_profit"]:
                    pnl = trade["risk_amount"] * REWARD_MULTIPLIER

                    balance += pnl
                    wins += 1
                    total_profit += pnl

                    trade = None

            else:

                if candle["high"] >= trade["stop_loss"]:
                    pnl = -trade["risk_amount"]

                    balance += pnl
                    losses += 1
                    total_loss += abs(pnl)

                    trade = None

                elif candle["low"] <= trade["take_profit"]:
                    pnl = trade["risk_amount"] * REWARD_MULTIPLIER

                    balance += pnl
                    wins += 1
                    total_profit += pnl

                    trade = None

        # Look for a new signal
        if trade is None:

            signal = generate_signal(closes)

            if signal in ("BUY", "SELL"):

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

        if balance > peak_balance:
            peak_balance = balance

        drawdown = peak_balance - balance

        if drawdown > max_drawdown:
            max_drawdown = drawdown

    profit = balance - STARTING_BALANCE

    if total_loss > 0:
        profit_factor = total_profit / total_loss
    else:
        profit_factor = 0.0

    if trades > 0:
        win_rate = (wins / trades) * 100
    else:
        win_rate = 0.0

    return balance, profit, trades, wins, losses, win_rate, profit_factor, max_drawdown


def run_walk_forward(candles):

    total = len(candles)

    # Four consecutive out-of-sample periods
    periods = [
        (0, int(total * 0.25)),
        (int(total * 0.25), int(total * 0.50)),
        (int(total * 0.50), int(total * 0.75)),
        (int(total * 0.75), total)
    ]

    print("===== WALK-FORWARD VALIDATION =====")
    print(f"Total candles: {total}")
    print("Testing 4 consecutive market periods")
    print("===================================")

    total_profit = 0.0

    for number, (start, end) in enumerate(periods, 1):

        result = test_period(candles, start, end)

        balance, profit, trades, wins, losses, win_rate, pf, dd = result

        print()
        print(f"========== PERIOD {number} ==========")
        print(
            f"{candles[start]['time']} "
            f"to "
            f"{candles[end - 1]['time']}"
        )
        print(f"Profit:          ${profit:.2f}")
        print(f"Trades:          {trades}")
        print(f"Wins:            {wins}")
        print(f"Losses:          {losses}")
        print(f"Win rate:        {win_rate:.1f}%")
        print(f"Profit factor:   {pf:.2f}")
        print(f"Max drawdown:    ${dd:.2f}")

        total_profit += profit

    print()
    print("========== SUMMARY ==========")
    print(f"Combined profit: ${total_profit:.2f}")
    print("=============================")


if __name__ == "__main__":

    candles = load_candles(CSV_FILE)

    run_walk_forward(candles)
