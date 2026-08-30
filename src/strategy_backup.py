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
    if len(prices) < 75:
        return "HOLD"

    ma5 = moving_average(prices, 5)
    ma30 = moving_average(prices, 30)
    ma75 = moving_average(prices, 75)

    current = prices[-1]
    previous = prices[-2]

    rsi = calculate_rsi(prices, 14)

    # Require a stronger trend
    trend_strength = abs(ma5 - ma75)

    if trend_strength < 0.0006:
        return "HOLD"

    # Bullish trend
    bullish = (
        ma5 > ma30
        and ma30 > ma75
    )

    # Bullish pullback
    bullish_recovery = (
        previous <= ma5
        and current > ma5
    )

    # BUY filter
    if bullish and bullish_recovery and 54 < rsi < 62:
        return "BUY"

    # Bearish trend
    bearish = (
        ma5 < ma30
        and ma30 < ma75
    )

    # Bearish pullback
    bearish_recovery = (
        previous >= ma5
        and current < ma5
    )

    # SELL filter
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
