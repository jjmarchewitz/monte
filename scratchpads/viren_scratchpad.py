from __future__ import annotations

from datetime import datetime

from alpaca_trade_api import TimeFrame, TimeFrameUnit

from algorithms.nearest_neighbors import NearestNeighbors
from monte.api import AlpacaAPIBundle
from monte.machine import TradingMachine
from monte.machine_settings import MachineSettings
from algorithms.linear_regression import LinearRegressionAlgo


def main():
    # Create an instance of the Alpaca API bundle
    alpaca_api = AlpacaAPIBundle()

    # Configure settings for the simulation
    ms = MachineSettings(
        start_date=datetime(2021, 10, 16),
        end_date=datetime(2021, 10, 30),
        training_data_percentage=0.0,
        time_frame=TimeFrame(1, TimeFrameUnit.Minute))

    # Create an instance of the trading machine
    trading_machine = TradingMachine(alpaca_api, ms)

    epsilon = 0.000001
    k = 1.5
    # Create an instance of a trading algorithm
    algo1 = NearestNeighbors(alpaca_api, ms, "Nearest Neighbors Alg",
                             10_000, ['GME'], (-epsilon, epsilon), k)

    algo2 = LinearRegressionAlgo(alpaca_api, ms, "Linear Regression Alg", 10_000,
                                 ['GME'], (-epsilon, epsilon), k)

    # Add the trading algorithm to the trading machine
    trading_machine.add_algo_instance(algo2)

    # Run the trading machine
    trading_machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
