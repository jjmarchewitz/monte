# DEFINITION: A portfolio is simply a collection of individual assets

from containers.position import Position


class Portfolio():
    def __init__(self, market_data_api, name=None):
        self.market_data_api = market_data_api
        self.name = name if name is not None else "Unnamed"
        self.positions = []
        self.cash = 0

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

    def copy(self, name=None):
        # TODO: Implement copy here and in Position
        new_name = name if name is not None else self.name
        copy_of_portfolio = Portfolio(self.market_data_api, name=self.name)
