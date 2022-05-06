from alpaca_trade_api import TimeFrame
from config.alpaca import alpaca_setup
from containers.portfolio import Portfolio
from containers.position import Position
from containers.trading_context import TradingContext


def main():
    trading_api, market_data_api = alpaca_setup()

    demo_context = TradingContext(
        trading_api, market_data_api, "2022-03-08", "2022-03-20")

    # demo_port = Portfolio(market_data_api)
    # demo_pos = Position(market_data_api, "AAPL")
    # demo_pos2 = Position(market_data_api, "GOOG")

    # demo_port.add_position(demo_pos)
    # demo_port.add_position(demo_pos2)

    breakpoint()


if __name__ == "__main__":
    main()
