from config.alpaca import alpaca_setup


##################################################################################
# This is just a template file, make your own copy before doing any scratch work #
##################################################################################


def main():
    tradeapi = alpaca_setup()
    print(tradeapi.get_account())


if __name__ == "__main__":
    main()
