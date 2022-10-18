from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from monte.orders import Order
from monte.portfolio import Portfolio


class Algorithm(ABC):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_portfolio(self) -> Portfolio:
        pass

    @abstractmethod
    def startup(self) -> None:
        pass

    @abstractmethod
    def run_one_time_frame(self, current_datetime: datetime, processed_orders: list[Order]) -> None:
        pass

    @abstractmethod
    def cleanup(self) -> None:
        pass
