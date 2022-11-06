from __future__ import annotations

import pandas as pd

from monte.api import AlpacaAPIBundle
from monte.asset_manager import AssetManager
from monte.machine_settings import MachineSettings

# TODO: Calculate returns for positions
# TODO: Calculate cost-basis for positions
# TODO: Orderbook/history of orders


class Position():
    """
    A Position represents an Asset that is held in a Portfolio. It is an Asset that has a concrete quantity
    associated with it. This class also acts as a shorthand interface with the AssetManager, as it can return
    the training_df and testing_df associated with the Asset an instance of Position is pointing to.
    """

    alpaca_api: AlpacaAPIBundle
    machine_settings: MachineSettings
    am: AssetManager
    symbol: str
    initial_quantity: float

    def __init__(self, alpaca_api: AlpacaAPIBundle, machine_settings: MachineSettings,
                 am: AssetManager, symbol: str, initial_quantity: float) -> None:
        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings
        self.am = am
        self.symbol = symbol
        self.quantity = initial_quantity

    @property
    def training_df(self) -> pd.DataFrame:
        """
        Returns the training dataframe for the Asset this Position represents.
        """
        return self.am.get_training_df(self.symbol)

    @property
    def testing_df(self) -> pd.DataFrame:
        """
        Returns the testing dataframe for the Asset this Position represents.
        """
        return self.am.get_testing_df(self.symbol)

    @property
    def price(self) -> float:
        """
        Returns the most recent volume-weighted average price (vwap) of the underlying Asset.
        """
        return self.am.get_testing_df(self.symbol).iloc[-1].vwap

    @property
    def total_value(self) -> float:
        """
        Returns the total value of this Position (i.e. current price * quantity held).
        """
        return self.price * self.quantity
