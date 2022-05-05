# Example imports
from config_alpaca import config_alpaca


##################################################################################
# This is just a template file, make your own copy before doing any scratch work #
##################################################################################


def main():
    tradeapi = config_alpaca()
    print(tradeapi.get_account())


if __name__ == "__main__":
    main()
