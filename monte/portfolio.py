from __future__ import annotations

from collections.abc import ItemsView
from datetime import datetime
from typing import Union

import pandas as pd

from monte.api import AlpacaAPIBundle
from monte.asset_manager import AssetManager
from monte.machine_settings import MachineSettings
from monte.orders import Order, OrderStatus, OrderType
from monte.position import Position


class Portfolio():
    """
    A portfolio is simply a collection of individual positions. This portfolio class acts as an algorithm's
    interface with all of its positions and all of their training/testing data.
    """

    # TODO: Dataframe that stores the returns at each time delta, with timestamps.

    machine_settings: MachineSettings
    asset_manager: AssetManager
    starting_cash: float
    cash: float
    positions: dict[str, Position]

    def __init__(self, machine_settings: MachineSettings, starting_cash: float = 10000):
        self.machine_settings = machine_settings
        self.starting_cash = starting_cash
        self.cash = starting_cash
        self.positions = {}

    def __getitem__(self, key: str) -> Position:
        return self.positions[key]

    def set_asset_manager(self, am: AssetManager) -> None:
        """
        DOC:
        """
        self.asset_manager = am

    def contains_position(self, symbol: str) -> bool:
        """
        Returns True if the given symbol corresponds to a Position in this Portfolio, False otherwise.
        """
        return symbol in self.positions.keys()

    def items(self) -> ItemsView:
        """
        Returns an ItemsView instance for all of the Positions in the Portfolio.
        """
        return self.positions.items()

    @property
    def total_value(self) -> float:
        """
        Returns the total value of this Portfolio, including any unused cash and the value of all Positions.
        """
        total = self.cash
        total += sum(position.total_value for position in self.positions.values())
        return total

    @property
    def current_return(self) -> float:
        """
        Returns the percent difference between the current total value of the Portfolio and the amount of
        starting cash.
        """
        return ((self.total_value - self.starting_cash) / self.starting_cash) * 100

    def _create_position(self, symbol: str, initial_quantity: float) -> Position:
        """
        Helper function that creates new Positions with this Portfolio's AlpacaAPIBundle, MachineSettings,
        and AssetManager instances.
        """
        return Position(self.machine_settings, self.asset_manager, symbol, initial_quantity)

    def _delete_empty_positions(self):
        """
        Removes all Positions with a quantity of 0 from the Portfolio.
        """
        for symbol in list(self.positions.keys()):
            if self.positions[symbol].quantity == 0:
                self.positions.pop(symbol)
