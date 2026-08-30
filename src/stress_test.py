import csv

from strategy import generate_signal
from risk_manager import calculate_trade


CSV_FILE = "data/EURUSD_H1.csv"

STARTING_BALANCE = 10000.0
RISK_PERCENT = 1.0

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

def run_test(candles, spread, slippage):

    balance = STARTING_BALANCE
    peak_balance = STARTING_BALANCE
    max_drawdown = 0.0

    trades = 0
    wins = 0
    losses = 0

    total_profit = 0.0
    total_loss = 0.0

    trade = None
    pending_signal = None

    for i in range(50, len(candles)):

        candle = candles[i]

        # Enter using the previous completed candle's signal
        if trade is None and pending_signal in ("BUY", "SELL"):

            signal = pending_signal

            if signal == "BUY":
                entry = (
                    candle["open"]
                    + spread / 2
                    + slippage
                )
            else:
                entry = (
                    candle["open"]
                    - spread / 2
                    - slippage
                )

            trade = calculate_trade(
                entry,
                signal,
                account_balance=balance,
                risk_percent=RISK_PERCENT,
                stop_distance=STOP_DISTANCE
            )

            trades += 1
            pending_signal = None

        # Manage open trade
        if trade is not None:

            if trade["signal"] == "BUY":

                if candle["low"] <= trade["stop_loss"]:

                    loss = trade["risk_amount"]
                    balance -= loss
                    total_loss += loss
                    losses += 1
                    trade = None

                elif candle["high"] >= trade["take_profit"]:

                    profit = (
                        trade["risk_amount"]
                        * REWARD_MULTIPLIER
                    )

                    balance += profit
                    total_profit += profit
                    wins += 1
                    trade = None

            else:

                if candle["high"] >= trade["stop_loss"]:

                    loss = trade["risk_amount"]
                    balance -= loss
                    total_loss += loss
                    losses += 1
                    trade = None

                elif candle["low"] <= trade["take_profit"]:

                    profit = (
                        trade["risk_amount"]
                        * REWARD_MULTIPLIER
                    )

                    balance += profit
                    total_profit += profit
                    wins += 1
                    trade = None        # Track drawdown
        if balance > peak_balance:
            peak_balance = balance

        drawdown = peak_balance - balance

        if drawdown > max_drawdown:
            max_drawdown = drawdown

        # Generate signal from completed candle
        if trade is None and i + 1 < len(candles):

            closes = [
                c["close"]
                for c in candles[:i + 1]
            ]

            pending_signal = generate_signal(closes)

    win_rate = (
        wins / trades * 100
        if trades
        else 0.0
    )

    profit_factor = (
        total_profit / total_loss
        if total_loss > 0
        else 0.0
    )

    return {
        "balance": balance,
        "profit": balance - STARTING_BALANCE,
        "trades": trades,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "drawdown": max_drawdown
    }

def main():

    candles = load_candles(CSV_FILE)

    tests = [
        ("Normal", 0.00010, 0.00002),
        ("Higher spread", 0.00015, 0.00002),
        ("High spread + slippage", 0.00020, 0.00005),
        ("Very harsh", 0.00025, 0.00008)
    ]

    print("===== FOREX BOT STRESS TEST =====")
    print(f"Candles: {len(candles)}")
    print("=================================")

    for name, spread, slippage in tests:

        result = run_test(
            candles,
            spread,
            slippage
        )

        print()
        print(f"--- {name} ---")
        print(f"Spread:        {spread:.5f}")
        print(f"Slippage:      {slippage:.5f}")
        print(f"Final balance: ${result['balance']:.2f}")
        print(f"Profit:        ${result['profit']:.2f}")
        print(f"Trades:        {result['trades']}")
        print(f"Win rate:      {result['win_rate']:.1f}%")
        print(f"Profit factor: {result['profit_factor']:.2f}")
        print(f"Max drawdown:  ${result['drawdown']:.2f}")


if __name__ == "__main__":
    main()
