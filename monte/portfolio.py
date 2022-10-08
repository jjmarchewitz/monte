
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Union

import monte.asset_manager as asset_manager
import monte.machine_settings as machine_settings
import monte.position as position
import monte.util as util


class OrderType(Enum):
    """
    An Enum holding a value for an order either being a buy or a sell order.
    """
    BUY = 1
    SELL = 2


class OrderStatus(Enum):
    """
    An Enum holding a value for the status of an order (pending, completed, failed).
    """
    PENDING = 1
    COMPLETED = 2
    FAILED = 3
    CANCELLED = 4


@dataclass
class Order():
    """
    A dataclass that represents a market order.
    """
    id_number: int
    symbol: str
    quantity: float
    order_type: OrderType
    status: OrderStatus


class Portfolio():
    """
    A portfolio is simply a collection of individual positions.
    """

    alpaca_api: util.AlpacaAPIBundle
    machine_settings: machine_settings.MachineSettings
    cash: int
    name: str
    positions: dict[str, position.Position]
    am: asset_manager.AssetManager
    _order_queue: list[Order]
    _current_order_id_number: int

    def __init__(self, alpaca_api: util.AlpacaAPIBundle, machine_settings: machine_settings.MachineSettings,
                 starting_cash: int = 10000, name: str = None) -> None:
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
        self.cash = starting_cash
        self.name = name
        self.positions = {}
        self.am = None
        self._order_queue = []
        self._current_order_id_number = 0

    def __getitem__(self, key: str) -> position.Position:
        return self.positions[key]

    def _delete_empty_positions(self) -> None:
        """DOC:"""
        for symbol in list(self.positions.keys()):
            if self.positions[symbol].quantity == 0:
                self.positions.pop(symbol)

    def contains_position(self, symbol: str) -> bool:
        """DOC:"""
        return symbol in self.positions.keys()

    def total_value(self) -> float:
        """DOC:"""
        total = self.cash

        for position in self.positions.values():
            total += position.total_value()

        return total

    def watch(self, symbol) -> None:
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
                processed_order = self._execute_buy_order(order)
            elif order.order_type == OrderType.SELL:
                processed_order = self._execute_sell_order(order)

            if processed_order.status == OrderStatus.PENDING:
                new_order_queue.append(order)
            else:
                list_of_processed_orders.append(order)

        self._order_queue = new_order_queue

        return list_of_processed_orders

    def _execute_buy_order(self, order):
        breakpoint()
        pass

    def _execute_sell_order(self, order):
        breakpoint()
        pass

    def copy(self):
        pass
