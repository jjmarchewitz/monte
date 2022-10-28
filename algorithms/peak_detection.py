from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from monte.algorithm import Algorithm
from monte.api import AlpacaAPIBundle
from monte.machine_settings import MachineSettings
from monte.orders import Order, OrderType
from monte.portfolio import Portfolio


class PeakDetection(Algorithm):

    def __init__(self, alpaca_api: AlpacaAPIBundle,
                 machine_settings: MachineSettings, name: str, starting_cash: float) -> None:

        # Sets up instance variables and instantiates a Portfolio as self.portfolio
        super().__init__(alpaca_api, machine_settings, name, starting_cash)

        self.symbol = "GME"

    def get_derived_columns(self) -> dict[str, Callable]:
        derived_columns = {}

        return derived_columns

    def startup(self) -> None:
        self.portfolio.watch(self.symbol)

        # Initial buy
        self.portfolio.place_order(self.symbol, 10, OrderType.BUY)

    def train(self) -> None:
        pass

    def run_one_time_frame(self, current_datetime: datetime, processed_orders: list[Order]):

        df = self.portfolio.get_testing_df(self.symbol)

        # Rules go here

        print(f"{current_datetime.date()} {current_datetime.hour}:{current_datetime.minute:02d} | "
              f"Total Value: ${self.portfolio.total_value():.2f}")

    def cleanup(self) -> None:
        pass
