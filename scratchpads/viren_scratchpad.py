from __future__ import annotations

from datetime import datetime

from alpaca_trade_api import TimeFrame, TimeFrameUnit

from algorithms.nearest_neighbors import NearestNeighbors
from monte.api import AlpacaAPIBundle
from monte.machine import TradingMachine
from monte.machine_settings import MachineSettings


def main():
    # Create an instance of the Alpaca API bundle
    alpaca_api = AlpacaAPIBundle()

    # Configure settings for the simulation
    ms = MachineSettings(
        start_date=datetime(2016, 3, 8),
        end_date=datetime(2022, 10, 23),
        training_data_percentage=0.1,
        time_frame=TimeFrame(1, TimeFrameUnit.Hour))

    # Create an instance of the trading machine
    trading_machine = TradingMachine(alpaca_api, ms)

    epsilon = 0.15
    # Create an instance of a trading algorithm
    algo1 = NearestNeighbors(alpaca_api, ms, "Test Alg",
                             10_000, ['GME'], (-epsilon, epsilon))

    # Add the trading algorithm to the trading machine
    trading_machine.add_algo_instance(algo1)

    # Run the trading machine
    trading_machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
