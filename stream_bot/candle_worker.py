import pickle
from queue import Queue
import threading
import time
from api.oanda_api import OandaApi
from infrastructure.log_wrapper import LogWrapper
from models.add_indicators import apply_indicators
from models.trade_decision import TradeDecision
from models.trade_settings import TradeSettings
from models.dollar_bars import generate_dollar_bars
from technicals.patterns import apply_patterns
import datetime as dt

class CandleWorker(threading.Thread):
    CANDLES_LEN = 2500

    def __init__(self, trade_settings: TradeSettings, candle_work: Queue, trade_work_queue: Queue, granularity: str):
        super().__init__()
        self.trade_settings = trade_settings
        self.candle_work = candle_work
        self.granularity = granularity
        self.trade_work_queue = trade_work_queue
        self.last_processed_candle_time = None
        
        self.log = LogWrapper(f"CandleWorker_{trade_settings.pair}")
        self.model = None
        self.load_model()
        self.api = OandaApi()
        
        self.log_message(f"Created CandleWorker for {trade_settings.pair} {trade_settings}")
        
        

    def load_model(self):
        try:
            with open(self.trade_settings.model, "rb") as f:
                self.model = pickle.load(f)
            self.log_message(f"Model loaded successfully for {self.trade_settings.pair}")
        except Exception as error:
            self.log_message(f"Failed to load the model for {self.trade_settings.pair}: {error}", error=True)


    def log_message(self, msg, error=False):
        if error == True:
            self.log.logger.error(msg)
        else:
            self.log.logger.debug(msg)

    def make_prediction(self, row):
        predictors = self.trade_settings.predictors
        model = self.model
        """
        pred_proba = model.predict_proba(row[predictors].to_frame().T)[0][1]    
        prediction = 1 if pred_proba > self.trade_settings.probability else 0"""
        prediction = model.predict(row[predictors].to_frame().T)[0]
        return prediction

    def find_SL_TP(self, row):

        stop_loss = row['mid_c'] - (self.trade_settings.risk * row['ATR_14'])
        take_profit = row['mid_c'] +  (self.trade_settings.reward * row['ATR_14'])

        return stop_loss, take_profit

    def run_analysis(self):
        attempts = 0
        tries =  5

        try:
            while attempts < tries:
                # count = candles you need to get in order to calculate your indicators!
                candles = self.api.get_candles_df(self.trade_settings.pair, granularity=self.granularity, count=self.CANDLES_LEN)
                
                if candles is None or candles.empty:
                    self.log_message("No candles fetched")
                    time.sleep(0.5)
                    attempts += 1
                    continue

                candles = generate_dollar_bars(candles, self.trade_settings.dollar_threshold)
                if candles.empty:
                    self.log_message("0 candles left after generating dollar bars")
                                
                current_last_candle_time = candles.iloc[-1].time
                self.log_message(f"Fetched last candle time: {current_last_candle_time}")

                if current_last_candle_time == self.last_processed_candle_time:

                    self.log_message(f"No new candle detected (last_processed_candle_time: {self.last_processed_candle_time})", error=True)
                    time.sleep(0.5)
                else:
                    print(candles.tail())
                    self.log_message(f"New dollar bar detected: {current_last_candle_time}")
                    candles = apply_patterns(candles)
                    candles = apply_indicators(candles)
                    candles = candles.dropna()

                    if candles.empty:
                        self.log_message("Candles empty after adding patterns and indicators")
                        break

                    last_row = candles.iloc[-1]
                    prediction = self.make_prediction(last_row)
                    self.log_message(f"Prediction made: {prediction}")
                    if prediction == 1:
                        stop_loss, take_profit = self.find_SL_TP(last_row)
                        trade_decision = TradeDecision(
                            self.trade_settings.pair,
                            prediction,
                            stop_loss,
                            take_profit
                        )
                        self.trade_work_queue.put(trade_decision)  # Add trade to queue
                        self.log_message(f"Trade decision added to queue: {trade_decision}")

                    self.last_processed_candle_time = current_last_candle_time
                    break
                attempts += 1
        except Exception as error:
            self.log_message(f"Exception in run_analysis: {error}", error=True)

    def run(self):
        while True:
            try:
                candle_time = self.candle_work.get()
                if candle_time is None:
                    self.log_message("Received None as candle_time, skipping analysis")
                    continue
                print(f"CandleWorker new candle: {candle_time} {self.trade_settings.pair}")
                self.log_message(f"CandleWorker received new candle_time: {candle_time}")

                self.run_analysis()
            except Exception as error:
                self.log_message(f"Exception in run loop: {error}", error=True)
#