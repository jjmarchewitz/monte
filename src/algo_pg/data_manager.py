"""
TODO:
"""

from os import stat
from time import time
from algo_pg.util import get_list_of_trading_days_in_range
from alpaca_trade_api import TimeFrame
from datetime import timedelta
from dateutil.parser import isoparse
import pandas as pd


class DataManager():
    """TODO:

    - can handle switching between allowing and disallowing after-hours data
    - can calculate summary statistics on the fly and add them to the main df
    - can add "buffer data" to the beginning of the raw df to allow for stats to be
      calculated correctly from data point 0

    """

    def __init__(
            self, alpaca_api, symbol, start_date=None, end_date=None,
            time_frame=TimeFrame.Hour, normal_market_hours_only=True,
            pre_start_buffer_period=timedelta(seconds=0),
            stat_dict=None):

        self.alpaca_api = alpaca_api
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.time_frame = time_frame
        # self.normal_market_hours_only = normal_market_hours_only
        # self.pre_start_buffer_period = pre_start_buffer_period
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

        # This must come after the dataframe initialization
        self.stat_dict = None

        # This is not the same as self.stat_dict, this is the constructor's argument
        if stat_dict is not None:
            self.add_stat_dict(stat_dict)

    def add_stat_dict(self, stat_dict):
        """TODO:"""
        self.stat_dict = stat_dict

        # Update the columns to include the statistics passed in
        self._df_columns.extend(self._get_statistics_column_names())

        # Recreate the dataframe with the new columns added in
        self.df = pd.DataFrame(columns=self._df_columns)

    def _get_statistics_column_names(self):
        """TODO:"""

        stat_column_names = []

        if self.stat_dict is not None:
            for key, _ in self.stat_dict.items():
                stat_column_names.append(key)

        return stat_column_names

    def set_start_and_end_dates(self, start_date, end_date):
        """TODO:"""
        self.start_date = start_date
        self.end_date = end_date

    def set_time_frame(self, time_frame):
        """TODO:"""
        self.time_frame = time_frame

    def get_last_row(self):
        """TODO:"""

        # TODO: Change this back to regular df instead of _raw_df
        return self.df.loc[len(self.df) - 1]

    def create_new_daily_row_generator(self, start_time, end_time):
        """TODO:"""
        self._row_generator = self._daily_row_generator(start_time, end_time)
        self.generator_at_end_of_day = False

    def _daily_row_generator(self, start_time, end_time):
        """TODO:"""

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
            # TODO: Use stats dict to add/generate stats columns

            yield self.generator_at_end_of_day

    def update_df(self):
        """TODO:"""

        # Add a new row to the main dataframe
        self.df.loc[len(self.df)] = ["ERROR_NOT_REPLACED" for _ in self._df_columns]

        last_row_of_raw_df = self._raw_df.loc[len(self._raw_df) - 1]

        for column, value in last_row_of_raw_df.items():
            setattr(self.df.loc[len(self.df) - 1], column, value)

        for column, func in self.stat_dict.items():
            value = func(self._raw_df)
            setattr(self.df.loc[len(self.df) - 1], column, value)

        breakpoint()

    def get_df_between_dates(self, start_date, end_date):
        """TODO:"""

        # Get a list of all valid trading days the market was open for in the date range
        # provided with open and close times as attributes.
        trading_days = get_list_of_trading_days_in_range(
            self.alpaca_api, start_date, end_date)

        for day in trading_days:

            self._row_generator = self._row_generator(
                day.open_time_iso, day.close_time_iso)

            while True:
                try:
                    next(self._row_generator)
                except StopIteration:
                    break

    def _generate_next_bar(self):
        """
        Set the current bar to the bar generator's next iteration.
        """
        try:
            # Grab the next bar from the generator and generate a price from it
            self.current_bar = next(self._bar_generator)

        except StopIteration:
            # When a generator tries to generate past the end of its intended range it will
            # throw this error, and I use it to indicate that a new bar generator for a
            # new day needs to be generated.
            self.generator_at_end_of_day = True

    def _add_current_bar_to_raw_df(self):
        """TODO:"""
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

            self._raw_df.loc[len(self._raw_df)] = row_data

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
            # If the time frame is a day, then creating a generator with the same start date
            # as its own end date will create an empty generator. What this all does is
            # it shifts the start of the generator back by one day so that when next() is
            # called on the generator, it will return the intended day's price.

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
