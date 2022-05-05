# DEFINITION: The "execution context" is meant to represent the timeline that a portfolio
# and trading algorithm are being run on. This encompasses backtesting (testing on
# historical data) as well as running an algorithm live.


class ExecutionContext():
    def __init__(self):
        self.portfolio = None
        self.trading_algorithm = None
