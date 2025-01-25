import json

from models.trade_settings import TradeSettings


class TradeSettingsCollection:

    FILENAME = "settings.json"

    def __init__(self):
        self.trade_settings_dict = {}

    def load_trade_settings(self):
        self.trade_settings_dict = {}
        fileName = f"./stream_bot/{self.FILENAME}"
        with open(fileName, "r") as f:
            data = json.loads(f.read())
            self.granularity = data['granularity']
            for pair, pair_settings in data['pairs'].items():
                self.trade_settings_dict[pair] = TradeSettings(pair_settings, pair)

    def print_collection(self):
        print(f"Granularity: {self.granularity}")
        [print(f"{k}: {v}") for k, v in self.trade_settings_dict.items()]
        
    def pair_list(self):
        return list(self.trade_settings_dict.keys())
    
    def get_trade_settings(self, pair) ->TradeSettings:
        return self.trade_settings_dict[pair]

tradeSettingsCollection = TradeSettingsCollection()