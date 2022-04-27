import yfinance
import data.stocks_get as data_getter
from algorithms.naive_star_boat.alg import NaiveStarBoat
from algorithms.bang_bang.alg import BangBang


def main():
    # This is a list of the class names (uninitialized) of all algorithms
    algorithm_class_list = [NaiveStarBoat, BangBang]

    # Create an instance of each algorithm listed in algorithm_class_list
    algorithm_instance_list = [alg_class() for alg_class in algorithm_class_list]

    data_getter.get_stock_data(ticker="MSFT", period="max")

    breakpoint()


if __name__ == "__main__":
    main()
