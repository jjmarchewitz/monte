# DEFINITION: This is a container for an individual asset, like ETH or IVV. An instance
# is meant to be stored inside of a portfolio, so the asset has a quantity currently held
# associated with it.

from alpaca_trade_api import TimeFrame
from datetime import timedelta
from dateutil.parser import isoparse
from pyrsistent import inc


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
            # Grab the next bar from the generator and generate a price from it
            current_bar = next(self.price_generator)
            self.price = self._get_price_from_bar(current_bar)

        # When a generator tries to generate past the end of its intended range it will
        # throw this error, and I use it to indicate that a new price generator for a
        # new day needs to be generated.
        except StopIteration:
            self.needs_new_price_generator = True

    def create_new_daily_price_generator(self, time_frame, start_time, end_time):

        if time_frame == TimeFrame.Day:
            # If the time frame is a day, then creating a generator with the same start date
            # as its own end date will create an empty generator. What this all does is
            # it shifts the start of the generator back by one day so that when next() is
            # called on the generator, it will return the intended day's price.

            # Shift the start date back by one day
            start_time_dt_obj = isoparse(start_time)
            incremented_start_time = start_time_dt_obj - timedelta(days=1)
            iso_inc_start_time = incremented_start_time.isoformat()

            # Create the new generator
            self.price_generator = self.market_data_api.get_bars_iter(
                self.symbol, time_frame, iso_inc_start_time, end_time)

        else:
            # Create a generator object that will return prices for the day
            self.price_generator = self.market_data_api.get_bars_iter(
                self.symbol, time_frame, start_time, end_time)

        self.needs_new_price_generator = False
