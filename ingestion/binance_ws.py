import time
import requests
from datetime import datetime

BINANCE_REST_URL = "https://api.binance.com/api/v3/trades"
SYMBOLS = ["BTCUSDT", "ETHUSDT"]
POLL_INTERVAL = 1  # seconds


def poll_trades():
    print("Starting Binance REST polling...")

    last_trade_id = {symbol: None for symbol in SYMBOLS}

    while True:
        for symbol in SYMBOLS:
            params = {"symbol": symbol, "limit": 1}
            response = requests.get(BINANCE_REST_URL, params=params, timeout=5)

            if response.status_code != 200:
                print(f"Error fetching trades for {symbol}")
                continue

            trade = response.json()[0]

            if last_trade_id[symbol] == trade["id"]:
                continue

            last_trade_id[symbol] = trade["id"]

            tick = {
                "timestamp": datetime.fromtimestamp(trade["time"] / 1000),
                "symbol": symbol,
                "price": float(trade["price"]),
                "quantity": float(trade["qty"]),
            }

            print(tick)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    poll_trades()
