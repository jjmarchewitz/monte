# DEFINITION: A portfolio is simply a collection of individual assets, and/or a collection
# of sub-portfolios


class Portfolio():
    def __init__(self):
        self.child_portfolios = []
        self.assets = []

    def total_value(self):
        total = 0

        for child_portfolio in self.child_portfolios:
            total += child_portfolio.total_value()

        for asset in self.assets:
            total += asset.current_value()

        return total
