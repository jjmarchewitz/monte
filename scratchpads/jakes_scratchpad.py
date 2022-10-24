from __future__ import annotations

from datetime import datetime

from alpaca_trade_api import TimeFrame, TimeFrameUnit

from algorithms import test
from monte.api import AlpacaAPIBundle
from monte.machine import TradingMachine
from monte.machine_settings import MachineSettings


def main():
    alpaca_api = AlpacaAPIBundle()

    # TODO: Documentation
    # TODO: Add logging
    # TODO: Add graphing, should be able to compare two (or more) algorithms in live time
    # TODO: Move algos and scratchpads to a separate repo, publish monte on pypi
    # TODO: Move datetime to left and timestamp to right before derived columns

    ms = MachineSettings(
        start_date=datetime(2018, 3, 8),
        end_date=datetime(2018, 5, 15),
        training_data_percentage=0.5,
        time_frame=TimeFrame(1, TimeFrameUnit.Hour),
    )

    trading_machine = TradingMachine(alpaca_api, ms)

    algo1 = test.TestAlg(alpaca_api, ms, "Test Alg", 10_000)

    trading_machine.add_algo_instance(algo1)

    trading_machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
