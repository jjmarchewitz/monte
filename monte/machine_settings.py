from datetime import datetime
from typing import Union

import pytz
from alpaca_trade_api import TimeFrame, TimeFrameUnit


class MachineSettings():
    """
    DOC:
    """
    start_date: datetime
    end_date: datetime
    training_data_percentage: float
    time_frame: TimeFrame
    derived_columns: dict
    max_rows_in_test_df: int
    start_buffer_days: int
    data_buffer_days: int
    time_zone: pytz.tzinfo.BaseTzInfo

    def __init__(
            self, start_date: datetime, end_date: datetime, training_data_percentage: float,
            time_frame: TimeFrame, derived_columns: dict = {},
            max_rows_in_test_df: int = 1_000, start_buffer_days: Union[int, None] = None,
            data_buffer_days: Union[int, None] = None, time_zone: pytz.tzinfo.BaseTzInfo = pytz.timezone(
                'US/Eastern')) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.training_data_percentage = training_data_percentage
        self.time_frame = time_frame
        self.derived_columns = derived_columns
        self.max_rows_in_test_df = max_rows_in_test_df
        self.time_zone = time_zone

        self.validate_dates()
        self.validate_trading_data_percentage()
        self.validate_time_frame()

        # Add timezone info to start_date and end_date
        self.add_tz_info_to_dates()

        # Derive the start buffer days if it is not provided
        if start_buffer_days is not None:
            self.start_buffer_days = start_buffer_days
        else:
            self.start_buffer_days = self.calculate_start_buffer_days()

        # Derive the data buffer days if it is not provided
        if data_buffer_days is not None:
            self.data_buffer_days = data_buffer_days
        else:
            self.data_buffer_days = self.calculate_data_buffer_days()

        self.validate_data_buffer_days()

    def validate_dates(self):
        """DOC:"""
        # Validate self.start_date
        if not isinstance(self.start_date, datetime):
            raise TypeError("The start date must be an instance of datetime.datetime")

        # Validate self.end_date
        if not isinstance(self.end_date, datetime):
            raise TypeError("The end date must be an instance of datetime.datetime")

    def validate_trading_data_percentage(self):
        """DOC:"""
        # Validate self.training_data_percentage
        if self.training_data_percentage < 0 or self.training_data_percentage > 1:
            raise ValueError(f"machine_settings.training_data_percentage must be a value between 0 and 1 "
                             f"(inclusive). The current value is {self.training_data_percentage}")

    def validate_time_frame(self):
        """DOC:"""
        # Validate self.time_frame
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
        """DOC:"""
        if self.data_buffer_days < 7:
            raise ValueError(
                f"Data buffers need to be greater than or equal to 7 days. The current data buffer is "
                f"{self.data_buffer_days} days")

    def add_tz_info_to_dates(self):
        """DOC:"""

        self.start_date = self.start_date.replace(tzinfo=self.time_zone)
        self.end_date = self.end_date.replace(tzinfo=self.time_zone)

    def calculate_start_buffer_days(self) -> int:
        """DOC:"""

        rows_per_day = self.rows_per_day()

        start_buffer_days = int(self.max_rows_in_test_df / rows_per_day) + 10

        return start_buffer_days

    def rows_per_day(self) -> int:
        """DOC:"""

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
                raise ValueError("machine_settings.time_frame.unit must be one of (TimeFrameUnit.Minute, "
                                 "TimeFrameUnit.Hour, TimeFrameUnit.Day)")

        return rows_per_day

    def calculate_data_buffer_days(self) -> int:
        """DOC:"""

        match self.time_frame.unit:

            # These multipliers were determined experimentally with a range of time_frames
            case TimeFrameUnit.Minute:
                return self.time_frame.amount * 8

            case TimeFrameUnit.Hour:
                return self.time_frame.amount * 500

            case TimeFrameUnit.Day:
                return self.time_frame.amount * 7000

            case _:
                raise ValueError("machine_settings.time_frame.unit must be one of (TimeFrameUnit.Minute, "
                                 "TimeFrameUnit.Hour, TimeFrameUnit.Day)")
