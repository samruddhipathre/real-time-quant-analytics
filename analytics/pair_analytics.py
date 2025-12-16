import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller

from analytics.resampling import get_ohlcv


def align_price_series(
    symbol_x: str,
    symbol_y: str,
    timeframe: str = "1T",
    price_col: str = "close",
):
    """
    Load and align two price series on timestamp
    """
    df_x = get_ohlcv(symbol_x, timeframe)[[price_col]].rename(
        columns={price_col: "x"}
    )
    df_y = get_ohlcv(symbol_y, timeframe)[[price_col]].rename(
        columns={price_col: "y"}
    )

    df = df_x.join(df_y, how="inner")
    return df.dropna()


def compute_hedge_ratio(df: pd.DataFrame):
    """
    OLS regression: y = alpha + beta * x
    """
    X = sm.add_constant(df["x"])
    model = sm.OLS(df["y"], X).fit()
    beta = model.params["x"]
    alpha = model.params["const"]

    return alpha, beta


def compute_spread(df: pd.DataFrame, alpha: float, beta: float):
    """
    Spread = y - (alpha + beta * x)
    """
    spread = df["y"] - (alpha + beta * df["x"])
    return spread


def compute_zscore(spread: pd.Series, window: int = 30):
    """
    Rolling z-score of spread
    """
    mean = spread.rolling(window).mean()
    std = spread.rolling(window).std()
    zscore = (spread - mean) / std
    return zscore


def compute_rolling_correlation(df: pd.DataFrame, window: int = 30):
    """
    Rolling correlation between x and y
    """
    return df["x"].rolling(window).corr(df["y"])


def adf_test(spread: pd.Series):
    """
    Augmented Dickey-Fuller test on spread
    """
    result = adfuller(spread.dropna())
    return {
        "adf_stat": result[0],
        "p_value": result[1],
        "used_lag": result[2],
        "n_obs": result[3],
        "critical_values": result[4],
    }


def run_pair_analytics(
    symbol_x: str,
    symbol_y: str,
    timeframe: str = "1T",
    z_window: int = 30,
):
    """
    High-level API for frontend / analysis
    """
    df = align_price_series(symbol_x, symbol_y, timeframe)

    alpha, beta = compute_hedge_ratio(df)
    spread = compute_spread(df, alpha, beta)
    zscore = compute_zscore(spread, z_window)
    corr = compute_rolling_correlation(df)

    return {
        "prices": df,
        "alpha": alpha,
        "beta": beta,
        "spread": spread,
        "zscore": zscore,
        "correlation": corr,
    }


if __name__ == "__main__":
    # Quick sanity test
    result = run_pair_analytics("BTCUSDT", "ETHUSDT", "1T")

    print("Hedge ratio (beta):", result["beta"])
    z = result["zscore"].dropna()
if not z.empty:
    print("Latest z-score:", z.iloc[-1])
else:
    print("Latest z-score: Not enough data yet")

