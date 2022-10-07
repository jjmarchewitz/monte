"""DOC:"""

from dataclasses import dataclass
from datetime import timedelta

from alpaca_trade_api import TimeFrame


class MachineSettings():
    """
    DOC:
    """
    start_date: str
    end_date: str
    time_frame: TimeFrame
    derived_columns: dict
    max_rows_in_df: int
    start_buffer_size: timedelta
    data_buffer_size: timedelta

    def __init__(
            self, start_date: str, end_date: str, time_frame: TimeFrame, derived_columns: dict = {},
            max_rows_in_df: int = 1_000, start_buffer_size: timedelta = timedelta(weeks=1),
            data_buffer_size: timedelta = timedelta(weeks=1)) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.time_frame = time_frame
        self.derived_columns = derived_columns
        self.max_rows_in_df = max_rows_in_df
        self.start_buffer_size = start_buffer_size
        self.data_buffer_size = data_buffer_size

        self.validate()

    def validate(self):
        if self.data_buffer_size < timedelta(weeks=1):
            raise ValueError(
                f"Data buffers need to be greater than or equal to 1 week. The current data buffer is {self.data_buffer_size}")


# TODO: Raise error if TimeFrame is > 1 Day


# Increment dataframes, then run algo
