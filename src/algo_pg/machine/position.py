"""
A Position is simply the name for an asset that a buyer actually has possession of. While
Apple's stock exists in the world as an asset, it only becomes a person's position if they
own Apple stock. A Position object as defined here has a symbol, quantity, and price
associated with it.
"""

from alpaca_trade_api import TimeFrame
from datetime import timedelta
from dateutil.parser import isoparse


class Position():
    """
    This is a container for an individual position, like ETH or IVV. An instance is meant\
    to be stored inside of a portfolio, so the position has a quantity currently held and\
    a current price associated with it.
    """

    def __init__(self, trading_api, market_data_api, symbol, initial_quantity):
        """
        Constructor for the Position class.

        Args: # TODO: (ADD TRADING_API documentation)
            market_data_api: An instance of the alpaca_trade_api package's own REST API
                set up to retrieve historical market data.
            symbol: A string for the market symbol of this position (i.e. "AAPL" or "GOOG").
            initial_quantity: The quantity of this asset that should be held when this
                instance is finished being constructed.
        """
        # TODO: Check that input symbol is valid and corresponds to an actual asset
        self.market_data_api = market_data_api
        self.trading_api = trading_api
        self.symbol = symbol
        self.quantity = initial_quantity
        self.price = 0
        self.asset = self.trading_api.get_asset(self.symbol)

        self._bar_generator = None
        self.time_when_price_last_updated = None
        self.needs_new_bar_generator = False

    def get_asset_class(self):
        """
        Gets the Asset Class for any symbol
        Asset Class is a string identifying what class an asset belongs to
        (i.e. "us equity")

        Returns: An an asset class string
        """
        return self.asset.__getattr__("class")

    def total_value(self):
        """
        Gets the total value of this position with the current market price.

        Returns:
            The total value of this position with the current market price.
        """
        return self.quantity * self.price

    def _get_price_from_bar(self, bar):
        """
        Determines an equivalent price for an asset during a bar from info about the
        bar itself.

        Args:
            bar: One bar of stock information that takes up one TimeFrame's worth of time.

        Returns:
            An average price to represent the bar, determined from information about the
            bar.
        """
        # TODO: Find a better way to approximate the average price during a bar
        price = (bar.h + bar.l) / 2
        self.time_when_price_last_updated = bar.t
        return price

    def generate_next_price(self):
        """
        Increment the bar generator to the next iteration and set the price based on the
        new bar.
        """
        try:
            # Grab the next bar from the generator and generate a price from it
            current_bar = next(self._bar_generator)
            self.price = self._get_price_from_bar(current_bar)

        except StopIteration:
            # When a generator tries to generate past the end of its intended range it will
            # throw this error, and I use it to indicate that a new bar generator for a
            # new day needs to be generated.
            self.needs_new_bar_generator = True

    def create_new_daily_bar_generator(self, time_frame, start_time, end_time):
        """
        Create a new bar generator with a start time and end time that occur on the same
        day and correspond to the open and close times of the market for that day.

        Args:
            time_frame: The time delta between bars. Can be a minute, hour, or day.
            start_time: The ISO-8601 compliant date/time for the generator to start 
                generating bars.
            end_time: The ISO-8601 compliant date/time for the generator to stop 
                generating bars.
        """
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
            self._bar_generator = self.market_data_api.get_bars_iter(
                self.symbol, time_frame, iso_inc_start_time, end_time)

        else:
            # Create a generator object that will return prices for the day
            self._bar_generator = self.market_data_api.get_bars_iter(
                self.symbol, time_frame, start_time, end_time)

        self.needs_new_bar_generator = False