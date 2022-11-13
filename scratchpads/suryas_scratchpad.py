from __future__ import annotations

from datetime import datetime

from alpaca_trade_api import TimeFrame, TimeFrameUnit

from algorithms.naive_sharpe import NaiveSharpe
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

    symbols = [
        "AAPL", "GOOG", "IVV", "AMD", "NVDA", "INTC", "QQQ", "DIA", "AMZN", "TSLA", "UNH", "JNJ",
        "XOM", "V", "TSM", "META", "WMT", "JPM", "LLY", "SUN", "CVX", "PG", "HD", "MA", "BAC",
        "ABBV", "PFE", "KO", "NVO", "PEP", "MRK", "BABA", "COST", "AVGO", "TM", "ASML", "DIS",
        "ABT", "ORCL", "TMUS", "MCD", "AZN", "CSCO", "VZ", "WFC", "CRM", "TXN", "UPS", "NKE",
        "ROK"
    ]

    # Create an instance of the trading machine
    trading_machine = TradingMachine(ms)

    # Create an instance of a trading algorithm
    algo1 = NaiveSharpe(ms, "Naive Sharpe... did I do it??", 10_000, symbols)

    # Add the trading algorithm to the trading machine
    trading_machine.add_algo(algo1)
    # ¡¡¡¡¡
    #
    # Hey surya, I added the ability to add multiple algos to the trading machine at once.
    # Ex: trading_machine.add_algo(algo1, algo2, algo3)
    #
    # !!!!!

    # Run the trading machine
    trading_machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
