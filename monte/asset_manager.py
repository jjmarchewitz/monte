from __future__ import annotations

from datetime import date, datetime, timedelta
from multiprocessing import Process, Queue
from typing import ItemsView

import pandas as pd
from alpaca_trade_api import TimeFrameUnit
from dateutil.parser import isoparse

from monte.dates import (TradingDay, get_list_of_buffer_ranges,
                         get_list_of_trading_days_in_range)
from monte.machine_settings import MachineSettings
from monte.util import AlpacaAPIBundle

BASE_COLUMNS = [
    'timestamp',
    'open',
    'high',
    'low',
    'close',
    'volume',
    'trade_count',
    'vwap',
    'datetime',
    'symbol']


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
        columns = BASE_COLUMNS.copy()
        columns.extend(self.machine_settings.derived_columns.keys())
        self.df = pd.DataFrame({}, columns=columns)

    def reset_buffer(self) -> None:
        """
        Creates a new, empty dataframe with only the base columns (NOT derived columns). The result is
        stored in self.buffer.
        """
        self.buffer = pd.DataFrame({}, columns=BASE_COLUMNS)

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
        if len(self.df.index) > self.machine_settings.max_rows_in_test_df:
            self.df.drop(self.df.head(1).index, inplace=True)

        # If the main dataframe has at least "start_buffer" amount of rows
        if (self._df_has_start_buffer_rows or
                self._count_unique_days_in_dataframe() > self.machine_settings.start_buffer_days):

            self._df_has_start_buffer_rows = True

            # Calculate and add the values of all derived columns
            for column_title, column_func in self.machine_settings.derived_columns.items():
                self.df.at[self.df.index[-1], column_title] = column_func(self.df)

    def _count_unique_days_in_dataframe(self):
        """DOC:"""
        unique_days = set()

        for datetime in self.df.datetime:
            unique_days.add(str(datetime.date()))

        return len(unique_days)


def _get_alpaca_data(
        alpaca_api: AlpacaAPIBundle, machine_settings: MachineSettings, symbols: list[str],
        start_date: date, end_date: date) -> dict[str, pd.DataFrame]:

    buffer_data = alpaca_api.async_market_data_bars.get_bulk_bars(
        symbols, machine_settings.time_frame, start_date, end_date)

    trading_days = get_list_of_trading_days_in_range(alpaca_api, start_date, end_date)

    for symbol, buffer in buffer_data.items():

        # Iterate over the rows
        for index, row in buffer.iterrows():

            # The date of the current row
            row_datetime = isoparse(row.t)

            # Flag variables
            date_in_buffer_range = False

            for trading_day in trading_days:

                # Check that the date is a valid day where the market was open
                if row_datetime.date() == trading_day.date:
                    date_in_buffer_range = True

                    # The current row should be dropped if its timestamp is outside the market hours for this
                    # TradingDay, except if the TimeFrameUnit is a Day. The timestamp doesnt matter then.
                    if (machine_settings.time_frame.unit != TimeFrameUnit.Day and (
                            row_datetime < trading_day.open_time or row_datetime > trading_day.close_time)):
                        buffer.drop(index, inplace=True)

            # If the date of the row does not correspond to a valid TradingDay, drop it.
            if not date_in_buffer_range:
                buffer.drop(index, inplace=True)

        # Reset the index to 'forget' about the dropped rows
        buffer.reset_index(drop=True, inplace=True)

        # Rename columns to more human-friendly names
        buffer.rename(columns={
            "t": BASE_COLUMNS[0],  # timestamp
            "o": BASE_COLUMNS[1],  # open
            "h": BASE_COLUMNS[2],  # high
            "l": BASE_COLUMNS[3],  # low
            "c": BASE_COLUMNS[4],  # close
            "v": BASE_COLUMNS[5],  # volume
            "n": BASE_COLUMNS[6],  # trade_count
            "vw": BASE_COLUMNS[7],  # vwap
        }, inplace=True)

        # Add datetimes as a column
        buffer.insert(loc=8, column=BASE_COLUMNS[8], value=-1)

        # Populate datetime column
        buffer[BASE_COLUMNS[8]] = buffer.apply(
            lambda row: isoparse(row.timestamp).astimezone(machine_settings.time_zone), axis=1)

        # Add symbol as a column
        buffer.insert(loc=9, column=BASE_COLUMNS[9], value=symbol)

    # TODO: Verify all timestamps are the same across assets for a given row

    return buffer_data


def _get_alpaca_data_as_process(
        output_queue: Queue, alpaca_api: AlpacaAPIBundle,
        machine_settings: MachineSettings, symbols: list[str],
        start_date: datetime, end_date: datetime) -> None:

    buffer_ranges = get_list_of_buffer_ranges(
        alpaca_api, machine_settings.data_buffer_days, start_date, end_date)

    for buffer_range in buffer_ranges:
        buffer_start_date = buffer_range[0]
        buffer_end_date = buffer_range[1]
        buffer_data = _get_alpaca_data(
            alpaca_api,
            machine_settings,
            symbols,
            buffer_start_date,
            buffer_end_date)
        output_queue.put(buffer_data)

    output_queue.put("DONE")


class AssetManager:
    """
    DOC:
    """

    alpaca_api: AlpacaAPIBundle
    machine_settings: MachineSettings
    watched_assets: dict[str, Asset]
    trading_days: list[TradingDay]
    most_recent_buffer_start_date: str
    most_recent_buffer_end_date: str
    _buffer_ranges: list[tuple[TradingDay, TradingDay]]
    data_getter_process: Process
    buffered_df_queue: Queue

    def __init__(self, alpaca_api: AlpacaAPIBundle, machine_settings: MachineSettings) -> None:
        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings
        self.watched_assets = {}  # Dict of Assets
        self.simulation_running = False

        self._reference_symbol = "SPY"
        self.watch_asset(self._reference_symbol)

        self.buffered_df_queue = Queue()

    def __setitem__(self, key: str, value) -> None:
        raise AttributeError(
            f"All keys of the AssetManager (such as \"{key}\") are read-only, and cannot be written to.")

    def __getitem__(self, key: str) -> pd.DataFrame:
        if not isinstance(key, str):
            raise KeyError("Only strings are accepted as keys for this object.")

        return self.watched_assets[key].df

    def startup(self) -> None:

        self.add_start_buffer_data()

        self.simulation_running = True

        self.data_getter_process = Process(
            name="Working Data Getter",
            target=_get_alpaca_data_as_process,
            args=(
                self.buffered_df_queue,
                self.alpaca_api,
                self.machine_settings,
                list(self.watched_assets.keys()),
                self.machine_settings.start_date,
                self.machine_settings.end_date),
            daemon=True)
        self.data_getter_process.start()

    def cleanup(self) -> None:
        self.data_getter_process.join()

    def items(self) -> ItemsView[str, Asset]:
        """DOC:"""
        return self.watched_assets.items()

    def increment_dataframes(self):
        """DOC:"""

        # If any asset's data buffer is empty, populate all assets with new data
        if any(asset.buffer.empty for asset in self.watched_assets.values()):
            self._populate_buffers()

        # Then, add the next row of buffered data to the watched assets (update the asset DFs)
        for asset in self.watched_assets.values():
            asset.increment_dataframe()

    def _populate_buffers(self):
        """DOC:"""

        new_data = self.buffered_df_queue.get()

        if isinstance(new_data, dict):
            for symbol, new_buffer in new_data.items():
                self.watched_assets[symbol].buffer = new_buffer
        elif isinstance(new_data, str) and new_data == "DONE":
            raise StopIteration("Reached the end of simulation. No more trading days to run.")
        else:
            raise TypeError("Received invalid data from the buffered_df_queue")

    def add_start_buffer_data(self):
        """DOC:"""

        trading_days_before_current = get_list_of_trading_days_in_range(
            self.alpaca_api,
            (
                self.machine_settings.start_date -
                timedelta(days=self.machine_settings.start_buffer_days) -
                timedelta(days=30)
            ),
            (
                self.machine_settings.start_date -
                timedelta(days=1)
            ))

        buffer_start_date = trading_days_before_current[-self.machine_settings.start_buffer_days].date
        buffer_end_date = trading_days_before_current[-1].date

        start_buffer_data = _get_alpaca_data(
            self.alpaca_api,
            self.machine_settings,
            list(self.watched_assets.keys()),
            buffer_start_date,
            buffer_end_date)

        for symbol, buffer_df in start_buffer_data.items():

            self.watched_assets[symbol].buffer = buffer_df

            while not self.watched_assets[symbol].buffer.empty:
                self.watched_assets[symbol].increment_dataframe()

    def watch_asset(self, symbol: str) -> None:
        """DOC:"""

        if self.simulation_running:
            raise RuntimeError("Cannot watch assets while a simulation is running.")

        elif not self.is_watching_asset(symbol):
            self.watched_assets[symbol] = Asset(self.alpaca_api, self.machine_settings, symbol)

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
