import random


STARTING_BALANCE = 10000.0
RISK_PER_LOSS = 100.0
REWARD_PER_WIN = 200.0

SIMULATIONS = 1000
TRADES = 41


def run_simulation():

    balance = STARTING_BALANCE
    peak = STARTING_BALANCE
    max_drawdown = 0.0

    wins = 19
    losses = 22

    results = (
        [REWARD_PER_WIN] * wins
        + [-RISK_PER_LOSS] * losses
    )

    random.shuffle(results)

    for pnl in results:

        balance += pnl

        if balance > peak:
            peak = balance

        drawdown = peak - balance

        if drawdown > max_drawdown:
            max_drawdown = drawdown

    return balance, max_drawdown


def main():

    final_balances = []
    drawdowns = []

    profitable = 0

    worst_balance = float("inf")
    best_balance = 0.0
    worst_drawdown = 0.0

    for _ in range(SIMULATIONS):

        balance, drawdown = run_simulation()

        final_balances.append(balance)
        drawdowns.append(drawdown)

        if balance > STARTING_BALANCE:
            profitable += 1

        if balance < worst_balance:
            worst_balance = balance

        if balance > best_balance:
            best_balance = balance

        if drawdown > worst_drawdown:
            worst_drawdown = drawdown

    final_balances.sort()
    drawdowns.sort()

    median_balance = final_balances[len(final_balances) // 2]
    median_drawdown = drawdowns[len(drawdowns) // 2]

    worst_5_percent_index = int(SIMULATIONS * 0.05)

    worst_5_balance = final_balances[worst_5_percent_index]
    worst_5_drawdown = drawdowns[-worst_5_percent_index - 1]

    print("===== MONTE CARLO TRADE-ORDER TEST =====")
    print(f"Simulations:       {SIMULATIONS}")
    print(f"Trades per test:   {TRADES}")
    print()
    print("Original OOS result:")
    print(f"Starting balance:  ${STARTING_BALANCE:.2f}")
    print(f"Expected balance:  ${STARTING_BALANCE + (19 * 200) - (22 * 100):.2f}")
    print()
    print("Monte Carlo results:")
    print(f"Profitable tests:  {profitable}/{SIMULATIONS}")
    print(
        f"Profit probability: "
        f"{profitable / SIMULATIONS * 100:.1f}%"
    )
    print(f"Worst balance:     ${worst_balance:.2f}")
    print(f"Median balance:    ${median_balance:.2f}")
    print(f"Best balance:      ${best_balance:.2f}")
    print()
    print(f"Median drawdown:   ${median_drawdown:.2f}")
    print(f"Worst drawdown:    ${worst_drawdown:.2f}")
    print()
    print("Worst 5% balance:")
    print(f"${worst_5_balance:.2f}")
    print()
    print("Worst 5% drawdown:")
    print(f"${worst_5_drawdown:.2f}")
    print("========================================")


if __name__ == "__main__":
    main()
