def calculate_trade(
    entry_price,
    signal,
    account_balance=10000.0,
    risk_percent=1.0,
    stop_distance=0.0010
):
    risk_amount = account_balance * (risk_percent / 100)

    if stop_distance <= 0:
        return None

    # Position size in units of the base currency.
    position_size = risk_amount / stop_distance

    if signal == "BUY":
        stop_loss = entry_price - stop_distance
        take_profit = entry_price + (stop_distance * 2)

    elif signal == "SELL":
        stop_loss = entry_price + stop_distance
        take_profit = entry_price - (stop_distance * 2)

    else:
        return None

    return {
        "signal": signal,
        "entry": round(entry_price, 5),
        "stop_loss": round(stop_loss, 5),
        "take_profit": round(take_profit, 5),
        "risk_amount": round(risk_amount, 2),
        "position_size": round(position_size, 2)
    }


if __name__ == "__main__":
    print("Risk Manager Test")

    balance = 10000.0

    for signal in ["BUY", "SELL"]:
        trade = calculate_trade(
            1.1000,
            signal,
            account_balance=balance,
            risk_percent=1.0
        )

        print(f"\n{signal} TRADE PLAN")
        print(f"Entry:         {trade['entry']}")
        print(f"Stop Loss:     {trade['stop_loss']}")
        print(f"Take Profit:   {trade['take_profit']}")
        print(f"Risk amount:   ${trade['risk_amount']:.2f}")
        print(f"Position size: {trade['position_size']:.2f}")
