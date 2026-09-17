import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import load_data, apply_plotly_theme, inject_css, page_header, insight, sidebar_badge, COLORS, YEAR_COLS, YEARS

st.set_page_config(page_title="Trends & Volatility", page_icon="📉", layout="wide", initial_sidebar_state="expanded")
apply_plotly_theme()
inject_css()
df = load_data()

with st.sidebar:
    sidebar_badge("📉 Trends & Volatility")
    st.caption("Global year-over-year patterns across all 199 countries.")

page_header("TRENDS & VOLATILITY", "Global Trends Over Time", "How B-visa refusal rates moved year by year, 2019–2025")

global_avg = df[YEAR_COLS].mean()
max_year = global_avg.idxmax()
min_year = global_avg.idxmin()

col1, col2 = st.columns([1.4, 1])

with col1:
    st.subheader("🌍 Global Average Refusal Rate by Year")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=YEARS, y=global_avg.values, mode="lines+markers",
                              line=dict(color=COLORS["primary"], width=3), marker=dict(size=9),
                              fill="tozeroy", fillcolor=COLORS["primary_light"]))
    fig.update_layout(height=400, yaxis_tickformat=".0%", yaxis_title="Avg refusal rate", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    insight(
        f"**{max_year}** had the highest global average refusal rate "
        f"({global_avg[max_year]*100:.1f}%), while **{min_year}** had the lowest "
        f"({global_avg[min_year]*100:.1f}%) — the 2020–2021 dip aligns with COVID-19 travel "
        f"restrictions reducing overall visa activity and shifting applicant mix."
    )

with col2:
    st.subheader("📦 Spread of Rates per Year")
    melted = df.melt(id_vars="Country", value_vars=YEAR_COLS, var_name="Year", value_name="Rate").dropna()
    fig = px.box(melted, x="Year", y="Rate", color="Year",
                 color_discrete_sequence=COLORS["sequence"])
    fig.update_layout(height=400, showlegend=False, yaxis_tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.write("")
st.subheader("↕️ Net Change: 2019 → 2025 (Top 15 Movers)")
change = df[["Country", "net_change"]].dropna().copy()
change["direction"] = change["net_change"].apply(lambda x: "Increase" if x >= 0 else "Decrease")
top_movers = pd.concat([
    change.sort_values("net_change", ascending=False).head(8),
    change.sort_values("net_change").head(7),
]).sort_values("net_change")

fig = px.bar(
    top_movers, x="net_change", y="Country", orientation="h", color="direction",
    color_discrete_map={"Increase": COLORS["negative"], "Decrease": COLORS["positive"]},
)
fig.update_layout(height=460, xaxis_tickformat="+.0%", xaxis_title="Change in refusal rate", yaxis_title="",
                   legend_title="")
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.write("")
st.subheader("⚡ Most Volatile Countries (Std. Deviation Across Years)")
volatile = df[["Country", "std_dev"]].dropna().sort_values("std_dev", ascending=False).head(10).sort_values("std_dev")
fig = px.bar(volatile, x="std_dev", y="Country", orientation="h",
             color_discrete_sequence=[COLORS["primary_dark"]])
fig.update_layout(height=400, xaxis_tickformat=".0%", xaxis_title="Std. deviation (2019-2025)", yaxis_title="")
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})