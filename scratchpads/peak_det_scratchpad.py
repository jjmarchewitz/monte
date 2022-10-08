from __future__ import annotations

from functools import partial

from alpaca_trade_api import TimeFrame, TimeFrameUnit

from algorithms.peak_detection import PeakDetection
from derived_columns import general
from monte.machine import TradingMachine
from monte.machine_settings import MachineSettings
from monte.util import AlpacaAPIBundle


def main():
    alpaca_api = AlpacaAPIBundle()

    ms = MachineSettings(
        start_date="2016-09-09",
        end_date="2022-10-04",
        time_frame=TimeFrame(1, TimeFrameUnit.Hour),
        derived_columns={

        },
        max_rows_in_df=500,
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
