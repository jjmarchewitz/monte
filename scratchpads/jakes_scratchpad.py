from __future__ import annotations

from datetime import datetime

from alpaca_trade_api import TimeFrame, TimeFrameUnit

from algorithms import test
from monte.api import AlpacaAPIBundle
from monte.machine import TradingMachine
from monte.machine_settings import MachineSettings


def main():
    alpaca_api = AlpacaAPIBundle()

    # TODO: Add logging (print statements).
    # TODO: Portfolios store executed order history
    # TODO: Add graphing, should be able to compare two (or more) algorithms in live time
    # TODO: Move algos and scratchpads to a separate repo, publish monte on pypi
    # TODO: Markdown documentation explaining the high-level concepts of this repo and some implementation
    # details.
    # TODO: Options trading
    # TODO: Broker object?

    ms = MachineSettings(
        start_date=datetime(2016, 3, 8),
        end_date=datetime(2022, 10, 23),
        training_data_percentage=0,
        time_frame=TimeFrame(1, TimeFrameUnit.Hour),
    )

    trading_machine = TradingMachine(alpaca_api, ms)

    symbols = [
        "AAPL", "GOOG", "IVV", "AMD", "NVDA", "INTC", "QQQ", "DIA", "AMZN", "TSLA", "UNH", "JNJ",
        "XOM", "V", "TSM", "META", "WMT", "JPM", "LLY", "SUN", "CVX", "PG", "HD", "MA", "BAC",
        "ABBV", "PFE", "KO", "NVO", "PEP", "MRK", "BABA", "COST", "AVGO", "TM", "ASML", "DIS",
        "ABT", "ORCL", "TMUS", "MCD", "AZN", "CSCO", "VZ", "WFC", "CRM", "TXN", "UPS", "NKE",
        "ROK"]

    # symbols = ["GME"]

    algo1 = test.TestAlg(alpaca_api, ms, "Test Alg", 10_000, symbols)
    algo2 = test.TestAlg(alpaca_api, ms, "Test Alg2", 10_000, symbols)

    trading_machine.add_algos(algo1, algo2)

    trading_machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
