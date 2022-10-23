
from __future__ import annotations

import pandas as pd

from monte.api import AlpacaAPIBundle
from monte.asset_manager import AssetManager
from monte.machine_settings import MachineSettings


class Position():

    alpaca_api: AlpacaAPIBundle
    machine_settings: MachineSettings
    am: AssetManager
    symbol: str
    initial_quantity: float

    def __init__(self, alpaca_api: AlpacaAPIBundle, machine_settings: MachineSettings,
                 am: AssetManager, symbol: str, initial_quantity: float) -> None:
        """DOC:"""
        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings
        self.am = am
        self.symbol = symbol
        self.quantity = initial_quantity

    @property
    def testing_df(self) -> pd.DataFrame:
        """DOC:"""
        return self.am.get_testing_data(self.symbol)

    @property
    def training_df(self) -> pd.DataFrame:
        """DOC:"""
        return self.am.get_training_data(self.symbol)

    def price(self) -> float:
        """DOC:"""
        return self.am.get_testing_data(self.symbol).iloc[-1].vwap

    def total_value(self) -> float:
        """DOC:"""
        return self.price() * self.quantity
