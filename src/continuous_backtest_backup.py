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


def run_backtest(candles):

    balance = STARTING_BALANCE
    peak = balance
    max_dd = 0.0

    trades = 0
    wins = 0
    losses = 0

    buy_trades = 0
    sell_trades = 0
    buy_wins = 0
    sell_wins = 0

    profit_total = 0.0
    loss_total = 0.0

    win_streak = 0
    loss_streak = 0
    max_win_streak = 0
    max_loss_streak = 0

    trade = None

    for i in range(75, len(candles)):

        candle = candles[i]

        closes = [c["close"] for c in candles[:i]]

        if trade is not None:

            if trade["signal"] == "BUY":

                if candle["low"] <= trade["stop_loss"]:

                    pnl = -trade["risk_amount"]
                    balance += pnl
                    losses += 1
                    loss_total += abs(pnl)

                    loss_streak += 1
                    win_streak = 0
                    max_loss_streak = max(
                        max_loss_streak,
                        loss_streak
                    )

                    trade = None

                elif candle["high"] >= trade["take_profit"]:

                    pnl = trade["risk_amount"] * REWARD_MULTIPLIER
                    balance += pnl
                    wins += 1
                    buy_wins += 1
                    profit_total += pnl

                    win_streak += 1
                    loss_streak = 0
                    max_win_streak = max(
                        max_win_streak,
                        win_streak
                    )

                    trade = None

            else:

                if candle["high"] >= trade["stop_loss"]:

                    pnl = -trade["risk_amount"]
                    balance += pnl
                    losses += 1
                    loss_total += abs(pnl)

                    loss_streak += 1
                    win_streak = 0
                    max_loss_streak = max(
                        max_loss_streak,
                        loss_streak
                    )

                    trade = None

                elif candle["low"] <= trade["take_profit"]:

                    pnl = trade["risk_amount"] * REWARD_MULTIPLIER
                    balance += pnl
                    wins += 1
                    sell_wins += 1
                    profit_total += pnl

                    win_streak += 1
                    loss_streak = 0

                    max_win_streak = max(
                        max_win_streak,
                        win_streak
                    )

                    trade = None

        if trade is None:

            signal = generate_signal(closes)

            if signal in ("BUY", "SELL"):

                if signal == "BUY":
                    entry = candle["open"] + SPREAD / 2 + SLIPPAGE
                    buy_trades += 1
                else:
                    entry = candle["open"] - SPREAD / 2 - SLIPPAGE
                    sell_trades += 1

                trade = calculate_trade(
                    entry,
                    signal,
                    account_balance=balance,
                    risk_percent=RISK_PERCENT,
                    stop_distance=STOP_DISTANCE
                )

                trades += 1

        if balance > peak:
            peak = balance

        dd = peak - balance

        if dd > max_dd:
            max_dd = dd
    win_rate = (wins / trades * 100) if trades else 0
    pf = profit_total / loss_total if loss_total > 0 else 0

    print()
    print("===== CONTINUOUS EQUITY BACKTEST =====")
    print(f"Starting balance: ${STARTING_BALANCE:.2f}")
    print(f"Final balance: ${balance:.2f}")
    print(f"Net profit: ${balance - STARTING_BALANCE:.2f}")
    print(f"Total trades: {trades}")
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    print(f"Win rate: {win_rate:.1f}%")
    print(f"Profit factor: {pf:.2f}")
    print(f"Maximum drawdown: ${max_dd:.2f}")
    print(f"Max consecutive wins: {max_win_streak}")
    print(f"Max consecutive losses: {max_loss_streak}")
    print()
    print(f"BUY trades: {buy_trades}")
    print(f"BUY wins: {buy_wins}")
    print(f"SELL trades: {sell_trades}")
    print(f"SELL wins: {sell_wins}")
    print("=======================================")


if __name__ == "__main__":

    candles = load_candles(CSV_FILE)

    print("===== EUR/USD CONTINUOUS TEST =====")
    print(f"Candles loaded: {len(candles)}")
    print(f"First candle: {candles[0]['time']}")
    print(f"Last candle: {candles[-1]['time']}")
    print("====================================")

    run_backtest(candles)
