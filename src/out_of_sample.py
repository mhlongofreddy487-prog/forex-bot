import csv

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

def moving_average(prices, period):
    return sum(prices[-period:]) / period


def calculate_rsi(prices, period):
    if len(prices) < period + 1:
        return 50.0

    gains = []
    losses = []

    for i in range(len(prices) - period, len(prices)):
        change = prices[i] - prices[i - 1]

        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    average_gain = sum(gains) / period
    average_loss = sum(losses) / period

    if average_loss == 0:
        return 100.0

    if average_gain == 0:
        return 0.0

    rs = average_gain / average_loss

    return 100 - (100 / (1 + rs))


def generate_test_signal(prices):

    fast = 5
    slow = 30
    trend = 75
    rsi_period = 14

    strength = 0.0006

    buy_low = 54
    buy_high = 62

    sell_low = 40
    sell_high = 50

    minimum_history = max(
        trend,
        rsi_period + 1
    )

    if len(prices) < minimum_history:
        return "HOLD"

    fast_ma = moving_average(prices, fast)
    slow_ma = moving_average(prices, slow)
    trend_ma = moving_average(prices, trend)

    current = prices[-1]
    previous = prices[-2]

    rsi = calculate_rsi(prices, rsi_period)

    trend_strength = abs(fast_ma - trend_ma)

    if trend_strength < strength:
        return "HOLD"

    bullish = (
        fast_ma > slow_ma
        and slow_ma > trend_ma
    )

    bullish_recovery = (
        previous <= fast_ma
        and current > fast_ma
    )

    if (
        bullish
        and bullish_recovery
        and buy_low < rsi < buy_high
    ):
        return "BUY"

    bearish = (
        fast_ma < slow_ma
        and slow_ma < trend_ma
    )

    bearish_recovery = (
        previous >= fast_ma
        and current < fast_ma
    )

    if (
        bearish
        and bearish_recovery
        and sell_low < rsi < sell_high
    ):
        return "SELL"

    return "HOLD"

def run_validation(candles):

    split = int(len(candles) * TRAINING_PERCENT / 100)

    training = candles[:split]
    validation = candles[split:]

    print("===== CLEAN OUT-OF-SAMPLE VALIDATION =====")
    print(f"Total candles:      {len(candles)}")
    print(f"Training candles:   {len(training)}")
    print(f"Validation candles: {len(validation)}")
    print()
    print("Training period:")
    print(training[0]["time"], "to", training[-1]["time"])
    print()
    print("Validation period:")
    print(validation[0]["time"], "to", validation[-1]["time"])
    print("==========================================")

    balance = STARTING_BALANCE
    peak_balance = STARTING_BALANCE
    max_drawdown = 0.0

    wins = 0
    losses = 0
    trades = 0

    buy_trades = 0
    sell_trades = 0

    buy_wins = 0
    sell_wins = 0

    total_profit = 0.0
    total_loss = 0.0
    trade_results = []

    trade = None
    pending_signal = None

    # Use training data to establish indicator history.
    closes = [
        candle["close"]
        for candle in training
    ]

    # Start validation one candle at a time.
    for i, candle in enumerate(validation):

        # First manage an existing position.
        if trade is not None:

            if trade["signal"] == "BUY":

                stop_hit = candle["low"] <= trade["stop_loss"]
                target_hit = candle["high"] >= trade["take_profit"]

                if stop_hit:

                    loss = trade["risk_amount"]

                    balance -= loss
                    total_loss += loss
                    losses += 1
                    trade_results.append(-loss)
                    trade = None

                elif target_hit:

                    profit = (
                        trade["risk_amount"]
                        * REWARD_MULTIPLIER
                    )

                    balance += profit
                    total_profit += profit
                    wins += 1
                    trade_results.append(profit)
                    buy_wins += 1
                    trade = None

            else:

                stop_hit = candle["high"] >= trade["stop_loss"]
                target_hit = candle["low"] <= trade["take_profit"]

                if stop_hit:

                    loss = trade["risk_amount"]

                    balance -= loss
                    total_loss += loss
                    losses += 1
                    trade_results.append(-loss)
                    trade = None

                elif target_hit:

                    profit = (
                        trade["risk_amount"]
                        * REWARD_MULTIPLIER
                    )

                    balance += profit
                    total_profit += profit
                    wins += 1
                    trade_results.append(profit)
                    sell_wins += 1
                    trade = None

        # Enter at this candle's OPEN using
        # a signal generated by the previous candle.
        if trade is None and pending_signal in ("BUY", "SELL"):

            signal = pending_signal

            if signal == "BUY":

                entry = (
                    candle["open"]
                    + SPREAD / 2
                    + SLIPPAGE
                )

                buy_trades += 1

            else:

                entry = (
                    candle["open"]
                    - SPREAD / 2
                    - SLIPPAGE
                )

                sell_trades += 1

            trade = calculate_trade(
                entry,
                signal,
                account_balance=balance,
                risk_percent=RISK_PERCENT,
                stop_distance=STOP_DISTANCE
            )

            trades += 1
            pending_signal = None

        # Add the completed validation candle to our
        # indicator history AFTER using its open.
        closes.append(candle["close"])

        # Track equity drawdown.
        if balance > peak_balance:
            peak_balance = balance

        drawdown = peak_balance - balance

        if drawdown > max_drawdown:
            max_drawdown = drawdown

        # Generate a signal AFTER this candle closes.
        # That signal can only be used on the NEXT candle.
        if trade is None:

            pending_signal = generate_test_signal(closes)

    closed = wins + losses

    win_rate = (
        wins / closed * 100
        if closed
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

    with open("data/oos_trade_results.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["trade_number", "profit_loss"])

        for number, result in enumerate(trade_results, 1):
            writer.writerow([number, f"{result:.2f}"])

    print()
    print("========== CLEAN VALIDATION RESULTS ==========")
    print(f"Starting balance:     ${STARTING_BALANCE:.2f}")
    print(f"Final balance:        ${balance:.2f}")
    print(f"Net profit:           ${balance - STARTING_BALANCE:.2f}")
    print(f"Total trades:         {trades}")
    print(f"Wins:                 {wins}")
    print(f"Losses:               {losses}")
    print(f"Win rate:             {win_rate:.1f}%")
    print(f"Profit factor:        {profit_factor:.2f}")
    print()
    print(f"BUY trades:           {buy_trades}")
    print(f"BUY wins:             {buy_wins}")
    print(f"BUY win rate:         {buy_win_rate:.1f}%")
    print()
    print(f"SELL trades:          {sell_trades}")
    print(f"SELL wins:            {sell_wins}")
    print(f"SELL win rate:        {sell_win_rate:.1f}%")
    print()
    print(f"Maximum drawdown:     ${max_drawdown:.2f}")
    print("==============================================")


if __name__ == "__main__":

    candles = load_candles(CSV_FILE)

    run_validation(candles)
