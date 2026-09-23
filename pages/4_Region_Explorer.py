import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import (
    load_data, apply_plotly_theme, inject_css, page_header, insight,
    sidebar_badge, get_iso_map, COLORS, YEAR_COLS,
)

st.set_page_config(page_title="Region Explorer", page_icon="🌏", layout="wide", initial_sidebar_state="expanded")
apply_plotly_theme()
inject_css()
df = load_data()

ALL_REGIONS = sorted(df["Region"].unique())

with st.sidebar:
    sidebar_badge("🌏 Region Explorer")
    region = st.selectbox("Select region", ["All Regions"] + ALL_REGIONS,
                           index=(["All Regions"] + ALL_REGIONS).index("Asia"))
    year = st.select_slider("Select year", options=YEAR_COLS, value="2025")

page_header("REGION EXPLORER", "B-Visa Refusal Rates by Region",
            f"Comparing {region if region != 'All Regions' else 'all regions'} for {year}")

year_data = df[["Country", "Region", year]].dropna()
scoped_for_kpi = year_data if region == "All Regions" else year_data[year_data["Region"] == region]

c1, c2, c3, c4 = st.columns(4)
c1.metric(f"Average — {region}", f"{scoped_for_kpi[year].mean()*100:.1f}%")
hi_row = scoped_for_kpi.loc[scoped_for_kpi[year].idxmax()]
c2.metric("Highest", f"{hi_row[year]*100:.1f}%", hi_row["Country"])
lo_row = scoped_for_kpi.loc[scoped_for_kpi[year].idxmin()]
c3.metric("Lowest", f"{lo_row[year]*100:.1f}%", lo_row["Country"])
c4.metric("Countries", f"{len(scoped_for_kpi)}")

st.write("")
# ---------------- 1. REGION COMPARISON BAR CHART (always shows every region) ----------------
st.subheader("🌐 Average Refusal Rate by Region")
region_avg = year_data.groupby("Region")[year].mean().sort_values(ascending=False) * 100
fig = go.Figure(go.Bar(
    x=region_avg.index, y=region_avg.values,
    marker_color=[COLORS["primary"] if r == region else COLORS["primary_light"] for r in region_avg.index],
    text=region_avg.round(1).astype(str) + "%", textposition="outside",
))
fig.update_layout(height=340, yaxis_title="Average refusal rate (%)", xaxis_title="", margin=dict(t=20, b=10))
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight("The selected region is highlighted in dark blue; others are shown lighter for context.")

st.write("")
# ---------------- 1.5 REGION TREND OVER TIME (all years, every region) ----------------
st.subheader("📈 Region Trend Over Time (2019–2025)")
region_year_avg = df.groupby("Region")[YEAR_COLS].mean().T  # index=year string, columns=region
region_year_avg.index = [int(y) for y in region_year_avg.index]
fig = go.Figure()
for i, reg in enumerate(sorted(region_year_avg.columns)):
    is_selected = (region == reg)
    fig.add_trace(go.Scatter(
        x=region_year_avg.index, y=region_year_avg[reg],
        mode="lines+markers", name=reg,
        line=dict(
            width=4 if is_selected else 2,
            color=COLORS["primary"] if is_selected else COLORS["sequence"][i % len(COLORS["sequence"])],
        ),
        opacity=1.0 if (region == "All Regions" or is_selected) else 0.35,
    ))
fig.update_layout(height=360, yaxis_tickformat=".0%", yaxis_title="Average refusal rate",
                   xaxis_title="", legend=dict(orientation="h", y=1.15))
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight(
    "All regions dipped around 2021–2022 and have climbed since. "
    + ("The selected region is bolded above so you can see whether it tracks the global pattern or moves differently."
       if region != "All Regions" else
       "Select a specific region from the sidebar to highlight its line.")
)

st.write("")
scoped = year_data if region == "All Regions" else year_data[year_data["Region"] == region]

col1, col2 = st.columns([1.4, 1])

# ---------------- 2. ZOOMED MAP WITH COUNTRY LABELS ----------------
with col1:
    st.subheader(f"🗺️ Map — {region if region != 'All Regions' else 'World'}")
    iso_map = get_iso_map(scoped["Country"].tolist())
    map_df = scoped.copy()
    map_df["iso3"] = map_df["Country"].map(iso_map)
    map_df = map_df.dropna(subset=["iso3"])

    fig = px.choropleth(
        map_df, locations="iso3", color=year,
        hover_name="Country",
        color_continuous_scale=COLORS["blue_scale"],
        range_color=(0, map_df[year].max()),
    )
    fig.update_traces(hovertemplate="<b>%{hovertext}</b><br>Refusal rate: %{z:.1%}<extra></extra>")
    fig.update_geos(fitbounds="locations", visible=False, projection_type="natural earth",
                     bgcolor="rgba(0,0,0,0)")
    fig.update_layout(
        height=460, margin=dict(l=0, r=0, t=10, b=0),
        coloraxis_colorbar=dict(tickformat=".0%", title=""),
    )
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
    st.caption("Hover any country for its exact name and refusal rate. Smaller countries are easiest to read via hover.")

# ---------------- 3. RANKED BAR CHART WITHIN REGION ----------------
with col2:
    st.subheader(f"📊 Countries in {region if region != 'All Regions' else 'All Regions'}")
    ranked = scoped.sort_values(year, ascending=True)
    show_labels = len(ranked) <= 40  # keep it readable when "All Regions" has ~199 bars
    fig = go.Figure(go.Bar(
        x=ranked[year] * 100, y=ranked["Country"], orientation="h",
        marker_color=COLORS["primary"],
        text=[f"{v*100:.1f}%" for v in ranked[year]] if show_labels else None,
        textposition="outside" if show_labels else None,
    ))
    bar_height = max(360, 22 * len(ranked))
    fig.update_layout(
        height=min(bar_height, 900), xaxis_title="Refusal rate (%)", yaxis_title="",
        margin=dict(t=10, b=10),
    )
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
    if not show_labels:
        st.caption("ℹ️ Bar labels are hidden here (too many countries) — hover any bar for its exact rate.")

# ---------------- 4. BOX PLOT — REGIONS SIDE BY SIDE ----------------
st.write("")
st.subheader("📦 Spread by Region — Box Plot")
fig = px.box(
    year_data, x="Region", y=year, color="Region",
    color_discrete_sequence=COLORS["sequence"],
)
fig.update_layout(
    height=420, showlegend=False, yaxis_tickformat=".0%",
    xaxis_title="", yaxis_title="Refusal rate",
)
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight(
    "Box plots show the median (middle line), the middle 50% of countries (box), and outliers (dots) "
    "for each region — useful for comparing consistency, not just averages."
)

# ---------------- 5. DISTRIBUTION HISTOGRAM FOR THE SELECTED REGION ----------------
st.write("")
st.subheader(f"📊 Distribution — {region if region != 'All Regions' else 'World'} ({year})")
fig = px.histogram(
    scoped, x=year, nbins=10,
    color_discrete_sequence=[COLORS["primary"]],
)
fig.update_traces(xbins=dict(start=0, end=1, size=0.1))
fig.update_layout(
    height=340, xaxis_tickformat=".0%", xaxis_title="Refusal rate",
    yaxis_title="Number of countries", margin=dict(t=10, b=10),
)
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
low_share = int((scoped[year] < 0.20).sum())
high_share = int((scoped[year] >= 0.60).sum())
insight(
    f"Within {region if region != 'All Regions' else 'the world'}, {low_share} of {len(scoped)} countries "
    f"sit under 20% refusal and {high_share} are at 60%+ — this shows whether the region is broadly "
    f"consistent or has a wide spread hiding behind its single average above."
)

# ---------------- 6. REGION VOLATILITY COMPARISON ----------------
st.write("")
st.subheader("⚡ Which Region Is Most Volatile?")
region_vol = df.groupby("Region")["std_dev"].mean().sort_values(ascending=False) * 100
fig = go.Figure(go.Bar(
    x=region_vol.index, y=region_vol.values,
    marker_color=[COLORS["primary"] if r == region else COLORS["primary_light"] for r in region_vol.index],
    text=[f"{v:.1f}" for v in region_vol.values], textposition="outside",
))
fig.update_layout(height=340, yaxis_title="Avg. std. deviation (points)", xaxis_title="", margin=dict(t=20, b=10))
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight("This averages each region's countries' own year-to-year volatility — a region can have a modest average rate but still be unstable underneath.")

# ---------------- 7. COUNTRIES PER REGION (COMPOSITION) ----------------
st.write("")
st.subheader("🗂️ Countries per Region")
region_count = df["Region"].value_counts().sort_values(ascending=True)
fig = go.Figure(go.Bar(
    x=region_count.values, y=region_count.index, orientation="h",
    marker_color=[COLORS["primary"] if r == region else COLORS["primary_light"] for r in region_count.index],
    text=region_count.values, textposition="outside",
))
fig.update_layout(height=340, xaxis_title="Number of countries", yaxis_title="", margin=dict(t=10, b=10))
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight("Context for every average shown above — a region with fewer countries is more sensitive to any single country's swing.")

# ---------------- 8. REGION NET CHANGE 2019 → 2025 ----------------
st.write("")
st.subheader("↕️ Region Net Change: 2019 → 2025")
region_net = (df.groupby("Region")["2025"].mean() - df.groupby("Region")["2019"].mean()).sort_values() * 100
fig = go.Figure(go.Bar(
    x=region_net.values, y=region_net.index, orientation="h",
    marker_color=[COLORS["negative"] if v >= 0 else COLORS["positive"] for v in region_net.values],
    text=[f"{v:+.1f}" for v in region_net.values], textposition="outside",
))
fig.update_layout(height=340, xaxis_title="Change in average refusal rate (points)", yaxis_title="",
                   margin=dict(t=10, b=10))
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight("Unlike the current-year snapshot above, this shows which region's average has moved the most over the full 7-year span.")

# ---------------- 9. HIGHEST-REFUSAL COUNTRY PER REGION ----------------
st.write("")
st.subheader(f"🚩 Highest-Refusal Country in Each Region — {year}")
leaders = year_data.loc[year_data.groupby("Region")[year].idxmax()].sort_values(year)
fig = go.Figure(go.Bar(
    x=leaders[year] * 100, y=leaders["Region"], orientation="h",
    marker_color=[COLORS["primary"] if r == region else COLORS["primary_light"] for r in leaders["Region"]],
    text=[f"{c} — {v*100:.1f}%" for c, v in zip(leaders["Country"], leaders[year])],
    textposition="outside",
))
fig.update_layout(height=340, xaxis_title="Refusal rate (%)", yaxis_title="", margin=dict(t=10, b=60))
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight("Each region's single highest-refusal country for the selected year — the country name is printed on its bar.")
