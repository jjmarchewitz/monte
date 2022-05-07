from alpaca_trade_api import TimeFrame
from config.alpaca import alpaca_setup
from containers.portfolio import Portfolio
from containers.position import Position
from containers.trading_machine import TradingMachine


def main():
    trading_api, market_data_api = alpaca_setup()

    machine = TradingMachine(
        trading_api, market_data_api, "2022-03-08", "2022-03-20",
        time_frame=TimeFrame.Day)

    portfolio1 = Portfolio(market_data_api, name="P1")
    portfolio1.add_position(Position(market_data_api, "AAPL", 5))
    portfolio1.add_position(Position(market_data_api, "GOOG", 1))

    portfolio2 = Portfolio(market_data_api, name="P2")
    portfolio2.add_position(Position(market_data_api, "IVV", 10.75))
    portfolio2.add_position(Position(market_data_api, "QQQ", 2.33))

    machine.add_algo_port_pair("DummyAlgo1", portfolio1)
    machine.add_algo_port_pair("DummyAlgo2", portfolio2)

    machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
