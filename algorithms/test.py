from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from functools import partial

import derived_columns.definitions as dcolumns
from monte.algorithm import Algorithm
from monte.api import AlpacaAPIBundle
from monte.machine_settings import MachineSettings
from monte.orders import Order, OrderType


class TestAlg(Algorithm):

    def __init__(self, alpaca_api: AlpacaAPIBundle,
                 machine_settings: MachineSettings, name: str, starting_cash: float) -> None:

        # Sets up instance variables and instantiates a Portfolio as self.portfolio
        super().__init__(alpaca_api, machine_settings, name, starting_cash)

        # self.symbols = ["AAPL", "GOOG", "IVV", "AMD", "NVDA", "INTC", "QQQ", "DIA", "AMZN", "TSLA", "UNH", "JNJ",
        #            "XOM", "V", "TSM", "META", "WMT", "JPM", "LLY", "SUN", "CVX", "PG", "HD", "MA", "BAC", "ABBV",
        #            "PFE", "KO", "NVO", "PEP", "MRK", "BABA", "COST", "AVGO", "TM", "ASML", "DIS", "ABT",
        #            "ORCL", "TMUS", "MCD", "AZN", "CSCO", "VZ", "WFC", "CRM", "TXN", "UPS", "NKE", "ROK"]

        self.symbols = ["AAPL", "GOOG", "IVV", "AMD", "NVDA"]

        # self.symbols = ["AAPL"]

    def get_derived_columns(self) -> dict[str, Callable]:
        derived_columns = {
            "net_l10": partial(dcolumns.net, n=10, col="vwap"),
            "avg_l10": partial(dcolumns.mean, n=10, col="vwap"),
            "std_dev_l10": partial(dcolumns.std_dev, n=10, col="vwap"),
            "pct_chg_l10": partial(dcolumns.percent_change, n=10, col="vwap")
        }

        return derived_columns

    def startup(self) -> None:
        for symbol in self.symbols:
            self.portfolio.watch(symbol)

        for symbol in self.symbols:
            self.portfolio.place_order(symbol, 10, OrderType.BUY)

    def train(self) -> None:
        pass

    def run_one_time_frame(self, current_datetime: datetime, processed_orders: list[Order]) -> None:
        for symbol in self.symbols:
            df = self.portfolio.get_testing_df(symbol)

            if df.iloc[-1].pct_chg_l10 < -1:
                self.portfolio.place_order(symbol, 1, OrderType.BUY)

            elif df.iloc[-1].pct_chg_l10 > 1:
                self.portfolio.place_order(symbol, 1, OrderType.SELL)

        print(f"{current_datetime.date()} {current_datetime.hour:02d}:{current_datetime.minute:02d} | "
              f"${round(self.portfolio.total_value(), 2):,.2f} | "
              f"{round(self.portfolio.current_return(), 3):+.3f}%")

    def cleanup(self) -> None:
        pass
