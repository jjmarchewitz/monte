# DEFINITION: A portfolio is simply a collection of individual assets

from containers.position import Position


class Portfolio():
    def __init__(self, market_data_api, name=None):
        self.market_data_api = market_data_api
        self.name = name if name is not None else "Unnamed"
        self.positions = []
        self.cash = 0
        self.time_of_last_price_gen_increment = None

    def add_position(self, new_position):
        # Check that the new_position is a position object
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

    def total_value(self):
        total = self.cash

        for position in self.positions:
            total += position.total_value()

        return total

    def increment_all_price_generators(self):
        for position in self.positions:
            position.increment_price_generator()

            # This is a bit of an odd piece of code but if a position has just been
            # incremented and it doesn't need a new price generator, then the increment
            # succeeded and the time when last updated for the position was just updated.
            # I am stealing that recently-updated time and making it the "most recent time
            # of an update" for the portfolio itself.
            if position.needs_new_price_generator == False:
                self.time_of_last_price_gen_increment = position.time_when_price_last_updated

    def create_new_price_generators(self, time_frame, start_time, end_time):
        for position in self.positions:
            position.create_new_daily_price_generator(time_frame, start_time, end_time)

    def market_day_needs_to_be_incremented(self):
        # If all of the positions need new generators, that means the end of the day has
        # been reached
        need_new_generators = True

        # Check if any of the positions don't need a new generator (i.e. they haven't
        # reached the end of their generation yet/haven't hit the end of the day)
        for position in self.positions:
            if position.needs_new_price_generator == False:
                need_new_generators = False

        return need_new_generators

    def copy(self, name=None):
        # TODO: Implement copy here and in Position
        new_name = name if name is not None else self.name
        copy_of_portfolio = Portfolio(self.market_data_api, name=new_name)
