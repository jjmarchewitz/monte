from config.alpaca import alpaca_setup


def main():
    tradeapi = alpaca_setup()
    account = tradeapi.get_account()
    # breakpoint()


if __name__ == "__main__":
    main()
