from alpaca_trade_api import TimeFrame
from config.alpaca import alpaca_setup
from containers.portfolio import Portfolio
from containers.position import Position
from containers.trading_machine import TradingMachine


def main():
    trading_api, market_data_api = alpaca_setup()

    demo_context = TradingMachine(
        trading_api, market_data_api, "2022-03-08", "2022-03-20",
        time_frame=TimeFrame.Hour)

    demo_port = Portfolio(market_data_api)
    demo_pos = Position(market_data_api, "AAPL", 1)
    # demo_pos2 = Position(market_data_api, "GOOG", 1)

    demo_port.add_position(demo_pos)
    # demo_port.add_position(demo_pos2)

    for market_day in demo_context.market_days:
        demo_port.create_new_price_generators(
            demo_context.time_frame,
            market_day.open_time_iso,
            market_day.close_time_iso
        )

        while True:
            demo_port.increment_all_price_generators()

        breakpoint()

    # for market_day in demo_context.market_days:
    #     print(market_data_api.get_bars_iter("AAPL", TimeFrame.Hour,
    #                                         market_day.open_time_iso, market_day.close_time_iso))

    breakpoint()


if __name__ == "__main__":
    main()
