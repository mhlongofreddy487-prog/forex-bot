class PerformanceReport:
    def __init__(self, starting_balance=10000.0):
        self.starting_balance = starting_balance
        self.balance = starting_balance
        self.trades = []

    def add_trade(self, profit):
        self.trades.append(profit)
        self.balance += profit

    def show_report(self):
        total_trades = len(self.trades)
        wins = [p for p in self.trades if p > 0]
        losses = [p for p in self.trades if p < 0]

        if total_trades > 0:
            win_rate = len(wins) / total_trades * 100
        else:
            win_rate = 0

        total_profit = sum(wins)
        total_loss = abs(sum(losses))

        if total_loss > 0:
            profit_factor = total_profit / total_loss
        else:
            profit_factor = 0

        print("\n--- PERFORMANCE REPORT ---")
        print(f"Starting balance: ${self.starting_balance:.2f}")
        print(f"Final balance: ${self.balance:.2f}")
        print(f"Total trades: {total_trades}")
        print(f"Wins: {len(wins)}")
        print(f"Losses: {len(losses)}")
        print(f"Win rate: {win_rate:.2f}%")
        print(f"Profit factor: {profit_factor:.2f}")


if __name__ == "__main__":
    report = PerformanceReport()

    report.add_trade(200)
    report.add_trade(-100)
    report.add_trade(200)
    report.add_trade(-100)

    report.show_report()
