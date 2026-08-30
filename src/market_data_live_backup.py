import requests
import time

API_URL = "https://api.frankfurter.app/latest?from=USD&to=EUR"

last_price = 1.1000


def get_price():
    global last_price

    try:
        response = requests.get(API_URL, timeout=10)
        data = response.json()

        rate = data["rates"]["EUR"]

        # Convert EUR/USD from USD/EUR
        price = 1 / rate

        last_price = round(price, 5)

    except Exception:
        # Keep last known price if internet fails
        pass

    return last_price


if __name__ == "__main__":

    print("Live market data test started")

    for _ in range(5):
        price = get_price()
        print(f"EUR/USD price: {price}")
        time.sleep(5)
