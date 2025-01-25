import pandas as pd
from technicals import indicators

def apply_indicators(df_analysis, time_col='time', ask_o='ask_o', bid_o='bid_o', mid_c='mid_c', mid_h='mid_h', mid_l='mid_l', spread='Y'):

    # Applly the spread
    if spread=='Y':
        df_analysis['spread'] = df_analysis[ask_o] - df_analysis[bid_o]
    
    # Apply time based features
    df_analysis[time_col] = pd.to_datetime(df_analysis[time_col])
    df_analysis['hour'] = df_analysis[time_col].dt.hour
    df_analysis['day_of_week'] = df_analysis[time_col].dt.dayofweek
    df_analysis['month'] = df_analysis[time_col].dt.month
    df_analysis['minute'] = df_analysis[time_col].dt.minute

    # Apply Bollinger Bands
    df_analysis = indicators.BollingerBands(df_analysis, [10, 30, 50], mid_c=mid_c, mid_h=mid_h, mid_l=mid_l)

    # Apply ATR indicators
    df_analysis = indicators.ATR(df_analysis, [7, 14, 40], mid_c=mid_c, mid_h=mid_h, mid_l=mid_l)

    # Apply Keltner Channels
    for ema, atr in [(20, 10), (50, 50), (200, 50)]:
        df_analysis = indicators.KeltnerChannels(df_analysis, ema, atr, mid_c=mid_c)

    # Apply RSI indicators
    df_analysis = indicators.RSI(df_analysis, [7, 14, 50], mid_c=mid_c)

    # Apply MACD indicators
    for slow, fast, signal in [(26, 12, 9), (52, 24, 9)]:
        df_analysis = indicators.MACD(df_analysis, slow, fast, signal, mid_c=mid_c)
        
    return df_analysis