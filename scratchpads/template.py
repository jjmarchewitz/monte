from __future__ import annotations

from datetime import datetime

from alpaca_trade_api import TimeFrame, TimeFrameUnit

from algorithms import proportional_to_returns
from monte.api import AlpacaAPIBundle
from monte.machine import TradingMachine
from monte.machine_settings import MachineSettings


def main():
    # Configure settings for the simulation
    ms = MachineSettings(
        alpaca_api=AlpacaAPIBundle(),
        start_date=datetime(2016, 3, 8),
        end_date=datetime(2022, 10, 23),
        training_data_percentage=0.1,
        time_frame=TimeFrame(1, TimeFrameUnit.Hour))

    # Create an instance of the trading machine
    trading_machine = TradingMachine(ms)

    # Define a list of symbols to trade on
    symbols = ["AAPL", "GOOG"]  # to the moon!

    # Create an instance of a trading algorithm
    algo1 = proportional_to_returns.ProportionalToReturns(ms, "Test Alg", 10_000, symbols)

    # Add the trading algorithm to the trading machine
    trading_machine.add_algo(algo1)

    # Run the trading machine
    trading_machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
