from algo_pg.util.alpaca import alpaca_setup


def main():
    alpaca_api = alpaca_setup()
    print(alpaca_api.trading.get_account())


if __name__ == "__main__":
    main()
