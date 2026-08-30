import csv

from backtest import run_backtest


CSV_FILE = "data/EURUSD_H1.csv"


def load_prices(filename):
    prices = []

    with open(filename, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            prices.append(float(row["close"]))

    return prices


if __name__ == "__main__":
    prices = load_prices(CSV_FILE)

    print("===== EUR/USD H1 DATA =====")
    print(f"Candles loaded: {len(prices)}")

    if prices:
        print(f"First close:    {prices[0]:.5f}")
        print(f"Last close:     {prices[-1]:.5f}")

    print("============================")

    run_backtest(prices)
