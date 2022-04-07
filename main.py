import yfinance
from algorithms.naive_star_boat.alg import *
from algorithms.bang_bang.alg import *

# This is a list of the class names (uninitialized) of all algorithms
algorithm_class_list = [NaiveStarBoat, BangBang]

# Create an instance of each algorithm listed in algorithm_class_list
algorithm_instance_list = [alg_class() for alg_class in algorithm_class_list]


def main():
    pass


if __name__ == "__main__":
    main()
