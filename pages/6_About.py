import streamlit as st
from utils import apply_plotly_theme, inject_css, page_header, sidebar_badge, insight, YEAR_COLS

st.set_page_config(page_title="About", page_icon="ℹ️", layout="wide", initial_sidebar_state="expanded")
apply_plotly_theme()
inject_css()

with st.sidebar:
    sidebar_badge("ℹ️ About")
    st.caption("What this dashboard shows, and how to read it.")

page_header("ABOUT", "About This Dashboard", "Data, definitions, and methodology behind the numbers")

st.subheader("📖 What is a B-Visa refusal rate?")
st.markdown(
    """
    The **B-1/B-2 visa** is the U.S. nonimmigrant visa category for short-term **business (B-1)** and
    **tourism (B-2)** travel. The **refusal rate** for a given country and year is the share of B-visa
    applications from that country which were refused (denied) rather than issued, expressed as a
    percentage:

    > Refusal rate = Refusals ÷ (Refusals + Issuances)

    A higher rate means a larger proportion of applicants from that country were turned down that year —
    it is **not** the same as application volume, and it says nothing about *why* individual applications
    were refused.
    """
)

st.write("")
st.subheader("🗂️ Data in this dashboard")
st.markdown(
    f"""
    - **Coverage:** 199 countries/territories, years **{YEAR_COLS[0]}–{YEAR_COLS[-1]}**
    - **Source file(s):** `data/visa_refusal.csv` and `data/Visa_refusal.xlsx` (identical data, two formats)
    - **Granularity:** one refusal rate per country per year
    """
)
st.info(
    "📝 **Source note:** this dashboard displays whatever refusal-rate figures are in the bundled data "
    "file. Add the original citation here (e.g. a specific U.S. Department of State NIV statistics "
    "report/date) so anyone using the dashboard can trace the numbers back to their source."
)

st.write("")
st.subheader("🧮 How the derived metrics are calculated")
st.markdown(
    """
    | Metric | How it's computed |
    |---|---|
    | **7-yr Average** | Mean of a country's refusal rate across all years it has data for |
    | **Highest / Lowest** | Max / min refusal rate across available years, with the year it occurred |
    | **Net Change (2019 → 2025)** | `2025 rate − 2019 rate`, in percentage points |
    | **YoY Change** | Selected year's rate minus the prior year's rate, in percentage points |
    | **Volatility (Std. Dev.)** | Standard deviation of a country's rate across all its available years — higher = more year-to-year swing |
    | **Risk Band** | Low (0–20%) · Moderate (20–40%) · High (40–60%) · Very High (60%+), based on that year's rate |
    | **Region** | Manually mapped from country name to continent/region (see `utils.py → REGION_MAP`) |
    """
)

st.write("")
st.subheader("⚠️ Known data limitation")
st.warning(
    "**Western Sahara** only has published data for 2019 and 2020. Years 2021–2025 are missing (not "
    "zero) for that entry — the dashboard shows these as *\"No data\"* rather than treating them as 0%, "
    "which would understate its true rate."
)

st.write("")
st.subheader("🧭 How to use this dashboard")
st.markdown(
    """
    - **Overview** — global snapshot for one year, plus how risk bands have shifted over time
    - **Rankings** — top/bottom countries, Top-10 movement, and a searchable/exportable table
    - **Country Spotlight** — deep dive into one country's history vs. the global average
    - **Trends & Volatility** — global patterns over time, biggest movers, and volatility analysis
    - **Region Explorer** — compare regions, with a live map and multi-year regional trend
    - **Compare** — overlay any set of countries side by side, with export
    """
)

insight(
    "Every page's year/country/region selectors live in its own sidebar and are independent of other "
    "pages — switching pages will not reset your selection on this page, but each page remembers its "
    "own choice separately."
)
