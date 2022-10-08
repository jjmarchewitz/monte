from __future__ import annotations

import monte.machine_settings as machine_settings
import monte.portfolio as portfolio
import monte.util as util
from monte.algorithm import Algorithm


class TestAlg(Algorithm):

    alpaca_api: util.AlpacaAPIBundle
    machine_settings: machine_settings.MachineSettings

    def __init__(self, alpaca_api: util.AlpacaAPIBundle,
                 machine_settings: machine_settings.MachineSettings) -> None:
        super().__init__()

        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings

        self.portfolio = portfolio.Portfolio(self.alpaca_api, self.machine_settings)

        # symbols = ["AAPL", "GOOG", "IVV", "AMD", "NVDA", "INTC", "QQQ", "DIA", "AMZN", "TSLA", "UNH", "JNJ",
        #            "XOM", "V", "TSM", "META", "WMT", "JPM", "LLY", "SUN", "CVX", "PG", "HD", "MA", "BAC", "ABBV",
        #            "PFE", "KO", "NVO", "PEP", "MRK", "BABA", "COST", "AVGO", "TM", "ASML", "DIS", "ABT",
        #            "ORCL", "TMUS", "MCD", "AZN", "CSCO", "VZ", "WFC", "CRM", "TXN", "UPS", "NKE", "ROK"]

        self.symbols = ["AAPL", "GOOG", "IVV", "AMD", "NVDA"]

        # symbols = ["AAPL"]

    def startup(self) -> None:
        for symbol in self.symbols:
            self.portfolio.watch(symbol)

    def get_portfolio(self) -> portfolio.Portfolio:
        return self.portfolio

    def run_one_time_frame(self, processed_orders):
        pass
