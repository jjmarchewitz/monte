
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

    alpaca_api: AlpacaAPIBundle
    machine_settings: MachineSettings
    starting_cash: float
    cash: float
    name: str
    positions: dict[str, Position]
    am: AssetManager
    _order_queue: list[Order]
    _current_order_id_number: int

    def __init__(self, alpaca_api: AlpacaAPIBundle, machine_settings: MachineSettings,
                 starting_cash: float = 10000, name: str = "") -> None:
        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings
        self.starting_cash = starting_cash
        self.cash = starting_cash
        self.name = name
        self.positions = {}
        self._order_queue = []
        self._current_order_id_number = 0

    def __getitem__(self, key: str) -> Position:
        return self.positions[key]

    def items(self) -> ItemsView:
        """
        Returns an ItemsView instance for all of the Positions in the Portfolio.
        """
        return self.positions.items()

    def get_training_df(self, symbol) -> pd.DataFrame:
        """
        Returns the training dataframe for the given symbol.
        """
        return self.am.get_training_df(symbol)

    def get_testing_df(self, symbol) -> pd.DataFrame:
        """
        Returns the testing dataframe for the given symbol.
        """
        return self.am.get_testing_df(symbol)

    def latest_datetime(self) -> datetime:
        """
        Returns the most recent datetime in the simulation.
        """
        return self.am.latest_datetime()

    def latest_timestamp(self) -> str:
        """
        Returns the most recent timestamp in the simulation.
        """
        return self.am.latest_timestamp()

    def total_value(self) -> float:
        """
        Returns the total value of this Portfolio, including any unused cash and the value of all Positions.
        """
        total = self.cash
        total += sum(position.total_value() for position in self.positions.values())
        return total

    def current_return(self) -> float:
        """
        Returns the percent difference between the current total value of the Portfolio and the amount of
        starting cash.
        """
        return ((self.total_value() - self.starting_cash) / self.starting_cash) * 100

    def watch(self, symbol: str) -> None:
        """
        Start watching a new asset. Can only be called before the simulation runs.
        """
        self.am.watch_asset(symbol)

    def is_watching(self, symbol: str) -> bool:
        """
        Returns True if a symbol is already being watched, False otherwise.
        """
        return self.am.is_watching_asset(symbol)

    def unwatch(self, symbol: str) -> bool:
        """
        Removes a given asset from the AssetManager.
        """
        return self.am.unwatch_asset(symbol)

    def _delete_empty_positions(self) -> None:
        """
        Removes all Positions with a quantity of 0 from the Portfolio.
        """
        for symbol in list(self.positions.keys()):
            if self.positions[symbol].quantity == 0:
                self.positions.pop(symbol)

    def contains_position(self, symbol: str) -> bool:
        """
        Returns True if the given symbol corresponds to a Position in this Portfolio, False otherwise.
        """
        return symbol in self.positions.keys()

    def _create_position(self, symbol: str, initial_quantity: float) -> Position:
        """
        Helper function that creates new Positions with this Portfolio's AlpacaAPIBundle, MachineSettings,
        and AssetManager instances.
        """
        return Position(self.alpaca_api, self.machine_settings, self.am, symbol, initial_quantity)

    def place_order(self, symbol: str, quantity: int, order_type: OrderType = OrderType.BUY) -> Order:
        """
        Place a buy or sell order on this Portfolio. The order will try to be executed in one or more
        TimeFrames relative to the current one.
        """
        # Check that the order type passed in is a valid order type from the enum
        # OrderType
        if order_type not in OrderType:
            raise ValueError("Invalid order type.")

        # Set the order number and increment it for the next order
        order_num = self._current_order_id_number
        self._current_order_id_number += 1

        # Create a new order object with the correct attributes and append it to the
        # order queue
        new_order = Order(order_num, symbol, quantity, order_type, OrderStatus.PENDING)
        self._order_queue.append(new_order)

        return new_order

    def get_order(self, order_id: int) -> Union[Order, None]:
        """
        Returns an order that is currently in the order queue, given that order's ID.
        """
        result = None

        for order in self._order_queue:
            if order.id_number == order_id:
                result = order

        return result

    def cancel_order(self, order_id: int) -> tuple[bool, Union[Order, None]]:
        """
        Cancel an order that is currently on the order queue.
        """
        was_order_successfully_cancelled = False
        cancelled_order = None

        # Check through all of the orders and remove the one that matches the provided ID
        for index, order in enumerate(self._order_queue):
            if order.id_number == order_id:
                cancelled_order = self._order_queue.pop(index)
                cancelled_order.status = OrderStatus.CANCELLED
                was_order_successfully_cancelled = True
                break

        return (was_order_successfully_cancelled, cancelled_order)

    def process_pending_orders(self) -> list[Order]:
        """
        Process orders that are currently in the order queue. Returns any orders that were attempted and
        updates each order's status based on whether or not it was executed successfully.
        """
        list_of_processed_orders = []
        new_order_queue = []

        # Check through every order in the order queue
        for order in self._order_queue:

            # Check that the order type passed in is a valid order type from the enum
            # OrderType
            if order.order_type not in OrderType:
                raise ValueError("Invalid order type.")

            # Process the order based on buy/sell
            if order.order_type == OrderType.BUY:
                self._execute_buy_order(order)
            elif order.order_type == OrderType.SELL:
                self._execute_sell_order(order)

            # Add the order back to the queue if it is still pending
            if order.status == OrderStatus.PENDING:
                new_order_queue.append(order)

            # Add the order to the output list if it completed or failed
            else:
                list_of_processed_orders.append(order)

        self._order_queue = new_order_queue

        return list_of_processed_orders

    def _execute_buy_order(self, order: Order) -> None:
        """
        Attempts to execute a buy order.
        """
        order_cost = self.am.get_testing_df(order.symbol).iloc[-1].vwap * order.quantity

        # If the portfolio has insufficient funds to make the purchase, the order fails
        if self.cash < order_cost:
            order.status = OrderStatus.FAILED

        # Otherwise, execute the order
        else:
            # Take the money out of the portfolio's account
            self.cash -= order_cost

            # If there is an existing position for this symbol, add to its existing quantity
            if self.contains_position(order.symbol):
                self.positions[order.symbol].quantity += order.quantity

            # If no position exists for this symbol, create a new one
            else:
                self.positions[order.symbol] = self._create_position(order.symbol, order.quantity)

            # Update the order status
            order.status = OrderStatus.COMPLETED

    def _execute_sell_order(self, order: Order) -> None:
        """
        Attempts to execute a sell order.
        """
        # If the portfolio doesn't contain the symbol being sold, the order fails
        if not self.contains_position(order.symbol):
            order.status = OrderStatus.FAILED

        else:
            # If the portfolio has too little of the asset for this sell order, the order fails
            if self.positions[order.symbol].quantity < order.quantity:
                order.status = OrderStatus.FAILED

            # Otherwise, execute the order
            else:
                self.positions[order.symbol].quantity -= order.quantity
                self.cash += self.am.get_testing_df(order.symbol).iloc[-1].vwap * order.quantity
                order.status = OrderStatus.COMPLETED
