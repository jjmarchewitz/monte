"""
A base class for all trading algorithms to be based off of/inherit from.
"""


class Algorithm():
    def __init__(self, alpaca_api, data_settings, portfolio):
        self.alpaca_api = alpaca_api
        self.data_settings = data_settings
        self.portfolio = portfolio

    def run_for_one_time_frame(self):
        print("You should have your own implementation of this for your algorithm!")
