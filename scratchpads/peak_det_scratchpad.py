from __future__ import annotations

from datetime import datetime
from functools import partial

from alpaca_trade_api import TimeFrame, TimeFrameUnit

from algorithms.peak_detection import PeakDetection
from derived_columns import general
from monte.api import AlpacaAPIBundle
from monte.machine import TradingMachine
from monte.machine_settings import MachineSettings


def main():
    alpaca_api = AlpacaAPIBundle()

    ms = MachineSettings(
        start_date=datetime(2016, 9, 9),
        end_date=datetime(2022, 10, 4),
        time_frame=TimeFrame(1, TimeFrameUnit.Hour),
        derived_columns={

        },
        max_rows_in_test_df=500,
        start_buffer_days=5,  # TradingDays
        data_buffer_days=500,  # TradingDays
    )

    trading_machine = TradingMachine(alpaca_api, ms)

    algo = PeakDetection(alpaca_api, ms)
    trading_machine.add_algo_instance(algo)

    trading_machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
