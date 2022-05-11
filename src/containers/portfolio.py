# DEFINITION: A portfolio is simply a collection of individual positions

from containers.position import Position
from enum import Enum


class OrderType(Enum):
    BUY = 1
    SELL = 2


class Portfolio():
    def __init__(self, market_data_api, starting_cash=10000, name=None):
        """
        Constructor for the Portfolio class.

        Arguments:
            market_data_api -- An instance of the alpaca_trade_api package's own REST API
                set up to retrieve historical market data.

        Keyword Arguments:
            starting_cash -- The starting cash that the portfolio will have before any
                orders are placed or any positions are held. (default: {10000})
            name -- A string name to give the portfolio, purely for aesthetic/debugging
                purposes. (default: {None})
        """
        self.market_data_api = market_data_api
        self.name = name if name is not None else "Unnamed"
        self.positions = []
        self.cash = starting_cash
        self.time_of_last_price_gen_increment = None
        self.most_recent_order_number = 0

    def create_new_position(self, symbol, initial_quantity):
        """
        Create a new Position from the provided args and add it to the Portfolio.

        Arguments:
            symbol -- A string for the market symbol of this position (i.e. "AAPL" or "GOOG").
            initial_quantity -- The quantity of this asset that should be held when this
                instance is finished being constructed.
        """
        new_position = Position(self.market_data_api, symbol, initial_quantity)
        self.add_existing_position(new_position)

    def add_existing_position(self, new_position):
        """
        Adds an initialized Position object to the Portfolio.

        Arguments:
            new_position -- The incoming and already initialized Position object to be added
                to the Portfolio.

        Raises:
            ValueError: Raises when there is a Position object for the same symbol as a
                Position already in the Portfolio.
            TypeError: Raises when new_position is not of type containers.position.Position.
        """
        # Check that the new_position is a Position object
        if type(new_position) is Position:

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

        else:
            raise TypeError(
                "The object passed is not of type containers.position.Position")

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

        Arguments:
            symbol -- A string for the market symbol of this position (i.e. "AAPL" or "GOOG").
            quantity -- The quantity of the asset to be bought or sold.

        Keyword Arguments:
            order_type -- A value from the enum OrderType that represents if the order is a 
                buy or a sell order (default: {OrderType.BUY})

        Raises:
            ValueError: Raises when the value passed into order_type is not in the enum
                OrderType.
        """
        # TODO: Finish implementing this
        if order_type == OrderType.BUY:
            pass
        elif order_type == OrderType.SELL:
            pass
        else:
            raise ValueError("Invalid order type.")

    def cancel_order(self):
        pass

    def process_pending_orders(self):
        pass

    def create_new_bar_generators(self, time_frame, start_time, end_time):
        """
        Replaces the bar generators in every Position with new ones for a new date/time.

        Arguments:
            time_frame -- An alpaca_trade_api.TimeFrame value corresponding to the time
                delta between price values.
            start_time -- An ISO-8061-compliant date and time to start the new generators
                at.
            end_time -- An ISO-8061-compliant date and time to start the new generators
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
        # TODO: Implement copy here and in Position
        new_name = name if name is not None else self.name
        copy_of_portfolio = Portfolio(self.market_data_api, name=new_name)
