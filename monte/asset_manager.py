"""DOC:"""


class AssetManager:
    """
    DOC:
    """

    def __init__(self, alpaca_api, machine_settings) -> None:
        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings
        self.watched_assets = {}
        self.asset_data_buffer = {}

    def __getitem__(self):
        # TODO: Figure out if this is even the right way to do it
        pass

    def increment_dataframes(self):
        """DOC:"""

        # If asset_data_buffer is empty, populate it with more data (threads)
        # else, add the next row of buffered data to the watched assets (update the asset DFs)
        pass

    def watch_asset(self, symbol):
        """DOC:"""
        if not self.is_watching_asset(symbol):
            # TODO: Populate this watched asset with a df?
            self.watched_assets[symbol] = None

    def is_watching_asset(self, symbol):
        """DOC:"""
        return symbol in self.watch_assets.keys()

    def remove_asset(self, symbol):
        """DOC:"""
        pass


# class Asset:
#     """
#     DOC:
#     """

#     def __init__(self, alpaca_api, machine_settings):
#         pass
