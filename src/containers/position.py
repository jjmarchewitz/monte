# DEFINITION: This is a container for an individual asset, like ETH or IVV. An instance
# is meant to be stored inside of a portfolio, so the asset has a quantity currently held
# associated with it.


class Position():
    def __init__(self, market_data_api, symbol, initial_quantity):
        self.market_data_api = market_data_api
        self.symbol = symbol
        self.quantity = initial_quantity
        self.price = 0

        self.price_generator = None
        self.time_when_price_last_updated = None
        self.needs_new_price_generator = False

    def total_value(self):
        return self.quantity * self.price

    def _get_price_from_bar(self, bar):
        # TODO: Find a better way to approximate the average price during a bar
        price = (bar.h + bar.l) / 2
        self.time_when_price_last_updated = bar.t
        return price

    def increment_price_generator(self):
        try:
            current_bar = next(self.price_generator)
            self.price = self._get_price_from_bar(current_bar)
        except StopIteration:
            self.needs_new_price_generator = True

    def update_daily_price_generator(self, time_frame, start_time, end_time):
        self.price_generator = self.market_data_api.get_bars_iter(
            self.symbol, time_frame, start_time, end_time)
        self.needs_new_price_generator = False
