# DEFINITION: The "trading context" is meant to represent the timeline that a portfolio
# and trading algorithm are being run on. This encompasses backtesting (testing on
# historical data) as well as running an algorithm live.


class TradingContext():
    def __init__(self, tradeapi):
        self.tradeapi = tradeapi
        self.portfolio = None
        self.trading_algorithm = None
