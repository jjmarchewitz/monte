from __future__ import annotations

from datetime import datetime

from alpaca_trade_api import TimeFrame, TimeFrameUnit
from algorithms.proportional_to_returns import ProportionalToReturns
from algorithms.linear_regression import LinearRegressionAlgo
from algorithms.nearest_neighbors import NearestNeighbors
from monte.api import AlpacaAPIBundle
from monte.machine import TradingMachine
from monte.machine_settings import MachineSettings
from algorithms.benchmarks.buy_and_hold import BuyAndHold
from algorithms.benchmarks.buy_and_hold_sp import BuyAndHoldSP500


def main():
    # Configure settings for the simulation
    ms = MachineSettings(
        alpaca_api=AlpacaAPIBundle(),
        start_date=datetime(2016, 10, 16),
        end_date=datetime(2016, 10, 23),
        training_data_percentage=0.70,
        time_frame=TimeFrame(1, TimeFrameUnit.Minute)

    )

    # Create an instance of the trading machine
    trading_machine = TradingMachine(ms)

    epsilon = 0.00002
    k = 2
    # Create an instance of a trading algorithm
    nearest_neighbors = NearestNeighbors(ms, "Nearest Neighbors Alg",
                                         10_000, ['AAPL'], (-epsilon, epsilon), k)

    linear_regression = LinearRegressionAlgo(ms, "Linear Regression Alg", 10_000,
                                             ['AAPL'], (-epsilon, epsilon), k)

    buy_and_hold_sp = BuyAndHoldSP500(ms, "S&P", 10_000)
    buy_and_hold = BuyAndHold(ms, "B&H", 10_000, ['AAPL'])
    prop_ret = ProportionalToReturns(ms, "PtR", 10_000, ['AAPL'])

    trading_machine.add_algo(buy_and_hold_sp, prop_ret,
                             buy_and_hold, nearest_neighbors, linear_regression)
    # Add the trading algorithm to the trading machine
    # trading_machine.add_algo(algo1)

    # Run the trading machine
    trading_machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
