"""DOC:"""

from monte import machine, util
from typing import Dict, List
import pandas as pd


class Asset:
    """
    DOC:
    """

    alpaca_api: util.AlpacaAPIBundle
    machine_settings: machine.MachineSettings
    df: pd.DataFrame
    buffer: pd.DataFrame

    def __init__(self, alpaca_api, machine_settings) -> None:
        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings

    def create_new_df(self):
        pass

    def create_new_buffer(self):
        pass


class AssetManager:
    """
    DOC:
    """

    alpaca_api: util.AlpacaAPIBundle
    machine_settings: machine.MachineSettings
    watched_assets: Dict[str, Asset]
    trading_days: List[util.TradingDay]

    def __init__(self, alpaca_api, machine_settings) -> None:
        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings
        self.watched_assets = {}  # Dict of Assets
        self.trading_days = util.get_list_of_trading_days_in_range(
            self.alpaca_api, self.machine_settings.start_date, self.machine_settings.end_date)

    def __setitem__(self, key: str, value):
        raise AttributeError(
            f"All keys of the AssetManager (such as \"{key}\") are read-only, and cannot be written to.")

    def __getitem__(self, key: str) -> pd.DataFrame:
        if not isinstance(key, str):
            raise IndexError("Only strings are accepted as keys for this object.")

        return self.watched_assets[key].df

    def increment_dataframes(self):
        """DOC:"""

        # If any asset's data buffer is empty, populate all assets with new data (replace old, use threads)
        # Then, add the next row of buffered data to the watched assets (update the asset DFs)
        pass

    def watch_asset(self, symbol: str) -> None:
        """DOC:"""
        if not self.is_watching_asset(symbol):
            # TODO: Populate this watched asset with a df?
            self.watched_assets[symbol] = None

    def is_watching_asset(self, symbol: str) -> bool:
        """DOC:"""
        return symbol in self.watch_assets.keys()

    def unwatch_asset(self, symbol: str) -> bool:
        """DOC:"""
        if self.is_watching_asset(symbol):
            self.watched_assets.pop(symbol)
            return True
        else:
            return False
