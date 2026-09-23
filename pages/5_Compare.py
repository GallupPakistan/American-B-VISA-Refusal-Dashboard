import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import load_data, apply_plotly_theme, inject_css, page_header, insight, sidebar_badge, COLORS, YEAR_COLS, YEARS

st.set_page_config(page_title="Compare", page_icon="🆚", layout="wide", initial_sidebar_state="expanded")
apply_plotly_theme()
inject_css()
df = load_data()

with st.sidebar:
    sidebar_badge("🆚 Compare Countries")
    countries = st.multiselect(
        "Select countries", sorted(df["Country"].unique()),
        default=["Pakistan", "India", "Afghanistan", "Iran"]
        if set(["Pakistan", "India", "Afghanistan", "Iran"]).issubset(set(df["Country"]))
        else list(df["Country"].head(4)),
    )
    yr_range = st.select_slider(
        "Year range", options=YEAR_COLS, value=("2019", "2025")
    )

page_header("COMPARE", "Custom Country Comparison", "Overlay B-visa refusal trends, averages, and a heatmap for your selection")

if not countries:
    st.info("Select at least one country from the sidebar to begin.")
    st.stop()

start_idx, end_idx = YEAR_COLS.index(yr_range[0]), YEAR_COLS.index(yr_range[1])
selected_years = YEAR_COLS[start_idx:end_idx + 1]
selected_year_ints = YEARS[start_idx:end_idx + 1]

sub = df[df["Country"].isin(countries)]

st.subheader("📈 Overlaid Trend Comparison")
show_line_labels = len(countries) <= 5  # avoid clutter when many countries/years are selected
fig = go.Figure()
for i, (_, r) in enumerate(sub.iterrows()):
    vals = [r[c] for c in selected_years]
    fig.add_trace(go.Scatter(
        x=selected_year_ints, y=vals,
        mode="lines+markers+text" if show_line_labels else "lines+markers", name=r["Country"],
        line=dict(width=3, color=COLORS["sequence"][i % len(COLORS["sequence"])]),
        text=[f"{v*100:.1f}%" for v in vals] if show_line_labels else None,
        textposition="top center",
    ))
fig.update_layout(height=430, yaxis_tickformat=".0%",
                   legend=dict(orientation="h", y=1.12, itemclick=False, itemdoubleclick=False))
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
if not show_line_labels:
    st.caption("ℹ️ Point labels are hidden here (too many countries selected) — hover any point for its exact rate.")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📊 Average Over Selected Range")
    avg_sel = sub[selected_years].mean(axis=1)
    bar_df = pd.DataFrame({"Country": sub["Country"], "Average": avg_sel}).sort_values("Average")
    fig = px.bar(bar_df, x="Average", y="Country", orientation="h",
                 color_discrete_sequence=[COLORS["primary"]],
                 text_auto=".1%")
    fig.update_traces(textposition="outside")
    fig.update_layout(height=380, xaxis_tickformat=".0%", xaxis_title="Avg refusal rate", yaxis_title="")
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

with col2:
    st.subheader("🔥 Heatmap — Country × Year")
    heat = sub.set_index("Country")[selected_years]
    fig = px.imshow(
        heat, text_auto=".0%", aspect="auto",
        color_continuous_scale=COLORS["blue_scale"],
        labels=dict(x="Year", y="", color="Rate"),
    )
    fig.update_layout(height=380)
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

st.write("")
st.subheader("📊 Range & Average — Min, Max, Avg per Country")
summary = pd.DataFrame({
    "Country": sub["Country"],
    "Min": sub[selected_years].min(axis=1) * 100,
    "Max": sub[selected_years].max(axis=1) * 100,
    "Average": sub[selected_years].mean(axis=1) * 100,
}).sort_values("Average", ascending=False)

fig = go.Figure()
for i, r in enumerate(summary.itertuples()):
    color = COLORS["sequence"][i % len(COLORS["sequence"])]
    fig.add_trace(go.Scatter(
        x=[r.Min, r.Max], y=[r.Country, r.Country],
        mode="lines", line=dict(color=color, width=8),
        opacity=0.35, showlegend=False,
        hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=[r.Average], y=[r.Country],
        mode="markers", marker=dict(color=color, size=14, line=dict(color="#FFFFFF", width=2)),
        showlegend=False,
        hovertemplate=f"<b>{r.Country}</b><br>Min: {r.Min:.1f}%<br>Avg: {r.Average:.1f}%<br>Max: {r.Max:.1f}%<extra></extra>",
    ))

fig.update_layout(
    height=max(300, 70 * len(summary)),
    xaxis=dict(title="Refusal rate (%)"),
    yaxis=dict(title=""),
    margin=dict(t=20, b=30),
)
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight("Each bar spans a country's lowest-to-highest refusal rate over the selected range, with the dot marking its average.")

best = summary.loc[summary["Average"].idxmin(), "Country"]
worst = summary.loc[summary["Average"].idxmax(), "Country"]
insight(f"Over {yr_range[0]}–{yr_range[1]}, **{best}** had the lowest average refusal rate among your "
        f"selection, while **{worst}** had the highest.")

st.write("")
st.subheader("🔗 Correlation — Do These Countries Move Together?")
if len(countries) < 2:
    st.info("Select at least 2 countries to see how closely their refusal rates move together over time.")
else:
    corr_input = sub.set_index("Country")[selected_years].T  # rows=years, cols=countries
    corr_matrix = corr_input.corr()
    if corr_matrix.isna().all().all():
        st.info("Not enough overlapping data across these countries/years to compute a correlation.")
    else:
        fig = px.imshow(
            corr_matrix, text_auto=".2f", aspect="auto",
            color_continuous_scale="RdBu", zmin=-1, zmax=1,
            labels=dict(x="", y="", color="Correlation"),
        )
        fig.update_layout(height=max(320, 60 * len(countries)))
        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

        # Find the most correlated off-diagonal pair for a quick takeaway
        pairs = []
        for i, a in enumerate(corr_matrix.columns):
            for b in corr_matrix.columns[i + 1:]:
                v = corr_matrix.loc[a, b]
                if pd.notna(v):
                    pairs.append((a, b, v))
        if pairs:
            top_pair = max(pairs, key=lambda p: p[2])
            insight(
                f"**+1.00** means two countries' rates rose and fell together every year; **-1.00** means "
                f"they moved in opposite directions. Here, **{top_pair[0]}** and **{top_pair[1]}** moved "
                f"most similarly (correlation {top_pair[2]:+.2f}) over {yr_range[0]}–{yr_range[1]}."
            )
        else:
            insight("+1.00 means two countries' rates rose and fell together every year; -1.00 means they moved oppositely.")

# ---------------- 6. YoY CHANGE COMPARISON (latest selected year) ----------------
st.write("")
end_year = yr_range[1]
end_idx_global = YEAR_COLS.index(end_year)
if end_idx_global > 0:
    prev_year_cmp = YEAR_COLS[end_idx_global - 1]
    st.subheader(f"📅 Year-over-Year Change ({prev_year_cmp} → {end_year})")
    yoy_cmp = (sub[end_year] - sub[prev_year_cmp]).dropna() * 100
    yoy_cmp_df = pd.DataFrame({"Country": sub.loc[yoy_cmp.index, "Country"], "Change": yoy_cmp}).sort_values("Change")
    fig = go.Figure(go.Bar(
        x=yoy_cmp_df["Change"], y=yoy_cmp_df["Country"], orientation="h",
        marker_color=[COLORS["negative"] if v >= 0 else COLORS["positive"] for v in yoy_cmp_df["Change"]],
        text=[f"{v:+.1f}%" for v in yoy_cmp_df["Change"]], textposition="outside",
    ))
    fig.update_layout(height=max(280, 55 * len(yoy_cmp_df)), xaxis_title="Change (points)", yaxis_title="",
                       margin=dict(t=10, b=10))
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
    insight(f"Each country's own single-year momentum going into {end_year}, among just your selection.")

# ---------------- 7. VOLATILITY COMPARISON ----------------
st.write("")
st.subheader("⚡ Volatility Comparison (Std. Deviation)")
vol_cmp = sub[["Country", "std_dev"]].dropna().sort_values("std_dev")
fig = go.Figure(go.Bar(
    x=vol_cmp["std_dev"] * 100, y=vol_cmp["Country"], orientation="h",
    marker_color=COLORS["primary_dark"],
    text=[f"{v*100:.1f}" for v in vol_cmp["std_dev"]], textposition="outside",
))
fig.update_layout(height=max(280, 55 * len(vol_cmp)), xaxis_title="Std. deviation (points)", yaxis_title="",
                   margin=dict(t=10, b=10))
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight("Higher bars mean that country's refusal rate swings around more from year to year, regardless of its average level.")

# ---------------- 8. RANK COMPARISON (selected end year, vs all 199) ----------------
st.write("")
st.subheader(f"🏁 Rank Comparison — {end_year} (out of {df[end_year].notna().sum()} countries)")
all_year_vals = df[end_year].dropna()
rank_cmp = []
for _, r in sub.iterrows():
    if pd.notna(r[end_year]):
        rk = int((all_year_vals > r[end_year]).sum()) + 1
        rank_cmp.append({"Country": r["Country"], "Rank": rk})
if rank_cmp:
    rank_cmp_df = pd.DataFrame(rank_cmp).sort_values("Rank", ascending=False)
    fig = go.Figure(go.Bar(
        x=rank_cmp_df["Rank"], y=rank_cmp_df["Country"], orientation="h",
        marker_color=COLORS["sequence"][:len(rank_cmp_df)],
        text=[f"#{r}" for r in rank_cmp_df["Rank"]], textposition="outside",
    ))
    fig.update_layout(height=max(280, 55 * len(rank_cmp_df)), xaxis_title=f"Rank in {end_year} (#1 = highest)",
                       yaxis_title="", margin=dict(t=10, b=10), xaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
    insight("Bars closer to #1 (right side) had the highest refusal rate among all 199 countries that year, not just among your selection.")

# ---------------- 9. MULTI-COUNTRY METRIC RADAR ----------------
st.write("")
st.subheader("🕸️ Metric Profile Comparison")
radar_labels = ["7yr Average", "Highest", "Lowest", f"{end_year} Rate", "Volatility"]
fig = go.Figure()
for i, (_, r) in enumerate(sub.iterrows()):
    vals = [
        (r["avg_rate"] or 0) * 100, (r["max_rate"] or 0) * 100, (r["min_rate"] or 0) * 100,
        (r[end_year] * 100 if pd.notna(r[end_year]) else 0), (r["std_dev"] or 0) * 100,
    ]
    fig.add_trace(go.Scatterpolar(
        r=vals + [vals[0]], theta=radar_labels + [radar_labels[0]],
        name=r["Country"], line=dict(color=COLORS["sequence"][i % len(COLORS["sequence"])], width=2),
    ))
fig.update_layout(height=420, polar=dict(radialaxis=dict(visible=True, ticksuffix="%")),
                   legend=dict(orientation="h", y=1.12), margin=dict(t=20, b=10))
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight("Overlaying each country's shape makes it easy to spot who's consistently higher, lower, or more erratic across all five metrics at once.")

# ---------------- 10. MINI SPARKLINES GRID (SMALL MULTIPLES) ----------------
st.write("")
st.subheader("📉 Quick-Glance Sparklines")
n_cols = min(len(countries), 4)
spark_cols = st.columns(n_cols)
for i, (_, r) in enumerate(sub.iterrows()):
    vals = [r[c] for c in selected_years]
    with spark_cols[i % n_cols]:
        fig = go.Figure(go.Scatter(
            x=selected_year_ints, y=vals, mode="lines", fill="tozeroy",
            line=dict(color=COLORS["sequence"][i % len(COLORS["sequence"])], width=2),
            fillcolor=COLORS["primary_light"],
        ))
        fig.update_layout(
            height=110, margin=dict(t=25, b=0, l=0, r=0),
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            title=dict(text=f"{r['Country']}", font=dict(size=13)),
        )
        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
insight("A compact shape-only view of each country's trend — useful for eyeballing patterns before digging into the detailed charts above.")

st.write("")
export_df = sub[["Country"] + selected_years].copy()
st.download_button(
    "⬇️ Download comparison data as CSV",
    data=export_df.to_csv(index=False).encode("utf-8"),
    file_name=f"visa_refusal_compare_{yr_range[0]}-{yr_range[1]}.csv",
    mime="text/csv",
)
