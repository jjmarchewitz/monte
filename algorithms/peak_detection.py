from __future__ import annotations

from datetime import datetime

from monte.algorithm import Algorithm
from monte.machine_settings import MachineSettings
from monte.orders import Order, OrderType
from monte.portfolio import Portfolio
from monte.util import AlpacaAPIBundle


class PeakDetection(Algorithm):

    alpaca_api: AlpacaAPIBundle
    machine_settings: MachineSettings
    portfolio: Portfolio

    def __init__(self, alpaca_api: AlpacaAPIBundle,
                 machine_settings: MachineSettings) -> None:

        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings

        self.portfolio = Portfolio(self.alpaca_api, self.machine_settings, starting_cash=10_000)

        self.symbol = "GME"

    def get_portfolio(self) -> Portfolio:
        return self.portfolio

    def startup(self) -> None:
        self.portfolio.watch(self.symbol)

        # Initial buy
        self.portfolio.place_order(self.symbol, 10, OrderType.BUY)

    def run_one_time_frame(self, current_datetime: datetime, processed_orders: list[Order]):

        df = self.portfolio.get_data(self.symbol)

        # Rules go here

        print(f"{current_datetime.date()} {current_datetime.hour}:{current_datetime.minute:02d} | "
              f"Total Value: ${self.portfolio.total_value():.2f}")

    def cleanup(self) -> None:
        pass
