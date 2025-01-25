import pandas as pd
from models.trade_decision import TradeDecision
from models.dollar_bars import generate_dollar_bars
from models.add_indicators import apply_indicators

pd.set_option('display.max_columns', None)
pd.set_option('expand_frame_repr', False)


from api.oanda_api import OandaApi
from models.trade_settings import TradeSettings
import constants.defs as defs

MIN_ROWS = 1500

def process_candles(df: pd.DataFrame, pair, trade_settings: TradeSettings, log_message, previous_dollar_bar):

    df.reset_index(drop=True, inplace=True)
    df['PAIR'] = pair

    dollar_bars_df = generate_dollar_bars(df, trade_settings.dollar_threshold) 
    
    if dollar_bars_df.empty:
        return None, previous_dollar_bar
    
    
    latest_dollar_bar = dollar_bars_df.iloc[-1]

    if (previous_dollar_bar is None) or (latest_dollar_bar['time'] != previous_dollar_bar['time']):
        dollar_bars_df = apply_indicators(dollar_bars_df)
        latest_row = dollar_bars_df.iloc[-1].copy()

        predictors = trade_settings.predictors 
        model = trade_settings.model 

        X = latest_row[predictors].to_frame().T
    
        probs = model.predict_proba(X)[:, 1]
        prediction = 1 if probs[0] >= 0.6 else 0

        if prediction == 1:
            latest_row['Prediction'] = defs.BUY
            latest_row['SL'] = latest_row['mid_c'] - latest_row['ATR_14'] * trade_settings.risk
            latest_row['TP'] = latest_row['mid_c'] + latest_row['ATR_14'] * trade_settings.reward
            latest_row['LOSS'] = latest_row['mid_c'] - latest_row['SL']

        else:
            latest_row['Prediction'] = defs.NONE

        decision = TradeDecision(latest_row)
        return decision, latest_row
    return None, previous_dollar_bar




def fetch_candles(pair, row_count, candle_time, granularity, api: OandaApi, log_message):

    df = api.get_candles_df(pair, count=row_count, granularity=granularity)

    if df is None or df.shape[0] == 0:
        log_message("tech_manager fetch_candles failed to get candles", pair)
        return None
    
    if df.iloc[-1].time != candle_time:
        log_message(f"tech_manager fetch_candles {df.iloc[-1].time} not correct", pair)
        return None

    return df

def get_trade_decision(candle_time, pair, granularity, api: OandaApi, trade_settings: TradeSettings, log_message, previous_dollar_bar=None, existing_df=None):

    log_message(f"tech_manager: min_rows:{MIN_ROWS} candle_time:{candle_time} granularity:{granularity}", pair)

    new_df = fetch_candles(pair, MIN_ROWS, candle_time,  granularity, api, log_message)

    if new_df is None:
        log_message("Failed to fetch new candles.", pair)
        return None, previous_dollar_bar, existing_df

    if existing_df is not None and not existing_df.empty:
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.drop_duplicates(subset='time', inplace=True)
        combined_df = combined_df.sort_values(by='time').reset_index(drop=True)
    else:
        combined_df = new_df
    
    trade_decision, updated_dollar_bar = process_candles(combined_df, pair, trade_settings, log_message, previous_dollar_bar)

    return trade_decision, updated_dollar_bar, combined_df