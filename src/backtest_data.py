import random
random.seed(42)

def generate_prices(start_price=1.1000, count=200):
    prices = [start_price]

    for _ in range(count - 1):
        change = random.uniform(-0.0010, 0.0010)
        new_price = prices[-1] + change

        if new_price <= 0:
            new_price = prices[-1]

        prices.append(round(new_price, 5))

    return prices


if __name__ == "__main__":
    prices = generate_prices()

    print(f"Generated {len(prices)} simulated prices")
    print("First 10 prices:")

    for price in prices[:10]:
        print(price)
