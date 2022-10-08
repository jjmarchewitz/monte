
from __future__ import annotations

import pandas as pd

from monte import asset_manager, machine_settings, util


class Position():

    alpaca_api: util.AlpacaAPIBundle
    machine_settings: machine_settings.MachineSettings
    am: asset_manager.AssetManager
    symbol: str
    initial_quantity: int

    def __init__(self, alpaca_api: util.AlpacaAPIBundle, machine_settings: machine_settings.MachineSettings,
                 am: asset_manager.AssetManager, symbol: str, initial_quantity: int) -> None:
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
