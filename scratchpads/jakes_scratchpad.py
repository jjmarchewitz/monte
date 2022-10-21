from __future__ import annotations

from datetime import datetime
from functools import partial

import pytz
from alpaca_trade_api import TimeFrame, TimeFrameUnit

import derived_columns.definitions as dcolumns
from algorithms import test
from monte.machine import TradingMachine
from monte.machine_settings import MachineSettings
from monte.util import AlpacaAPIBundle


def main():
    alpaca_api = AlpacaAPIBundle()

    # TODO: Add optional "training data" section
    # TODO: Documentation
    # TODO: Add logging
    # TODO: Add graphing, should be able to compare two (or more) algorithms in live time
    # TODO: Move algos and scratchpads to a separate repo, publish monte on pypi

    ms = MachineSettings(
        start_date=datetime(2016, 6, 20),
        end_date=datetime(2019, 6, 25),
        # start_date=datetime(2022, 3, 8),
        # end_date=datetime(2022, 3, 15),
        time_frame=TimeFrame(1, TimeFrameUnit.Minute),
        derived_columns={
            "net_l10": partial(dcolumns.net_over_last_n, col="vwap", n=10),
            "avg_l10": partial(dcolumns.avg_over_last_n, col="vwap", n=10),
            "std_dev_l10": partial(dcolumns.std_dev_over_last_n, col="vwap", n=10)
        },
        max_rows_in_df=500,
        start_buffer_days=5,  # TradingDays
        data_buffer_days=10,  # TradingDays
    )

    trading_machine = TradingMachine(alpaca_api, ms)

    algo1 = test.TestAlg(alpaca_api, ms)

    trading_machine.add_algo_instance(algo1)

    trading_machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
