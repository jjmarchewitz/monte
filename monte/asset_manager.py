from __future__ import annotations

from datetime import date, datetime, timedelta
from enum import Enum
from multiprocessing import Process, Queue
from typing import ItemsView

import pandas as pd
from alpaca_trade_api import TimeFrameUnit
from dateutil.parser import isoparse

from monte.api import AlpacaAPIBundle
from monte.dates import (TradingDay, get_list_of_buffer_ranges,
                         get_list_of_trading_days_in_range)
from monte.machine_settings import MachineSettings

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


class DataDestination(Enum):
    TRAINING_DATA = 1
    TESTING_DATA = 2


class Asset:
    """
    Represents one single asset from the markets, this object constructs and manages dataframes for the given
    symbol.
    """

    alpaca_api: AlpacaAPIBundle
    machine_settings: MachineSettings
    training_df: pd.DataFrame
    testing_df: pd.DataFrame
    buffer: pd.DataFrame
    base_columns: list[str]
    _finished_populating_start_buffer: bool

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
        self.reset_main_dfs()
        self.reset_buffer()

        self._finished_populating_start_buffer = False

    def price(self):
        return self.testing_df.iloc[-1].vwap

    def timestamp(self):
        return self.testing_df.iloc[-1].timestamp

    def datetime(self):
        return self.testing_df.iloc[-1].datetime

    def reset_main_dfs(self) -> None:
        """
        Creates a new, empty dataframe with all of the base columns and derived columns. The result is
        stored in self.df.
        """
        columns = BASE_COLUMNS.copy()
        columns.extend(self.machine_settings.derived_columns.keys())
        self.training_df = pd.DataFrame({}, columns=columns)
        self.testing_df = pd.DataFrame({}, columns=columns)

    def reset_buffer(self) -> None:
        """
        Creates a new, empty dataframe with only the base columns (NOT derived columns). The result is
        stored in self.buffer.
        """
        self.buffer = pd.DataFrame({}, columns=BASE_COLUMNS)

    def increment_dataframe(self, data_destination: DataDestination):
        """DOC:"""

        # Grab a copy of the latest row from the buffer
        latest_row = self.buffer.head(1)

        # Drop the top row of the buffer (the row we just copied)
        self.buffer.drop(self.buffer.head(1).index, inplace=True)

        # Depending on the data destination, choose a pd.DataFrame to write to
        if data_destination is DataDestination.TRAINING_DATA:
            self.training_df = pd.concat(objs=[self.training_df, latest_row], ignore_index=True)
            destination_df = self.training_df
        elif data_destination is DataDestination.TESTING_DATA:
            self.testing_df = pd.concat(objs=[self.testing_df, latest_row], ignore_index=True)
            destination_df = self.testing_df
        else:
            raise ValueError("Invalid data_destination. Must be a member of the DataDestination enum.")

        # If the testing df is selected
        if (data_destination is DataDestination.TESTING_DATA and
                len(self.testing_df.index) > self.machine_settings.max_rows_in_test_df):

            # Drop the oldest row if it exceeds the configured length limit (machine_settings.max_rows_in_df)
            self.testing_df.drop(self.testing_df.head(1).index, inplace=True)

        # If the dataframes have at least "start_buffer" amount of rows
        if (self._finished_populating_start_buffer or self._count_unique_days_in_dataframes()
                > self.machine_settings.start_buffer_days):

            self._finished_populating_start_buffer = True

            # Calculate and add the values of all derived columns
            for column_title, column_func in self.machine_settings.derived_columns.items():
                destination_df.at[destination_df.index[-1], column_title] = column_func(destination_df)

    def _switch_to_testing_data(self) -> None:
        """DOC:"""
        # Remove the start buffer data from the training_df
        self.training_df = self.training_df.loc[
            self.training_df['datetime'] > self.machine_settings.start_date]

        # Copy a start buffer's worth of data to the head of the testing_df
        self.testing_df = self.training_df.iloc[
            -(self.machine_settings.rows_per_day() * self.machine_settings.start_buffer_days):-1]

    def _count_unique_days_in_dataframes(self):
        """DOC:"""
        unique_days = set()

        for datetime in self.training_df.datetime:
            unique_days.add(str(datetime.date()))

        for datetime in self.testing_df.datetime:
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
    data_getter_process: Process
    buffered_df_queue: Queue
    simulation_running: bool
    data_destination: DataDestination
    testing_df_threshold: TradingDay

    def __init__(self, alpaca_api: AlpacaAPIBundle, machine_settings: MachineSettings) -> None:
        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings
        self.watched_assets = {}  # Dict of Assets
        self.simulation_running = False

        self._reference_symbol = "SPY"
        self.watch_asset(self._reference_symbol)

        self.buffered_df_queue = Queue()

        self.testing_df_threshold = self.threshold_to_start_using_testing_df()

    def startup(self) -> None:
        """DOC:"""

        # Must happen before add_start_buffer_data() so that the start buffer data has a destination
        self.data_destination = DataDestination.TRAINING_DATA

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
        """DOC:"""
        self.data_getter_process.join()

    def get_training_data(self, symbol) -> pd.DataFrame:
        """DOC:"""
        return self.watched_assets[symbol].training_df

    def get_testing_data(self, symbol) -> pd.DataFrame:
        """DOC:"""
        return self.watched_assets[symbol].testing_df

    def items(self) -> ItemsView[str, Asset]:
        """DOC:"""
        return self.watched_assets.items()

    def threshold_to_start_using_testing_df(self) -> TradingDay:
        """DOC:"""
        trading_days = get_list_of_trading_days_in_range(
            self.alpaca_api,
            self.machine_settings.start_date,
            self.machine_settings.end_date)

        threshold_index = int(self.machine_settings.training_data_percentage * (len(trading_days) - 1)) + 1

        return trading_days[threshold_index]

    def increment_dataframes(self) -> None:
        """DOC:"""

        # If any asset's data buffer is empty, populate all assets with new data
        if any(asset.buffer.empty for asset in self.watched_assets.values()):
            self._populate_buffers()

        # If the top row of the reference asset's buffer has a date that matches the testing_df_threshold
        # date, switch the data destination to be testing data
        top_row_of_reference_asset_buffer = self.watched_assets[self._reference_symbol].buffer.head(1)
        if (self.data_destination is DataDestination.TRAINING_DATA and
                top_row_of_reference_asset_buffer.iloc[0].datetime.date() == self.testing_df_threshold.date):
            self._switch_to_testing_data()

        # Then, add the next row of buffered data to the watched assets (update the asset DFs)
        for asset in self.watched_assets.values():
            asset.increment_dataframe(self.data_destination)

    def _populate_buffers(self) -> None:
        """DOC:"""

        new_data = self.buffered_df_queue.get()

        if isinstance(new_data, dict):
            for symbol, new_buffer in new_data.items():
                self.watched_assets[symbol].buffer = new_buffer
        elif isinstance(new_data, str) and new_data == "DONE":
            raise StopIteration("Reached the end of simulation. No more trading days to run.")
        else:
            raise TypeError("Received invalid data from the buffered_df_queue")

    def _switch_to_testing_data(self) -> None:
        """DOC:"""
        self.data_destination = DataDestination.TESTING_DATA

        for asset in self.watched_assets.values():
            asset._switch_to_testing_data()

    def add_start_buffer_data(self) -> None:
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
                self.watched_assets[symbol].increment_dataframe(self.data_destination)

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
