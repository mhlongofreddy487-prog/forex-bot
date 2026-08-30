import random

from strategy import generate_signal
from risk_manager import calculate_trade

STARTING_BALANCE = 10000.0
RISK_PERCENT = 1.0
MAX_DRAWDOWN_PERCENT = 10.0


def run_backtest(prices):
    balance = STARTING_BALANCE
    peak_balance = STARTING_BALANCE

    wins = 0
    losses = 0
    trades = 0
    buy_trades = 0
    sell_trades = 0

    total_profit = 0.0
    total_loss = 0.0

    trade = None
    max_drawdown = 0.0
    risk_stop_triggered = False

    for i, price in enumerate(prices):

        if trade is not None:

            if trade["signal"] == "BUY":
                if price >= trade["take_profit"]:
                    risk_amount = trade["risk_amount"]
                    balance += risk_amount * 2
                    total_profit += risk_amount * 2
                    wins += 1
                    trade = None

                elif price <= trade["stop_loss"]:
                    risk_amount = trade["risk_amount"]
                    balance -= risk_amount
                    total_loss += risk_amount
                    losses += 1
                    trade = None

            elif trade["signal"] == "SELL":
                if price <= trade["take_profit"]:
                    risk_amount = trade["risk_amount"]
                    balance += risk_amount * 2
                    total_profit += risk_amount * 2
                    wins += 1
                    trade = None

                elif price >= trade["stop_loss"]:
                    risk_amount = trade["risk_amount"]
                    balance -= risk_amount
                    total_loss += risk_amount
                    losses += 1
                    trade = None

        if balance > peak_balance:
            peak_balance = balance

        drawdown = peak_balance - balance

        if drawdown > max_drawdown:
            max_drawdown = drawdown

        drawdown_percent = (drawdown / peak_balance) * 100

        if drawdown_percent >= MAX_DRAWDOWN_PERCENT:
            risk_stop_triggered = True
            break

        if trade is None and i >= 9:
            signal = generate_signal(prices[:i + 1])

            if signal in ("BUY", "SELL"):
                trade = calculate_trade(
                    price,
                    signal,
                    risk_percent=RISK_PERCENT
                )

                trades += 1

                if signal == "BUY":
                    buy_trades += 1
                else:
                    sell_trades += 1

    closed_trades = wins + losses

    win_rate = (
        wins / closed_trades * 100
        if closed_trades > 0
        else 0
    )

    profit_factor = (
        total_profit / total_loss
        if total_loss > 0
        else 0
    )

    print("\n========== 1% RISK BACKTEST ==========")
    print(f"Starting balance:     ${STARTING_BALANCE:.2f}")
    print(f"Final balance:        ${balance:.2f}")
    print(f"Net profit:           ${balance - STARTING_BALANCE:.2f}")
    print(f"Total trades:         {trades}")
    print(f"Closed trades:        {closed_trades}")
    print(f"Wins:                 {wins}")
    print(f"Losses:               {losses}")
    print(f"Win rate:             {win_rate:.1f}%")
    print(f"Profit factor:        {profit_factor:.2f}")
    print(f"BUY trades:           {buy_trades}")
    print(f"SELL trades:          {sell_trades}")
    print(f"Maximum drawdown:     ${max_drawdown:.2f}")
    print(f"Risk stop triggered:  {'YES' if risk_stop_triggered else 'NO'}")
    print(f"Open trade:           {'YES' if trade else 'NO'}")
    print("=======================================")


if __name__ == "__main__":

    random.seed(42)

    prices = []
    price = 1.1000

    for i in range(2000):

        if i < 500:
            drift = 0.00008
        elif i < 1000:
            drift = -0.00008
        elif i < 1500:
            drift = 0.0
        else:
            drift = 0.00004

        noise = random.uniform(-0.00035, 0.00035)

        price += drift + noise
        price = max(1.0500, min(1.1500, price))

        prices.append(round(price, 5))

    run_backtest(prices)
