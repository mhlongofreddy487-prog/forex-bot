import csv
import random
import statistics


STARTING_BALANCE = 10000.0
RISK_PERCENT = 1.0

SIMULATIONS = 10000
TRADES_PER_SIMULATION = 148

TRADE_LOG = "data/trade_log.csv"


def load_r_multiples():
    """
    Recover each historical trade's R-multiple.

    The backtest risks 1% of the balance before each trade.
    Therefore:

        R = profit / risk_amount

    The trade log contains the balance AFTER each trade.
    We can reconstruct the balance BEFORE each trade.
    """

    r_multiples = []

    previous_balance = STARTING_BALANCE

    with open(TRADE_LOG, "r", newline="") as file:

        reader = csv.DictReader(file)

        for row in reader:

            profit = float(row["profit"])
            balance_after = float(row["balance"])

            risk_amount = previous_balance * (
                RISK_PERCENT / 100
            )

            if risk_amount > 0:
                r_multiple = profit / risk_amount
                r_multiples.append(r_multiple)

            previous_balance = balance_after

    return r_multiples


def simulate(r_multiples):

    balance = STARTING_BALANCE
    peak = STARTING_BALANCE

    max_drawdown = 0.0
    max_drawdown_percent = 0.0

    wins = 0
    losses = 0

    # Bootstrap actual historical R results
    simulated_trades = random.choices(
        r_multiples,
        k=TRADES_PER_SIMULATION
    )

    for r_multiple in simulated_trades:

        risk_amount = balance * (
            RISK_PERCENT / 100
        )

        profit_loss = risk_amount * r_multiple

        balance += profit_loss

        if r_multiple > 0:
            wins += 1
        elif r_multiple < 0:
            losses += 1

        if balance > peak:
            peak = balance

        drawdown = peak - balance

        drawdown_percent = (
            drawdown / peak * 100
            if peak > 0
            else 0.0
        )

        max_drawdown = max(
            max_drawdown,
            drawdown
        )

        max_drawdown_percent = max(
            max_drawdown_percent,
            drawdown_percent
        )

    win_rate = (
        wins / (wins + losses) * 100
        if wins + losses > 0
        else 0.0
    )

    return (
        balance,
        max_drawdown,
        max_drawdown_percent,
        win_rate
    )


def percentile(values, p):

    index = int((len(values) - 1) * p)

    return values[index]


# ==========================================
# LOAD HISTORICAL RESULTS
# ==========================================

r_multiples = load_r_multiples()

if not r_multiples:
    raise RuntimeError(
        "No historical trades found."
    )


historical_wins = sum(
    1 for r in r_multiples
    if r > 0
)

historical_losses = sum(
    1 for r in r_multiples
    if r < 0
)


historical_average_r = statistics.mean(
    r_multiples
)


# ==========================================
# MONTE CARLO
# ==========================================

results = []

for _ in range(SIMULATIONS):

    results.append(
        simulate(r_multiples)
    )


balances = sorted(
    r[0] for r in results
)

drawdowns = sorted(
    r[1] for r in results
)

drawdown_percentages = sorted(
    r[2] for r in results
)

win_rates = sorted(
    r[3] for r in results
)


# ==========================================
# PROFITABILITY
# ==========================================

profitable = sum(
    1
    for balance in balances
    if balance > STARTING_BALANCE
)

losing = SIMULATIONS - profitable


# ==========================================
# DRAWDOWN THRESHOLDS
# ==========================================

dd10 = sum(
    1
    for dd in drawdown_percentages
    if dd >= 10
)

dd20 = sum(
    1
    for dd in drawdown_percentages
    if dd >= 20
)

dd30 = sum(
    1
    for dd in drawdown_percentages
    if dd >= 30
)

dd40 = sum(
    1
    for dd in drawdown_percentages
    if dd >= 40
)

dd50 = sum(
    1
    for dd in drawdown_percentages
    if dd >= 50
)


# ==========================================
# PRINT RESULTS
# ==========================================

print()

print("===== MONTE CARLO V4 VARIABLE-R TEST =====")

print(
    f"Starting balance:       "
    f"${STARTING_BALANCE:.2f}"
)

print(
    f"Historical trades:      "
    f"{len(r_multiples)}"
)

print(
    f"Historical wins:        "
    f"{historical_wins}"
)

print(
    f"Historical losses:      "
    f"{historical_losses}"
)

print(
    f"Average historical R:   "
    f"{historical_average_r:.4f}R"
)

print(
    f"Trades per simulation:  "
    f"{TRADES_PER_SIMULATION}"
)

print(
    f"Simulations:            "
    f"{SIMULATIONS}"
)

print()

print("FINAL BALANCE")

print(
    f"Average:                "
    f"${statistics.mean(balances):.2f}"
)

print(
    f"Minimum:                "
    f"${balances[0]:.2f}"
)

print(
    f"5th percentile:         "
    f"${percentile(balances, 0.05):.2f}"
)

print(
    f"Median:                 "
    f"${percentile(balances, 0.50):.2f}"
)

print(
    f"95th percentile:        "
    f"${percentile(balances, 0.95):.2f}"
)

print(
    f"Maximum:                "
    f"${balances[-1]:.2f}"
)

print()

print("WIN RATE")

print(
    f"Average:                "
    f"{statistics.mean(win_rates):.2f}%"
)

print(
    f"5th percentile:         "
    f"{percentile(win_rates, 0.05):.2f}%"
)

print(
    f"Median:                 "
    f"{percentile(win_rates, 0.50):.2f}%"
)

print(
    f"95th percentile:        "
    f"{percentile(win_rates, 0.95):.2f}%"
)

print()

print("MAXIMUM DRAWDOWN")

print(
    f"Average:                "
    f"${statistics.mean(drawdowns):.2f}"
)

print(
    f"Median:                 "
    f"${percentile(drawdowns, 0.50):.2f}"
)

print(
    f"95th percentile:        "
    f"${percentile(drawdowns, 0.95):.2f}"
)

print(
    f"Maximum:                "
    f"${drawdowns[-1]:.2f}"
)

print()

print("MAXIMUM DRAWDOWN %")

print(
    f"Average:                "
    f"{statistics.mean(drawdown_percentages):.2f}%"
)

print(
    f"Median:                 "
    f"{percentile(drawdown_percentages, 0.50):.2f}%"
)

print(
    f"95th percentile:        "
    f"{percentile(drawdown_percentages, 0.95):.2f}%"
)

print(
    f"Maximum:                "
    f"{drawdown_percentages[-1]:.2f}%"
)

print()

print("PROFITABILITY")

print(
    f"Profitable simulations: "
    f"{profitable}/{SIMULATIONS}"
)

print(
    f"Probability profitable: "
    f"{profitable / SIMULATIONS * 100:.2f}%"
)

print(
    f"Probability losing:     "
    f"{losing / SIMULATIONS * 100:.2f}%"
)

print()

print("DRAWDOWN RISK")

print(
    f"Probability DD >= 10%:  "
    f"{dd10 / SIMULATIONS * 100:.2f}%"
)

print(
    f"Probability DD >= 20%:  "
    f"{dd20 / SIMULATIONS * 100:.2f}%"
)

print(
    f"Probability DD >= 30%:  "
    f"{dd30 / SIMULATIONS * 100:.2f}%"
)

print(
    f"Probability DD >= 40%:  "
    f"{dd40 / SIMULATIONS * 100:.2f}%"
)

print(
    f"Probability DD >= 50%:  "
    f"{dd50 / SIMULATIONS * 100:.2f}%"
)

print("==========================================")
