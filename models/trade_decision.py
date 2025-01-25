class TradeDecision:

    def __init__(self, pair, prediction, stop_loss, take_profit):
        self.pair = pair
        self.prediction = prediction
        self.sl = stop_loss
        self.tp = take_profit

    def __repr__(self):
        return f"TradeDecision(): {self.pair} dir:{self.prediction} sl:{self.sl:.4f} tp:{self.tp:.4f}"