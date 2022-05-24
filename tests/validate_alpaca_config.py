from algo_pg.util.alpaca import alpaca_setup


def main():
    trading_api, market_data_api = alpaca_setup()
    print(trading_api.get_account())


if __name__ == "__main__":
    main()
