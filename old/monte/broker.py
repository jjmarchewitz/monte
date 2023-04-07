from typing import Union

import pandas as pd

from monte.asset_manager import AssetManager, CommonAssetData
from monte.machine_settings import MachineSettings
from monte.orders import Order, OrderStatus, OrderType
from monte.portfolio import Portfolio


class Asset():

    asset_manager: AssetManager
    symbol: str
    quantity: int

    def __init__(self, asset_manager: AssetManager, symbol: str):
        self.asset_manager = asset_manager
        self.symbol = symbol
        self.quantity = 0

    @property
    def price(self) -> float:
        """
        DOC:
        """
        return self.asset_manager.get_testing_df(self.symbol).iloc[-1].vwap

    @property
    def training_df(self) -> pd.DataFrame:
        """
        Returns the training dataframe for the Asset this Position represents.
        """
        return self.asset_manager.get_training_df(self.symbol)

    @property
    def testing_df(self) -> pd.DataFrame:
        """
        Returns the testing dataframe for the Asset this Position represents.
        """
        return self.asset_manager.get_testing_df(self.symbol)


class Broker():

    assets: dict[str, Asset]
    asset_manager: AssetManager
    machine_settings: MachineSettings
    portfolio: Portfolio
    _order_queue: list[Order]
    _current_order_id_number: int

    def __init__(self, machine_settings: MachineSettings, starting_cash: float = 10_000):
        self.machine_settings = machine_settings
        self.portfolio = Portfolio(machine_settings, starting_cash)
        self.assets = {}
        self._order_queue = []
        self._current_order_id_number = 0

    def set_asset_manager(self, asset_manager: AssetManager):
        """
        DOC:
        """
        if not isinstance(asset_manager, AssetManager):
            raise TypeError("Must pass an instance of AssetManager into set_asset_manager()")

        self.asset_manager = asset_manager
        self.portfolio.set_asset_manager(asset_manager)

    def watch(self, symbol):
        """
        DOC:
        """
        self.asset_manager.watch_asset(symbol)
        self.assets[symbol] = Asset(self.asset_manager, symbol)

    def is_watching(self, symbol) -> bool:
        """
        DOC:
        """
        return symbol in self.assets.keys()

    # def unwatch(self, symbol) -> bool:
    #     """
    #     DOC:
    #     """

    def place_order(self, symbol: str, quantity: float, order_type: OrderType) -> Order:
        """
        Place a buy or sell order on this Portfolio. The order will try to be executed in one or more
        TimeFrames relative to the current one.
        """
        # Check that the order type passed in is a valid order type from the enum
        # OrderType
        if order_type not in OrderType:
            raise ValueError("Invalid order type.")

        # Check that the quantity is valid
        if quantity <= 0:
            raise ValueError("Order quantities must be positive and non-zero.")

        order_num = self._current_order_id_number
        self._current_order_id_number += 1

        # Create a new order object with the correct attributes and append it to the
        # order queue
        new_order = Order(order_num, symbol, quantity,
                          order_type, OrderStatus.PENDING)
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

        for order in self._order_queue:

            # Check that the order type passed in is a valid order type from the enum OrderType
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

    def _execute_buy_order(self, order: Order):
        """
        Attempts to execute a buy order.
        """
        unit_price = self.asset_manager.get_testing_df(order.symbol).iloc[-1].vwap
        order_cost = unit_price * order.quantity

        # If the portfolio has insufficient funds to make the purchase, the order fails
        if self.portfolio.cash < order_cost:
            order.status = OrderStatus.FAILED
        # Otherwise, execute the order
        else:
            # Take the money out of the portfolio
            self.portfolio.cash -= order_cost

            # If there is an existing position for this symbol, add to its existing quantity
            if self.portfolio.contains_position(order.symbol):
                self.portfolio.positions[order.symbol].quantity += order.quantity
            # If no position exists for this symbol, create a new one
            else:
                new_position = self.portfolio._create_position(order.symbol, order.quantity)
                self.portfolio.positions[order.symbol] = new_position

            # Update the order status
            order.status = OrderStatus.COMPLETED

    def _execute_sell_order(self, order: Order):
        """
        Attempts to execute a sell order.
        """
        # If the portfolio doesn't contain the symbol being sold, the order fails
        if not self.portfolio.contains_position(order.symbol):
            order.status = OrderStatus.FAILED

        else:
            # If the portfolio has too little of the asset for this sell order, the order fails
            if self.portfolio.positions[order.symbol].quantity < order.quantity:
                order.status = OrderStatus.FAILED

            # Otherwise, execute the order
            else:
                self.portfolio.positions[order.symbol].quantity -= order.quantity

                unit_price = self.asset_manager.get_testing_df(order.symbol).iloc[-1].vwap
                self.portfolio.cash += unit_price * order.quantity
                order.status = OrderStatus.COMPLETED
