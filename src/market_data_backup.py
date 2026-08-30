import random
import time

def get_price():
    price = 1.1000 + random.uniform(-0.0020, 0.0020)
    return round(price, 5)

if __name__ == "__main__":
    print("Market data simulator started")

    for _ in range(5):
        price = get_price()
        print(f"Simulated EUR/USD price: {price}")
        time.sleep(2)
