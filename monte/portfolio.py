
from __future__ import annotations

from typing import Union

import pandas as pd

from monte.api import AlpacaAPIBundle
from monte.asset_manager import AssetManager
from monte.machine_settings import MachineSettings
from monte.orders import Order, OrderStatus, OrderType
from monte.position import Position


class Portfolio():
    """
    A portfolio is simply a collection of individual positions.
    """

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
        """
        Constructor for the Portfolio class.

        Args:
            alpaca_api:
                A bundle of Alpaca APIs all created and authenticated with the keys in the repo's
                alpaca_config.json

            machine_settings:
                An instance of machine.MachineSettings that contains configuration for the current simulation.

            starting_cash:
                The starting cash that the portfolio will have before any orders are placed or any positions
                are held. Defaults to 10000.

            name:
                A string name to give the portfolio, purely for aesthetic/debugging purposes. Defaults to None.
        """

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

    def items(self):
        return self.positions.items()

    def get_data(self, symbol) -> Union[pd.DataFrame, None]:
        result = None

        if self.am.is_watching_asset(symbol):
            result = self.am[symbol]

        return result

    def delete_empty_positions(self) -> None:
        """DOC:"""
        for symbol in list(self.positions.keys()):
            if self.positions[symbol].quantity == 0:
                self.positions.pop(symbol)

    def contains_position(self, symbol: str) -> bool:
        """DOC:"""
        return symbol in self.positions.keys()

    def _create_position(self, symbol: str, initial_quantity: float) -> Position:
        """DOC:"""
        return Position(self.alpaca_api, self.machine_settings, self.am, symbol, initial_quantity)

    def total_value(self) -> float:
        """DOC:"""
        total = self.cash

        for position in self.positions.values():
            total += position.total_value()

        return total

    def current_return(self) -> float:
        """DOC:"""
        return ((self.total_value() - self.starting_cash) / self.starting_cash) * 100

    def watch(self, symbol: str) -> None:
        """DOC:"""
        self.am.watch_asset(symbol)

    def place_order(self, symbol: str, quantity: int, order_type: OrderType = OrderType.BUY) -> Order:
        """DOC:"""
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
        """DOC:"""
        result = None

        for order in self._order_queue:
            if order.id_number == order_id:
                result = order

        return result

    def cancel_order(self, order_id: int) -> tuple[bool, Union[Order, None]]:
        """DOC:"""
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
        """DOC:"""
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
        """DOC:"""
        order_cost = self.am[order.symbol].iloc[-1].vwap * order.quantity

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
        """DOC:"""

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
                self.cash += self.am[order.symbol].iloc[-1].vwap * order.quantity
                order.status = OrderStatus.COMPLETED

    def latest_datetime(self):
        """DOC:"""
        return self.am.latest_datetime()

    def latest_timestamp(self):
        """DOC:"""
        return self.am.latest_timestamp()

    def copy(self):
        raise NotImplementedError
