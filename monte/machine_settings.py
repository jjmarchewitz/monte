from typing import Union

from alpaca_trade_api import TimeFrame, TimeFrameUnit


class MachineSettings():
    """
    DOC:
    """
    start_date: str
    end_date: str
    time_frame: TimeFrame
    derived_columns: dict
    max_rows_in_df: int
    start_buffer_days: int
    data_buffer_days: int

    def __init__(
            self, start_date: str, end_date: str, time_frame: TimeFrame, derived_columns: dict = {},
            max_rows_in_df: int = 1_000, start_buffer_days: Union[int, None] = None,
            data_buffer_days: Union[int, None] = None) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.time_frame = time_frame
        self.derived_columns = derived_columns
        self.max_rows_in_df = max_rows_in_df
        self.start_buffer_days = start_buffer_days
        self.data_buffer_days = data_buffer_days

        self.validate()

        # TODO: Auto-calculate the data buffer size based on time_frame
        # TODO: Auto-calculate the start buffer size based on max_rows_in_df and time_frame
        # TODO: Convert constructor args to start date, simulation length, and training length

    def validate(self):

        if (
            (self.time_frame.unit == TimeFrameUnit.Minute and self.time_frame.amount > 59) or
            (self.time_frame.unit == TimeFrameUnit.Hour and self.time_frame.amount > 7) or  # 7 hours in a market day
            (self.time_frame.unit == TimeFrameUnit.Day and self.time_frame.amount != 1) or
            (self.time_frame.unit in (TimeFrameUnit.Week, TimeFrameUnit.Month))
        ):
            raise ValueError(
                f"TimeFrames must be 1Day or shorter. The TimeFrame is currently set to {self.time_frame}")

        if self.data_buffer_days < 7:
            raise ValueError(
                f"Data buffers need to be greater than or equal to 7 days. The current data buffer is {self.data_buffer_days} days")
