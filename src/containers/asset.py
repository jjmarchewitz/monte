# DEFINITION: This is a container for an individual asset, like ETH or IVV. An instance
# is meant to be stored inside of a portfolio, so the asset has a quantity currently held
# associated with it.

import alpaca_trade_api


class Asset():
    def __init__(self, name=None):
        self.name = name if name is not None else "Unnamed"
        self.quantity_held = 0
        self.current_price_per_unit = 0
        self.total_value_held = 0

    def buy(self, quantity=0):
        pass

    def sell(self, quantity=0):
        pass

    def sell_all(self):
        self.sell(self.quantity_held)

    def current_value(self):
        return self.quantity_held * self.current_price_per_unit
