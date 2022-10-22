
from __future__ import annotations

import pandas as pd

from monte.asset_manager import AssetManager
from monte.machine_settings import MachineSettings
from monte.util import AlpacaAPIBundle


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
    def df(self) -> pd.DataFrame:
        """DOC:"""
        return self.am[self.symbol]

    def price(self):
        """DOC:"""
        return self.am[self.symbol].iloc[-1].vwap

    def total_value(self):
        """DOC:"""
        return self.price() * self.quantity
