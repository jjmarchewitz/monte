"""
A Position is simply the name for an asset that a buyer actually has possession of. While
Apple's stock exists in the world as an asset, it only becomes a person's position if they
own Apple stock. A Position object as defined here has a symbol, quantity, and price
associated with it.
"""

from algo_pg.data_manager import DataManager
from algo_pg.util import get_list_of_trading_days_in_range, get_price_from_bar


class Position():
    """
    This is a container for an individual position, like ETH or IVV. An instance is meant\
    to be stored inside of a portfolio, so the position has a quantity currently held and\
    a current price associated with it.
    """

    def __init__(self, alpaca_api, data_settings, symbol, initial_quantity):
        """
        Constructor for the Position class.

        Args:
            alpaca_api: A bundle of Alpaca APIs all created and authenticated with the keys
                in the repo's alpaca.config.
            TODO: data_settings
            symbol: A string for the market symbol of this position (i.e. "AAPL" or "GOOG").
            initial_quantity: The quantity of this asset that should be held when this
                instance is finished being constructed.
        """
        # Bundled alpaca API dataclass
        self.alpaca_api = alpaca_api

        # Trading Machine settings dataclass
        self.data_settings = data_settings

        # TODO: Check that input symbol is valid and corresponds to an actual asset.
        self.symbol = symbol
        self.quantity = initial_quantity
        self.price = 0
        self.asset = self.alpaca_api.trading.get_asset(self.symbol)
        self.data_manager = DataManager(
            self.alpaca_api, self.data_settings, self.symbol)

        # TODO: self.time_when_price_last_updated = None

    def update_price_from_current_bar(self):
        """TODO:"""
        self.price = get_price_from_bar(self.data_manager.current_bar)

    def get_asset_class(self):
        """
        Gets the Asset Class for any symbol.
        Asset Class is a string identifying what class an asset belongs to
        (i.e. "us equity")

        Returns: 
            An asset class string
        """
        return getattr(self.asset, "class")

    def total_value(self):
        """
        Gets the total value of this position with the current market price.

        Returns:
            The total value of this position with the current market price.
        """
        return self.quantity * self.price

    def _catch_up_to_reference_position(self, reference_position, increments):
        """TODO:"""

        target_timestamp = reference_position.data_manager.get_last_row().timestamp

        # Get a list of all valid trading days the market was open for in the date range
        # provided with open and close times as attributes.
        trading_days = get_list_of_trading_days_in_range(
            self.alpaca_api, self.data_settings.start_date, self.data_settings.end_date)

        for day in trading_days:

            self.data_manager.create_new_daily_row_generator(
                day.open_time_iso, day.close_time_iso)

            while True:
                try:
                    next(self.data_manager._row_generator)
                except StopIteration:
                    break

                current_timestamp = self.data_manager.get_last_row().timestamp
                if current_timestamp == target_timestamp:
                    break

            if current_timestamp == target_timestamp:
                break

        # TODO: Use the increments arg to only generate the number of rows needed, not from the
        # start of the whole machine
