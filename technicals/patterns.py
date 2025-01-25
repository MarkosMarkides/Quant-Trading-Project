import pandas as pd

# --- Constants ---
HANGING_MAN_BODY = 15.0
HANGING_MAN_HEIGHT = 75.0
SHOOTING_STAR_HEIGHT = 25.0
SPINNING_TOP_MIN = 40.0
SPINNING_TOP_MAX = 60.0
MARUBOZU = 98.0
ENGULFING_FACTOR = 1.1
MORNING_STAR_PREV2_BODY = 90.0
MORNING_STAR_PREV_BODY = 10.0
TWEEZER_BODY = 15.0
TWEEZER_HL = 0.01
TWEEZER_TOP_BODY = 40.0
TWEEZER_BOTTOM_BODY = 60.0

# --- Pattern Functions ---
def apply_marubozu(row):
    return 1 if row.body_perc > MARUBOZU else 0

def apply_hanging_man(row):
    if row.body_bottom_perc > HANGING_MAN_HEIGHT and row.body_perc < HANGING_MAN_BODY:
        return 1
    return 0

def apply_shooting_star(row):
    if row.body_top_perc < SHOOTING_STAR_HEIGHT and row.body_perc < HANGING_MAN_BODY:
        return 1
    return 0

def apply_spinning_top(row):
    if (row.body_top_perc < SPINNING_TOP_MAX
        and row.body_bottom_perc > SPINNING_TOP_MIN
        and row.body_perc < HANGING_MAN_BODY):
        return 1
    return 0

def apply_engulfing(row):
    if row.direction != row.direction_prev:
        if row.body_size > row.body_size_prev * ENGULFING_FACTOR:
            return 1
    return 0

def apply_tweezer_top(row):
    if abs(row.body_size_change) < TWEEZER_BODY:
        if row.direction == -1 and row.direction != row.direction_prev:
            if abs(row.low_change) < TWEEZER_HL and abs(row.high_change) < TWEEZER_HL:
                if row.body_top_perc < TWEEZER_TOP_BODY:
                    return 1
    return 0

def apply_tweezer_bottom(row):
    if abs(row.body_size_change) < TWEEZER_BODY:
        if row.direction == 1 and row.direction != row.direction_prev:
            if abs(row.low_change) < TWEEZER_HL and abs(row.high_change) < TWEEZER_HL:
                if row.body_bottom_perc > TWEEZER_BOTTOM_BODY:
                    return 1
    return 0

def apply_morning_star(row, direction=1):
    """
    direction=1 => Morning Star
    direction=-1 => Evening Star
    """
    if row.body_perc_prev_2 > MORNING_STAR_PREV2_BODY:
        if row.body_perc_prev < MORNING_STAR_PREV_BODY:
            if row.direction == direction and row.direction_prev_2 != direction:
                if direction == 1:
                    if row.mid_c > row.mid_point_prev_2:
                        return 1
                else:  # direction == -1 => Evening Star
                    if row.mid_c < row.mid_point_prev_2:
                        return 1
    return 0

# --- Main Candle Properties Function ---
def apply_candle_props(df: pd.DataFrame) -> pd.DataFrame:
    df_an = df.copy()

    # Basic candle measures
    direction_series = df_an.mid_c - df_an.mid_o
    body_size = direction_series.abs()
    full_range = df_an.mid_h - df_an.mid_l

    # Handle zero range to avoid division by zero to avoid inf values
    full_range = full_range.replace(0, 1e-4)  

    direction = direction_series.apply(lambda x: 1 if x >= 0 else -1)
    body_perc = (body_size / full_range) * 100

    body_lower = df_an[['mid_c','mid_o']].min(axis=1)
    body_upper = df_an[['mid_c','mid_o']].max(axis=1)
    body_bottom_perc = ((body_lower - df_an.mid_l) / full_range) * 100
    body_top_perc = 100 - (((df_an.mid_h - body_upper) / full_range) * 100)
    mid_point = full_range / 2 + df_an.mid_l

    # Percentage changes for tweezer logic
    low_change = df_an.mid_l.pct_change() * 100
    high_change = df_an.mid_h.pct_change() * 100
    body_size_change = body_size.pct_change() * 100

    # Assign to DataFrame
    df_an['direction'] = direction
    df_an['body_size'] = body_size
    df_an['body_perc'] = body_perc
    df_an['body_lower'] = body_lower
    df_an['body_upper'] = body_upper
    df_an['body_bottom_perc'] = body_bottom_perc
    df_an['body_top_perc'] = body_top_perc
    df_an['mid_point'] = mid_point

    df_an['low_change'] = low_change
    df_an['high_change'] = high_change
    df_an['body_size_change'] = body_size_change

    # Shifts for previous candle references
    df_an['body_size_prev'] = df_an['body_size'].shift(1)
    df_an['direction_prev'] = df_an['direction'].shift(1)
    df_an['direction_prev_2'] = df_an['direction'].shift(2)
    df_an['body_perc_prev'] = df_an['body_perc'].shift(1)
    df_an['body_perc_prev_2'] = df_an['body_perc'].shift(2)
    df_an['mid_point_prev_2'] = df_an['mid_point'].shift(2)

    return df_an

# --- Setting Candle Patterns ---
def set_candle_patterns(df_an: pd.DataFrame) -> None:
    df_an['HANGING_MAN'] = df_an.apply(apply_hanging_man, axis=1)
    df_an['SHOOTING_STAR'] = df_an.apply(apply_shooting_star, axis=1)
    df_an['SPINNING_TOP'] = df_an.apply(apply_spinning_top, axis=1)
    df_an['MARUBOZU'] = df_an.apply(apply_marubozu, axis=1)
    df_an['ENGULFING'] = df_an.apply(apply_engulfing, axis=1)
    df_an['TWEEZER_TOP'] = df_an.apply(apply_tweezer_top, axis=1)
    df_an['TWEEZER_BOTTOM'] = df_an.apply(apply_tweezer_bottom, axis=1)

    # For morning/evening star patterns:
    df_an['MORNING_STAR'] = df_an.apply(apply_morning_star, axis=1, args=(1,))
    df_an['EVENING_STAR'] = df_an.apply(apply_morning_star, axis=1, args=(-1,))

def apply_patterns(df: pd.DataFrame):
    df_an = apply_candle_props(df)
    set_candle_patterns(df_an)
    return df_an