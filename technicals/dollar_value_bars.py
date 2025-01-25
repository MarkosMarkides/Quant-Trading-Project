import pandas as pd

def generate_dollar_bars(df, dollar_threshold, price_col='mid_c', volume_col='volume'):

    df['dollar_value'] = df[price_col] * df[volume_col]
    cum_dollar_value = 0
    dollar_bars = []
    bar = {}

    for _,row in df.iterrows():
        cum_dollar_value += row['dollar_value']

        if not bar:
            bar = {
                'time': row['time'],  # Open time
                'volume': row[volume_col],  # Initialize volume
                'mid_o': row['mid_o'],  # Open price
                'mid_h': row['mid_h'],  # High price
                'mid_l': row['mid_l'],  # Low price
                'mid_c': row['mid_c'],  # Close price
                'bid_o': row['bid_o'],  # Open bid
                'bid_h': row['bid_h'],  # High bid
                'bid_l': row['bid_l'],  # Low bid
                'bid_c': row['bid_c'],  # Close bid
                'ask_o': row['ask_o'],  # Open ask
                'ask_h': row['ask_h'],  # High ask
                'ask_l': row['ask_l'],  # Low ask
                'ask_c': row['ask_c']   # Close ask
            }
        else:
            # Update the bar
            bar['mid_h'] = max(bar['mid_h'], row['mid_h'])  # High price
            bar['mid_l'] = min(bar['mid_l'], row['mid_l'])  # Low price
            bar['mid_c'] = row['mid_c']  # Close price
            bar['bid_h'] = max(bar['bid_h'], row['bid_h'])  # High bid
            bar['bid_l'] = min(bar['bid_l'], row['bid_l'])  # Low bid
            bar['bid_c'] = row['bid_c']  # Close bid
            bar['ask_h'] = max(bar['ask_h'], row['ask_h'])  # High ask
            bar['ask_l'] = min(bar['ask_l'], row['ask_l'])  # Low ask
            bar['ask_c'] = row['ask_c']  # Close ask
            bar['volume'] += row[volume_col]  # Aggregate volume

        if cum_dollar_value >= dollar_threshold:
            dollar_bars.append(bar)
            bar = {}
            cum_dollar_value = 0

    dollar_bars_df = pd.DataFrame(dollar_bars)
    return dollar_bars_df