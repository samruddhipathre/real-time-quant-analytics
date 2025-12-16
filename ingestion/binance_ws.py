import time
import requests
from datetime import datetime

from storage.db import init_db, insert_tick

BINANCE_REST_URL = "https://api.binance.com/api/v3/trades"
SYMBOLS = ["BTCUSDT", "ETHUSDT"]
POLL_INTERVAL = 1  # seconds


def poll_trades():
    print("Starting Binance REST polling with SQLite storage...")
    init_db()

    while True:
        for symbol in SYMBOLS:
            params = {"symbol": symbol, "limit": 1}

            try:
                response = requests.get(
                    BINANCE_REST_URL, params=params, timeout=5
                )
                response.raise_for_status()
            except Exception as e:
                print("Request error:", e)
                continue

            trade = response.json()[0]

            tick = {
                "timestamp": datetime.fromtimestamp(trade["time"] / 1000),
                "symbol": symbol,
                "price": float(trade["price"]),
                "quantity": float(trade["qty"]),
            }

            insert_tick(tick)
            print(tick)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    poll_trades()
