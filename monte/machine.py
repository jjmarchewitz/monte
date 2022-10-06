"""DOC:"""

from dataclasses import dataclass
from datetime import timedelta

from alpaca_trade_api import TimeFrame


@dataclass
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


# TODO: Raise error if TimeFrame is > 1 Day
