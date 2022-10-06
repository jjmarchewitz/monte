"""
TODO:
"""

from datetime import timedelta

import pandas as pd
from algo_pg.util import get_list_of_trading_days_in_range
from alpaca_trade_api import TimeFrame
from dateutil.parser import isoparse


class DataManager():
    """
    The DataManager is meant to handle acquiring and synchronizing data from Alpaca, as
    well as building and formatting an output dataframe.
    """

    # TODO: can handle switching between allowing and disallowing after-hours data

    def __init__(self, alpaca_api, data_settings, symbol):
        """
        Constructor for the DataManager object.

        Args:
            alpaca_api: A bundle of Alpaca APIs all created and authenticated with the
                keys in the repo's alpaca.config.
            data_settings: An instance of the DataSettings dataclass.
            symbol: A string for the market symbol of this position (i.e. "AAPL" or
                "GOOG").
        """

        self.alpaca_api = alpaca_api
        self.data_settings = data_settings
        self.symbol = symbol

        self.time_frame = data_settings.time_frame

        self.current_bar = None

        # Start as True to force a new generator to be created
        self._bar_generator = None
        self._row_generator = None
        self.generator_at_end_of_day = True

        self._raw_df_columns = ['timestamp', 'open', 'high',
                                'low', 'close', 'volume', 'trade_count', 'vwap']
        self._raw_df = pd.DataFrame(columns=self._raw_df_columns)

        self._df_columns = self._raw_df_columns
        self.df = pd.DataFrame(columns=self._df_columns)

        self.max_rows = self.data_settings.max_rows_in_df
        self._next_df_index = 0
        self._next_raw_df_index = 0

        # This is not the same as self.stat_dict, this is the constructor's argument
        if self.data_settings.stat_dict is not None:
            self.add_stat_dict(data_settings.stat_dict)

        if self.data_settings.start_buffer_time_delta is not None:
            self._add_start_buffer_data_to_raw_df()

    def add_stat_dict(self, stat_dict):
        """
        Add a new statistics calculating dictionary and update the main dataframe with
        a column for each statistic.

        Args:
            stat_dict: A dictionary where the keys are strings that represent the name of
                a statistic, and where the values are function objects that calculate
                the given statistic.
        """
        self.stat_dict = stat_dict

        # Update the columns to include the statistics passed in
        self._df_columns.extend(self._get_statistics_column_names())

        # Recreate the dataframe with the new columns added in
        self.df = pd.DataFrame(columns=self._df_columns)

    def _get_statistics_column_names(self):
        """
        Extract the column names from the stat_dict (i.e. the keys of the dict).

        Returns:
            A list of column names.
        """

        stat_column_names = []

        if self.stat_dict is not None:
            for key, _ in self.stat_dict.items():
                stat_column_names.append(key)

        return stat_column_names

    def get_last_row(self):
        """
        Get the last row of the main dataframe.

        Returns:
            The last row of the main dataframe.
        """

        return self.df.loc[self._next_df_index - 1]

    def clear_df(self):
        """Clears the main dataframe and the raw (backend) dataframe."""
        self._raw_df = pd.DataFrame(columns=self._raw_df_columns)
        self.df = pd.DataFrame(columns=self._df_columns)

    def _add_start_buffer_data_to_raw_df(self):
        """TODO:"""

        # Shift the start date back by one day
        original_start_dt = isoparse(self.data_settings.start_date)
        new_start_dt_obj = original_start_dt - self.data_settings.start_buffer_time_delta
        buffer_start_date = new_start_dt_obj.isoformat() + "Z"
        buffer_end_date = original_start_dt.isoformat() + "Z"

        self.update_df_with_dates(buffer_start_date, buffer_end_date, raw_df_only=True)

    def update_df_with_dates(self, start_date, end_date, raw_df_only=False):
        """
        Updates self.df to contain a dataframe for self.symbol in the date range between
        start_date and end_date.

        Args:
            start_date: A string for the start date of the dataframe in the form
                YYYY-MM-DD.
            end_date: A string for the end date of the dataframe in the form YYYY-MM-DD.
        """

        # Get a list of all valid trading days the market was open for in the date range
        # provided with open and close times as attributes.
        trading_days = get_list_of_trading_days_in_range(
            self.alpaca_api, start_date, end_date)

        for day in trading_days:

            self.create_new_daily_row_generator(
                day.open_time_iso, day.close_time_iso, raw_df_only)

            while True:
                try:
                    next(self._row_generator)
                except StopIteration:
                    break

    def create_new_daily_row_generator(self, start_time, end_time, raw_df_only=False):
        """
        Creates a new generator object that will generate rows from the start_time to the
        end_time, with the TimeFrame being given by self.data_settings

        Args:
            start_time: The ISO-8601 compliant date/time for the generator to start
                generating bars.
            end_time: The ISO-8601 compliant date/time for the generator to stop
                generating bars.
        """
        self._row_generator = self._daily_row_generator(
            start_time, end_time, raw_df_only)
        self.generator_at_end_of_day = False

    def _daily_row_generator(self, start_time, end_time, raw_df_only=False):
        """
        A generator object that updates the main dataframe with information from the next
        TimeFrame.

        Args:
            start_time: The ISO-8601 compliant date/time for the generator to start
                generating bars.
            end_time: The ISO-8601 compliant date/time for the generator to stop
                generating bars.

        Yields:
            A bool representing if the generator has reached the end of the day.
        """

        # Create a new bar generator each day, regardless of the TimeFrame. This is
        # to synchronize the start and end times on each new day, as some assets have
        # after-hours data that we are excluding
        self._create_new_daily_bar_generator(
            start_time, end_time)

        # While the end of the day has not yet been reached, generate the next bar and
        # add it to the raw dataframe
        while not self.generator_at_end_of_day:
            self._generate_next_bar()
            self._add_current_bar_to_raw_df()
            self._update_raw_df()

            if not raw_df_only:
                self._update_df()

            yield self.generator_at_end_of_day

    def _generate_next_bar(self):
        """
        Set the current bar to the bar generator's next iteration.
        """
        try:
            # Grab the next bar from the generator and generate a price from it
            self.current_bar = next(self._bar_generator)

        except StopIteration:
            # When a generator tries to generate past the end of its intended range it
            # will throw this error, and I use it to indicate that a new bar generator
            # for a new day needs to be generated.
            self.generator_at_end_of_day = True

    def _add_current_bar_to_raw_df(self):
        """
        Add the current bar grabbed from Alpaca to self._raw_df
        """
        if not self.generator_at_end_of_day:
            row_data = [
                self.current_bar.t,  # Timestamp
                self.current_bar.o,  # Open price
                self.current_bar.h,  # High price
                self.current_bar.l,  # Low price
                self.current_bar.c,  # Close price
                self.current_bar.v,  # Volume
                self.current_bar.n,  # Number of Trades (trade count)
                self.current_bar.vw  # Volume-weighted average price
            ]

            self._raw_df.loc[self._next_raw_df_index] = row_data
            self._next_raw_df_index += 1

    def _update_raw_df(self):
        """TODO:"""
        # Remove the first row from the raw df if the total row count is above the limit
        if len(self._raw_df.index) > self.max_rows:
            self._raw_df = self._raw_df.iloc[1:]

    def _update_df(self):
        """
        Updates self.df with the newest input data from self._raw_df and then calculates
        summary statistics from those new entries and adds them to the appropriate
        column.
        """
        # Remove the first row from the main df if the total row count is above the limit
        if len(self.df.index) > self.max_rows:
            self.df = self.df.iloc[1:]

        if not self.generator_at_end_of_day:

            # Add a new row to the main dataframe
            self.df.loc[self._next_df_index] = ["ERROR_NOT_REPLACED"
                                                for _ in self._df_columns]

            last_row_of_raw_df = self._raw_df.loc[self._next_raw_df_index - 1]

            # Copy over columns from raw_df
            for column, value in last_row_of_raw_df.items():
                setattr(self.df.loc[self._next_df_index], column, value)

            # Calculate any statistics from the stat dict and add them to the appropriate
            # column in self.df
            for column, func in self.stat_dict.items():
                last_raw_df_row_index = self._next_raw_df_index - 1
                value = func(self._raw_df, last_raw_df_row_index)
                setattr(self.df.loc[self._next_df_index], column, value)

            self._next_df_index += 1

    def _create_new_daily_bar_generator(self, start_time, end_time):
        """
        Create a new bar generator with a start time and end time that occur on the same
        day and correspond to the open and close times of the market for that day.

        Args:
            start_time: The ISO-8601 compliant date/time for the generator to start
                generating bars.
            end_time: The ISO-8601 compliant date/time for the generator to stop
                generating bars.
        """
        if self.time_frame == TimeFrame.Day:
            # If the time frame is a day, then creating a generator with the same start
            # date as its own end date will create an empty generator. What this all
            # does is it shifts the start of the generator back by one day so that when
            # next() is called on the generator, it will return the intended day's price.

            # Shift the start date back by one day
            start_time_dt_obj = isoparse(start_time)
            incremented_start_time = start_time_dt_obj - timedelta(days=1)
            iso_inc_start_time = incremented_start_time.isoformat()

            # Create the new generator
            self._bar_generator = self.alpaca_api.market_data.get_bars_iter(
                self.symbol, self.time_frame, iso_inc_start_time, end_time)

        else:
            # Create a generator object that will return prices for the day
            self._bar_generator = self.alpaca_api.market_data.get_bars_iter(
                self.symbol, self.time_frame, start_time, end_time)

        self.generator_at_end_of_day = False
