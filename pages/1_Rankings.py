import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import load_data, apply_plotly_theme, inject_css, page_header, insight, sidebar_badge, COLORS, YEAR_COLS

st.set_page_config(page_title="Rankings", page_icon="🏆", layout="wide", initial_sidebar_state="expanded")
apply_plotly_theme()
inject_css()
df = load_data()

with st.sidebar:
    sidebar_badge("🏆 Rankings")
    year = st.select_slider("Select year", options=YEAR_COLS, value="2025")
    country_filter = st.multiselect(
        "Filter countries (optional)", sorted(df["Country"].unique()),
        placeholder="All countries shown by default",
    )

if country_filter:
    df = df[df["Country"].isin(country_filter)]

page_header("RANKINGS", "Top & Bottom Countries", f"Ranked by B-visa refusal rate in {year}")
if country_filter:
    st.info(f"📌 Rankings below are computed within your **{len(country_filter)} selected countries** only, not all 199.")

year_data = df[["Country", year]].dropna().sort_values(year, ascending=False)
if year_data.empty:
    st.warning(f"⚠️ None of your selected countries have data for {year}. Try a different year or adjust the filter.")
    st.stop()

top10 = year_data.head(10).sort_values(year)
bottom10 = year_data.tail(10).sort_values(year, ascending=False)

col1, col2 = st.columns(2)
with col1:
    st.subheader("🔺 Top 10 — Highest Refusal Rate")
    fig = px.bar(top10, x=year, y="Country", orientation="h",
                 color_discrete_sequence=[COLORS["negative"]],
                 text_auto=".1%")
    fig.update_traces(textposition="outside")
    fig.update_layout(height=420, xaxis_tickformat=".0%", yaxis_title="", xaxis_title="Refusal rate")
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

with col2:
    st.subheader("🔻 Bottom 10 — Lowest Refusal Rate")
    fig = px.bar(bottom10, x=year, y="Country", orientation="h",
                 color_discrete_sequence=[COLORS["positive"]],
                 text_auto=".1%")
    fig.update_traces(textposition="outside")
    fig.update_layout(height=420, xaxis_tickformat=".0%", yaxis_title="", xaxis_title="Refusal rate")
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

# ---------------- MIDDLE COUNTRIES — HORIZONTAL DOT PLOT ----------------
st.write("")
top10_names = set(top10["Country"])
bottom10_names = set(bottom10["Country"])
middle = year_data[~year_data["Country"].isin(top10_names | bottom10_names)]

st.subheader(f"⚪ The Remaining {len(middle)} Countries")
fig = go.Figure(go.Scatter(
    x=middle[year], y=[""] * len(middle),
    mode="markers",
    marker=dict(size=9, color=COLORS["primary"], opacity=0.55,
                line=dict(width=1, color="#FFFFFF")),
    customdata=middle["Country"],
    hovertemplate="<b>%{customdata}</b><br>Refusal rate: %{x:.1%}<extra></extra>",
))
fig.update_layout(
    height=180,
    xaxis=dict(title="Refusal rate", tickformat=".0%"),
    yaxis=dict(visible=False),
    margin=dict(t=10, b=40, l=10, r=10),
)
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight(
    f"These {len(middle)} countries fall outside both the Top 10 and Bottom 10 — hover any dot "
    f"to see the country and its exact {year} refusal rate."
)

st.write("")
st.subheader("🔁 Top-10 Movement: 2019 vs 2025")
top2019 = set(df[["Country", "2019"]].dropna().sort_values("2019", ascending=False).head(10)["Country"])
top2025 = set(df[["Country", "2025"]].dropna().sort_values("2025", ascending=False).head(10)["Country"])
new_entries = top2025 - top2019
dropped = top2019 - top2025

movers = df[df["Country"].isin(new_entries | dropped)][["Country", "net_change"]].copy()
movers["status"] = movers["Country"].apply(lambda c: "Entered Top 10" if c in new_entries else "Dropped out")
movers = movers.sort_values("net_change")

if movers.empty:
    st.info("No change in the Top 10 between 2019 and 2025.")
else:
    fig = px.bar(
        movers, x="net_change", y="Country", orientation="h", color="status",
        color_discrete_map={"Entered Top 10": COLORS["negative"], "Dropped out": COLORS["positive"]},
        text_auto="+.1%",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=max(280, 40 * len(movers)), xaxis_tickformat="+.0%",
        xaxis_title="Change in refusal rate (2019 → 2025)", yaxis_title="", legend_title="",
    )
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

st.write("")
# ---------------- 6. RANK MOVEMENT: 2019 RANK vs 2025 RANK (SCATTER) ----------------
st.subheader("↗️ Rank Movement: 2019 Rank vs 2025 Rank")
rank_df = df[["Country", "2019", "2025"]].dropna().copy()
rank_df["rank_2019"] = rank_df["2019"].rank(ascending=False, method="min").astype(int)
rank_df["rank_2025"] = rank_df["2025"].rank(ascending=False, method="min").astype(int)
n_countries = len(rank_df)
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=[1, n_countries], y=[1, n_countries], mode="lines",
    line=dict(color="#CBD5E1", width=2, dash="dash"), showlegend=False, hoverinfo="skip",
))
fig.add_trace(go.Scatter(
    x=rank_df["rank_2019"], y=rank_df["rank_2025"], mode="markers",
    marker=dict(size=7, color=COLORS["primary"], opacity=0.6, line=dict(width=1, color="#FFFFFF")),
    customdata=rank_df["Country"],
    hovertemplate="<b>%{customdata}</b><br>2019 Rank: #%{x}<br>2025 Rank: #%{y}<extra></extra>",
))
fig.update_layout(
    height=420, showlegend=False,
    xaxis_title="Rank in 2019 (#1 = highest refusal rate)",
    yaxis_title="Rank in 2025", margin=dict(t=20, b=10),
)
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight(
    "Dots on the dashed line kept the same rank; dots above it fell to a higher (worse) rank in "
    "2025, dots below it improved — a quick view of how much the whole ranking reshuffled."
)

# ---------------- 7. REGIONAL MAKE-UP OF THE TOP 20 (DONUT) ----------------
st.write("")
st.subheader(f"🍩 Regional Make-up of the {year} Top 20")
top20 = year_data.head(20).merge(df[["Country", "Region"]], on="Country")
region_counts_top20 = top20["Region"].value_counts()
fig = go.Figure(go.Pie(
    labels=region_counts_top20.index, values=region_counts_top20.values, hole=0.5,
    marker=dict(colors=COLORS["sequence"]),
    texttemplate="%{label}<br>%{percent}", textposition="outside",
))
fig.update_layout(height=380, showlegend=False, margin=dict(t=20, b=10))
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
top_region = region_counts_top20.idxmax()
insight(
    f"**{top_region}** contributes the most countries ({int(region_counts_top20.max())} of 20) to this "
    f"year's highest-refusal group."
)

# ---------------- 8. FULL DISTRIBUTION STRIP: TOP10 / MIDDLE / BOTTOM10 ----------------
st.write("")
st.subheader(f"🎯 All {len(year_data)} Countries at a Glance — {year}")
strip_df = year_data.copy()
strip_df["Tier"] = strip_df["Country"].apply(
    lambda c: "Top 10" if c in top10_names else ("Bottom 10" if c in bottom10_names else "Middle")
)
tier_colors = {"Top 10": COLORS["negative"], "Bottom 10": COLORS["positive"], "Middle": "#94A3B8"}
fig = go.Figure()
for tier in ["Top 10", "Middle", "Bottom 10"]:
    sub = strip_df[strip_df["Tier"] == tier]
    fig.add_trace(go.Scatter(
        x=sub[year], y=[tier] * len(sub), mode="markers", name=tier,
        marker=dict(size=8, color=tier_colors[tier], opacity=0.7 if tier == "Middle" else 0.9),
        customdata=sub["Country"],
        hovertemplate="<b>%{customdata}</b><br>Rate: %{x:.1%}<extra></extra>",
    ))
fig.update_layout(
    height=260, xaxis=dict(title="Refusal rate", tickformat=".0%"), yaxis_title="",
    legend=dict(orientation="h", y=1.15), margin=dict(t=10, b=10),
)
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight("One picture of every country in the dataset, colored by which tier it falls in.")

# ---------------- 9. PERCENTILE TIER BREAKDOWN ----------------
st.write("")
st.subheader(f"📶 Percentile Tiers — {year}")
pct_ranks = year_data[year].rank(pct=True)

combined = pd.Series({
    "Top 10%": (pct_ranks >= 0.90).sum(),
    "Next 15% (upper)": ((pct_ranks >= 0.75) & (pct_ranks < 0.90)).sum(),
    "Middle 50%": ((pct_ranks >= 0.25) & (pct_ranks < 0.75)).sum(),
    "Next 15% (lower)": ((pct_ranks >= 0.10) & (pct_ranks < 0.25)).sum(),
    "Bottom 10%": (pct_ranks < 0.10).sum(),
})
fig = go.Figure(go.Bar(
    x=combined.index, y=combined.values,
    marker_color=[COLORS["negative"], COLORS["sequence"][1], "#94A3B8", COLORS["sequence"][3], COLORS["positive"]],
    text=combined.values, textposition="outside",
))
fig.update_layout(height=340, xaxis_title="", yaxis_title="Number of countries", margin=dict(t=20, b=10))
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight(
    "Percentile tiers rank countries relative to each other (not by a fixed rate cutoff) — the "
    "\"Top 10%\" here are the highest-refusal 10% of countries in the dataset, whatever their exact rate."
)

# ---------------- 10. "YEARS IN TOP 10" CONSISTENCY ----------------
st.write("")
st.subheader("🔂 How Often Has Each Country Been in the Top 10?")
top10_streak = pd.Series(0, index=df["Country"], dtype=int)
for yc in YEAR_COLS:
    yr_top10 = set(df[["Country", yc]].dropna().sort_values(yc, ascending=False).head(10)["Country"])
    top10_streak.loc[list(yr_top10)] += 1
streak_df = top10_streak[top10_streak > 0].sort_values(ascending=True).reset_index()
streak_df.columns = ["Country", "Years in Top 10"]
fig = go.Figure(go.Bar(
    x=streak_df["Years in Top 10"], y=streak_df["Country"], orientation="h",
    marker_color=COLORS["primary_dark"],
    text=streak_df["Years in Top 10"], textposition="outside",
))
fig.update_layout(
    height=max(300, 22 * len(streak_df)), xaxis_title=f"Years in Top 10 (out of {len(YEAR_COLS)})",
    yaxis_title="", margin=dict(t=10, b=10), xaxis=dict(dtick=1),
)
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
persistent = streak_df[streak_df["Years in Top 10"] == len(YEAR_COLS)]["Country"].tolist()
insight(
    f"{len(persistent)} countries have been in the Top 10 in **every single year** ({', '.join(persistent) if persistent else 'none'})"
    if persistent else
    "No country has stayed in the Top 10 every single year — the highest-refusal group does shift over time."
)

st.write("")
st.subheader("🔍 Filterable Country Table")
threshold = st.slider(f"Show countries with {year} refusal rate above:", 0, 100, 0, format="%d%%") / 100
search = st.text_input("Search country name")

# Year-over-year change vs the prior year (only when the selected year isn't 2019)
sel_idx = YEAR_COLS.index(year)
table = df[["Country"] + YEAR_COLS + ["avg_rate", "net_change"]].copy()
if sel_idx > 0:
    prev_year = YEAR_COLS[sel_idx - 1]
    table["yoy_change"] = table[year] - table[prev_year]
else:
    prev_year = None
    table["yoy_change"] = float("nan")

table = table[table[year] >= threshold]
if search:
    table = table[table["Country"].str.contains(search, case=False, na=False)]

display_table = table.copy()
for c in YEAR_COLS + ["avg_rate"]:
    display_table[c] = (display_table[c] * 100).round(1)
display_table["net_change"] = (display_table["net_change"] * 100).round(1)
display_table["yoy_change"] = (display_table["yoy_change"] * 100).round(1)
yoy_label = f"YoY Δ ({prev_year}→{year})" if prev_year else "YoY Δ (n/a, first year)"
display_table = display_table.rename(columns={
    "avg_rate": "7yr Avg %", "net_change": "Net Change % (19→25)", "yoy_change": yoy_label,
})

st.dataframe(display_table, width='stretch', height=380)
st.download_button(
    "⬇️ Download filtered data as CSV",
    data=table.to_csv(index=False).encode("utf-8"),
    file_name=f"visa_refusal_filtered_{year}.csv",
    mime="text/csv",
)

insight(f"{len(table)} countries match your current filters ({year} rate ≥ {int(threshold*100)}%).")
