# 📈 Real-Time Quant Pair Analytics Dashboard

A real-time quantitative analytics system for crypto trading pairs that performs
tick ingestion, resampling, statistical analysis, and interactive visualization
of mean-reversion signals such as Z-score.

---

## 🚀 Features

- Real-time tick ingestion from Binance
- Persistent storage using SQLite
- Tick → OHLCV resampling
- Pair analytics:
  - Hedge ratio (β)
  - Spread computation
  - Z-score (mean reversion signal)
  - Rolling correlation
- Interactive Streamlit dashboard
- KPI cards and alerts
- CSV export
- Auto-refreshing live view

---

## 🧠 Architecture Overview

Binance API
↓
Ingestion Layer (WebSocket / REST)
↓
SQLite Storage (ticks.db)
↓
Analytics Layer (Resampling + Statistics)
↓
Streamlit Dashboard (Visualization & Controls)

---

## 📂 Project Structure

real-time-quant-analytics/
│
├── ingestion/
│ └── binance_ws.py # Tick ingestion
│
├── storage/
│ └── db.py # SQLite persistence
│
├── analytics/
│ ├── resampling.py # Tick → OHLCV
│ └── pairs.py # Pair analytics (β, spread, z-score)
│
├── data/
│ └── ticks.db # Local tick database
│
├── app.py # Streamlit dashboard
├── requirements.txt
└── README.md

---

## 📊 Analytics Explained

### Hedge Ratio (β)
Computed using OLS regression:
y = α + βx

### Spread
spread = y - (α + βx)

### Z-Score (Mean Reversion)
z = (spread - mean) / std

### Why Z-Score?
- |z| > 2 → potential trading opportunity
- Used in statistical arbitrage strategies

---

## 🖥 Dashboard Features

- Symbol selection
- Timeframe selection
- Rolling window control
- KPI cards:
  - Z-score
  - Hedge ratio
  - Spread
  - Correlation
  - Data points
- Visual alerts
- CSV export

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
python ingestion/binance_ws.py
streamlit run app.py

