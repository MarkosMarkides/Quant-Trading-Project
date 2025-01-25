import pandas as pd
import matplotlib.pyplot as plt


def create_cummulative_pnl_col(df, predictions, label_column='Label',risk=1, reward=2):
    
    # Create a pnl collum 
    df['Predictions'] = predictions

    df['pnl'] = df.apply(
    lambda row: reward if row['Predictions'] == 1 and row[label_column] == 1 else
                -risk if row['Predictions'] == 1 and row[label_column] == 0 else
                0,
    axis=1
    )
    df['Cumulative Pnl'] = df['pnl'].cumsum()

    return df


def calculate_metrics(df, predictions, pnl_column='pnl', label_column='Label', time_column='time'):
    
    df = create_cummulative_pnl_col(df, predictions, label_column)
    
    metrics = {}

    # Net Profit
    metrics['Net Profit'] = df[pnl_column].sum()

    # Sharpe Ratio 
    metrics['Sharpe Ratio'] = df[pnl_column].mean() / df[pnl_column].std() if df[pnl_column].std()!=0 else 0
    
    downside_returns = df[df[pnl_column] < 0][pnl_column]
    downside_std = downside_returns.std() if not downside_returns.empty else 0
    metrics['Sortino Ratio'] = df[pnl_column].mean() / downside_std

    cumulative_pnl = df['Cumulative Pnl']
    running_max = cumulative_pnl.cummax()
    drawdowns = (cumulative_pnl - running_max) / running_max
    metrics['Max Drawdown'] = drawdowns.min()

    df['Month'] = df[time_column].dt.to_period('M')
    monthly_pnl = df.groupby('Month')[pnl_column].sum()
    metrics['Percentage of Profitable Months'] = ( (monthly_pnl > 0).sum() )/ len(monthly_pnl) * 100

    metrics['Win Rate'] = len(df[df[label_column] == 1]) / len(df) * 100

    metrics['Average Trade Duration'] = df['trade_duration'].mean()

    df['Current Loss Streak'] = df['Cumulative Pnl'].max() - df['Cumulative Pnl']
    df['Max Drawdown'] = df['Current Loss Streak'].max()
    
    metrics_df = pd.DataFrame(metrics, index=[0])

    return metrics_df, df

def plot_cumulative_pnl(df, pnl_column='Cumulative Pnl'):
    plt.figure(figsize=(12, 6))
    plt.plot(df['time'], df[pnl_column], label='Cumulative Pnl', color='blue')
    plt.title('Cumulative Pnl Over Time')
    plt.xlabel('Time')
    plt.ylabel('Cumulative Pnl')
    plt.legend()
    plt.grid()
    plt.show()