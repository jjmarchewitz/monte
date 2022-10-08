from __future__ import annotations

from monte import machine_settings, portfolio, util
from monte.algorithm import Algorithm
from monte.orders import Order, OrderType


class TestAlg(Algorithm):

    alpaca_api: util.AlpacaAPIBundle
    machine_settings: machine_settings.MachineSettings

    def __init__(self, alpaca_api: util.AlpacaAPIBundle,
                 machine_settings: machine_settings.MachineSettings) -> None:

        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings

        self.portfolio = portfolio.Portfolio(self.alpaca_api, self.machine_settings)

        # symbols = ["AAPL", "GOOG", "IVV", "AMD", "NVDA", "INTC", "QQQ", "DIA", "AMZN", "TSLA", "UNH", "JNJ",
        #            "XOM", "V", "TSM", "META", "WMT", "JPM", "LLY", "SUN", "CVX", "PG", "HD", "MA", "BAC", "ABBV",
        #            "PFE", "KO", "NVO", "PEP", "MRK", "BABA", "COST", "AVGO", "TM", "ASML", "DIS", "ABT",
        #            "ORCL", "TMUS", "MCD", "AZN", "CSCO", "VZ", "WFC", "CRM", "TXN", "UPS", "NKE", "ROK"]

        self.symbols = ["AAPL", "GOOG", "IVV", "AMD", "NVDA"]

        # symbols = ["AAPL"]

    def get_portfolio(self) -> portfolio.Portfolio:
        return self.portfolio

    def startup(self) -> None:
        for symbol in self.symbols:
            self.portfolio.watch(symbol)

        for symbol in self.symbols:
            self.portfolio.place_order(symbol, 10, OrderType.BUY)

    def run_one_time_frame(self, processed_orders: list[Order]):

        for symbol in self.symbols:
            self.portfolio.place_order(symbol, 1, OrderType.SELL)
