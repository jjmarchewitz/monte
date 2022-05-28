"""
A Portfolio is meant to represent a collection of individual Positions.
"""

from algo_pg.machine.position import Position
from dataclasses import dataclass
from enum import Enum


class OrderType(Enum):
    """
    An Enum holding a value for an order either being a buy or a sell order.
    """
    BUY = 1
    SELL = 2


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

    def __init__(self, alpaca_api, starting_cash=10000, name=None):
        """
        Constructor for the Portfolio class.

        Args:
            alpaca_api: A bundle of Alpaca APIs all created and authenticated with the keys
                in the repo's alpaca.config.
            starting_cash: The starting cash that the portfolio will have before any
                orders are placed or any positions are held. Defaults to 10000.
            name: A string name to give the portfolio, purely for aesthetic/debugging
                purposes. Defaults to None.
        """
        self.alpaca_api = alpaca_api

        self.name = name if name is not None else "Unnamed"
        self.positions = []
        self.cash = starting_cash
        self.time_of_last_price_gen_increment = None
        self._current_order_id_number = 1
        self._order_queue = []

    def create_new_position(self, symbol, initial_quantity):
        """
        Create a new Position from the provided args and add it to the Portfolio.

        Args:
            symbol: A string for the market symbol of this position (i.e. "AAPL" or "GOOG").
            initial_quantity: The quantity of this asset that should be held when this
                instance is finished being constructed.
        """
        new_position = Position(self.alpaca_api, symbol, initial_quantity)
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

    def increment_all_bar_generators(self):
        """
        Steps every position's bar generator forward by one time increment (TimeFrame).
        """
        for position in self.positions:
            position.generate_next_price()

            # This is a bit of an odd piece of code but if a position has just been
            # incremented and it doesn't need a new bar generator, then the increment
            # succeeded and the time when last updated for the position was just updated.
            # I am stealing that recently-updated time and making it the "most recent time
            # of an update" for the portfolio itself.
            if position.needs_new_bar_generator == False:
                self.time_of_last_price_gen_increment = position.time_when_price_last_updated

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

    def process_pending_orders(self):
        list_of_completed_order_ids = []

        # Check through every order in the order queue
        for order in self._order_queue:

            # Check that the order type passed in is a valid order type from the enum
            # OrderType
            if order.order_type not in OrderType:
                raise ValueError("Invalid order type.")

            # Process the order based on buy/sell
            if order.order_type == OrderType.BUY:
                pass
            elif order.order_type == OrderType.SELL:
                pass

        return list_of_completed_order_ids

    def create_new_bar_generators(self, time_frame, start_time, end_time):
        """
        Replaces the bar generators in every Position with new ones for a new date/time.

        Args:
            time_frame: An alpaca_trade_api.TimeFrame value corresponding to the time
                delta between price values.
            start_time: An ISO-8601-compliant date and time to start the new generators
                at.
            end_time: An ISO-8601-compliant date and time to start the new generators
                at.
        """

        for position in self.positions:
            position.create_new_daily_bar_generator(time_frame, start_time, end_time)

    def market_day_needs_to_be_incremented(self):
        """
        Determines whether or not all of the bar generators have hit the end of the market
        day, meaning the simulated market day is over and needs to be replaced with the next
        market day.

        Returns:
            Whether or not the market day has ended and needs to be replaced by the next
            market day.
        """

        # If all of the positions need new generators, that means the end of the day has
        # been reached
        need_new_generators = True

        # Check if any of the positions don't need a new generator (i.e. they haven't
        # reached the end of their generation yet/haven't hit the end of the day)
        for position in self.positions:
            if position.needs_new_bar_generator == False:
                need_new_generators = False

        return need_new_generators

    def copy(self, name=None):
        # TODO: Implement deep copy here and in Position
        new_name = name if name is not None else self.name
        copy_of_portfolio = Portfolio(self.alpaca_api, name=new_name)
