import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

from analytics.pair_analytics import run_pair_analytics
from analytics.resampling import get_ohlcv

st.set_page_config(
    page_title="Real-Time Quant Analytics",
    layout="wide",
)

st.title("📈 Real-Time Quant Pair Analytics Dashboard")

# ---------------- Sidebar Controls ----------------

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

timeframe = st.sidebar.selectbox(
    "Timeframe",
    {
        "1 Second": "1S",
        "1 Minute": "1min",
        "5 Minutes": "5min",
    },
)

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

# ---------------- Load Data ----------------

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

# ---------------- Alerts ----------------

latest_z = zscore.dropna().iloc[-1] if not zscore.dropna().empty else None

if latest_z is not None and abs(latest_z) > 2:
    st.error(f"🚨 ALERT: |Z-score| > 2 ({latest_z:.2f})")
elif latest_z is not None:
    st.success(f"Z-score is normal ({latest_z:.2f})")
else:
    st.warning("Not enough data yet for Z-score")

# ---------------- Charts ----------------

col1, col2 = st.columns(2)

with col1:
    st.subheader("Price Series")

    fig_price = go.Figure()
    fig_price.add_trace(
        go.Scatter(
            x=prices.index,
            y=prices["x"],
            name=symbol_x,
        )
    )
    fig_price.add_trace(
        go.Scatter(
            x=prices.index,
            y=prices["y"],
            name=symbol_y,
        )
    )

    fig_price.update_layout(
        height=400,
        xaxis_title="Time",
        yaxis_title="Price",
    )

    st.plotly_chart(fig_price, use_container_width=True)

with col2:
    st.subheader("Spread")

    fig_spread = go.Figure()
    fig_spread.add_trace(
        go.Scatter(
            x=spread.index,
            y=spread,
            name="Spread",
        )
    )

    fig_spread.update_layout(
        height=400,
        xaxis_title="Time",
        yaxis_title="Spread",
    )

    st.plotly_chart(fig_spread, use_container_width=True)

st.subheader("Z-score")

fig_z = go.Figure()
fig_z.add_trace(
    go.Scatter(
        x=zscore.index,
        y=zscore,
        name="Z-score",
    )
)

fig_z.add_hline(y=2, line_dash="dash", line_color="red")
fig_z.add_hline(y=-2, line_dash="dash", line_color="red")

fig_z.update_layout(
    height=300,
    xaxis_title="Time",
    yaxis_title="Z-score",
)

st.plotly_chart(fig_z, use_container_width=True)

# ---------------- Data Export ----------------

st.subheader("Download Data")

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

# ---------------- Auto Refresh ----------------

time.sleep(refresh)
st.rerun()

