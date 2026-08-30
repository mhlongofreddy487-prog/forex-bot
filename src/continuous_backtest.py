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
    peak_balance = STARTING_BALANCE
    max_drawdown = 0.0

    trades = 0
    wins = 0
    losses = 0

    buy_trades = 0
    sell_trades = 0

    buy_wins = 0
    sell_wins = 0

    total_profit = 0.0
    total_loss = 0.0

    max_consecutive_wins = 0
    max_consecutive_losses = 0

    consecutive_wins = 0
    consecutive_losses = 0

    trade = None
    pending_signal = None

    for i in range(50, len(candles)):

        candle = candles[i]

        # Enter using the signal generated
        # from the previous completed candle.
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

            trades += 1

            if signal == "BUY":
                buy_trades += 1
            else:
                sell_trades += 1

            pending_signal = None        # Manage the open trade
        if trade is not None:

            if trade["signal"] == "BUY":

                stop_hit = candle["low"] <= trade["stop_loss"]
                target_hit = candle["high"] >= trade["take_profit"]

                if stop_hit:

                    loss = trade["risk_amount"]
                    balance -= loss

                    total_loss += loss
                    losses += 1

                    consecutive_losses += 1
                    consecutive_wins = 0

                    max_consecutive_losses = max(
                        max_consecutive_losses,
                        consecutive_losses
                    )

                    trade = None

                elif target_hit:

                    profit = (
                        trade["risk_amount"]
                        * REWARD_MULTIPLIER
                    )

                    balance += profit

                    total_profit += profit
                    wins += 1
                    buy_wins += 1

                    consecutive_wins += 1
                    consecutive_losses = 0

                    max_consecutive_wins = max(
                        max_consecutive_wins,
                        consecutive_wins
                    )

                    trade = None

            else:

                stop_hit = candle["high"] >= trade["stop_loss"]
                target_hit = candle["low"] <= trade["take_profit"]

                if stop_hit:

                    loss = trade["risk_amount"]
                    balance -= loss

                    total_loss += loss
                    losses += 1

                    consecutive_losses += 1
                    consecutive_wins = 0

                    max_consecutive_losses = max(
                        max_consecutive_losses,
                        consecutive_losses
                    )

                    trade = None

                elif target_hit:

                    profit = (
                        trade["risk_amount"]
                        * REWARD_MULTIPLIER
                    )

                    balance += profit

                    total_profit += profit
                    wins += 1
                    sell_wins += 1

                    consecutive_wins += 1
                    consecutive_losses = 0

                    max_consecutive_wins = max(
                        max_consecutive_wins,
                        consecutive_wins
                    )

                    trade = None        # Track drawdown
        if balance > peak_balance:
            peak_balance = balance

        drawdown = peak_balance - balance

        if drawdown > max_drawdown:
            max_drawdown = drawdown

        # Generate the NEXT signal only after
        # the current candle has completed.
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

    buy_win_rate = (
        buy_wins / buy_trades * 100
        if buy_trades
        else 0.0
    )

    sell_win_rate = (
        sell_wins / sell_trades * 100
        if sell_trades
        else 0.0
    )

    print()
    print("===== FAIR CONTINUOUS BACKTEST =====")
    print(f"Starting balance:     ${STARTING_BALANCE:.2f}")
    print(f"Final balance:        ${balance:.2f}")
    print(f"Net profit:           ${balance - STARTING_BALANCE:.2f}")
    print(f"Total trades:         {trades}")
    print(f"Wins:                 {wins}")
    print(f"Losses:               {losses}")
    print(f"Win rate:             {win_rate:.1f}%")
    print(f"Profit factor:        {profit_factor:.2f}")
    print(f"Maximum drawdown:     ${max_drawdown:.2f}")
    print(f"Max consecutive wins: {max_consecutive_wins}")
    print(f"Max consecutive losses: {max_consecutive_losses}")
    print()
    print(f"BUY trades:           {buy_trades}")
    print(f"BUY wins:             {buy_wins}")
    print(f"BUY win rate:         {buy_win_rate:.1f}%")
    print()
    print(f"SELL trades:          {sell_trades}")
    print(f"SELL wins:            {sell_wins}")
    print(f"SELL win rate:        {sell_win_rate:.1f}%")
    print("====================================")


if __name__ == "__main__":

    candles = load_candles(CSV_FILE)

    print("===== EUR/USD FAIR CONTINUOUS TEST =====")
    print(f"Candles loaded: {len(candles)}")
    print(f"First candle:  {candles[0]['time']}")
    print(f"Last candle:   {candles[-1]['time']}")
    print("========================================")

    run_backtest(candles)
