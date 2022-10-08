from __future__ import annotations

from functools import partial

from alpaca_trade_api import TimeFrame, TimeFrameUnit

from algorithms import test
from monte import derived_columns
from monte.machine import TradingMachine
from monte.machine_settings import MachineSettings
from monte.util import AlpacaAPIBundle


def main():
    alpaca_api = AlpacaAPIBundle()

    # TODO: Create pre-defined "configs" for the most commonly used TimeFrames that auto-sets the TimeFrame
    # and data_buffer_days.
    # TODO: Add logging

    ms = MachineSettings(
        start_date="2020-09-09",
        end_date="2022-10-04",
        time_frame=TimeFrame(1, TimeFrameUnit.Hour),
        derived_columns={
            "avg_l5": partial(derived_columns.avg_last_n, n=5)
        },
        max_rows_in_df=500,
        start_buffer_days=5,  # TradingDays
        data_buffer_days=500,  # TradingDays
    )

    trading_machine = TradingMachine(alpaca_api, ms)

    algo1 = test.TestAlg(alpaca_api, ms)

    trading_machine.add_algo_instance(algo1)

    trading_machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
