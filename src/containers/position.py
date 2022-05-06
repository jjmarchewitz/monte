# DEFINITION: This is a container for an individual asset, like ETH or IVV. An instance
# is meant to be stored inside of a portfolio, so the asset has a quantity currently held
# associated with it.

import alpaca_trade_api
from containers.trading_context import TradingContext


class Position():
    def __init__(self, market_data_api, symbol):
        self.market_data_api = market_data_api
        self.symbol = symbol
        self.quantity = 0
        self.price = 0

    def total_value(self):
        return self.quantity * self.current_price
