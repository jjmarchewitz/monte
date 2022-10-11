from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

import pandas as pd
from alpaca_trade_api import TimeFrameUnit, entity
from dateutil.parser import isoparse
from pytz import timezone

from derived_columns.decorator import DFIdentifier
from monte.machine_settings import MachineSettings
from monte.util import AlpacaAPIBundle

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


def get_list_of_trading_days_in_range(alpaca_api: AlpacaAPIBundle,
                                      start_date: str, end_date: str) -> list[TradingDay]:
    """
    Returns a list of days (as TradingDay instances) that U.S. markets are open between the start and end
    dates provided. The result is inclusive of both the start and end dates.

    Args:
        alpaca_api:
            A valid, authenticated util.AlpacaAPIBundle instance.

        start_date:
            The beginning of the range of trading days. The date is represented as YYYY-MM-DD. This follows
            the ISO-8601 date standard.

        end_date:
            The end of the range of trading days. The date is represented as YYYY-MM-DD. This follows the
            ISO-8601 date standard.

    Returns:
        A list of TradingDay instances that represents all of the days that U.S. markets were open.
    """
    raw_market_days = _get_raw_trading_dates_in_range(alpaca_api, start_date, end_date)
    return _get_trading_day_obj_list_from_date_list(raw_market_days)


def _get_raw_trading_dates_in_range(alpaca_api: AlpacaAPIBundle,
                                    start_date: str, end_date: str) -> list[entity.Calendar]:
    """
    This should not be used by end-users.

    Returns a list of days (as alpaca_trade_api.Calendar instances) that U.S. markets are open between the
    start and end dates provided. The result is inclusive of both the start and end dates.

    Args:
        alpaca_api:
            A valid, authenticated util.AlpacaAPIBundle instance.

        start_date:
            The beginning of the range of trading days. The date is represented as YYYY-MM-DD. This follows
            the ISO-8601 date standard.

        end_date:
            The end of the range of trading days. The date is represented as YYYY-MM-DD. This follows the
            ISO-8601 date standard.

    Returns:
        A list of alpaca_trade_api.Calendar instances that represents all of the days that U.S. markets were
        open.
    """
    return alpaca_api.trading.get_calendar(start_date, end_date)


def _get_trading_day_obj_list_from_date_list(
        calendar_instance_list: list[entity.Calendar]) -> list[TradingDay]:
    """
    Converts a list of alpaca_trade_api.Calendar instances into a list of TradingDay instances.

    Args:
        calendar_instance_list:
            A list of alpaca_trade_api.Calendar instances that represents a range of days the market was
            open.

    Returns:
        A list of TradingDay instances that represents a range of days the market was open.
    """
    trading_days = []

    for day in calendar_instance_list:

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
    Represents one single asset from the markets, this object constructs and manages dataframes for the given
    symbol.
    """

    alpaca_api: AlpacaAPIBundle
    machine_settings: MachineSettings
    df: pd.DataFrame
    buffer: pd.DataFrame
    base_columns: list[str]
    _df_has_start_buffer_rows: bool

    def __init__(self, alpaca_api: AlpacaAPIBundle,
                 machine_settings: MachineSettings, symbol: str) -> None:
        """
        Constructor for Asset

        Args:
            alpaca_api:
                A bundle of Alpaca APIs all created and authenticated with the keys in the repo's
                alpaca_config.json

            machine_settings:
                An instance of machine.MachineSettings that contains configuration for the current simulation.

            symbol:
                A string containing the market symbol that this Asset represents.
        """
        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings
        self.symbol = symbol

        # Columns that come from the Alpaca API
        self.base_columns = [
            'timestamp',
            'open',
            'high',
            'low',
            'close',
            'volume',
            'trade_count',
            'vwap',
            'datetime']

        # Create empty dataframes
        self.reset_df()
        self.reset_buffer()

        self._df_has_start_buffer_rows = False

    def price(self):
        return self.df.iloc[-1].vwap

    def timestamp(self):
        return self.df.iloc[-1].timestamp

    def datetime(self):
        return self.df.iloc[-1].datetime

    def reset_df(self) -> None:
        """
        Creates a new, empty dataframe with all of the base columns and derived columns. The result is
        stored in self.df.
        """
        columns = self.base_columns.copy()
        columns.extend(self.machine_settings.derived_columns.keys())
        self.df = pd.DataFrame({}, columns=columns)

    def reset_buffer(self) -> None:
        """
        Creates a new, empty dataframe with only the base columns (NOT derived columns). The result is
        stored in self.buffer.
        """
        self.buffer = pd.DataFrame({}, columns=self.base_columns)

    def populate_buffer(self, df, buffer_start_date, buffer_end_date):
        """
        DOC:
        """

        # Store the incoming dataframe in the buffer
        self.buffer = df

        # Get a list of TradingDays between the first and last date of the buffer
        trading_days_in_buffer_range = get_list_of_trading_days_in_range(
            self.alpaca_api, buffer_start_date, buffer_end_date)

        for index, row in self.buffer.iterrows():

            # The date of the current row
            row_datetime = isoparse(row.t)

            # Flag variables
            date_in_buffer_range = False
            dropped = False

            for trading_day in trading_days_in_buffer_range:

                # Check that the date is a valid day where the market was open
                if row_datetime.date() == trading_day.date:
                    date_in_buffer_range = True

                    # The current row should be dropped if its timestamp is outside the market hours for this
                    # TradingDay, except if the TimeFrameUnit is a Day. The timestamp doesnt matter then.
                    if (self.machine_settings.time_frame.unit != TimeFrameUnit.Day and (
                            row_datetime < trading_day.open_time or row_datetime > trading_day.close_time)):
                        self.buffer.drop(index, inplace=True)

            # If the date of the row does not correspond to a valid TradingDay, drop it.
            if not date_in_buffer_range:
                self.buffer.drop(index, inplace=True)

        # Reset the index to 'forget' about the dropped rows
        self.buffer.reset_index(drop=True, inplace=True)

        # Rename columns to more human-friendly names
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

        # TODO: Standardize the timestamps and datetimes to be DST-aware (i.e. the market should always
        # open at 9:30, not 10:30 or 13:30 or 14:30)

        # Add datetimes as a column
        self.buffer[self.base_columns[8]] = self.buffer.apply(
            lambda row: isoparse(row.timestamp).astimezone(timezone('UTC')), axis=1)

    def increment_dataframe(self):
        """DOC:"""

        # Grab the latest row from the buffer
        latest_row = self.buffer.head(1)

        # Add the latest row to the bottom of the main df
        self.df = pd.concat(objs=[self.df, latest_row], ignore_index=True)

        # Drop the top row of the buffer (the row we just moved)
        self.buffer.drop(self.buffer.head(1).index, inplace=True)

        # Drop the oldest row in the main df if it exceeds the configured length limit
        # (machine_settings.max_rows_in_df)
        if len(self.df.index) > self.machine_settings.max_rows_in_df:
            self.df.drop(self.df.head(1).index, inplace=True)

        # If the main dataframe has at least "start_buffer" amount of rows
        if (self._df_has_start_buffer_rows or
                self._count_unique_days_in_dataframe() >= self.machine_settings.start_buffer_days):

            self._df_has_start_buffer_rows = True

            # Create an identifier for the dataframe in its current state
            timestamp = self.df.iloc[-1].timestamp
            identifier = DFIdentifier(self.symbol, timestamp)

            # Calculate and add the values of all derived columns
            for column_title, column_func in self.machine_settings.derived_columns.items():
                self.df.at[self.df.index[-1], column_title] = column_func(identifier, self.df)

    def _count_unique_days_in_dataframe(self):
        """DOC:"""
        unique_days = set()

        for datetime in self.df.datetime:
            unique_days.add(str(datetime.date()))

        return len(unique_days)


class AssetManager:
    """
    DOC:
    """

    alpaca_api: AlpacaAPIBundle
    machine_settings: machine_settings.MachineSettings
    watched_assets: dict[str, Asset]
    trading_days: list[TradingDay]
    buffer_start_date: str
    buffer_end_date: str

    def __init__(self, alpaca_api: AlpacaAPIBundle, machine_settings: MachineSettings) -> None:
        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings
        self.watched_assets = {}  # Dict of Assets
        self.trading_days = get_list_of_trading_days_in_range(
            self.alpaca_api, self.machine_settings.start_date, self.machine_settings.end_date)

        # self._calculate_list_of_buffer_dates()

        self._set_next_buffer_dates()

        self._reference_symbol = "SPY"
        self.watch_asset(self._reference_symbol)

        self.simulation_running = False

    def __setitem__(self, key: str, value) -> None:
        raise AttributeError(
            f"All keys of the AssetManager (such as \"{key}\") are read-only, and cannot be written to.")

    def __getitem__(self, key: str) -> pd.DataFrame:
        if not isinstance(key, str):
            raise KeyError("Only strings are accepted as keys for this object.")

        return self.watched_assets[key].df

    def startup(self) -> None:
        self.simulation_running = True

    def cleanup(self) -> None:
        # TODO: Join on the process
        pass

    def items(self) -> dict[str, Asset]:
        """DOC:"""
        return self.watched_assets.items()

    def increment_dataframes(self):
        """DOC:"""

        if not self.simulation_running:
            raise StopIteration("Reached the end of simulation. No more trading days to run.")

        # TODO: Verify all timestamps are the same across assets for a given row

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
            self.simulation_running = False

    def _calculate_list_of_buffer_dates(self) -> list[tuple[TradingDay, TradingDay]]:
        """DOC:"""

        # TODO:
        finished = False
        start_index = 0
        end_index = self.machine_settings.data_buffer_days - 1

        while not finished:

            buffer_start_date = self.trading_days[0].date.isoformat()

        breakpoint()

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

    def _populate_buffers(self, symbols: list[str], buffer_start_date: str, buffer_end_date: str):
        """DOC:"""

        # TODO: put get_bulk_bars on another process, make this a call to mp.Queue.get()

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
            if symbol != self._reference_symbol:
                self.watched_assets.pop(symbol)

            # This still returns true so the user thinks the reference symbol has been removed
            return True
        else:
            return False

    def _get_reference_asset(self):
        """DOC:"""
        return self.watched_assets[self._reference_symbol]

    def latest_timestamp(self):
        """DOC:"""
        return self._get_reference_asset().timestamp()

    def latest_datetime(self):
        """DOC:"""
        return self._get_reference_asset().datetime()
