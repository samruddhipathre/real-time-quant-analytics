import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

from analytics.pairs import run_pair_analytics

# ---------------- Page Config ----------------

st.set_page_config(
    page_title="Real-Time Quant Pair Analytics",
    layout="wide",
)

# ---------------- Title ----------------

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

# ---------------- Run Analytics ----------------

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

latest_z = zscore.dropna().iloc[-1] if not zscore.dropna().empty else None

# ---------------- KPI Card Helper ----------------

def kpi_card(title, value, color="#00e5ff"):
    st.markdown(
        f"""
        <div style="
            background:#0f172a;
            padding:14px;
            border-radius:14px;
            text-align:center;
            height:90px;
            display:flex;
            flex-direction:column;
            justify-content:center;
            box-shadow:0 0 12px rgba(0,0,0,0.4);
        ">
            <div style="color:#94a3b8; font-size:13px; margin-bottom:6px;">
                {title}
            </div>
            <div style="color:{color}; font-size:26px; font-weight:600;">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------- KPI Section ----------------

st.markdown("## 📌 Key Metrics")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    kpi_card(
        "Z-Score",
        f"{latest_z:.2f}" if latest_z is not None else "—",
        "#22c55e" if latest_z is not None and abs(latest_z) < 2 else "#ef4444",
    )

with c2:
    kpi_card("Hedge Ratio (β)", f"{result['beta']:.4f}")

with c3:
    kpi_card(
        "Spread",
        f"{spread.iloc[-1]:.4f}" if not spread.empty else "—"
    )

with c4:
    kpi_card(
        "Correlation",
        f"{correlation.dropna().iloc[-1]:.2f}" if not correlation.dropna().empty else "—"
    )

with c5:
    kpi_card("Data Points", len(prices))

# ---------------- Alerts ----------------

if latest_z is not None:
    if abs(latest_z) > 2:
        st.error(f"🚨 Mean Reversion Signal ACTIVE | Z = {latest_z:.2f}")
    else:
        st.success(f"Z-score within normal range ({latest_z:.2f})")
else:
    st.warning("Not enough data yet to compute Z-score")

# ---------------- Charts ----------------

col1, col2 = st.columns(2)

with col1:
    st.subheader("Price Series")

    fig_price = go.Figure()
    fig_price.add_trace(go.Scatter(x=prices.index, y=prices["x"], name=symbol_x))
    fig_price.add_trace(go.Scatter(x=prices.index, y=prices["y"], name=symbol_y))

    fig_price.update_layout(
        height=400,
        xaxis_title="Time",
        yaxis_title="Price",
        template="plotly_dark",
    )

    st.plotly_chart(fig_price, use_container_width=True)

with col2:
    st.subheader("Spread")

    fig_spread = go.Figure()
    fig_spread.add_trace(go.Scatter(x=spread.index, y=spread, name="Spread"))

    fig_spread.update_layout(
        height=400,
        xaxis_title="Time",
        yaxis_title="Spread",
        template="plotly_dark",
    )

    st.plotly_chart(fig_spread, use_container_width=True)

# ---------------- Z-Score Chart ----------------

st.subheader("Z-Score (Mean Reversion Signal)")

fig_z = go.Figure()
fig_z.add_trace(go.Scatter(x=zscore.index, y=zscore, name="Z-score"))

fig_z.add_hline(y=2, line_dash="dash", line_color="red")
fig_z.add_hline(y=-2, line_dash="dash", line_color="green")
fig_z.add_hline(y=0, line_dash="dot", line_color="gray")

fig_z.update_layout(
    height=320,
    xaxis_title="Time",
    yaxis_title="Z-score",
    template="plotly_dark",
)

st.plotly_chart(fig_z, use_container_width=True)

# ---------------- Export ----------------

st.subheader("Download Analytics")

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
