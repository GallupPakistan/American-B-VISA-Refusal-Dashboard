import streamlit as st
import pandas as pd
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
region = row["Region"]
page_header("COUNTRY SPOTLIGHT", country, f"Historic B-Visa refusal trend, extremes, and standing vs. the world · Region: {region}")

global_avg_by_year = df[YEAR_COLS].mean()
region_avg_by_year = df[df["Region"] == region][YEAR_COLS].mean()

# Only look at years up to (and including) the year selected in the sidebar
sel_idx = YEAR_COLS.index(year)
visible_year_cols = YEAR_COLS[:sel_idx + 1]
visible_years = YEARS[:sel_idx + 1]

c1, c2, c3, c4, c5 = st.columns(5)
available_vals = [row[c] for c in visible_year_cols if pd.notna(row[c])]
if available_vals:
    avg_to_date = sum(available_vals) / len(available_vals)
    c1.metric(f"{len(available_vals)}-Year Average", f"{avg_to_date*100:.1f}%")
else:
    c1.metric("Average", "No data")

if pd.notna(row['max_rate']):
    c2.metric("Highest", f"{row['max_rate']*100:.1f}%", f"in {row['max_year']}")
else:
    c2.metric("Highest", "No data")

if pd.notna(row['min_rate']):
    c3.metric("Lowest", f"{row['min_rate']*100:.1f}%", f"in {row['min_year']}")
else:
    c3.metric("Lowest", "No data")

if pd.notna(row[year]):
    delta_vs_global = (row[year] - global_avg_by_year[year]) * 100
    c4.metric(f"{year} vs Global Avg", f"{row[year]*100:.1f}%", f"{delta_vs_global:+.1f} pts")
    delta_vs_region = (row[year] - region_avg_by_year[year]) * 100
    c5.metric(f"{year} vs {region} Avg", f"{row[year]*100:.1f}%", f"{delta_vs_region:+.1f} pts")
else:
    c4.metric(f"{year} vs Global Avg", "No data")
    c5.metric(f"{year} vs {region} Avg", "No data")
    st.warning(f"⚠️ No refusal-rate data is available for **{country}** in **{year}**. "
               f"Showing whatever history exists below.")

st.write("")
col1, col2 = st.columns([1.4, 1])

with col1:
    st.subheader(f"📈 Historic Trend (2019–{year})")
    # Only plot years that actually have data for this country
    plot_years = [y for y, c in zip(visible_years, visible_year_cols) if pd.notna(row[c])]
    vals = [row[c] for c in visible_year_cols if pd.notna(row[c])]
    if vals:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=plot_years, y=vals, mode="lines+markers+text", name=country,
                                  line=dict(color=COLORS["primary"], width=3), marker=dict(size=8),
                                  text=[f"{v*100:.1f}%" for v in vals], textposition="top center"))
        local_max, local_min = max(vals), min(vals)
        max_idx = vals.index(local_max)
        min_idx = vals.index(local_min)
        fig.add_annotation(x=plot_years[max_idx], y=vals[max_idx], text="Max", showarrow=True, arrowhead=2)
        fig.add_annotation(x=plot_years[min_idx], y=vals[min_idx], text="Min", showarrow=True, arrowhead=2)
        fig.update_layout(height=400, yaxis_tickformat=".0%", yaxis_title="Refusal rate", xaxis_title="")
        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
    else:
        st.info(f"No historic data available for {country} up to {year}.")

with col2:
    st.subheader(f"⚖️ vs. Global & Region Average")
    bar_years = [y for y, c in zip(visible_years, visible_year_cols) if pd.notna(row[c])]
    bar_country_vals = [row[c] for c in visible_year_cols if pd.notna(row[c])]
    bar_global_vals = [global_avg_by_year[c] for c in visible_year_cols if pd.notna(row[c])]
    bar_region_vals = [region_avg_by_year[c] for c in visible_year_cols if pd.notna(row[c])]
    if bar_years:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=bar_years, y=bar_country_vals, name=country,
                              marker_color=COLORS["primary"],
                              text=[f"{v*100:.1f}%" for v in bar_country_vals], textposition="outside"))
        fig.add_trace(go.Bar(x=bar_years, y=bar_region_vals, name=f"{region} Avg",
                              marker_color=COLORS["sequence"][2],
                              text=[f"{v*100:.1f}%" for v in bar_region_vals], textposition="outside"))
        fig.add_trace(go.Bar(x=bar_years, y=bar_global_vals, name="Global Avg",
                              marker_color=COLORS["sequence"][4],
                              text=[f"{v*100:.1f}%" for v in bar_global_vals], textposition="outside"))
        fig.update_layout(height=430, barmode="group", yaxis_tickformat=".0%",
                           legend=dict(orientation="h", y=1.1, itemclick=False, itemdoubleclick=False))
        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
    else:
        st.info(f"No historic data available for {country} up to {year}.")

st.write("")
st.subheader(f"📍 {year} Standing Relative to Global Range")
gmin, gmax, gavg = df[year].min(), df[year].max(), df[year].mean()
if pd.notna(row[year]):
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
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
else:
    st.info(f"No {year} data available for {country} to plot on the gauge.")

if pd.notna(row['max_rate']):
    insight(
        f"{country}'s refusal rate peaked at {row['max_rate']*100:.1f}% in {row['max_year']} and "
        f"bottomed out at {row['min_rate']*100:.1f}% in {row['min_year']}. "
        f"The orange line on the gauge marks the {year} global average ({gavg*100:.1f}%); "
        f"the {region} regional average that year was {region_avg_by_year[year]*100:.1f}%."
    )
else:
    insight(f"No refusal-rate history is available for {country}.")

# ---------------- 4. GLOBAL DISTRIBUTION WITH THIS COUNTRY MARKED ----------------
st.write("")
st.subheader(f"📊 Where {country} Sits in the {year} Global Distribution")
year_all = df[year].dropna()
fig = go.Figure(go.Histogram(
    x=year_all * 100, nbinsx=20, marker_color=COLORS["primary_light"],
    marker_line=dict(color=COLORS["primary"], width=1), name="All countries",
))
if pd.notna(row[year]):
    rank_this_year = int((year_all > row[year]).sum()) + 1
    fig.add_vline(x=row[year] * 100, line_width=3, line_dash="dash", line_color=COLORS["negative"],
                  annotation_text=f"{country}: {row[year]*100:.1f}%", annotation_position="top")
fig.update_layout(height=340, xaxis_title="Refusal rate (%)", yaxis_title="Number of countries",
                   showlegend=False, margin=dict(t=40, b=10))
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
if pd.notna(row[year]):
    insight(
        f"{country} ranks **#{rank_this_year} of {len(year_all)}** countries in {year} "
        f"(#1 = highest refusal rate) — the dashed line marks where it sits among everyone else."
    )

# ---------------- 5. PER-COUNTRY YEAR-OVER-YEAR CHANGE ----------------
st.write("")
st.subheader(f"📅 {country}'s Year-over-Year Change")
own_series = row[YEAR_COLS]
own_yoy = own_series.astype(float).diff().dropna() * 100
if own_yoy.notna().any():
    yoy_years_c = [int(y) for y in own_yoy.index]
    fig = go.Figure(go.Bar(
        x=yoy_years_c, y=own_yoy.values,
        marker_color=[COLORS["negative"] if v >= 0 else COLORS["positive"] for v in own_yoy.values],
        text=[f"{v:+.1f}%" for v in own_yoy.values], textposition="outside",
    ))
    fig.update_layout(height=320, yaxis_title="Change vs prior year (pts)", xaxis_title="",
                       xaxis=dict(tickmode="array", tickvals=yoy_years_c), margin=dict(t=20, b=10))
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
    insight(f"{country}'s own year-to-year momentum, separate from the global YoY chart on **Trends & Volatility**.")
else:
    st.info(f"Not enough consecutive-year data for {country} to compute year-over-year change.")

# ---------------- 6. RANK-OVER-TIME ----------------
st.write("")
st.subheader(f"🏁 {country}'s Rank Over Time")
rank_over_time = []
for yc in YEAR_COLS:
    yc_all = df[yc].dropna()
    if pd.notna(row[yc]):
        r = int((yc_all > row[yc]).sum()) + 1
        rank_over_time.append((int(yc), r, len(yc_all)))
if rank_over_time:
    rot_years = [t[0] for t in rank_over_time]
    rot_ranks = [t[1] for t in rank_over_time]
    rot_totals = [t[2] for t in rank_over_time]
    fig = go.Figure(go.Scatter(
        x=rot_years, y=rot_ranks, mode="lines+markers+text",
        line=dict(color=COLORS["primary_dark"], width=3), marker=dict(size=9),
        text=[f"#{r}" for r in rot_ranks], textposition="top center",
    ))
    fig.update_layout(
        height=320, yaxis_title="Rank (#1 = highest refusal rate)", xaxis_title="",
        yaxis=dict(autorange="reversed"), margin=dict(t=30, b=10),
    )
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
    insight(f"Lower on this chart = higher rank (closer to #1, the world's highest refusal rate).")
else:
    st.info(f"Not enough data to trace {country}'s rank over time.")

# ---------------- 7. METRIC PROFILE RADAR ----------------
st.write("")
st.subheader(f"🕸️ {country}'s Metric Profile")
if pd.notna(row['avg_rate']):
    radar_metrics = ["7yr Average", "Highest", "Lowest", f"{year} Rate", "Volatility (Std Dev)"]
    radar_vals = [
        row['avg_rate'] * 100, row['max_rate'] * 100, row['min_rate'] * 100,
        (row[year] * 100 if pd.notna(row[year]) else 0), row['std_dev'] * 100,
    ]
    fig = go.Figure(go.Scatterpolar(
        r=radar_vals + [radar_vals[0]], theta=radar_metrics + [radar_metrics[0]],
        fill="toself", line=dict(color=COLORS["primary"], width=2),
        fillcolor=COLORS["primary_light"],
    ))
    fig.update_layout(
        height=380, polar=dict(radialaxis=dict(visible=True, ticksuffix="%")),
        showlegend=False, margin=dict(t=30, b=10),
    )
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
    insight("A quick visual fingerprint combining five metrics at once — a bigger, more lopsided shape means more extreme or more volatile.")
else:
    st.info(f"Not enough data to build a metric profile for {country}.")

# ---------------- 8. YEARS ABOVE GLOBAL AVERAGE (DONUT) ----------------
st.write("")
st.subheader(f"🍩 Years {country} Was Above the Global Average")
comparable_years = [yc for yc in YEAR_COLS if pd.notna(row[yc])]
above = sum(1 for yc in comparable_years if row[yc] > global_avg_by_year[yc])
below = len(comparable_years) - above
if comparable_years:
    fig = go.Figure(go.Pie(
        labels=["Above global average", "At or below global average"], values=[above, below],
        hole=0.55, marker=dict(colors=[COLORS["negative"], COLORS["positive"]]),
        texttemplate="%{label}<br>%{value} yrs", textposition="outside",
    ))
    fig.update_layout(height=340, showlegend=False, margin=dict(t=20, b=10))
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
    insight(f"Out of {len(comparable_years)} years with data, {country} was above the global average in {above} of them.")

# ---------------- 9. REGIONAL PEER COMPARISON ----------------
st.write("")
st.subheader(f"👥 {country} vs. Its Top {region} Peers — {year}")
region_peers = df[(df["Region"] == region) & df[year].notna()].sort_values(year, ascending=False)
peer_set = region_peers.head(5).copy()
if country not in peer_set["Country"].values and country in region_peers["Country"].values:
    own_row_df = region_peers[region_peers["Country"] == country]
    peer_set = pd.concat([peer_set.head(4), own_row_df])
if not peer_set.empty:
    peer_set = peer_set.sort_values(year)
    fig = go.Figure(go.Bar(
        x=peer_set[year] * 100, y=peer_set["Country"], orientation="h",
        marker_color=[COLORS["negative"] if c == country else COLORS["primary_light"] for c in peer_set["Country"]],
        text=[f"{v*100:.1f}%" for v in peer_set[year]], textposition="outside",
    ))
    fig.update_layout(height=320, xaxis_title="Refusal rate (%)", yaxis_title="", margin=dict(t=20, b=10))
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
    insight(f"{country} highlighted in orange, shown against the highest-refusal countries in {region} for {year}.")
else:
    st.info(f"Not enough {region} peer data for {year} to build this comparison.")

# ---------------- 10. VOLATILITY GAUGE ----------------
st.write("")
st.subheader(f"⚡ {country}'s Volatility vs. the Most Volatile Country")
if pd.notna(row['std_dev']):
    max_std = df["std_dev"].max()
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=row['std_dev'] * 100,
        number={"suffix": " pts"},
        gauge={
            "axis": {"range": [0, max_std * 100]},
            "bar": {"color": COLORS["primary_dark"]},
            "steps": [{"range": [0, df["std_dev"].mean() * 100], "color": COLORS["primary_light"]}],
        },
    ))
    fig.update_layout(height=280, margin=dict(t=30, b=10))
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
    insight(
        f"{country}'s year-to-year swing (standard deviation of {row['std_dev']*100:.1f} points) compared "
        f"against the most volatile country in the dataset ({max_std*100:.1f} points)."
    )
else:
    st.info(f"Not enough data to compute volatility for {country}.")
