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
    fig.add_trace(go.Scatter(x=YEARS, y=global_avg.values, mode="lines+markers+text",
                              line=dict(color=COLORS["primary"], width=3), marker=dict(size=9),
                              fill="tozeroy", fillcolor=COLORS["primary_light"],
                              text=[f"{v*100:.1f}%" for v in global_avg.values],
                              textposition="top center"))
    fig.update_layout(height=400, yaxis_tickformat=".0%", yaxis_title="Avg refusal rate", xaxis_title="")
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
    insight(
        f"**{max_year}** had the highest global average refusal rate "
        f"({global_avg[max_year]*100:.1f}%), while **{min_year}** had the lowest "
        f"({global_avg[min_year]*100:.1f}%). Rates dipped through 2021–2022 — consistent with "
        f"reduced/altered visa activity during the COVID-19 period — before climbing back up "
        f"in the years that followed."
    )

with col2:
    st.subheader("📦 Spread of Rates per Year")
    melted = df.melt(id_vars="Country", value_vars=YEAR_COLS, var_name="Year", value_name="Rate").dropna()
    fig = px.box(melted, x="Year", y="Rate", color="Year",
                 color_discrete_sequence=COLORS["sequence"])
    fig.update_layout(height=400, showlegend=False, yaxis_tickformat=".0%")
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

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
    text_auto="+.1%",
)
fig.update_traces(textposition="outside")
fig.update_layout(height=460, xaxis_tickformat="+.0%", xaxis_title="Change in refusal rate", yaxis_title="",
                   legend_title="")
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

st.write("")
st.subheader("⚡ Most Volatile Countries (Std. Deviation Across Years)")
volatile = df[["Country", "std_dev"]].dropna().sort_values("std_dev", ascending=False).head(10).sort_values("std_dev")
fig = px.bar(volatile, x="std_dev", y="Country", orientation="h",
             color_discrete_sequence=[COLORS["primary_dark"]],
             text_auto=".1%")
fig.update_traces(textposition="outside")
fig.update_layout(height=400, xaxis_tickformat=".0%", xaxis_title="Std. deviation (2019-2025)", yaxis_title="")
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

st.write("")
st.subheader("📅 Year-over-Year Change in Global Average")
yoy = global_avg.diff().dropna() * 100  # percentage-point change vs prior year
yoy_years = [int(y) for y in yoy.index]
fig = go.Figure(go.Bar(
    x=yoy_years, y=yoy.values,
    marker_color=[COLORS["negative"] if v >= 0 else COLORS["positive"] for v in yoy.values],
    text=[f"{v:+.1f}%" for v in yoy.values], textposition="outside",
))
fig.update_layout(height=340, yaxis_title="Change vs prior year (pts)", xaxis_title="",
                   xaxis=dict(tickmode="array", tickvals=yoy_years))
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
biggest_jump_year = yoy.idxmax()
insight(
    f"This shows momentum year to year, not just the 2019→2025 total. The sharpest single-year jump was "
    f"**{biggest_jump_year}** ({yoy[biggest_jump_year]:+.1f} points vs the year before)."
)

st.write("")
st.subheader("🎯 Volatility vs. Average Rate — Is Instability Linked to Higher Refusals?")
scatter_df = df[["Country", "avg_rate", "std_dev"]].dropna()
corr = scatter_df["avg_rate"].corr(scatter_df["std_dev"])
fig = px.scatter(
    scatter_df, x="avg_rate", y="std_dev", hover_name="Country",
    color_discrete_sequence=[COLORS["primary"]], opacity=0.65,
)
fig.update_traces(marker=dict(size=9, line=dict(width=1, color="#FFFFFF")))
fig.update_layout(
    height=420, xaxis_tickformat=".0%", yaxis_tickformat=".0%",
    xaxis_title="7-year average refusal rate", yaxis_title="Volatility (std. deviation)",
)
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
strength = "a weak" if abs(corr) < 0.3 else ("a moderate" if abs(corr) < 0.6 else "a strong")
direction = "positive" if corr >= 0 else "negative"
insight(
    f"Each dot is a country. The correlation between average rate and volatility is **{corr:+.2f}** — "
    f"{strength} {direction} relationship, meaning countries with a higher average refusal rate tend to "
    f"{'also swing more year to year' if corr > 0 else 'not necessarily swing more year to year'}."
)

# ---------------- 7. 3-YEAR ROLLING AVERAGE (SMOOTHED TREND) ----------------
st.write("")
st.subheader("〜 3-Year Rolling Average (Smoothed Trend)")
rolling = global_avg.rolling(window=3, min_periods=1).mean()
fig = go.Figure()
fig.add_trace(go.Scatter(x=YEARS, y=global_avg.values, mode="lines+markers", name="Yearly average",
                          line=dict(color="#CBD5E1", width=2, dash="dot")))
fig.add_trace(go.Scatter(x=YEARS, y=rolling.values, mode="lines+markers+text", name="3-yr rolling avg",
                          line=dict(color=COLORS["primary_dark"], width=3), marker=dict(size=8),
                          text=[f"{v*100:.1f}%" for v in rolling.values], textposition="bottom center"))
fig.update_layout(height=360, yaxis_tickformat=".0%", yaxis_title="Refusal rate", xaxis_title="",
                   legend=dict(orientation="h", y=1.12))
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight("The smoothed (dark) line filters out single-year noise so the underlying direction is easier to read than the raw yearly average alone.")

# ---------------- 8. TRENDING UP vs DOWN (DONUT) ----------------
st.write("")
st.subheader("🍩 How Many Countries Are Trending Up vs Down (2019 → 2025)?")
trend_counts = df["net_change"].dropna().apply(lambda x: "Trending Up (worse)" if x > 0 else ("Trending Down (better)" if x < 0 else "No change")).value_counts()
fig = go.Figure(go.Pie(
    labels=trend_counts.index, values=trend_counts.values, hole=0.55,
    marker=dict(colors=[COLORS["negative"], COLORS["positive"], "#94A3B8"]),
    texttemplate="%{label}<br>%{value} countries", textposition="outside",
))
fig.update_layout(height=380, showlegend=False, margin=dict(t=20, b=10))
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight("A simple up/down split across all countries with data for both endpoint years — the long-run direction, ignoring the exact size of the move.")

# ---------------- 9. VOLATILITY DISTRIBUTION (ALL COUNTRIES) ----------------
st.write("")
st.subheader("📊 Volatility Distribution — All Countries")
fig = go.Figure(go.Histogram(
    x=df["std_dev"].dropna() * 100, nbinsx=20,
    marker_color=COLORS["primary_light"], marker_line=dict(color=COLORS["primary_dark"], width=1),
))
fig.update_layout(height=340, xaxis_title="Std. deviation (points)", yaxis_title="Number of countries",
                   margin=dict(t=20, b=10))
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight("Most countries cluster at low volatility (stable rates); the 'Most Volatile' bar chart above only showed the extreme tail — this shows the full picture.")

# ---------------- 10. MOST STABLE COUNTRIES (LOWEST VOLATILITY) ----------------
st.write("")
st.subheader("🧘 Most Stable Countries (Lowest Std. Deviation)")
stable = df[["Country", "std_dev"]].dropna().sort_values("std_dev", ascending=True).head(10).sort_values("std_dev", ascending=False)
fig = px.bar(stable, x="std_dev", y="Country", orientation="h",
             color_discrete_sequence=[COLORS["positive"]], text_auto=".1%")
fig.update_traces(textposition="outside")
fig.update_layout(height=400, xaxis_tickformat=".1%", xaxis_title="Std. deviation (2019-2025)", yaxis_title="",
                   margin=dict(t=10, b=10))
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight("The mirror image of the 'Most Volatile' chart — these countries' refusal rates barely moved across the 7 years.")
