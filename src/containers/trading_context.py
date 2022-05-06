# DEFINITION: The "trading context" is meant to represent the timeline that a portfolio
# and trading algorithm are being run on. This encompasses backtesting (testing on
# historical data) as well as running an algorithm live.


from enum import Enum
from alpaca_trade_api import TimeFrame


class TradingContext():
    def __init__(
            self, trading_api, market_data_api, start_date, end_date,
            time_frame=TimeFrame.Minute):
        self.trading_api = trading_api
        self.market_data_api = market_data_api
        self.start_date = start_date
        self.end_date = end_date
        self.time_frame = time_frame

        # Pairs of algorithms and portfolios
        self.alg_port_pairs = {}
