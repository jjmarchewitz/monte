from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Protocol, runtime_checkable

from monte.api import AlpacaAPIBundle
from monte.machine_settings import MachineSettings
from monte.orders import Order
from monte.portfolio import Portfolio


class Algorithm(ABC):

    alpaca_api: AlpacaAPIBundle
    machine_settings: MachineSettings
    portfolio: Portfolio
    name: str

    def __init__(self, alpaca_api: AlpacaAPIBundle, machine_settings: MachineSettings, name: str,
                 starting_cash: float) -> None:
        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings
        self.name = name
        self.portfolio = Portfolio(self.alpaca_api, self.machine_settings, starting_cash)

    def get_portfolio(self) -> Portfolio:
        return self.portfolio

    def get_name(self) -> str:
        return self.name

    @abstractmethod
    def startup(self) -> None:
        ...

    @abstractmethod
    def run_one_time_frame(self, current_datetime: datetime, processed_orders: list[Order]) -> None:
        ...

    @abstractmethod
    def cleanup(self) -> None:
        ...
