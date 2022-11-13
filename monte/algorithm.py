from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from derived_columns import DerivedColumn
from monte.api import AlpacaAPIBundle
from monte.broker import Broker
from monte.machine_settings import MachineSettings
from monte.orders import Order
from monte.portfolio import Portfolio


class Algorithm(ABC):
    """
    Abstract base class for trading algorithms used with the monte backtester.
    """

    def __init__(self, machine_settings: MachineSettings, name: str,
                 starting_cash: float, symbols: list[str]):
        ...

    @abstractmethod
    def get_name(self) -> str:
        """
        Returns the name of this instance, used to help identify this instance in print statements.
        """
        ...

    @abstractmethod
    def get_broker(self) -> Broker:
        """
        Returns the broker instance for this algorithm.
        """
        ...

    @abstractmethod
    def get_derived_columns(self) -> dict[str, DerivedColumn]:
        """
        Returns a dictionary of derived columns this algorithm needs in order to run.
        """
        ...

    @abstractmethod
    def startup(self):
        """
        This method is called when the trading machine starts up and can contain any behavior that
        needs to happen right on startup.
        """
        ...

    @abstractmethod
    def train(self):
        """
        This method is called when the trading machine finishes collecting the training data and is about
        to transition into adding the testing data to the testing dataframes one row at a time.
        """
        ...

    @abstractmethod
    def run_one_time_frame(self, current_datetime: datetime, processed_orders: list[Order]):
        """
        This method is called once on every time_frame during the testing data phase. The current datetime
        of the simulation is passed in along with a list of orders that were completed this time_frame.
        """
        ...

    @abstractmethod
    def cleanup(self):
        """
        This method is called when the trading machine has finished and can contain any behavior that needs
        to happen at the end of the simulation.
        """
        ...
