class TradeManager:
    def __init__(self):
        self.trades = []
        self.wins = 0
        self.losses = 0

    def record_trade(self, signal, entry, stop_loss, take_profit):
        trade = {
            "signal": signal,
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "status": "OPEN"
        }

        self.trades.append(trade)
        return trade

    def update_trade(self, price):
        for trade in self.trades:
            if trade["status"] != "OPEN":
                continue

            if trade["signal"] == "BUY":
                if price >= trade["take_profit"]:
                    trade["status"] = "WIN"
                    self.wins += 1
                    print("\nTAKE PROFIT HIT - WIN")
                elif price <= trade["stop_loss"]:
                    trade["status"] = "LOSS"
                    self.losses += 1
                    print("\nSTOP LOSS HIT - LOSS")

            elif trade["signal"] == "SELL":
                if price <= trade["take_profit"]:
                    trade["status"] = "WIN"
                    self.wins += 1
                    print("\nTAKE PROFIT HIT - WIN")
                elif price >= trade["stop_loss"]:
                    trade["status"] = "LOSS"
                    self.losses += 1
                    print("\nSTOP LOSS HIT - LOSS")

    def has_open_trade(self):
        return any(
            trade["status"] == "OPEN"
            for trade in self.trades
        )

    def show_summary(self):
        closed_trades = self.wins + self.losses

        if closed_trades > 0:
            win_rate = (self.wins / closed_trades) * 100
        else:
            win_rate = 0.0

        print("\n--- TRADE SUMMARY ---")
        print(f"Total trades: {closed_trades}")
        print(f"Wins: {self.wins}")
        print(f"Losses: {self.losses}")
        print(f"Win rate: {win_rate:.1f}%")
        print(f"Open trades: {sum(1 for trade in self.trades if trade['status'] == 'OPEN')}")


if __name__ == "__main__":
    manager = TradeManager()

    manager.record_trade(
        "BUY",
        1.1000,
        1.0990,
        1.1020
    )

    print("Trade Manager initialized")
    manager.show_summary()
