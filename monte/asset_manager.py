"""DOC:"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List

import pandas as pd
from pytz import timezone

from monte import machine, util

##################
# DATE UTILITIES #
##################


@dataclass
class TradingDay():
    """
    A dataclass holding information for a single day the market is open, like the date.
    This dataclass also stores the market open time and close time in the ISO-8601
    format.
    """
    date: str
    open_time_iso: str
    close_time_iso: str
    # df: Optional[pd.DataFrame]


def get_list_of_trading_days_in_range(alpaca_api, start_date, end_date):
    """
    DOC:
    """
    raw_market_days = get_raw_trading_dates_in_range(alpaca_api, start_date, end_date)
    return get_trading_day_obj_list_from_date_list(raw_market_days)


def get_raw_trading_dates_in_range(alpaca_api, start_date, end_date):
    """
    DOC:
    """
    return alpaca_api.trading.get_calendar(start_date, end_date)


def get_trading_day_obj_list_from_date_list(trading_date_list):
    """
    DOC:
    """
    trading_days = []

    for day in trading_date_list:

        # Create a date object (from the datetime library) for the calendar date of the
        # market day
        trading_date = date(
            day.date.year,
            day.date.month,
            day.date.day
        )

        # Grab the DST-aware timezone object for eastern time
        timezone_ET = timezone("America/New_York")

        # Create a datetime object for the opening time with the timezone info attached
        open_time = timezone_ET.localize(datetime(
            day.date.year,
            day.date.month,
            day.date.day,
            day.open.hour,
            day.open.minute
        ))

        # Create a datetime object for the closing time with the timezone info attached
        close_time = timezone_ET.localize(datetime(
            day.date.year,
            day.date.month,
            day.date.day,
            day.close.hour,
            day.close.minute
        ))

        # Convert the opening and closing times to ISO-8601
        # Literally dont even fucking ask me how long it took to get the data in the
        # right format for this to work.
        open_time = open_time.isoformat()
        close_time = close_time.isoformat()

        # Create a TradingDay object with the right open/close times and append it to
        # the list of all such TradingDay objects within the span between start_date and
        # end_date
        trading_day = TradingDay(trading_date, open_time, close_time)
        trading_days.append(trading_day)

    return trading_days


#################
# ASSET MANAGER #
#################

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

        # Create empty dataframes
        self.reset_df()
        self.buffer = []

    def reset_df(self):
        """DOC:"""
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trade_count', 'vwap']
        columns.extend(self.machine_settings.derived_columns.keys())
        self.df = pd.DataFrame({}, columns=columns)

    def reset_buffer(self):
        """DOC:"""
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trade_count', 'vwap']
        self.df = pd.DataFrame({}, columns=columns)

    def populate_buffer(self, df, start_date):
        pass


class AssetManager:
    """
    DOC:
    """

    alpaca_api: util.AlpacaAPIBundle
    machine_settings: machine.MachineSettings
    watched_assets: Dict[str, Asset]
    trading_days: List[TradingDay]

    def __init__(self, alpaca_api, machine_settings) -> None:
        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings
        self.watched_assets = {}  # Dict of Assets
        self.trading_days = get_list_of_trading_days_in_range(
            self.alpaca_api, self.machine_settings.start_date, self.machine_settings.end_date)

    def __setitem__(self, key: str, value) -> None:
        raise AttributeError(
            f"All keys of the AssetManager (such as \"{key}\") are read-only, and cannot be written to.")

    def __getitem__(self, key: str) -> pd.DataFrame:
        if not isinstance(key, str):
            raise KeyError("Only strings are accepted as keys for this object.")

        return self.watched_assets[key].df

    def increment_dataframes(self):
        """DOC:"""

        # If any asset's data buffer is empty, populate all assets with new data
        # TODO: add conditional

        symbols = self.watched_assets.keys()
        barz = self.alpaca_api.async_market_data_bars.get_bulk_bars(
            symbols,
            self.machine_settings.time_frame,
            self.machine_settings.start_date,
            self.machine_settings.end_date)

        breakpoint()

        # Then, add the next row of buffered data to the watched assets (update the asset DFs)
        pass

    def watch_asset(self, symbol: str) -> None:
        """DOC:"""
        if not self.is_watching_asset(symbol):
            self.watched_assets[symbol] = Asset(self.alpaca_api, self.machine_settings)

    def is_watching_asset(self, symbol: str) -> bool:
        """DOC:"""
        return symbol in self.watched_assets.keys()

    def unwatch_asset(self, symbol: str) -> bool:
        """DOC:"""
        if self.is_watching_asset(symbol):
            self.watched_assets.pop(symbol)
            return True
        else:
            return False
