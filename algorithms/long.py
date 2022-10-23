from __future__ import annotations

from datetime import datetime

from monte.algorithm import Algorithm
from monte.api import AlpacaAPIBundle
from monte.machine_settings import MachineSettings
from monte.orders import Order, OrderType
from monte.portfolio import Portfolio


class Long(Algorithm):

    def __init__(self, alpaca_api: AlpacaAPIBundle,
                 machine_settings: MachineSettings, name: str, starting_cash: float) -> None:

        # Sets up instance variables and instantiates a Portfolio as self.portfolio
        super().__init__(alpaca_api, machine_settings, name, starting_cash)

        # symbols = ["AAPL", "GOOG", "IVV", "AMD", "NVDA", "INTC", "QQQ", "DIA", "AMZN", "TSLA", "UNH", "JNJ",
        #            "XOM", "V", "TSM", "META", "WMT", "JPM", "LLY", "SUN", "CVX", "PG", "HD", "MA", "BAC", "ABBV",
        #            "PFE", "KO", "NVO", "PEP", "MRK", "BABA", "COST", "AVGO", "TM", "ASML", "DIS", "ABT",
        #            "ORCL", "TMUS", "MCD", "AZN", "CSCO", "VZ", "WFC", "CRM", "TXN", "UPS", "NKE", "ROK"]

        self.symbols = ["AAPL", "GOOG", "IVV", "AMD", "NVDA"]

        # symbols = ["AAPL"]

    def get_portfolio(self) -> Portfolio:
        return self.portfolio

    def startup(self) -> None:
        for symbol in self.symbols:
            self.portfolio.watch(symbol)

        for symbol in self.symbols:
            self.portfolio.place_order(symbol, 10, OrderType.BUY)

    def train(self) -> None:
        pass

    def run_one_time_frame(self, current_datetime: datetime, processed_orders: list[Order]):

        for symbol in self.symbols:
            df = self.portfolio.get_testing_data(symbol)

            if (df.iloc[-1].avg_l5 - df.iloc[-1].vwap) > 0:
                self.portfolio.place_order(symbol, 1, OrderType.BUY)

            elif (df.iloc[-1].avg_l5 - df.iloc[-1].vwap) <= 0:
                self.portfolio.place_order(symbol, 1, OrderType.SELL)

        print(f"{current_datetime.date()} {current_datetime.hour}:{current_datetime.minute:02d} | "
              f"Total Value: ${self.portfolio.total_value():.2f}")

    def cleanup(self) -> None:
        pass
