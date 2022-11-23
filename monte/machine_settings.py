import math
from datetime import datetime

import pytz
from alpaca_trade_api import TimeFrame, TimeFrameUnit

from derived_columns import DerivedColumn
from monte.api import AlpacaAPIBundle


class MachineSettings():
    """
    A class to store important settings for the trading machine. Can automatically derive many of these
    settings.
    """

    alpaca_api: AlpacaAPIBundle
    start_date: datetime
    end_date: datetime
    training_data_percentage: float
    time_frame: TimeFrame
    derived_columns: dict[str, DerivedColumn]
    max_rows_in_test_df: int
    start_buffer_days: int
    data_buffer_days: int
    time_zone: pytz.tzinfo.BaseTzInfo

    # TODO: Default to user's current timezone instead of US/Eastern

    def __init__(self, alpaca_api: AlpacaAPIBundle, start_date: datetime, end_date: datetime,
                 training_data_percentage: float, time_frame: TimeFrame,
                 derived_columns: dict[str, DerivedColumn] = {},
                 max_rows_in_test_df: int = 10, time_zone: pytz.tzinfo.BaseTzInfo = pytz.timezone('US/Eastern')):
        self.alpaca_api = alpaca_api
        self.start_date = start_date
        self.end_date = end_date
        self.training_data_percentage = training_data_percentage
        self.time_frame = time_frame
        self.derived_columns = derived_columns
        self.time_zone = time_zone

        self.max_rows_in_test_df = max_rows_in_test_df

        self.validate_dates()
        self.validate_training_data_percentage()
        self.validate_time_frame()

        # Add timezone info to start_date and end_date
        self.add_tz_info_to_dates()

        # Derive the start buffer days
        self.start_buffer_days = self.calculate_start_buffer_days()

        # Derive the data buffer days
        self.data_buffer_days = self.calculate_data_buffer_days()

        self.validate_data_buffer_days()

    def validate_dates(self):
        """
        Checks that ``self.start_date`` and ``self.end_date`` are valid and can be used in the trading
        machine.
        """
        # Validate self.start_date
        if not isinstance(self.start_date, datetime):
            raise TypeError("The start date must be an instance of datetime.datetime")

        # Validate self.end_date
        if not isinstance(self.end_date, datetime):
            raise TypeError("The end date must be an instance of datetime.datetime")

        # Raise an error if the start date is after the end date
        if self.start_date > self.end_date:
            raise ValueError("The end date must come after the start date.")

        # Raise an error if the start date is before Jan 1st, 2016 (earliest that Alpaca has)
        if self.start_date < datetime(2016, 1, 1):
            raise ValueError(f"The start date must be after Jan 1st, 2016. This is the earliest date where"
                             "Alpaca has data for all symbols.")

        # Raise an error if the end date is on or after the current real-life day
        if self.end_date.date() >= datetime.today().date():
            raise ValueError(f"The end date must be before today's date: {datetime.today().date()}")

    def validate_training_data_percentage(self):
        """
        Checks that ``self.training_data_percentage`` is valid and can be used in the trading machine.
        """
        if self.training_data_percentage < 0 or self.training_data_percentage > 1:
            raise ValueError(
                f"machine_settings.training_data_percentage must be a value between 0 and 1 "
                f"(inclusive). The current value is {self.training_data_percentage}")

    def validate_time_frame(self):
        """
        Checks that ``self.time_frame`` is valid and can be used in the trading machine.
        """
        if self.time_frame.unit == TimeFrameUnit.Minute and self.time_frame.amount > 59:
            raise ValueError(
                f"TimeFrames with a unit of Minutes must have a value less than or equal to 59. "
                f"The current value is {self.time_frame.amount}.")
        elif self.time_frame.unit == TimeFrameUnit.Hour and self.time_frame.amount > 7:
            raise ValueError(
                f"TimeFrames with a unit of Hours must have a value less than or equal to 7. "
                f"The current value is {self.time_frame.amount}")
        elif self.time_frame.unit == TimeFrameUnit.Day and self.time_frame.amount != 1:
            raise ValueError(
                f"TimeFrames with a unit of Days must have a value of 1. "
                f"The current value is {self.time_frame.amount}")
        elif self.time_frame.unit in (TimeFrameUnit.Week, TimeFrameUnit.Month):
            raise ValueError(f"Cannot have a TimeFrameUnit of {self.time_frame.unit}")

    def validate_data_buffer_days(self):
        """
        Checks that ``self.data_buffer_days`` is valid and can be used in the trading machine.
        """
        if self.data_buffer_days < 7:
            raise ValueError(
                f"Data buffers need to be greater than or equal to 7 days. The current data buffer is "
                f"{self.data_buffer_days} days")

    def add_tz_info_to_dates(self):
        """
        Adds timezone info to ``self.start_date`` and ``self.end_date``.
        """
        self.start_date = self.start_date.replace(tzinfo=self.time_zone)
        self.end_date = self.end_date.replace(tzinfo=self.time_zone)

    def calculate_start_buffer_days(self) -> int:
        """
        Calculates the number of start buffer days needed based on ``self.max_rows_in_test_df`` and
        ``self.rows_per_day()``.
        """
        # Get the number of start buffer days needed to make the derived columns in the test df run correctly.
        # During the testing phase, all of the derived columns already have data to use and
        rows_per_day = self.get_rows_per_day()
        days_needed_for_test_df = math.ceil(self.max_rows_in_test_df / rows_per_day)

        max_days_needed_by_derived_columns = 0
        for derived_column in self.derived_columns.values():
            # Get the number of days needed by the current derived column
            days_needed_by_derived_column = self.get_start_buffer_days_needed_by_derived_column(
                derived_column, rows_per_day)

            # Update the maximum number of days needed by any derived column
            max_days_needed_by_derived_columns = max(
                max_days_needed_by_derived_columns, days_needed_by_derived_column)

        # Set the start buffer days to the maximum of the days needed by the testing df and the days needed
        # by the derived columns
        start_buffer_days = max(days_needed_for_test_df, max_days_needed_by_derived_columns)

        return start_buffer_days

    def get_start_buffer_days_needed_by_derived_column(self, dcol: DerivedColumn, rows_per_day: int) -> int:
        """
        Returns the number of start buffer days needed by a derived column and its entire dependency tree.

        If a derived column needs 10 days and it depends on a column that needs 20 days, this will return 30
        days.
        """
        parent_column_days_needed = 0

        # If the derived column has dependencies
        if dcol.column_dependencies:
            # For each column it depends on
            for column_title in dcol.column_dependencies:

                # Calculate how many start buffer days the depended column needs
                column_obj = self.derived_columns[column_title]
                dependent_column_days_needed = self.get_start_buffer_days_needed_by_derived_column(
                    column_obj, rows_per_day)

                # Update the parent column days needed to be the max of all of the depended columns days
                parent_column_days_needed = max(parent_column_days_needed, dependent_column_days_needed)

        # Add the days needed by the parent derived column itself to the total
        parent_column_days_needed += math.ceil(dcol.num_rows_needed / rows_per_day)

        return parent_column_days_needed

    def get_rows_per_day(self) -> int:
        """
        Calculates the number of rows in a typical day of trading based on ``self.time_frame``.
        """
        rows_per_day = 0

        # Calculate how many self.time_frames occur in an average market day
        if self.time_frame.unit == TimeFrameUnit.Minute:
            # time frames per hour times 7.5 since there are 7.5 hours in a market day, on average
            # (9:30a - 4:00p)
            rows_per_day = int(int(60 / self.time_frame.amount) * 7.5)

        elif self.time_frame.unit == TimeFrameUnit.Hour:
            # There are 7 time frames that start on the hour in an average market day, so Alpaca
            # only returns 7 time frames per day if the TimeFrameUnit is hours
            rows_per_day = int(7 / self.time_frame.amount)

        elif self.time_frame.unit == TimeFrameUnit.Day:
            rows_per_day = 1

        else:
            raise ValueError(
                "machine_settings.time_frame.unit must be one of (TimeFrameUnit.Minute, "
                "TimeFrameUnit.Hour, TimeFrameUnit.Day)")

        return rows_per_day

    def calculate_data_buffer_days(self) -> int:
        """
        Calculates a close-to-optimal number of data buffer days based on ``self.time_frame``
        """

        # These multipliers were determined experimentally with a range of time_frames
        if self.time_frame.unit == TimeFrameUnit.Minute:
            return self.time_frame.amount * 8

        elif self.time_frame.unit == TimeFrameUnit.Hour:
            return self.time_frame.amount * 500

        elif self.time_frame.unit == TimeFrameUnit.Day:
            return self.time_frame.amount * 7000

        else:
            raise ValueError(
                "machine_settings.time_frame.unit must be one of (TimeFrameUnit.Minute, "
                "TimeFrameUnit.Hour, TimeFrameUnit.Day)")

    def add_derived_columns(self, new_columns: dict[str, DerivedColumn]):
        """
        Adds derived columns contained in ``new_columns`` to ``self.derived_columns`` if the column names
        have no clashes. Also updates ``self.max_rows_in_test_df`` and ``self.start_buffer_days`` based on
        the new columns.
        """
        for column_title, new_derived_column in new_columns.items():

            # Check that the new derivec column is an instance of Derived Column
            if not isinstance(new_derived_column, DerivedColumn):
                raise ValueError(
                    "Only instances of DerivedColumn can be added as a derived column.")

            # If a derived column with the same name exists
            if column_title in self.derived_columns.keys():

                existing_derived_column = self.derived_columns[column_title]

                # If the two derived columns with the same name are different, raise an error
                if existing_derived_column != new_derived_column:
                    raise ValueError(
                        f"Attempted to add a new derived column with the same name as an existing column "
                        f"but a different function or arguments. This is possibly because two algorithms "
                        f"use the same name with different values. The column name is {column_title}. \n")

            # Else, add the new derived column to self.derived_columns
            else:
                self.derived_columns[column_title] = new_derived_column

        # Update the maximum number of rows in the testing dataframe to be the maximum of the number of rows
        # each derived column uses.
        for derived_column in self.derived_columns.values():
            self.max_rows_in_test_df = max(self.max_rows_in_test_df, derived_column.num_rows_needed)

        # Re-calculate the number of start buffer days needed since it is calculated based on
        # self.max_rows_in_test_df.
        self.start_buffer_days = self.calculate_start_buffer_days()
