import streamlit as st
import plotly.graph_objects as go
from utils import load_data, apply_plotly_theme, inject_css, page_header, insight, sidebar_badge, COLORS, YEAR_COLS, YEARS

st.set_page_config(page_title="Country Spotlight", page_icon="🔎", layout="wide", initial_sidebar_state="expanded")
apply_plotly_theme()
inject_css()
df = load_data()

with st.sidebar:
    sidebar_badge("🔎 Country Spotlight")
    countries_sorted = sorted(df["Country"].unique())
    default_idx = countries_sorted.index("Pakistan") if "Pakistan" in countries_sorted else 0
    country = st.selectbox("Select a country", countries_sorted, index=default_idx)
    year = st.select_slider("Select year", options=YEAR_COLS, value="2025")

row = df[df["Country"] == country].iloc[0]
page_header("COUNTRY SPOTLIGHT", country, "Historic B-Visa refusal trend, extremes, and standing vs. the world")

global_avg_by_year = df[YEAR_COLS].mean()

# Only look at years up to (and including) the year selected in the sidebar
sel_idx = YEAR_COLS.index(year)
visible_year_cols = YEAR_COLS[:sel_idx + 1]
visible_years = YEARS[:sel_idx + 1]

c1, c2, c3, c4 = st.columns(4)
avg_to_date = sum(row[c] for c in visible_year_cols) / len(visible_year_cols)
c1.metric(f"{len(visible_year_cols)}-Year Average", f"{avg_to_date*100:.1f}%")
c2.metric("Highest", f"{row['max_rate']*100:.1f}%", f"in {row['max_year']}")
c3.metric("Lowest", f"{row['min_rate']*100:.1f}%", f"in {row['min_year']}")
delta_vs_global = (row[year] - global_avg_by_year[year]) * 100
c4.metric(f"{year} vs Global Avg", f"{row[year]*100:.1f}%", f"{delta_vs_global:+.1f} pts")

st.write("")
col1, col2 = st.columns([1.4, 1])

with col1:
    st.subheader(f"📈 Historic Trend (2019–{year})")
    vals = [row[c] for c in visible_year_cols]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=visible_years, y=vals, mode="lines+markers", name=country,
                              line=dict(color=COLORS["primary"], width=3), marker=dict(size=8)))
    local_max, local_min = max(vals), min(vals)
    max_idx = vals.index(local_max)
    min_idx = vals.index(local_min)
    fig.add_annotation(x=visible_years[max_idx], y=vals[max_idx], text="Max", showarrow=True, arrowhead=2)
    fig.add_annotation(x=visible_years[min_idx], y=vals[min_idx], text="Min", showarrow=True, arrowhead=2)
    fig.update_layout(height=400, yaxis_tickformat=".0%", yaxis_title="Refusal rate", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col2:
    st.subheader("⚖️ vs. Global Average")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=visible_years, y=[row[c] for c in visible_year_cols], name=country,
                          marker_color=COLORS["primary"]))
    fig.add_trace(go.Bar(x=visible_years, y=[global_avg_by_year[c] for c in visible_year_cols], name="Global Avg",
                          marker_color=COLORS["sequence"][4]))
    fig.update_layout(height=400, barmode="group", yaxis_tickformat=".0%",
                       legend=dict(orientation="h", y=1.1, itemclick=False, itemdoubleclick=False))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.write("")
st.subheader(f"📍 {year} Standing Relative to Global Range")
gmin, gmax, gavg = df[year].min(), df[year].max(), df[year].mean()
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=row[year] * 100,
    number={"suffix": "%"},
    gauge={
        "axis": {"range": [0, gmax * 100]},
        "bar": {"color": COLORS["primary"]},
        "steps": [
            {"range": [0, gavg * 100], "color": COLORS["primary_light"]},
            {"range": [gavg * 100, gmax * 100], "color": "#F1F5F9"},
        ],
        "threshold": {"line": {"color": COLORS["negative"], "width": 3},
                      "thickness": 0.8, "value": gavg * 100},
    },
))
fig.update_layout(height=280, margin=dict(t=30, b=10))
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

insight(
    f"{country}'s refusal rate peaked at {row['max_rate']*100:.1f}% in {row['max_year']} and "
    f"bottomed out at {row['min_rate']*100:.1f}% in {row['min_year']}. "
    f"The orange line on the gauge marks the {year} global average ({gavg*100:.1f}%)."
)