import pandas as pd
import numpy as np

def stationarize_data(df, columns, log_transform=True):

    df_stationary = df.copy()

    for col in columns:
        if pd.api.types.is_numeric_dtype(df_stationary[col]):
            
            # Apply log transformation if the column is strictly positive
            if log_transform:
                min_val = df_stationary[col].min()
                if min_val > 0:
                    df_stationary[col] = np.log(df_stationary[col])
                # If min_val <= 0, we skip log transform for that column
            df_stationary[col] = df_stationary[col].diff()

    return df_stationary