from __future__ import annotations

from datetime import datetime

from alpaca_trade_api import TimeFrame, TimeFrameUnit

from algorithms.benchmarks.buy_and_hold import BuyAndHold
from algorithms.benchmarks.buy_and_hold_sp import BuyAndHoldSP500
from algorithms.proportional_to_returns import ProportionalToReturns
from monte.api import AlpacaAPIBundle
from monte.machine import TradingMachine
from monte.machine_settings import MachineSettings


def main():

    # TODO: Broker object
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
        start_date=datetime(2016, 3, 8),
        end_date=datetime(2016, 11, 7),
        training_data_percentage=0,
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

    buy_and_hold = BuyAndHold(ms, "B&H", starting_cash, symbols)
    trading_machine.add_algo(buy_and_hold)

    buy_and_hold_sp = BuyAndHoldSP500(ms, "S&P", starting_cash)
    trading_machine.add_algo(buy_and_hold_sp)

    prop_ret = ProportionalToReturns(ms, "PtR", starting_cash, symbols)
    trading_machine.add_algo(prop_ret)

    trading_machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
