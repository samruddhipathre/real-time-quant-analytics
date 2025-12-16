import sqlite3
from pathlib import Path
from datetime import datetime

# Absolute project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Database path (stable, no cwd issues)
DB_PATH = BASE_DIR / "data"
DB_PATH.mkdir(exist_ok=True)
DB_FILE = DB_PATH / "ticks.db"

print("DB FILE PATH:", DB_FILE)


def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ticks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            symbol TEXT NOT NULL,
            price REAL NOT NULL,
            quantity REAL NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


def insert_tick(tick: dict):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO ticks (timestamp, symbol, price, quantity)
        VALUES (?, ?, ?, ?)
        """,
        (
            tick["timestamp"].isoformat()
            if isinstance(tick["timestamp"], datetime)
            else tick["timestamp"],
            tick["symbol"],
            tick["price"],
            tick["quantity"],
        ),
    )

    conn.commit()
    conn.close()


def fetch_recent_ticks(symbol: str, limit: int = 1000):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT timestamp, symbol, price, quantity
        FROM ticks
        WHERE symbol = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (symbol, limit),
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def debug_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ticks")
    count = cursor.fetchone()[0]
    conn.close()
    return count
