from __future__ import annotations

from datetime import datetime

from alpaca_trade_api import TimeFrame, TimeFrameUnit

from algorithms.proportional_to_returns import ProportionalToReturns
from monte.api import AlpacaAPIBundle
from monte.machine import TradingMachine
from monte.machine_settings import MachineSettings


def main():
    # Configure settings for the simulation
    ms = MachineSettings(
        alpaca_api=AlpacaAPIBundle(),
        start_date=datetime(2022, 4, 1),
        end_date=datetime(2022, 10, 23),
        training_data_percentage=0,
        time_frame=TimeFrame(1, TimeFrameUnit.Hour))

    # Create an instance of the trading machine
    trading_machine = TradingMachine(ms)

    # Define a list of symbols to trade on
    symbols = ["GOOG"]  # to the moon!

    # Define the starting cash that the algos will have
    starting_cash = 10_000

    # Create an instance of a trading algorithm
    algo1 = ProportionalToReturns(ms, "Proportional to Returns", starting_cash, symbols)

    # Add the trading algorithm to the trading machine
    trading_machine.add_algo(algo1)

    # Run the trading machine
    trading_machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
