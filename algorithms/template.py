from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from functools import partial

import derived_columns.definitions as dcolumns
from monte.algorithm import Algorithm
from monte.api import AlpacaAPIBundle
from monte.machine_settings import MachineSettings
from monte.orders import Order


class Template(Algorithm):

    def __init__(self, alpaca_api: AlpacaAPIBundle,
                 machine_settings: MachineSettings, name: str, starting_cash: float) -> None:

        # Sets up instance variables and instantiates a Portfolio as self.portfolio
        super().__init__(alpaca_api, machine_settings, name, starting_cash)

    def get_derived_columns(self) -> dict[str, Callable]:
        derived_columns = {}

        return derived_columns

    def startup(self) -> None:
        ...

    def train(self) -> None:
        ...

    def run_one_time_frame(self, current_datetime: datetime, processed_orders: list[Order]) -> None:
        ...

    def cleanup(self) -> None:
        ...
