# DEFINITION: A portfolio is simply a collection of individual assets


class Portfolio():
    def __init__(self, tradeapi):
        self.tradeapi = tradeapi
        self.positions = []

    def __get_positions_from_alpaca(self):
        self.positions = self.tradeapi.list_positions()

    def total_value(self):
        total = 0

        for asset in self.assets:
            total += asset.current_value()

        return total
