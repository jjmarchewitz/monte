from __future__ import annotations

from datetime import datetime

from alpaca_trade_api import TimeFrame, TimeFrameUnit

from algorithms import naive_sharpe
from monte.api import AlpacaAPIBundle
from monte.machine import TradingMachine
from monte.machine_settings import MachineSettings


def main():
    # Create an instance of the Alpaca API bundle
    alpaca_api = AlpacaAPIBundle()

    # Configure settings for the simulation
    ms = MachineSettings(
        start_date=datetime(2016, 3, 8),
        end_date=datetime(2016, 5, 8),
        training_data_percentage=0.0,
        time_frame=TimeFrame(1, TimeFrameUnit.Day))

    symbols = [
        "AAPL", "GOOG", "IVV", "AMD", "NVDA", "INTC", "QQQ", "DIA", "AMZN", "TSLA", "UNH", "JNJ",
        "XOM", "V", "TSM", "META", "WMT", "JPM", "LLY", "SUN", "CVX", "PG", "HD", "MA", "BAC",
        "ABBV", "PFE", "KO", "NVO", "PEP", "MRK", "BABA", "COST", "AVGO", "TM", "ASML", "DIS",
        "ABT", "ORCL", "TMUS", "MCD", "AZN", "CSCO", "VZ", "WFC", "CRM", "TXN", "UPS", "NKE",
        "ROK"]

    # Create an instance of the trading machine
    trading_machine = TradingMachine(alpaca_api, ms)

    # Create an instance of a trading algorithm
    algo1 = naive_sharpe.NaiveSharpe(
        alpaca_api, ms, "Naive Sharpe... did I do it??", 10_000, symbols)

    # Add the trading algorithm to the trading machine
    trading_machine.add_algo_instance(algo1)

    # Run the trading machine
    trading_machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
