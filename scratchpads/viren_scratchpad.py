from __future__ import annotations

from datetime import datetime

from alpaca_trade_api import TimeFrame, TimeFrameUnit

from algorithms.linear_regression import LinearRegressionAlgo
from algorithms.nearest_neighbors import NearestNeighbors
from monte.api import AlpacaAPIBundle
from monte.machine import TradingMachine
from monte.machine_settings import MachineSettings


def main():
    # Configure settings for the simulation
    ms = MachineSettings(
        alpaca_api=AlpacaAPIBundle(),
        start_date=datetime(2016, 3, 8),
        end_date=datetime(2016, 10, 23),
        training_data_percentage=0,
        time_frame=TimeFrame(1, TimeFrameUnit.Hour),
    )

    # Create an instance of the trading machine
    trading_machine = TradingMachine(ms)

    epsilon = 0.000001
    k = 1.5
    # Create an instance of a trading algorithm
    algo1 = NearestNeighbors(ms, "Nearest Neighbors Alg",
                             10_000, ['GME'], (-epsilon, epsilon), k)

    algo2 = LinearRegressionAlgo(ms, "Linear Regression Alg", 10_000,
                                 ['GME'], (-epsilon, epsilon), k)

    # Add the trading algorithm to the trading machine
    trading_machine.add_algo(algo1, algo2)

    # Run the trading machine
    trading_machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
