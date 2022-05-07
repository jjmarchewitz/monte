from alpaca_trade_api import TimeFrame
from config.alpaca import alpaca_setup
from containers.portfolio import Portfolio
from containers.position import Position
from containers.trading_machine import TradingMachine


def main():
    trading_api, market_data_api = alpaca_setup()

    # Only Days, Hours, and Minutes are supported as time frames
    machine = TradingMachine(
        trading_api, market_data_api, "2022-03-08", "2022-03-20",
        time_frame=TimeFrame.Day)

    # Create the first portfolio
    portfolio1 = Portfolio(market_data_api, name="P1")
    portfolio1.add_position(Position(market_data_api, "AAPL", 5))
    portfolio1.add_position(Position(market_data_api, "GOOG", 1))

    # Create the second portfolio
    portfolio2 = Portfolio(market_data_api, name="P2")
    portfolio2.add_position(Position(market_data_api, "IVV", 10.75))
    portfolio2.add_position(Position(market_data_api, "QQQ", 2.33))

    # Add both portfolios along with fake algorithms to the trading machine. The algos
    # are dummy strings (for now) because they are keys in a dictionary, so if you add
    # more make sure to make the name unique from all others. Later, the actual instance
    # of the algorithm will be able to be the key in the dict.
    machine.add_algo_port_pair("DummyAlgo1", portfolio1)
    machine.add_algo_port_pair("DummyAlgo2", portfolio2)

    # Rage against the machine
    machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
