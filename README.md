# Real-Time Quant Pair Analytics Dashboard

A production-style real-time quantitative analytics system for crypto pairs using live market data.

## Features
- Live tick ingestion from Binance
- Persistent SQLite storage
- Tick-to-OHLCV resampling
- Pair trading analytics:
  - Hedge ratio (OLS regression)
  - Spread calculation
  - Rolling Z-score
  - Rolling correlation
  - ADF stationarity test
- Interactive Streamlit dashboard
- Auto-refresh & CSV export

## Tech Stack
- Python 3.10
- Pandas, NumPy
- Statsmodels
- SQLite
- Plotly
- Streamlit

## Project Structure
