class TradeSettings:

    def __init__(self, ob, pair):
        self.pair = pair
        self.dollar_threshold = ob['dollar_threshold']
        self.model = ob['model']
        self.reward = ob['reward']
        self.risk = ob['risk']
        self.probability = ob['probability']
        self.predictors = ob['predictors']

    def __repr__(self):
        return str(vars(self))

    @classmethod
    def settings_to_str(cls, settings):
        ret_str = "Trade Settings:\n"
        for _, v in settings.items():
            ret_str += f"{v}\n"

        return ret_str