from __future__ import annotations

from datetime import datetime

from alpaca_trade_api import TimeFrame, TimeFrameUnit

from algorithms.benchmarks import BuyAndHold, BuyAndHoldSP500
from algorithms.linear_regression import LinearRegressionAlgo
from algorithms.naive_sharpe import NaiveSharpe
from algorithms.nearest_neighbors import NearestNeighbors
from algorithms.proportional_to_returns import ProportionalToReturns
from monte.api import AlpacaAPIBundle
from monte.machine import TradingMachine
from monte.machine_settings import MachineSettings


def main():

    # TODO: Run multiple TradingMachine instances simultaneously, on separate processes (?)
    #           - The purpose would be to run with multiple date ranges/time frames to compare results
    # TODO: Add argument validation across the backend.
    # TODO: Add logging (print statements).
    # TODO: Positions store executed order history
    # TODO: Add graphing, should be able to compare two (or more) algorithms in live time
    # TODO: Move algos and scratchpads to a separate repo, publish monte on pypi
    # TODO: Markdown documentation explaining the high-level concepts of this repo and some implementation
    # details.
    # TODO: Options trading

    ms = MachineSettings(
        alpaca_api=AlpacaAPIBundle(),
        start_date=datetime(2016, 1, 1),
        end_date=datetime(2016, 4, 12),
        training_data_percentage=0.2,
        time_frame=TimeFrame(1, TimeFrameUnit.Hour),
    )

    trading_machine = TradingMachine(ms)

    # symbols = [
    #     "AAPL", "GOOG", "IVV", "AMD", "NVDA", "INTC", "QQQ", "DIA", "AMZN", "TSLA", "UNH", "JNJ",
    #     "XOM", "V", "TSM", "META", "WMT", "JPM", "LLY", "SUN", "CVX", "PG", "HD", "MA", "BAC",
    #     "ABBV", "PFE", "KO", "NVO", "PEP", "MRK", "BABA", "COST", "AVGO", "TM", "ASML", "DIS",
    #     "ABT", "ORCL", "TMUS", "MCD", "AZN", "CSCO", "VZ", "WFC", "CRM", "TXN", "UPS", "NKE",
    #     "ROK"]

    symbols = ["AAPL", "GOOG"]
    # symbols = ["GME"]

    starting_cash = 10_000

    buy_and_hold = BuyAndHold(ms, "Buy and Hold - Symbols", starting_cash, symbols)
    trading_machine.add_algo(buy_and_hold)

    buy_and_hold_sp = BuyAndHoldSP500(ms, "Buy and Hold - S&P 500", starting_cash)
    trading_machine.add_algo(buy_and_hold_sp)

    prop_ret = ProportionalToReturns(ms, "Proportional to Returns", starting_cash, symbols)
    trading_machine.add_algo(prop_ret)

    n_sharpe = NaiveSharpe(ms, "Naive Sharpe", starting_cash, symbols)
    trading_machine.add_algo(n_sharpe)

    epsilon = 1e-5
    k = 1.5

    near_neighbors = NearestNeighbors(ms, "Nearest Neighbor", starting_cash, symbols, (-epsilon, epsilon), k)
    trading_machine.add_algo(near_neighbors)

    lin_reg = LinearRegressionAlgo(ms, "Linear Regression", starting_cash, symbols, (-epsilon, epsilon), k)
    trading_machine.add_algo(lin_reg)

    # TODO: Allow users to add statistics for post-run
    # trading_machine.add_run_statistic(func, *args, **kwargs)?

    trading_machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
