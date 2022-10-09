from __future__ import annotations

from functools import partial

from alpaca_trade_api import TimeFrame, TimeFrameUnit

from algorithms import test
from derived_columns.definitions import (avg_vwap_last_n, jake_test,
                                         net_vwap_last_n)
from monte.machine import TradingMachine
from monte.machine_settings import MachineSettings
from monte.util import AlpacaAPIBundle


def main():
    alpaca_api = AlpacaAPIBundle()

    # TODO: Create pre-defined "configs" for the most commonly used TimeFrames that auto-sets the TimeFrame
    # and data_buffer_days.
    # TODO: Auto-calculate the data buffer size based on TimeFrame
    # TODO: Add logging
    # TODO: Buy and hold algorithm

    ms = MachineSettings(
        start_date="2016-09-09",
        end_date="2017-10-04",
        time_frame=TimeFrame(1, TimeFrameUnit.Hour),
        derived_columns={
            "net_l5": partial(net_vwap_last_n, n=5),
            "avg_l5": partial(avg_vwap_last_n, n=5),
            "jake": partial(jake_test, n=5)
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
