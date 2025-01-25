from technicals.indicators import ATR

def tripple_barrier_labeling(df, win=4, loss=2, time_horizon=50, bid_c='bid_c', ask_h='ask_h', ask_l='ask_l', atr=14):
    df = ATR(df, [atr])
    labels = []
    durations = []

    for idx in range(len(df)):

        row = df.iloc[idx]
        
        take_profit_target = row[bid_c] + win * row[f"ATR_{atr}"]
        stop_loss_target = row[bid_c] - loss * row[f"ATR_{atr}"]

        label = 0 
        trade_duration = 0

        for i in range(1, time_horizon+1):
            if idx + i >= len(df):
                break
            
            future_row = df.iloc[idx+i]

            high = future_row[ask_h]
            low = future_row[ask_l]

            if low <= stop_loss_target:
                label = 0
                trade_duration = i
                break
            if high >= take_profit_target:
                label = 1
                trade_duration = i
                break

        if trade_duration == 0:
            trade_duration = time_horizon
        
        labels.append(label)
        durations.append(trade_duration)
    
    df['Label'] = labels
    df['trade_duration'] = durations

    return df


