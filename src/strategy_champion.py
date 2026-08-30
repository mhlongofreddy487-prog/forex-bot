def moving_average(prices, period):
    return sum(prices[-period:]) / period


def calculate_rsi(prices, period=14):
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


def generate_signal(prices):
    if len(prices) < 100:
        return "HOLD"

    ma20 = moving_average(prices, 20)
    ma50 = moving_average(prices, 50)
    ma100 = moving_average(prices, 100)

    current = prices[-1]
    previous = prices[-2]

    rsi = calculate_rsi(prices, 14)

    # Require a stronger trend
    trend_strength = abs(ma20 - ma100)

    if trend_strength < 0.0008:
        return "HOLD"

    # Bullish trend
    bullish = (
        ma20 > ma50
        and ma50 > ma100
    )

    # Bullish pullback
    bullish_recovery = (
        previous <= ma20
        and current > ma20
    )

    # Stronger BUY filter
    if bullish and bullish_recovery and 53 < rsi < 60:
        return "BUY"

    # Bearish trend
    bearish = (
        ma20 < ma50
        and ma50 < ma100
    )

    # Bearish pullback
    bearish_recovery = (
        previous >= ma20
        and current < ma20
    )

    # Stronger SELL filter
    if bearish and bearish_recovery and 40 < rsi < 50:
        return "SELL"

    return "HOLD"


def calculate_atr(candles, period=14):
    if len(candles) < period + 1:
        return 0.0

    true_ranges = []

    for i in range(len(candles) - period, len(candles)):
        high = candles[i]["high"]
        low = candles[i]["low"]
        previous_close = candles[i - 1]["close"]

        true_range = max(
            high - low,
            abs(high - previous_close),
            abs(low - previous_close)
        )

        true_ranges.append(true_range)

    return sum(true_ranges) / period
