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

page_header("RANKINGS", "Top & Bottom Countries", f"Ranked by B-visa refusal rate in {year}")

year_data = df[["Country", year]].dropna().sort_values(year, ascending=False)
top10 = year_data.head(10).sort_values(year)
bottom10 = year_data.tail(10).sort_values(year, ascending=False)

col1, col2 = st.columns(2)
with col1:
    st.subheader("🔺 Top 10 — Highest Refusal Rate")
    fig = px.bar(top10, x=year, y="Country", orientation="h",
                 color_discrete_sequence=[COLORS["negative"]])
    fig.update_layout(height=420, xaxis_tickformat=".0%", yaxis_title="", xaxis_title="Refusal rate")
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

with col2:
    st.subheader("🔻 Bottom 10 — Lowest Refusal Rate")
    fig = px.bar(bottom10, x=year, y="Country", orientation="h",
                 color_discrete_sequence=[COLORS["positive"]])
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
    )
    fig.update_layout(
        height=max(280, 40 * len(movers)), xaxis_tickformat="+.0%",
        xaxis_title="Change in refusal rate (2019 → 2025)", yaxis_title="", legend_title="",
    )
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

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
    table["yoy_change"] = pd.NA

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