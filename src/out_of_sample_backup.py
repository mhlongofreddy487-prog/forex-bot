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

TRAINING_PERCENT = 70


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


def run_validation(candles):

    split = int(len(candles) * TRAINING_PERCENT / 100)

    training = candles[:split]
    validation = candles[split:]

    print("===== OUT-OF-SAMPLE VALIDATION =====")
    print(f"Total candles:      {len(candles)}")
    print(f"Training candles:   {len(training)}")
    print(f"Validation candles: {len(validation)}")
    print()
    print("Training period:")
    print(training[0]["time"], "to", training[-1]["time"])
    print()
    print("Validation period:")
    print(validation[0]["time"], "to", validation[-1]["time"])
    print("====================================")

    balance = STARTING_BALANCE
    peak_balance = STARTING_BALANCE
    max_drawdown = 0.0

    wins = 0
    losses = 0
    trades = 0

    buy_trades = 0
    sell_trades = 0

    buy_wins = 0
    buy_losses = 0

    sell_wins = 0
    sell_losses = 0

    total_profit = 0.0
    total_loss = 0.0

    trade = None
    pending_signal = None

    closes = []

    for i, candle in enumerate(validation):

        closes.append(candle["close"])

        if len(closes) < 75:
            continue

        # Manage existing trade
        if trade is not None:

            if trade["signal"] == "BUY":

                if candle["low"] <= trade["stop_loss"]:
                    exit_price = trade["stop_loss"]
                    pnl = -trade["risk_amount"]

                    balance += pnl
                    losses += 1
                    buy_losses += 1
                    total_loss += abs(pnl)

                    trade = None

                elif candle["high"] >= trade["take_profit"]:
                    exit_price = trade["take_profit"]

                    pnl = trade["risk_amount"] * REWARD_MULTIPLIER

                    balance += pnl
                    wins += 1
                    buy_wins += 1
                    total_profit += pnl

                    trade = None

            else:

                if candle["high"] >= trade["stop_loss"]:
                    exit_price = trade["stop_loss"]
                    pnl = -trade["risk_amount"]

                    balance += pnl
                    losses += 1
                    sell_losses += 1
                    total_loss += abs(pnl)

                    trade = None

                elif candle["low"] <= trade["take_profit"]:
                    exit_price = trade["take_profit"]

                    pnl = trade["risk_amount"] * REWARD_MULTIPLIER

                    balance += pnl
                    wins += 1
                    sell_wins += 1
                    total_profit += pnl

                    trade = None

        # Enter new trade
        if trade is None:

            signal = generate_signal(closes)

            if signal in ("BUY", "SELL"):

                if signal == "BUY":
                    entry = candle["open"] + (SPREAD / 2) + SLIPPAGE
                    buy_trades += 1

                else:
                    entry = candle["open"] - (SPREAD / 2) - SLIPPAGE
                    sell_trades += 1

                trade = calculate_trade(
                    entry,
                    signal,
                    account_balance=balance,
                    risk_percent=RISK_PERCENT,
                    stop_distance=STOP_DISTANCE
                )

                trade["entry_time"] = candle["time"]

                trades += 1

        # Drawdown tracking
        if balance > peak_balance:
            peak_balance = balance

        drawdown = peak_balance - balance

        if drawdown > max_drawdown:
            max_drawdown = drawdown

    print()
    print("========== VALIDATION RESULTS ==========")
    print(f"Starting balance:     ${STARTING_BALANCE:.2f}")
    print(f"Final balance:        ${balance:.2f}")
    print(f"Net profit:           ${balance - STARTING_BALANCE:.2f}")
    print(f"Total trades:         {trades}")
    print(f"Wins:                 {wins}")
    print(f"Losses:               {losses}")

    if trades > 0:
        print(f"Win rate:             {(wins / trades) * 100:.1f}%")

    if total_loss > 0:
        print(f"Profit factor:        {total_profit / total_loss:.2f}")
    else:
        print("Profit factor:        N/A")

    print()
    print(f"BUY trades:           {buy_trades}")
    print(f"BUY wins:             {buy_wins}")
    print(f"BUY losses:           {buy_losses}")

    if buy_trades > 0:
        print(f"BUY win rate:         {(buy_wins / buy_trades) * 100:.1f}%")

    print()
    print(f"SELL trades:          {sell_trades}")
    print(f"SELL wins:            {sell_wins}")
    print(f"SELL losses:          {sell_losses}")

    if sell_trades > 0:
        print(f"SELL win rate:        {(sell_wins / sell_trades) * 100:.1f}%")

    print()
    print(f"Maximum drawdown:     ${max_drawdown:.2f}")
    print("========================================")


if __name__ == "__main__":

    candles = load_candles(CSV_FILE)

    run_validation(candles)
