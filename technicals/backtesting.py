import pandas as pd

def predict(train, test, predictors, model, label_column='Label', pred_threshold=0.6):
    
    model.fit(train[predictors], train[label_column])
    if hasattr(model, 'predict_proba'):
        preds = model.predict_proba(test[predictors])[:, 1]
        preds[preds>=pred_threshold] = 1
        preds[preds<pred_threshold] = 0
    else:
        preds = model.predict(test[predictors])
    preds = pd.Series(preds, index=test.index, name='Predictions')
    combined = pd.concat([test[label_column], preds], axis=1)

    return combined


def model_evaluation(df, model, predictors, start=10_000, step=10_000, label_column='Label', pred_threshold=0.6, memory='on'):

    all_predictions = []
    memory_index = 0
    
    for i in range(start, df.shape[0], step):

        print(f"{((i/df.shape[0])*100):.2f}% there...")

        train = df.iloc[memory_index:i]
        test = df.iloc[i: (i+step)]

        predictions = predict(train, test, predictors, model,label_column, pred_threshold)
        all_predictions.append(predictions)

        if memory == 'off':
            memory_index = i

    return pd.concat(all_predictions)

def live_backtest(df, win=2, loss=1, prediction_column='Prediction', label_column='Label', trade_duration_column='trade_duration'):

    i = 0
    trade_remaining = 0
    cum_PnL = 0
    in_trade = False

    df['Live_PnL'] = 0
    df['Live_Cum_PnL'] = 0

    while i < len(df):
        if in_trade:
            trade_remaining -= 1
            if trade_remaining <= 0:
                in_trade=False
            i += 1
            continue

        row = df.iloc[i]

        if row[prediction_column] == 0:
            i += 1
            df.at[i, 'Live_PnL'] = 0
            df.at[i, 'Live_Cum_PnL'] = cum_PnL
            continue

        if row[prediction_column] == 1:
            if row[label_column] == 1:
                cum_PnL += win
                df.at[i, 'Live_PnL'] = win
                df.at[i, 'Live_Cum_PnL'] = cum_PnL
            else:
                cum_PnL -= loss
                df.at[i, 'Live_PnL'] = loss
                df.at[i, 'Live_Cum_PnL'] = cum_PnL

        trade_remaining = row[trade_duration_column]
        i += 1
        in_trade = True
    return df
