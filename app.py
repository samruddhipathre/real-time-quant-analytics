import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

from analytics.pair_analytics import run_pair_analytics

# -------------------------------------------------
# Page Config
# -------------------------------------------------

st.set_page_config(
    page_title="Real-Time Quant Analytics",
    layout="wide",
)

st.title("📈 Real-Time Quant Pair Analytics Dashboard")

# -------------------------------------------------
# Sidebar Controls
# -------------------------------------------------

st.sidebar.header("Controls")

symbol_x = st.sidebar.selectbox(
    "Select Symbol X",
    ["BTCUSDT", "ETHUSDT"],
    index=0,
)

symbol_y = st.sidebar.selectbox(
    "Select Symbol Y",
    ["ETHUSDT", "BTCUSDT"],
    index=1,
)

# --- Timeframe (FIXED & SAFE) ---
timeframe_label = st.sidebar.selectbox(
    "Timeframe",
    ["1 Second", "1 Minute", "5 Minutes"],
)

TIMEFRAME_MAP = {
    "1 Second": "1S",
    "1 Minute": "1min",
    "5 Minutes": "5min",
}

timeframe = TIMEFRAME_MAP[timeframe_label]

z_window = st.sidebar.slider(
    "Z-score Rolling Window",
    min_value=10,
    max_value=100,
    value=30,
    step=5,
)

refresh = st.sidebar.slider(
    "Refresh interval (seconds)",
    min_value=5,
    max_value=60,
    value=10,
    step=5,
)

# -------------------------------------------------
# Run Analytics
# -------------------------------------------------

with st.spinner("Running analytics..."):
    result = run_pair_analytics(
        symbol_x,
        symbol_y,
        timeframe,
        z_window,
    )

prices = result["prices"]
spread = result["spread"]
zscore = result["zscore"]
correlation = result["correlation"]
beta = result["beta"]

# -------------------------------------------------
# KPI Computation
# -------------------------------------------------

latest_spread = spread.dropna().iloc[-1] if not spread.dropna().empty else None
latest_z = zscore.dropna().iloc[-1] if not zscore.dropna().empty else None
latest_corr = (
    correlation.dropna().iloc[-1] if not correlation.dropna().empty else None
)

num_points = len(prices)

# -------------------------------------------------
# KPI Cards
# -------------------------------------------------

st.subheader("📊 Key Metrics")

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Z-Score", f"{latest_z:.2f}" if latest_z is not None else "N/A")
k2.metric("Hedge Ratio (β)", f"{beta:.4f}")
k3.metric("Spread", f"{latest_spread:.4f}" if latest_spread is not None else "N/A")
k4.metric("Correlation", f"{latest_corr:.2f}" if latest_corr is not None else "N/A")
k5.metric("Data Points", num_points)

# -------------------------------------------------
# Alerts
# -------------------------------------------------

if latest_z is not None:
    if latest_z > 2:
        st.error("🚨 Z-Score above +2 → Potential SHORT signal")
    elif latest_z < -2:
        st.success("🟢 Z-Score below -2 → Potential LONG signal")
    else:
        st.info("Z-Score within normal range")
else:
    st.warning("Not enough data yet for Z-score")

# -------------------------------------------------
# Charts
# -------------------------------------------------

col1, col2 = st.columns(2)

# --- Price Chart ---
with col1:
    st.subheader("Price Series")

    fig_price = go.Figure()
    fig_price.add_trace(go.Scatter(x=prices.index, y=prices["x"], name=symbol_x))
    fig_price.add_trace(go.Scatter(x=prices.index, y=prices["y"], name=symbol_y))

    fig_price.update_layout(
        height=400,
        xaxis_title="Time",
        yaxis_title="Price",
    )

    st.plotly_chart(fig_price, use_container_width=True)

# --- Spread Chart ---
with col2:
    st.subheader("Spread")

    fig_spread = go.Figure()
    fig_spread.add_trace(go.Scatter(x=spread.index, y=spread, name="Spread"))

    fig_spread.update_layout(
        height=400,
        xaxis_title="Time",
        yaxis_title="Spread",
    )

    st.plotly_chart(fig_spread, use_container_width=True)

# -------------------------------------------------
# Z-Score Chart with Bands
# -------------------------------------------------

st.subheader("📉 Z-Score (Mean Reversion Signal)")

fig_z = go.Figure()

fig_z.add_trace(
    go.Scatter(
        x=zscore.index,
        y=zscore,
        name="Z-Score",
        line=dict(color="cyan"),
    )
)

fig_z.add_hline(y=0, line_dash="dot", line_color="gray", annotation_text="Mean")
fig_z.add_hline(y=2, line_dash="dash", line_color="red", annotation_text="+2")
fig_z.add_hline(y=-2, line_dash="dash", line_color="green", annotation_text="-2")

fig_z.update_layout(
    height=320,
    xaxis_title="Time",
    yaxis_title="Z-Score",
)

st.plotly_chart(fig_z, use_container_width=True)

# -------------------------------------------------
# Data Export
# -------------------------------------------------

st.subheader("📥 Download Analytics")

export_df = pd.DataFrame(
    {
        "price_x": prices["x"],
        "price_y": prices["y"],
        "spread": spread,
        "zscore": zscore,
    }
)

st.download_button(
    label="Download analytics as CSV",
    data=export_df.dropna().to_csv().encode("utf-8"),
    file_name="pair_analytics.csv",
    mime="text/csv",
)

# -------------------------------------------------
# Auto Refresh
# -------------------------------------------------

time.sleep(refresh)
st.rerun()
