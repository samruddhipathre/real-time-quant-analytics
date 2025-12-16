import sqlite3
import pandas as pd
from pathlib import Path

# Absolute path to project root
BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "data" / "ticks.db"


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
    timeframe examples: '1S', '1T', '5T'
    """
    ohlc = df["price"].resample(timeframe).ohlc()
    volume = df["quantity"].resample(timeframe).sum()

    ohlcv = ohlc.join(volume.rename("volume"))
    ohlcv.dropna(inplace=True)

    return ohlcv


def get_ohlcv(symbol: str, timeframe: str = "1T") -> pd.DataFrame:
    """
    Public API used by analytics / frontend
    """
    ticks = load_ticks(symbol)
    return resample_ohlcv(ticks, timeframe)


if __name__ == "__main__":
    # Quick manual test
    df = get_ohlcv("BTCUSDT", "1T")
    print(df.tail())
