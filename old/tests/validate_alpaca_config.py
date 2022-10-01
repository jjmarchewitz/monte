from algo_pg.util import AlpacaAPIBundle


def main():
    alpaca_api = AlpacaAPIBundle()
    print(alpaca_api.trading.get_account())


if __name__ == "__main__":
    main()
