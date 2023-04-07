from __future__ import annotations

from datetime import datetime

from alpaca_trade_api import TimeFrame, TimeFrameUnit

from algorithms.benchmarks import BuyAndHold, BuyAndHoldSP500
from algorithms.linear_regression import LinearRegressionAlgo
from algorithms.nearest_neighbors import NearestNeighbors
from monte.api import AlpacaAPIBundle
from monte.machine import TradingMachine
from monte.machine_settings import MachineSettings


def main():
    # Configure settings for the simulation
    ms = MachineSettings(
        alpaca_api=AlpacaAPIBundle(),
        start_date=datetime(2016, 2, 1),
        end_date=datetime(2022, 11, 13),
        training_data_percentage=0,
        time_frame=TimeFrame(1, TimeFrameUnit.Hour))

    # Create an instance of the trading machine
    trading_machine = TradingMachine(ms)

    # Define a list of symbols to trade on
    symbols = ["AAPL", "GOOG", "IVV", "QQQ", "DIA"]  # to the moon!

    # Define the starting cash that the algos will have
    starting_cash = 100_000

    # Construct a bunch of algos
    for epsilon_mantissa in (1, 2.5, 5, 7.5):
        for epsilon_exponent in range(8, -9, -1):
            for k_mantissa in range(1, 10):
                for k_exponent in range(3, -4, -1):
                    for algo_class in (LinearRegressionAlgo, NearestNeighbors):

                        # mantissa * (10 ^ exponent)
                        epsilon = epsilon_mantissa * (10 ** epsilon_exponent)
                        k = k_mantissa * (10 ** k_exponent)

                        # Get the class name as a string (i.e. 'LinearRegressionAlgo')
                        algo_class_name = algo_class.__name__

                        # Use the upper-case letters of the class to act as a shorthand (i.e. 'LRA')
                        algo_class_shorthand = "".join([c for c in algo_class_name if c.isupper()])

                        # Give the algo a name, use scientific notation to display the epsilon and k values
                        algo_nickname = f"{algo_class_shorthand}; E={epsilon:.2e}; K={k:.2e}"

                        # Instantiate the algorithm
                        algo = algo_class(
                            ms, algo_nickname, starting_cash, symbols, (-epsilon, epsilon), k)

                        # Add the algo to the trading machine
                        trading_machine.add_algo(algo)

    buy_and_hold = BuyAndHold(ms, "Buy and Hold - Symbols", starting_cash, symbols)
    trading_machine.add_algo(buy_and_hold)

    buy_and_hold_sp = BuyAndHoldSP500(ms, "Buy and Hold - S&P 500", starting_cash)
    trading_machine.add_algo(buy_and_hold_sp)

    # Run the trading machine
    trading_machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
