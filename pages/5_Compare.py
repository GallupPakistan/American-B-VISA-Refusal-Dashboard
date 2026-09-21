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
fig = go.Figure()
for i, (_, r) in enumerate(sub.iterrows()):
    fig.add_trace(go.Scatter(
        x=selected_year_ints, y=[r[c] for c in selected_years],
        mode="lines+markers", name=r["Country"],
        line=dict(width=3, color=COLORS["sequence"][i % len(COLORS["sequence"])]),
    ))
fig.update_layout(height=430, yaxis_tickformat=".0%",
                   legend=dict(orientation="h", y=1.12, itemclick=False, itemdoubleclick=False))
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📊 Average Over Selected Range")
    avg_sel = sub[selected_years].mean(axis=1)
    bar_df = pd.DataFrame({"Country": sub["Country"], "Average": avg_sel}).sort_values("Average")
    fig = px.bar(bar_df, x="Average", y="Country", orientation="h",
                 color_discrete_sequence=[COLORS["primary"]])
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
export_df = sub[["Country"] + selected_years].copy()
st.download_button(
    "⬇️ Download comparison data as CSV",
    data=export_df.to_csv(index=False).encode("utf-8"),
    file_name=f"visa_refusal_compare_{yr_range[0]}-{yr_range[1]}.csv",
    mime="text/csv",
)