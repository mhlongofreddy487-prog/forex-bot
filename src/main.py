import time

from market_data import get_price
from strategy import generate_signal
from risk_manager import calculate_trade
from trade_manager import TradeManager

print("Forex Bot is starting...")
print("Day-Trading System initialized")
print("SIMULATION MODE - No real trades")

prices = []
manager = TradeManager()

while True:
    price = get_price()
    prices.append(price)

    print(f"\nMarket price: {price}")

    # Check any existing trade
    manager.update_trade(price)

    # Only look for a new trade when there is no open trade
    if len(prices) >= 10 and not manager.has_open_trade():
        signal = generate_signal(prices)
        print(f"Signal: {signal}")

        if signal in ("BUY", "SELL"):
            trade = calculate_trade(price, signal)

            manager.record_trade(
                trade["signal"],
                trade["entry"],
                trade["stop_loss"],
                trade["take_profit"]
            )

            print("\nSIMULATED TRADE OPENED")
            print(f"Direction:   {trade['signal']}")
            print(f"Entry:       {trade['entry']}")
            print(f"Stop Loss:   {trade['stop_loss']}")
            print(f"Take Profit: {trade['take_profit']}")

    manager.show_summary()

    time.sleep(5)
