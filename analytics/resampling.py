import sqlite3
import pandas as pd
from pathlib import Path

# Absolute path to project root
BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "data" / "ticks.db"


def normalize_timeframe(tf: str) -> str:
    """
    Normalize human-readable or UI timeframe labels
    into valid Pandas frequency strings
    """
    tf = tf.strip()

    mapping = {
        # Seconds
        "1 Second": "1S",
        "1 second": "1S",
        "1S": "1S",

        # Minutes
        "1 Minute": "1min",
        "1 minute": "1min",
        "1min": "1min",

        "5 Minutes": "5min",
        "5 minutes": "5min",
        "5min": "5min",

        # Hours / Days
        "1h": "1H",
        "4h": "4H",
        "1d": "1D",
    }

    return mapping.get(tf, tf)


def load_ticks(symbol: str) -> pd.DataFrame:
    """
    Load tick data for a symbol from SQLite into a DataFrame
    """
    conn = sqlite3.connect(DB_FILE)

    query = """
        SELECT timestamp, price, quantity
        FROM ticks
        WHERE symbol = ?
        ORDER BY timestamp
    """

    df = pd.read_sql_query(query, conn, params=(symbol,))
    conn.close()

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)

    return df


def resample_ohlcv(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """
    Resample tick data into OHLCV bars
    """
    timeframe = normalize_timeframe(timeframe)

    ohlc = df["price"].resample(timeframe).ohlc()
    volume = df["quantity"].resample(timeframe).sum()

    ohlcv = ohlc.join(volume.rename("volume"))
    ohlcv.dropna(inplace=True)

    return ohlcv


def get_ohlcv(symbol: str, timeframe: str = "1min") -> pd.DataFrame:
    """
    Public API used by analytics / frontend
    """
    ticks = load_ticks(symbol)
    return resample_ohlcv(ticks, timeframe)


if __name__ == "__main__":
    # Quick manual test
    df = get_ohlcv("BTCUSDT", "1min")
    print(df.tail())
