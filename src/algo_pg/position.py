"""
A Position is simply the name for an asset that a buyer actually has possession of. While
Apple's stock exists in the world as an asset, it only becomes a person's position if they
own Apple stock. A Position object as defined here has a symbol, quantity, and price
associated with it.
"""

from algo_pg.data_manager import DataManager
from algo_pg.util import get_price_from_bar


class Position():
    """
    This is a container for an individual position, like ETH or IVV. An instance is meant\
    to be stored inside of a portfolio, so the position has a quantity currently held and\
    a current price associated with it.
    """

    def __init__(self, alpaca_api, symbol, initial_quantity):
        """
        Constructor for the Position class.

        Args:
            alpaca_api: A bundle of Alpaca APIs all created and authenticated with the keys
                in the repo's alpaca.config.
            symbol: A string for the market symbol of this position (i.e. "AAPL" or "GOOG").
            initial_quantity: The quantity of this asset that should be held when this
                instance is finished being constructed.
        """
        # Bundled alpaca API dataclass
        self.alpaca_api = alpaca_api
        # TODO: Check that input symbol is valid and corresponds to an actual asset.
        self.symbol = symbol
        self.quantity = initial_quantity
        self.price = 0
        self.asset = self.alpaca_api.trading.get_asset(self.symbol)
        self.data_manager = DataManager(self.alpaca_api, self.symbol)

        # TODO: self.time_when_price_last_updated = None

    def update_price_for_current_bar(self):
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
