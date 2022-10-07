"""DOC:"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta

import pandas as pd
from alpaca_trade_api import TimeFrameUnit
from dateutil.parser import isoparse
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
    date: date
    open_time: datetime
    close_time: datetime


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
        open_time = isoparse(open_time.isoformat())
        close_time = isoparse(close_time.isoformat())

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

    def __init__(self, alpaca_api, machine_settings, symbol) -> None:
        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings
        self.symbol = symbol

        # Columns that come from the Alpaca API
        # TODO: add datetime object column
        self.base_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trade_count', 'vwap']

        # Create empty dataframes
        self.reset_df()
        self.reset_buffer()

    def reset_df(self) -> None:
        """DOC:"""
        columns = self.base_columns.copy()
        columns.extend(self.machine_settings.derived_columns.keys())
        self.df = pd.DataFrame({}, columns=columns)

    def reset_buffer(self) -> None:
        """DOC:"""
        self.buffer = pd.DataFrame({}, columns=self.base_columns)

    def populate_buffer(self, df, buffer_start_date, buffer_end_date):
        """DOC:"""

        # TODO: Derived columns

        self.buffer = df

        trading_days_in_buffer_range = get_list_of_trading_days_in_range(
            self.alpaca_api, buffer_start_date, buffer_end_date)

        for index, row in self.buffer.iterrows():

            # The date of the current row
            row_datetime = isoparse(row.t)

            date_in_buffer_range = False

            for trading_day in trading_days_in_buffer_range:

                # Check that the date is a valid day where the market was open
                if row_datetime.date() == trading_day.date:
                    date_in_buffer_range = True

                    # If the TimeFrameUnit
                    if (self.machine_settings.time_frame.unit != TimeFrameUnit.Day and (
                            row_datetime < trading_day.open_time or row_datetime > trading_day.close_time)):
                        self.buffer.drop(index, inplace=True)

            if not date_in_buffer_range:
                self.buffer.drop(index, inplace=True)

        self.buffer.reset_index(drop=True, inplace=True)

        self.buffer.rename(columns={
            "t": self.base_columns[0],  # timestamp
            "o": self.base_columns[1],  # open
            "h": self.base_columns[2],  # high
            "l": self.base_columns[3],  # low
            "c": self.base_columns[4],  # close
            "v": self.base_columns[5],  # volume
            "n": self.base_columns[6],  # trade_count
            "vw": self.base_columns[7],  # vwap
        }, inplace=True)

    def increment_dataframe(self):
        """DOC:"""

        latest_row = self.buffer.head(1)

        self.df = pd.concat(objs=[self.df, latest_row], ignore_index=True)

        self.buffer.drop(self.buffer.head(1).index, inplace=True)

        if len(self.df.index) > self.machine_settings.max_rows_in_df:
            self.df.drop(self.df.head(1).index, inplace=True)


class AssetManager:
    """
    DOC:
    """

    alpaca_api: util.AlpacaAPIBundle
    machine_settings: machine.MachineSettings
    watched_assets: dict[str, Asset]
    trading_days: list[TradingDay]
    buffer_start_date: str
    buffer_end_date: str

    def __init__(self, alpaca_api, machine_settings) -> None:
        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings
        self.watched_assets = {}  # Dict of Assets
        self.trading_days = get_list_of_trading_days_in_range(
            self.alpaca_api, self.machine_settings.start_date, self.machine_settings.end_date)
        self._set_next_buffer_dates()

    def __setitem__(self, key: str, value) -> None:
        raise AttributeError(
            f"All keys of the AssetManager (such as \"{key}\") are read-only, and cannot be written to.")

    def __getitem__(self, key: str) -> pd.DataFrame:
        if not isinstance(key, str):
            raise KeyError("Only strings are accepted as keys for this object.")

        return self.watched_assets[key].df

    def items(self) -> dict[str, Asset]:
        """DOC:"""
        return self.watched_assets.items()

    def increment_dataframes(self):
        """DOC:"""

        # If any asset's data buffer is empty, populate all assets with new data
        if any(asset.buffer.empty for asset in self.watched_assets.values()):
            self._set_next_buffer_dates()
            symbols = self.watched_assets.keys()
            self._populate_buffers(
                symbols,
                self.most_recent_buffer_start_date,
                self.most_recent_buffer_end_date)

        # Then, add the next row of buffered data to the watched assets (update the asset DFs)
        for asset in self.watched_assets.values():
            asset.increment_dataframe()

        # If the buffer dataframes are on the next day, pop off the current TradingDay instance so it matches
        if self._trading_date_needs_to_be_incremented():
            self.trading_days.pop(0)

        # If any buffers are empty at this point, that means they just ran out of data on the last
        # asset.increment_dataframe() call. A new buffer's worth of data must be requested from Alpaca
        # and another trading day must be skipped so that the new data does not overlap with the current
        # data. Without this, they overlap by one day.
        if any(asset.buffer.empty for asset in self.watched_assets.values()):
            self.trading_days.pop(0)

        if len(self.trading_days) == 0:
            raise StopIteration("Reached the end of simulation. No more trading days to run.")

    def _set_next_buffer_dates(self):
        """DOC:"""

        # The start date of the current batch of data is the current/most recent trading day in ISO format
        self.most_recent_buffer_start_date = self.trading_days[0].date.isoformat()

        # The end date is the minimum between the current trading date plus the data buffer size, and
        # the last trading date. In other words, the buffer end date will be one "data buffer size" past
        # the start date unless that end date is past the end date of the whole simulation.
        if self.machine_settings.data_buffer_days > len(self.trading_days):
            self.most_recent_buffer_end_date = self.trading_days[-1]
        else:
            self.most_recent_buffer_end_date = self.trading_days[self.machine_settings.data_buffer_days]

        self.most_recent_buffer_end_date = self.most_recent_buffer_end_date.date.isoformat()

    def _populate_buffers(self, symbols, buffer_start_date: str, buffer_end_date: str):
        """DOC:"""

        # Get the bars for all assets from the calculated date range as a dictionary
        bars_for_all_assets = self.alpaca_api.async_market_data_bars.get_bulk_bars(
            symbols,
            self.machine_settings.time_frame,
            buffer_start_date,
            buffer_end_date)

        # Add the data to each Asset instance's "buffer" DataFrame
        for symbol in bars_for_all_assets.keys():
            # DataFrame containing unfiltered data (i.e. bars that are outside normal market hours) that
            # corresponds to the symbol at hand
            df = bars_for_all_assets[symbol]

            # Add the newly acquired data to the buffer
            self.watched_assets[symbol].populate_buffer(df, buffer_start_date, buffer_end_date)

    def add_start_buffer_data(self, symbol):
        """DOC:"""

        trading_days_before_current = get_list_of_trading_days_in_range(
            self.alpaca_api,
            (self.trading_days[0].date - timedelta(days=2 * self.machine_settings.start_buffer_days)).isoformat(),
            self.trading_days[0].date - timedelta(days=1))

        buffer_start_date = trading_days_before_current[-self.machine_settings.start_buffer_days].date.isoformat()
        buffer_end_date = trading_days_before_current[-1].date.isoformat()

        self._populate_buffers([symbol], buffer_start_date, buffer_end_date)

        while not self.watched_assets[symbol].buffer.empty:
            self.watched_assets[symbol].increment_dataframe()

    def _trading_date_needs_to_be_incremented(self) -> bool:
        """DOC:"""
        # Detect when the buffer dataframes have moved on past the current trading day (i.e. the TradingDay
        # instance at index 0 in self.trading_days).
        date_has_changed = False

        for asset in self.watched_assets.values():
            most_recent_row_timestamp = isoparse(asset.df.iloc[-1].timestamp)

            if len(self.trading_days) > 1:
                if most_recent_row_timestamp.date() != self.trading_days[0].date:
                    if most_recent_row_timestamp.date() == self.trading_days[1].date:
                        date_has_changed = True

        return date_has_changed

    def watch_asset(self, symbol: str) -> None:
        """DOC:"""
        if not self.is_watching_asset(symbol):
            self.watched_assets[symbol] = Asset(self.alpaca_api, self.machine_settings, symbol)
            self.add_start_buffer_data(symbol)

            self._populate_buffers(
                [symbol],
                self.trading_days[0].date.isoformat(),
                self.most_recent_buffer_end_date)

            while isoparse(
                    self.watched_assets[symbol].df.iloc[-1].timestamp).date() < self.trading_days[0].date:
                self.watched_assets[symbol].increment_dataframe()

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
