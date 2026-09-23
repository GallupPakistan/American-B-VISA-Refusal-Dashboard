import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    load_data, apply_plotly_theme, inject_css, page_header, insight,
    get_iso_map, sidebar_badge, chip_list, COLORS, YEAR_COLS,
)

st.set_page_config(
    page_title="Visa Refusal Dashboard",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_plotly_theme()
inject_css()

df = load_data()

with st.sidebar:
    sidebar_badge("🌐 Visa Refusal Explorer")
    st.caption("US B-Visa refusal rates · 2019–2025 · 199 countries")
    st.divider()
    year = st.select_slider("Select year", options=YEAR_COLS, value="2025")
    st.divider()
    st.caption("Navigate using the pages above ⬆️")

page_header(
    "OVERVIEW",
    "Global B-Visa Refusal Dashboard",
    f"Snapshot of B-visa refusal rates across 199 countries for {year}",
)

year_data = df[["Country", year]].dropna()

# ---------------- EXECUTIVE SUMMARY ----------------
sel_idx = YEAR_COLS.index(year)
prev_year = YEAR_COLS[sel_idx - 1] if sel_idx > 0 else None
global_avg_now = year_data[year].mean()
very_high_count = int((year_data[year] >= 0.60).sum())
top_row_summary = year_data.loc[year_data[year].idxmax()]

yoy_line = ""
if prev_year:
    prev_data = df[["Country", prev_year]].dropna()
    global_avg_prev = prev_data[prev_year].mean()
    delta = (global_avg_now - global_avg_prev) * 100
    direction = "up" if delta >= 0 else "down"
    yoy_line = f" That's **{direction} {abs(delta):.1f} points** from {prev_year} ({global_avg_prev*100:.1f}%)."

st.info(
    f"📌 **Executive Summary — {year}:** Global average refusal rate is **{global_avg_now*100:.1f}%** "
    f"across {year_data.shape[0]} countries.{yoy_line} **{top_row_summary['Country']}** has the highest "
    f"rate ({top_row_summary[year]*100:.1f}%), and **{very_high_count} countries** are in the "
    f"\"Very High\" (60%+) risk band."
)

st.write("")

# ---------------- KPI CARDS ----------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Global Average", f"{year_data[year].mean()*100:.1f}%")
top_row = year_data.loc[year_data[year].idxmax()]
c2.metric("Highest Refusal Rate", f"{top_row[year]*100:.1f}%", top_row["Country"])
low_row = year_data.loc[year_data[year].idxmin()]
c3.metric("Lowest Refusal Rate", f"{low_row[year]*100:.1f}%", low_row["Country"])
c4.metric("Countries Covered", f"{year_data.shape[0]}")

st.write("")

# ---------------- BIGGEST MOVERS THIS YEAR (single-year YoY) ----------------
if prev_year:
    st.subheader(f"📣 Biggest Movers: {prev_year} → {year}")
    yoy_df = df[["Country", prev_year, year]].dropna().copy()
    yoy_df["change"] = (yoy_df[year] - yoy_df[prev_year]) * 100
    gainers = yoy_df.sort_values("change", ascending=False).head(5)
    decliners = yoy_df.sort_values("change", ascending=True).head(5)

    mc1, mc2 = st.columns(2)
    with mc1:
        st.markdown("**🔺 Rate increased most (worse)**")
        fig = go.Figure(go.Bar(
            x=gainers["change"], y=gainers["Country"], orientation="h",
            marker_color=COLORS["negative"], text=[f"+{v:.1f}%" for v in gainers["change"]],
            textposition="outside",
        ))
        fig.update_layout(height=260, xaxis_title="Change (pts)", yaxis_title="",
                           margin=dict(t=10, b=10), yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
    with mc2:
        st.markdown("**🔻 Rate decreased most (better)**")
        fig = go.Figure(go.Bar(
            x=decliners["change"], y=decliners["Country"], orientation="h",
            marker_color=COLORS["positive"], text=[f"{v:.1f}%" for v in decliners["change"]],
            textposition="outside",
        ))
        fig.update_layout(height=260, xaxis_title="Change (pts)", yaxis_title="",
                           margin=dict(t=10, b=10), yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
    insight(
        f"These are the sharpest single-year swings ({prev_year}→{year}), separate from the "
        f"2019→2025 long-term movers on the **Rankings** page."
    )
    st.write("")
col_left, col_right = st.columns([1.6, 1])

# ---------------- CHOROPLETH MAP ----------------
with col_left:
    st.subheader("🗺️ World Map — Refusal Rate")
    iso_map = get_iso_map(df["Country"].tolist())
    map_df = year_data.copy()
    map_df["iso3"] = map_df["Country"].map(iso_map)
    map_df = map_df.dropna(subset=["iso3"])
    fig = px.choropleth(
        map_df, locations="iso3", color=year,
        hover_name="Country",
        color_continuous_scale=COLORS["blue_scale"],
        range_color=(0, map_df[year].max()),
        labels={year: "Refusal Rate"},
    )
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Refusal rate: %{z:.1%}<extra></extra>"
    )
    fig.update_layout(
        geo=dict(bgcolor="rgba(0,0,0,0)", showframe=False, showcoastlines=False,
                 projection_type="natural earth"),
        coloraxis_colorbar=dict(tickformat=".0%", title=""),
        height=430, margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

# ---------------- HISTOGRAM ----------------
with col_right:
    st.subheader("📊 Distribution")

    # Build our own fixed 10%-wide bins so we can map a clicked bar back to an exact range
    n_bins = 10
    bin_edges = list(range(0, 101, 10))
    bin_labels = [f"{bin_edges[i]}-{bin_edges[i+1]}%" for i in range(n_bins)]
    pct = (year_data[year] * 100).clip(upper=99.999)  # keep 100% inside the last bin
    bin_idx = (pct // 10).astype(int).clip(upper=n_bins - 1)
    counts = bin_idx.value_counts().reindex(range(n_bins), fill_value=0)

    fig = go.Figure(go.Bar(
        x=bin_labels, y=counts.values,
        marker_color=COLORS["primary"],
    ))
    fig.update_layout(
        height=430, bargap=0.08,
        xaxis_title="Refusal rate", yaxis_title="Number of countries",
    )
    click = st.plotly_chart(
        fig, width='stretch', config={'displayModeBar': False},
        on_select="rerun", selection_mode="points", key="dist_hist",
    )

    clicked_points = click["selection"]["points"] if click and click.get("selection") else []
    if clicked_points:
        clicked_label = clicked_points[0]["x"]
        i = bin_labels.index(clicked_label)
        in_bin = year_data[bin_idx == i]
        st.caption(f"👆 {len(in_bin)} countries with a {clicked_label} refusal rate in {year}:")
        chip_list(in_bin["Country"].tolist(), kind="positive")
    else:
        st.caption("👆 Click a bar above to see which countries fall in that range.")

st.write("")
st.subheader("📊 Risk-Band Composition")

# compute band for the selected year dynamically
def band(x):
    if x < 0.20: return "Low (0-20%)"
    if x < 0.40: return "Moderate (20-40%)"
    if x < 0.60: return "High (40-60%)"
    return "Very High (60%+)"

bands = year_data[year].apply(band).value_counts().reindex(
    ["Low (0-20%)", "Moderate (20-40%)", "High (40-60%)", "Very High (60%+)"]
).fillna(0)

fig = go.Figure(go.Bar(
    x=bands.index, y=bands.values,
    marker=dict(color=[COLORS["sequence"][i] for i in (5, 3, 1, 0)]),
    text=bands.values.astype(int), textposition="outside",
))
fig.update_layout(
    height=380, showlegend=False,
    xaxis_title="", yaxis_title="Number of countries",
    margin=dict(t=30, b=10),
)
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

insight(
    f"In {year}, {int(bands['Very High (60%+)'])} countries had a refusal rate above 60%, "
    f"while {int(bands['Low (0-20%)'])} stayed under 20% — explore the **Rankings** and "
    f"**Country Spotlight** pages for details."
)

st.write("")
st.subheader("📊 Risk-Band Composition — Trend Across All Years")
band_order = ["Low (0-20%)", "Moderate (20-40%)", "High (40-60%)", "Very High (60%+)"]
band_colors = {band_order[i]: COLORS["sequence"][c] for i, c in zip(range(4), (5, 3, 1, 0))}
band_trend = {}
for yc in YEAR_COLS:
    col_bands = df[yc].dropna().apply(band).value_counts().reindex(band_order).fillna(0)
    band_trend[yc] = col_bands

fig = go.Figure()
for b in band_order:
    fig.add_trace(go.Bar(
        x=[int(y) for y in YEAR_COLS],
        y=[band_trend[yc][b] for yc in YEAR_COLS],
        name=b, marker_color=band_colors[b],
    ))
fig.update_layout(
    height=380, barmode="stack", xaxis_title="", yaxis_title="Number of countries",
    legend=dict(orientation="h", y=1.15), margin=dict(t=30, b=10),
)
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight(
    "This stacked view shows how many countries sat in each risk band every year — useful for spotting "
    "whether the world is drifting toward higher or lower refusal risk over time, not just in the year selected above."
)

st.caption(
    "📌 Data note: Western Sahara only has published refusal-rate data for 2019–2020; "
    "later years are shown as unavailable rather than zero."
)
