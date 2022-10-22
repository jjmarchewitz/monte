from __future__ import annotations

from datetime import datetime
from functools import partial

import pytz
from alpaca_trade_api import TimeFrame, TimeFrameUnit

import derived_columns.definitions as dcolumns
from algorithms import test
from monte.api import AlpacaAPIBundle
from monte.machine import TradingMachine
from monte.machine_settings import MachineSettings


def main():
    alpaca_api = AlpacaAPIBundle()

    # TODO: Add optional "training data" section. Add new training_data_percentage (float between
    # 0 and 1), where the training data is the first chunk of the date range provided by
    # (start_date, end_date)
    # TODO: Improve the interface of getting data
    # TODO: Documentation
    # TODO: Add logging
    # TODO: Add graphing, should be able to compare two (or more) algorithms in live time
    # TODO: Move algos and scratchpads to a separate repo, publish monte on pypi

    ms = MachineSettings(
        start_date=datetime(2018, 3, 8),
        end_date=datetime(2018, 3, 15),
        time_frame=TimeFrame(1, TimeFrameUnit.Minute),
        derived_columns={
            "net_l10": partial(dcolumns.net_over, col="vwap", n=10),
            "avg_l10": partial(dcolumns.avg_over, col="vwap", n=10),
            "std_dev_l10": partial(dcolumns.std_dev, col="vwap", n=10)
        },
        max_rows_in_test_df=20,
    )

    trading_machine = TradingMachine(alpaca_api, ms)

    algo1 = test.TestAlg(alpaca_api, ms, "Test Alg", 10_000)

    trading_machine.add_algo_instance(algo1)

    trading_machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
