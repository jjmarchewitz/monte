from algo_pg.machine.portfolio import Portfolio
from algo_pg.machine.position import Position
from algo_pg.machine.trading_machine import TradingMachine
from algo_pg.util.alpaca import alpaca_setup
from alpaca_trade_api import TimeFrame


def main():
    trading_api, market_data_api = alpaca_setup()

    # Only Days, Hours, and Minutes are supported as time frames
    machine = TradingMachine(
        trading_api, market_data_api, "2022-03-08", "2022-03-20",
        time_frame=TimeFrame.Day)

    # Create the first portfolio
    portfolio1 = Portfolio(market_data_api, starting_cash=10000, name="P1")

    # Create a new position directly into the portfolio
    portfolio1.create_new_position("AAPL", 5)

    # Add an existing position to the portfolio
    position1 = Position(market_data_api, "GOOG", 1)
    portfolio1.add_existing_position(position1)

    # Create the second portfolio
    portfolio2 = Portfolio(market_data_api, starting_cash=10000, name="P2")
    portfolio2.add_existing_position(Position(market_data_api, "IVV", 10.75))
    portfolio2.add_existing_position(Position(market_data_api, "QQQ", 2.33))

    # Add both portfolios along with fake algorithms to the trading machine. The algos
    # are dummy strings (for now) because they are keys in a dictionary, so if you add
    # more make sure to make the name unique from all others. Later, the actual instance
    # of the algorithm will be able to be the key in the dict.
    machine.add_algo_portfolio_pair("DummyAlgo1", portfolio1)
    machine.add_algo_portfolio_pair("DummyAlgo2", portfolio2)

    # Rage against the machine
    machine.run()

    # breakpoint()


if __name__ == "__main__":
    main()
