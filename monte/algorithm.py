from __future__ import annotations

from monte.portfolio import Portfolio


class Algorithm():

    def __init__(self) -> None:
        pass

    def get_portfolio(self) -> Portfolio:
        raise NotImplementedError("You have to implement portfolio()!")

    def startup(self) -> None:
        raise NotImplementedError("You have to implement startup()!")

    def run_one_time_frame(self, processed_orders) -> None:
        raise NotImplementedError("You have to implement run_one_time_frame()!")
