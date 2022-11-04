import math
from datetime import datetime
from functools import partial

import pytz
from alpaca_trade_api import TimeFrame, TimeFrameUnit

from derived_columns import DerivedColumn


class MachineSettings():
    """
    A class to store important settings for the trading machine. Can automatically derive many of these
    settings.
    """
    # TODO: Make alpaca_api one of the MachineSettings??
    start_date: datetime
    end_date: datetime
    training_data_percentage: float
    time_frame: TimeFrame
    derived_columns: dict[str, DerivedColumn]
    max_rows_in_test_df: int
    start_buffer_days: int
    data_buffer_days: int
    time_zone: pytz.tzinfo.BaseTzInfo

    def __init__(
            self, start_date: datetime, end_date: datetime, training_data_percentage: float,
            time_frame: TimeFrame, derived_columns: dict[str, DerivedColumn] = {},
            max_rows_in_test_df: int = 10,
            time_zone: pytz.tzinfo.BaseTzInfo = pytz.timezone('US/Eastern')) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.training_data_percentage = training_data_percentage
        self.time_frame = time_frame
        self.derived_columns = derived_columns
        self.time_zone = time_zone

        self.max_rows_in_test_df = max_rows_in_test_df

        self.validate_dates()
        self.validate_trading_data_percentage()
        self.validate_time_frame()

        # Add timezone info to start_date and end_date
        self.add_tz_info_to_dates()

        # Derive the start buffer days if it is not provided
        self.start_buffer_days = self.calculate_start_buffer_days()

        # Derive the data buffer days if it is not provided
        self.data_buffer_days = self.calculate_data_buffer_days()

        self.validate_data_buffer_days()

    def validate_dates(self) -> None:
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

    def validate_trading_data_percentage(self) -> None:
        """
        Checks that ``self.training_data_percentage`` is valid and can be used in the trading machine.
        """
        if self.training_data_percentage < 0 or self.training_data_percentage > 1:
            raise ValueError(
                f"machine_settings.training_data_percentage must be a value between 0 and 1 "
                f"(inclusive). The current value is {self.training_data_percentage}")

    def validate_time_frame(self) -> None:
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

    def validate_data_buffer_days(self) -> None:
        """
        Checks that ``self.data_buffer_days`` is valid and can be used in the trading machine.
        """
        if self.data_buffer_days < 7:
            raise ValueError(
                f"Data buffers need to be greater than or equal to 7 days. The current data buffer is "
                f"{self.data_buffer_days} days")

    def add_tz_info_to_dates(self) -> None:
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
        rows_per_day = self.rows_per_day()

        start_buffer_days = math.ceil(self.max_rows_in_test_df / rows_per_day)

        return start_buffer_days

    def rows_per_day(self) -> int:
        """
        Calculates the number of rows in a typical day of trading based on ``self.time_frame``.
        """
        rows_per_day = 0

        # Calculate how many self.time_frames occur in an average market day
        match self.time_frame.unit:

            case TimeFrameUnit.Minute:
                # time frames per hour times 7.5 since there are 7.5 hours in a market day, on average
                # (9:30a - 4:00p)
                rows_per_day = int(int(60 / self.time_frame.amount) * 7.5)

            case TimeFrameUnit.Hour:
                # There are 7 time frames that start on the hour in an average market day, so Alpaca
                # only returns 7 time frames per day if the TimeFrameUnit is hours
                rows_per_day = int(7 / self.time_frame.amount)

            case TimeFrameUnit.Day:
                rows_per_day = 1

            case _:
                raise ValueError(
                    "machine_settings.time_frame.unit must be one of (TimeFrameUnit.Minute, "
                    "TimeFrameUnit.Hour, TimeFrameUnit.Day)")

        return rows_per_day

    def calculate_data_buffer_days(self) -> int:
        """
        Calculates a close-to-optimal number of data buffer days based on ``self.time_frame``
        """
        match self.time_frame.unit:

            # These multipliers were determined experimentally with a range of time_frames
            case TimeFrameUnit.Minute:
                return self.time_frame.amount * 8

            case TimeFrameUnit.Hour:
                return self.time_frame.amount * 500

            case TimeFrameUnit.Day:
                return self.time_frame.amount * 7000

            case _:
                raise ValueError(
                    "machine_settings.time_frame.unit must be one of (TimeFrameUnit.Minute, "
                    "TimeFrameUnit.Hour, TimeFrameUnit.Day)")

    def add_derived_columns(self, new_columns: dict[str, DerivedColumn]) -> None:
        """
        Adds derived columns contained in ``new_columns`` to ``self.derived_columns`` if the column names
        have no clashes. Also updates ``self.max_rows_in_test_df`` and ``self.start_buffer_days`` based on
        the new columns.
        """
        for column_title, new_derived_column in new_columns.items():

            if column_title in self.derived_columns.keys():

                existing_derived_column = self.derived_columns[column_title]

                if (isinstance(existing_derived_column, DerivedColumn) and
                    isinstance(new_derived_column, DerivedColumn) and
                        existing_derived_column == new_derived_column):
                    continue
                else:
                    raise ValueError(
                        f"Attempted to add a new derived column with the same name as an existing column "
                        f"but a different function or arguments. The column name is {column_title}. \n"
                        f"Existing Derived Column: {existing_derived_column}\n"
                        f"New Derived Column: {new_derived_column}")

            else:
                if callable(new_derived_column):
                    self.derived_columns[column_title] = new_derived_column
                else:
                    raise ValueError("Tried to add a non-callable object as a derived column.")

        # Update other attributes of machine_settings based on the new derived columns
        self.update_max_rows_in_df()
        self.start_buffer_days = self.calculate_start_buffer_days()

    def update_max_rows_in_df(self) -> None:
        """
        Sets ``self.max_rows_in_test_df`` to the maximum number of rows needed by any single derived column.
        """
        for _, column_func in self.derived_columns.items():
            # If the function is a partial function and it has a variable designated as storing the number
            # of rows used
            if isinstance(column_func, partial) and column_func.func.num_rows_arg_name is not None:
                # Update the maximum number of rows in the df to be the maximum between its current value
                # and the value from the current column_func
                num_rows_arg_name = column_func.func.num_rows_arg_name
                self.max_rows_in_test_df = max(self.max_rows_in_test_df,
                                               column_func.keywords[num_rows_arg_name])
