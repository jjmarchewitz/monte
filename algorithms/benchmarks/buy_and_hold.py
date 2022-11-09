from __future__ import annotations

from datetime import datetime

import derived_columns.definitions as dcolumns
from derived_columns import DerivedColumn
from monte import display
from monte.algorithm import Algorithm
from monte.machine_settings import MachineSettings
from monte.orders import Order, OrderType


class BuyAndHold(Algorithm):

    finished_buying: bool

    def __init__(
            self, machine_settings: MachineSettings, name: str,
            starting_cash: float, symbols: list[str]) -> None:

        # Sets up instance variables and instantiates a Portfolio as self.portfolio
        super().__init__(machine_settings, name, starting_cash, symbols)

        self.finished_buying = False

    def get_derived_columns(self) -> dict[str, DerivedColumn]:
        """
        Returns a dictionary containing the derived columns this algorithm needs to run.
        """
        # Add any derived columns to the dictionary.
        derived_columns = {}

        return derived_columns

    def startup(self) -> None:
        """
        Runs before the simulation starts (and before any training data is acquired).
        """
        # Watch all of your symbols from here
        for symbol in self.symbols:
            self.portfolio.watch(symbol)

    def train(self) -> None:
        """
        Runs right before the end of the training phase of the simulation (after the training data is
        acquired). Train any models here.
        """
        # Training code, called once
        ...

    def run_one_time_frame(self, current_datetime: datetime, processed_orders: list[Order]) -> None:
        """
        Runs on every time frame during the testing phase of the simulation. This is the main body of the
        algorithm.
        """

        if not self.finished_buying:
            # Determine if the portfolio has enough money to buy any more shares
            can_buy_more_shares = False
            for _, position in self.portfolio.positions.items():
                if self.portfolio.cash > position.price:
                    can_buy_more_shares = True
                    break

            # If we can buy more shares, place an order of 1 share for all symbols in self.symbols
            if can_buy_more_shares:
                for symbol in self.symbols:
                    self.portfolio.place_order(symbol, 1, OrderType.BUY)

            # If we can't buy more shares, prevent the algo from even attempting to
            else:
                self.finished_buying = True

        display.print_total_value(self.name, self.portfolio, current_datetime)

    def cleanup(self) -> None:
        """
        Runs after the end of the testing phase of the simulation. Run any needed post-simulation code here.
        """
        # Runs once the simulation is over and the last TimeFrame has been run.
        ...
