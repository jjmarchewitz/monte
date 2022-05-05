from config_alpaca import config_alpaca


def main():
    tradeapi = config_alpaca()
    account = tradeapi.get_account()
    breakpoint()


if __name__ == "__main__":
    main()
