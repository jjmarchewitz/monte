"""
A Portfolio is meant to represent a collection of individual Positions.
"""

from algo_pg.position import Position
from algo_pg.util import get_price_from_bar
from dataclasses import dataclass
from enum import Enum


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


@dataclass
class Order():
    """
    A dataclass that represents a market order.
    """
    id_number: int
    symbol: str
    quantity: float
    order_type: OrderType
    # TODO: creation_time: str


class Portfolio():
    """
    A portfolio is simply a collection of individual positions.
    """

    def __init__(self, alpaca_api, data_settings, starting_cash=10000, name=None):
        """
        Constructor for the Portfolio class.

        Args:
            alpaca_api: A bundle of Alpaca APIs all created and authenticated with the keys
                in the repo's alpaca.config.
            data_settings: An instance of the DataSettings dataclass.
            starting_cash: The starting cash that the portfolio will have before any
                orders are placed or any positions are held. Defaults to 10000.
            name: A string name to give the portfolio, purely for aesthetic/debugging
                purposes. Defaults to None.
        """
        # Bundled alpaca API dataclass
        self.alpaca_api = alpaca_api

        # Trading Machine settings dataclass
        self.data_settings = data_settings

        self.name = name if name is not None else "Unnamed"
        self.positions = []
        self.cash = starting_cash

        self.time_of_last_price_gen_increment = None
        self._current_order_id_number = 1
        self._order_queue = []

        self._increment_count = 0

        # This exists for timing and synchronization purposes, this is a reference position
        # that does count towards the value of the portfolio
        self._reference_position = Position(
            self.alpaca_api, self.data_settings, "SPY", 1.0)

    def create_new_position(self, symbol, initial_quantity):
        """
        Create a new Position from the provided args and add it to the Portfolio.

        Args:
            symbol: A string for the market symbol of this position (i.e. "AAPL" or "GOOG").
            initial_quantity: The quantity of this asset that should be held when this
                instance is finished being constructed.
        """
        new_position = Position(self.alpaca_api, self.data_settings,
                                symbol, initial_quantity)
        self.add_existing_position(new_position)

    def add_existing_position(self, new_position):
        """
        Adds an initialized Position object to the Portfolio.

        Args:
            new_position: The incoming and already initialized Position object to be added
                to the Portfolio.

        Raises:
            ValueError: When there is a Position object for the same symbol as a
                Position already in the Portfolio.
            TypeError: When new_position is not of type machine.position.Position.
        """
        # Check that the new_position is a Position object
        if type(new_position) is not Position:
            raise TypeError(
                "The object passed is not of type machine.position.Position")

        # Check that there is not already a position with this symbol in this portfolio
        for position in self.positions:
            if new_position.symbol == position.symbol:
                raise ValueError(
                    f"There is already a position with symbol {position.symbol} in" +
                    f"this Portfolio (name of portfolio: {self.name}).")

        # If there was already a position with the incoming position's symbol in the
        # portfolio, then the above error would be raised. If not, the program will
        # keep running and add the position to the portfolio as below
        self.positions.append(new_position)

    def delete_empty_positions(self):
        """
        Delete all positions in the portfolio that have 0 quantity currently held.
        """
        non_empty_positions = []

        for position in self.positions:
            if position.quantity != 0:
                non_empty_positions.append(position)

        self.positions = non_empty_positions

    def contains_position(self, symbol):
        """
        Determines if any Position in the Portfolio uses the given symbol.

        Args:
            symbol: A string for the market symbol of this position (i.e. "AAPL" or "GOOG").

        Returns:
            A bool for if the given symbol was found in any Position in the Portfolio.
        """
        has_position = False

        # Check if any position has the symbol that was passed in
        if any([position.symbol == symbol for position in self.positions]):
            has_position = True

        return has_position

    def get_position(self, symbol):
        """
        Gets the Position object from the Portfolio with the given symbol

        Args:
            symbol: A string for the market symbol of this position (i.e. "AAPL" or "GOOG").

        Returns:
            The Position object with the given symbol from within this Portfolio, returns None
            if no such Position exists.
        """
        retval = None

        if self.contains_position(symbol):
            for position in self.positions:
                if position.symbol == symbol:
                    retval = position
                    break

        return retval

    def total_value(self):
        """
        Generates the total value of the Portfolio, including Positions and total cash.

        Returns:
            The total value of the Portfolio, including Positions and total cash.
        """
        total = self.cash

        for position in self.positions:
            total += position.total_value()

        return total

    def place_order(self, symbol, quantity, order_type=OrderType.BUY):
        """
        Places an order to buy or sell some quantity of an asset. Adds the order to an order
        queue and does not directly execute the order. That is done by process_pending_orders().

        Args:
            symbol: A string for the market symbol of this position (i.e. "AAPL" or "GOOG").
            quantity: The quantity of the asset to be bought or sold.
            order_type: A value from the enum OrderType that represents if the order is a
                buy or a sell order. Defaults to OrderType.BUY.

        Raises:
            ValueError: When the value passed into order_type is not in the enum
                OrderType.

        Returns:
            The unique order ID number for the order being created.
        """
        # Check that the order type passed in is a valid order type from the enum OrderType
        if order_type not in OrderType:
            raise ValueError("Invalid order type.")

        # Set the order number and increment it for the next order
        order_num = self._current_order_id_number
        self._current_order_id_number += 1

        # Create a new order object with the correct attributes and append it to the order
        # queue
        new_order = Order(order_num, symbol, quantity, order_type)
        self._order_queue.append(new_order)

        return order_num

    def cancel_order(self, id_of_order_to_cancel):
        """
        Removes the order with the given ID from the order queue.

        Args:
            id_of_order_to_cancel: The ID of the order that needs to be cancelled.

        Returns:
            True if the order was successfully removed from the queue, False otherwise.
        """
        was_order_successfully_cancelled = False

        # Check through all of the orders and remove the one that matches the provided ID
        for index, order in enumerate(self._order_queue):
            if order.id_number == id_of_order_to_cancel:
                self._order_queue.pop(index)
                was_order_successfully_cancelled = True
                break

        return was_order_successfully_cancelled

    def _process_pending_orders(self):
        """
        Processes any pending orders and executes any that are ready to be executed.

        Raises:
            ValueError: When an order is passed in with an invalid order type.

        Returns:
            A list of the order IDs that were executed/completed.
        """
        list_of_completed_order_ids = []
        new_order_queue = []

        # Check through every order in the order queue
        for order in self._order_queue:

            # Check that the order type passed in is a valid order type from the enum
            # OrderType
            if order.order_type not in OrderType:
                raise ValueError("Invalid order type.")

            # Process the order based on buy/sell
            if order.order_type == OrderType.BUY:
                status = self._execute_buy_order(order)
            elif order.order_type == OrderType.SELL:
                status = self._execute_sell_order(order)

            if status == OrderStatus.PENDING:
                new_order_queue.append(order)

        self._order_queue = new_order_queue

        return list_of_completed_order_ids

    def _execute_buy_order(self, order):
        """
        Executes a buy order if it is ready to be executed (does not have any delay 
        associated with it).

        Args:
            order: An Order dataclass instance.

        Returns:
            A value from the OrderStatus Enum to indicate the order's status.
        """

        # TODO: Add Logging
        order_status = OrderStatus.PENDING

        # Calculate total price of the order on the current bar
        current_timestamp = self.get_current_timestamp()
        bar_for_current_order = self.alpaca_api.market_data.get_bars(
            order.symbol,
            self.data_settings.time_frame,
            start=current_timestamp.isoformat(),
            limit=1
        )[0]

        # Determine what the unit price for the order's symbol currently is
        unit_price = get_price_from_bar(bar_for_current_order)

        # Determine the total cost of the order
        total_order_cost = unit_price * order.quantity

        # Check if the Portfolio has enough money in cash to make the purchase
        if self.cash >= total_order_cost:

            # Remove the total cost of the order from the Portfolio's liquid cash
            self.cash -= total_order_cost

            # Check if a Position already exists
            if self.contains_position(order.symbol):
                target_position = self.get_position(order.symbol)
                target_position.quantity += order.quantity

            # Create a new Position if one doesn't exist
            else:
                self.create_new_position(order.symbol, order.quantity)
                new_position = self.get_position(order.symbol)

                # Get the new position to the same state as the reference position by
                # generating the historical data for the asset going back either to the
                # beginning of the simulation or for the max number of rows
                new_position._catch_up_to_reference_position(
                    self._reference_position, self._increment_count)

            order_status = OrderStatus.COMPLETED

            print(
                f"{self.get_current_timestamp()} - BOUGHT: {order.quantity} shares of {order.symbol}")

        else:
            order_status = OrderStatus.FAILED

        # TODO: Logging

        return order_status

    def _execute_sell_order(self, order):
        """
        Executes a sell order if it is ready to be executed (does not have any delay 
        associated with it).

        Args:
            order: An Order dataclass instance.

        Returns:
            A value from the OrderStatus Enum to indicate the order's status.
        """
        order_status = OrderStatus.PENDING

        # TODO: Add Logging
        if not self.contains_position(order.symbol):
            order_status = OrderStatus.FAILED
        else:
            position_from_sell_order = self.get_position(order.symbol)

            if position_from_sell_order.quantity < order.quantity:
                order_status = OrderStatus.FAILED

        # If there are enough units of the currently-held position that the sell order
        # can succeed, perform the sell order
        if not order_status is OrderStatus.FAILED:
            self.cash += order.quantity * position_from_sell_order.price
            position_from_sell_order.quantity -= order.quantity
            order_status = OrderStatus.COMPLETED

            print(
                f"{self.get_current_timestamp()} - SOLD: {order.quantity} shares of {order.symbol}")

        # TODO: Logging

        return order_status

    def get_current_timestamp(self):
        """
        Gets the most recent timestamp that the DataManagers are on.

        Returns:
            The most recent timestamp from the reference position's dataframe
        """

        # Check if positions has items in it
        return self._reference_position.data_manager.get_last_row().timestamp

    def _create_new_daily_row_generators(self, start_time, end_time):
        """
        Creates new daily row generators for each Position associated with this Portfolio.

        Args:
            start_time: The ISO-8601 compliant date/time for the generators to start
                generating bars.
            end_time: The ISO-8601 compliant date/time for the generators to stop
                generating bars.
        """

        self._reference_position.data_manager.create_new_daily_row_generator(
            start_time, end_time)

        for position in self.positions:
            position.data_manager.create_new_daily_row_generator(start_time, end_time)

    def _increment_all_positions(self):
        """
        Increment the generator for every Position associated with this Portfolio and
        update the price attribute for each Position to use the new price data.
        """

        next(self._reference_position.data_manager._row_generator)
        self._reference_position.update_price_from_current_bar()

        for position in self.positions:

            # Increment the row generator to update the raw data to the next TimeFrame
            next(position.data_manager._row_generator)

            # Update the price attribute based on the current bar
            position.update_price_from_current_bar()

        if not self._any_generator_reached_end_of_day():
            self._increment_count += 1

    def _any_generator_reached_end_of_day(self):
        """
        Determines if any generator inside any Position has hit the end of its generation.
        That indicates it has reached the end of the day and a new daily generator needs to
        be created.

        Returns:
            A bool that shows if any generator inside any Position has reached the end of the
            day.
        """
        generator_at_end_of_day = False

        if self._reference_position.data_manager.generator_at_end_of_day == True:
            generator_at_end_of_day = True

        for position in self.positions:
            if (position.data_manager.generator_at_end_of_day == True):
                generator_at_end_of_day = True
                break

        return generator_at_end_of_day

    def copy(self, name=None):
        # TODO: Implement deep copy here and in Position
        new_name = name if name is not None else self.name
        copy_of_portfolio = Portfolio(self.alpaca_api, name=new_name)
