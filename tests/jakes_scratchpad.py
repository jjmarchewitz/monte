from config.alpaca import alpaca_setup
from alpaca_trade_api import TimeFrame


def main():
    tradeapi = alpaca_setup()
    account = tradeapi.get_account()

    # Demo buy order
    tradeapi.submit_order(
        symbol="IVV",
        qty="1",
        side="buy",
        type="market",
    )

    tradeapi.list_positions()
    breakpoint()


if __name__ == "__main__":
    main()
