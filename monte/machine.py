"""DOC:"""

from alpaca_trade_api import TimeFrame
from dataclasses import dataclass
from datetime import timedelta


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
    start_buffer_time_delta: timedelta
