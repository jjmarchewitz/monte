from algo_pg.algorithms.base_algorithm import Algorithm
from algo_pg.portfolio import OrderType


class BangBang(Algorithm):
    def __init__(self, alpaca_api, data_settings, portfolio):
        super().__init__(alpaca_api, data_settings, portfolio)
        self.alpaca_api = alpaca_api
        self.data_settings = data_settings
        self.portfolio = portfolio

        # Some initial stock purchases, optional
        self.portfolio.place_order("AAPL", 5, OrderType.BUY)
        self.portfolio.place_order("SPY", 5, OrderType.BUY)
        self.portfolio.place_order("GME", 5, OrderType.BUY)

    def run_for_one_time_frame(self):

        for position in self.portfolio.positions:
            data_manager = position.data_manager
            df = position.get_df()

            # Grab the last (most recent) row of data from the position's dataframe
            last_row = data_manager.get_last_row()

            # This is a statistic I made up. I took the net change in vwap over the last 5
            # TimeFrames and divided it by the current vwap to get a rough indicator of
            # growth
            percent_change_l5_over_current_vwap = (
                last_row.net_l5_vwap / last_row.vwap) * 100

            # If this percentage growth number is more than 1%, buy 1 share
            if percent_change_l5_over_current_vwap > 1:
                self.portfolio.place_order(position.symbol, 1, OrderType.BUY)

            # If this percentage growth number is less than -1%, sell 1 share
            elif percent_change_l5_over_current_vwap < -1:
                self.portfolio.place_order(position.symbol, 1, OrderType.SELL)

            # breakpoint()
