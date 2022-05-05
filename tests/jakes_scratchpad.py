from config.alpaca import alpaca_setup


def main():
    tradeapi = alpaca_setup()
    account = tradeapi.get_account()

    tradeapi.submit_order(
        symbol="IVV",
        qty="1",
        side="buy",
        type="market",
    )


if __name__ == "__main__":
    main()
