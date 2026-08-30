import csv

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


def signal(
    prices,
    fast,
    slow,
    trend,
    rsi_period,
    strength,
    buy_low,
    buy_high,
    sell_low,
    sell_high
):

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


def test_strategy(
    candles,
    fast,
    slow,
    trend,
    rsi_period,
    strength,
    buy_low,
    buy_high,
    sell_low,
    sell_high
):

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

    for i in range(50, len(candles)):

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
                    total_loss += loss
                    losses += 1
                    trade = None

                elif target_hit:
                    profit = trade["risk_amount"] * REWARD_MULTIPLIER
                    balance += profit
                    total_profit += profit
                    wins += 1
                    trade = None

            else:

                stop_hit = candle["high"] >= trade["stop_loss"]
                target_hit = candle["low"] <= trade["take_profit"]

                if stop_hit:
                    loss = trade["risk_amount"]
                    balance -= loss
                    total_loss += loss
                    losses += 1
                    trade = None

                elif target_hit:
                    profit = trade["risk_amount"] * REWARD_MULTIPLIER
                    balance += profit
                    total_profit += profit
                    wins += 1
                    trade = None

        if balance > peak_balance:
            peak_balance = balance

        drawdown = peak_balance - balance

        if drawdown > max_drawdown:
            max_drawdown = drawdown

        closes = [c["close"] for c in candles[:i + 1]]

        if trade is None:
            pending_signal = signal(
                closes,
                fast,
                slow,
                trend,
                rsi_period,
                strength,
                buy_low,
                buy_high,
                sell_low,
                sell_high
            )

    closed = wins + losses

    win_rate = wins / closed * 100 if closed else 0.0

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


if __name__ == "__main__":

    candles = load_candles(CSV_FILE)

    fast_values = [5, 10, 15]
    slow_values = [20, 30, 40]
    trend_values = [50, 75, 100]
    rsi_values = [10, 14, 20]
    strength_values = [0.0006, 0.0008, 0.0010]

    buy_ranges = [
        (52, 60),
        (53, 60),
        (54, 62)
    ]

    sell_ranges = [
        (38, 48),
        (40, 50),
        (40, 52)
    ]

    results = []

    print("\n===== PARAMETER TEST =====")
    print(f"Candles: {len(candles)}")
    print("Testing strategy combinations...")
    print()

    for fast in fast_values:
        for slow in slow_values:
            for trend in trend_values:
                for rsi_period in rsi_values:
                    for strength in strength_values:
                        for buy_range in buy_ranges:
                            for sell_range in sell_ranges:

                                if fast >= slow or slow >= trend:
                                    continue

                                result = test_strategy(
                                    candles,
                                    fast,
                                    slow,
                                    trend,
                                    rsi_period,
                                    strength,
                                    buy_range[0],
                                    buy_range[1],
                                    sell_range[0],
                                    sell_range[1]
                                )

                                results.append((
                                    result["profit"],
                                    result["profit_factor"],
                                    result["win_rate"],
                                    result["drawdown"],
                                    result["trades"],
                                    fast,
                                    slow,
                                    trend,
                                    rsi_period,
                                    strength,
                                    buy_range,
                                    sell_range
                                ))

    results.sort(reverse=True)

    print("===== TOP 10 RESULTS =====")

    for result in results[:10]:

        (
            profit,
            pf,
            win_rate,
            drawdown,
            trades,
            fast,
            slow,
            trend,
            rsi_period,
            strength,
            buy_range,
            sell_range
        ) = result

        print(
            f"Profit ${profit:8.2f} | "
            f"PF {pf:.2f} | "
            f"Win {win_rate:5.1f}% | "
            f"DD ${drawdown:7.2f} | "
            f"Trades {trades:3d} | "
            f"MA {fast}/{slow}/{trend} | "
            f"RSI {rsi_period} | "
            f"Strength {strength:.4f} | "
            f"BUY {buy_range[0]}-{buy_range[1]} | "
            f"SELL {sell_range[0]}-{sell_range[1]}"
        )

    print("==========================")
