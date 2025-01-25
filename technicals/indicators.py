import pandas as pd

def BollingerBands(df: pd.DataFrame, periods=[20], s=2, mid_c='mid_c', mid_h='mid_h', mid_l='mid_l'):
    for period in periods:
        typical_p = ( df[mid_c] + df[mid_h] + df[mid_l] ) / 3
        stddev = typical_p.rolling(window=period).std()
        df[f'BB_MA{period}'] = typical_p.rolling(window=period).mean()
        df[f'BB_UP{period}'] = df[f'BB_MA{period}'] + stddev * s
        df[f'BB_LW{period}'] = df[f'BB_MA{period}'] - stddev * s
    return df

def ATR(df: pd.DataFrame, periods=[14],mid_c='mid_c', mid_h='mid_h', mid_l='mid_l'):
    for period in periods:
        prev_c = df[mid_c].shift(1)
        tr1 = df[mid_h] - df[mid_l]
        tr2 = abs(df[mid_h] - prev_c)
        tr3 = abs(prev_c - df[mid_l])
        tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
        df[f"ATR_{period}"] = tr.rolling(window=period).mean()
    return df

def KeltnerChannels(df: pd.DataFrame, n_ema=20, n_atr=10, mid_c='mid_c'):
    df[f'EMA{n_ema}'] = df[mid_c].ewm(span=n_ema, min_periods=n_ema).mean()
    df = ATR(df, periods=[n_atr])
    c_atr = f"ATR_{n_atr}"
    df[f'KeUp{n_ema}_{n_atr}'] = df[c_atr] * 2 + df[f'EMA{n_ema}']
    df[f'KeLo{n_ema}_{n_atr}'] = df[f'EMA{n_ema}'] - df[c_atr] * 2
    df.drop(c_atr, axis=1, inplace=True)
    return df


def MACD(df: pd.DataFrame, n_slow=26, n_fast=12, n_signal=9, mid_c='mid_c'):

    ema_long = df[mid_c].ewm(min_periods=n_slow, span=n_slow).mean()
    ema_short = df[mid_c].ewm(min_periods=n_fast, span=n_fast).mean()

    df[f'MACD{n_slow}_{n_fast}'] = ema_short - ema_long
    df[f'SIGNAL{n_slow}_{n_fast}'] = df[f'MACD{n_slow}_{n_fast}'].ewm(min_periods=n_signal, span=n_signal).mean()
    df[f'HIST{n_slow}_{n_fast}'] = df[f'MACD{n_slow}_{n_fast}'] - df[f'SIGNAL{n_slow}_{n_fast}']

    return df


#Chat
def RSI(df: pd.DataFrame, periods=[14], mid_c='mid_c'):
    
    for period in periods:
        df = df.copy()
        delta = df[mid_c].diff()

        # Separate gains and losses
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)

        gains_ewm = gains.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        losses_ewm = losses.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

        # Avoid division by zero
        eps = 1e-8
        rs = gains_ewm / (losses_ewm + eps)

        # Compute RSI
        df[f'RSI_{period}'] = 100 - (100 / (1 + rs))
    return df



























