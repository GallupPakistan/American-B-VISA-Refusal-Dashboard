"""
Shared utilities for the Visa Refusal Dashboard.
Edit COLORS / PLOTLY_TEMPLATE here to change chart styling.
Edit inject_css() to change card / layout styling.
"""

import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# Absolute path to the folder this file lives in — makes data loading work
# no matter which directory you launch `streamlit run` from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "visa_refusal.csv")

YEARS = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
YEAR_COLS = [str(y) for y in YEARS]

# ----------------------------------------------------------------------
# COLOR PALETTE  (change these to re-theme every chart in the app)
# ----------------------------------------------------------------------
COLORS = {
    "bg": "#F6F7FB",
    "card_bg": "#FFFFFF",
    "primary": "#4F46E5",
    "primary_light": "#E7E5FB",
    "primary_dark": "#312E81",
    "text": "#1E1B4B",
    "text_muted": "#64748B",
    "grid": "#E5E7F2",
    "positive": "#10B981",
    "negative": "#F43F5E",
    "sequence": ["#312E81", "#4F46E5", "#6366F1", "#818CF8", "#0EA5E9", "#38BDF8", "#A5B4FC"],
    "diverging": ["#10B981", "#A7F3D0", "#F1F5F9", "#FDA4AF", "#F43F5E"],
    "blue_scale": ["#EEF2FF", "#C7D2FE", "#818CF8", "#4F46E5", "#312E81"],
    # Dark ink sidebar + hero header gradient
    "navy_top": "#111827",
    "navy_bottom": "#1E1B4B",
    "navy_active": "#4F46E5",
    "navy_text": "#E4E6F7",
    "navy_text_muted": "#9CA3D4",
    "accent_teal": "#2DD4BF",
}


def apply_plotly_theme():
    """Register and activate a shared Plotly template across the whole app."""
    template = go.layout.Template()
    template.layout = go.Layout(
        font=dict(family="Segoe UI, Helvetica, Arial, sans-serif", color=COLORS["text"], size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=COLORS["sequence"],
        xaxis=dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"], linecolor=COLORS["grid"]),
        yaxis=dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"], linecolor=COLORS["grid"]),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=40, r=30, t=50, b=40),
        hoverlabel=dict(bgcolor="white", font_size=13, bordercolor=COLORS["grid"]),
    )
    pio.templates["visa_theme"] = template
    pio.templates.default = "visa_theme"


def inject_css():
    """Custom CSS for card styling, spacing, fonts beyond what config.toml can do."""
    st.markdown(
        f"""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
        html, body, [class*="css"] {{ font-family: 'Inter', 'Segoe UI', Helvetica, Arial, sans-serif; }}
        .main {{ background-color: {COLORS['bg']}; }}

        /* Hide the Deploy button + hamburger menu, WITHOUT touching stToolbar itself —
           the sidebar's collapse/expand arrow lives inside stToolbar in this Streamlit
           version, so hiding stToolbar wholesale was breaking the sidebar toggle.
           toolbarMode = "minimal" in .streamlit/config.toml already removes
           Deploy/menu/settings while leaving the sidebar arrow intact. */
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        [data-testid="stDecoration"] {{ display: none; }}
        [data-testid="stHeader"] {{
            background: transparent;
            box-shadow: none;
        }}

        /* Pull the page content right up under that (now invisible) header */
        div[data-testid="stAppViewContainer"] > .main .block-container {{
            padding-top: 0.4rem;
            padding-bottom: 1.2rem;
        }}

        h1, h2, h3 {{ color: {COLORS['primary_dark']}; font-weight: 700; }}

        /* ---------------- DARK NAVY SIDEBAR ---------------- */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {COLORS['navy_top']} 0%, {COLORS['navy_bottom']} 100%);
            border-right: none;
        }}
        [data-testid="stSidebar"] .block-container {{
            padding-top: 1.4rem;
        }}
        /* All default sidebar text (captions, labels, widget text) → light */
        [data-testid="stSidebar"] * {{
            color: {COLORS['navy_text']};
        }}
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] p {{
            color: {COLORS['navy_text_muted']} !important;
        }}
        [data-testid="stSidebar"] hr {{
            border-color: rgba(255,255,255,0.14);
        }}

        /* Native multipage nav wrapped as a rounded card, like the reference sidebar */
        [data-testid="stSidebarNav"] {{
            background-color: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            margin: 4px 10px 10px 10px;
            padding: 6px 0;
        }}
        [data-testid="stSidebarNav"] ul {{
            padding-top: 4px;
        }}
        [data-testid="stSidebarNav"] li {{
            margin: 3px 8px;
        }}
        [data-testid="stSidebarNav"] a {{
            border-radius: 10px;
            padding: 10px 14px !important;
            color: {COLORS['navy_text']} !important;
            font-weight: 500;
            border-left: 3px solid transparent;
            transition: background-color 0.15s ease, border-color 0.15s ease;
        }}
        [data-testid="stSidebarNav"] a:hover {{
            background-color: rgba(255,255,255,0.08);
        }}
        [data-testid="stSidebarNav"] a[aria-current="page"] {{
            background-color: {COLORS['navy_active']};
            border-left: 3px solid {COLORS['accent_teal']};
            font-weight: 700;
            color: #FFFFFF !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
        [data-testid="stSidebarNav"] span {{
            color: inherit !important;
        }}

        /* Sidebar select/input widgets — white pill, dark readable text
           (baseweb nests several inner divs, so target all descendants). */
        [data-testid="stSidebar"] [data-baseweb="select"] > div {{
            background-color: #FFFFFF !important;
            border-radius: 8px !important;
            border: 1px solid rgba(255,255,255,0.25) !important;
        }}
        [data-testid="stSidebar"] [data-baseweb="select"] * {{
            color: {COLORS['text']} !important;
            fill: {COLORS['text']} !important;
        }}
        [data-testid="stSidebar"] input {{
            background-color: #FFFFFF !important;
            border-radius: 8px !important;
            border: 1px solid rgba(255,255,255,0.25) !important;
            color: {COLORS['text']} !important;
        }}
        [data-testid="stSidebar"] [data-baseweb="slider"] {{
            padding-top: 6px;
        }}

        /* Selectbox dropdown list (Country picker etc.) is portaled OUTSIDE the sidebar,
           so it needs its own rule — force dark text on its white background. */
        ul[data-testid="stSelectboxVirtualDropdown"] {{
            background-color: #FFFFFF !important;
        }}
        ul[data-testid="stSelectboxVirtualDropdown"] li,
        ul[data-testid="stSelectboxVirtualDropdown"] li * {{
            color: {COLORS['text']} !important;
        }}
        ul[data-testid="stSelectboxVirtualDropdown"] li:hover {{
            background-color: {COLORS['primary_light']} !important;
        }}

        /* KPI / metric cards — fixed height + fixed label zone so every card aligns */
        div[data-testid="stMetric"] {{
            background-color: {COLORS['card_bg']};
            border: 1px solid {COLORS['grid']};
            border-left: 4px solid {COLORS['primary']};
            border-radius: 14px;
            padding: 16px 20px 16px 20px;
            box-shadow: 0 2px 10px rgba(49, 46, 129, 0.07);
            height: 150px;
            min-height: 150px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            overflow: hidden;
            transition: box-shadow 0.15s ease, transform 0.15s ease;
        }}
        div[data-testid="stMetric"]:hover {{
            box-shadow: 0 6px 18px rgba(49, 46, 129, 0.14);
            transform: translateY(-1px);
        }}
        div[data-testid="stMetric"] label {{
            color: {COLORS['text_muted']} !important;
            font-weight: 700 !important;
            min-height: 40px;
            display: flex;
            align-items: flex-end;
            line-height: 1.2;
        }}
        div[data-testid="stMetricValue"] {{
            font-size: 1.9rem;
            font-weight: 800;
        }}
        div[data-testid="stMetricDelta"] {{
            font-size: 0.85rem;
            font-weight: 700;
            white-space: normal !important;
            overflow-wrap: break-word;
            line-height: 1.3;
        }}
        div[data-testid="stMetricDelta"] svg {{
            flex-shrink: 0;
        }}
        div[data-testid="column"] {{
            display: flex;
            align-items: stretch;
        }}
        div[data-testid="column"] > div {{
            width: 100%;
        }}

        /* ---------------- HERO HEADER CARD ---------------- */
        .hero-card {{
            background: linear-gradient(135deg, {COLORS['navy_top']} 0%, {COLORS['primary_dark']} 55%, {COLORS['primary']} 130%);
            border-radius: 20px;
            padding: 24px 34px 26px 34px;
            margin: 0 0 18px 0;
            box-shadow: 0 10px 30px rgba(17, 24, 39, 0.28);
        }}
        .hero-kicker {{
            display: inline-block;
            background-color: rgba(255,255,255,0.14);
            color: {COLORS['accent_teal']};
            font-weight: 700;
            font-size: 0.75rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 5px 14px;
            border-radius: 999px;
            margin-bottom: 12px;
        }}
        .hero-title {{
            color: #FFFFFF;
            font-size: 2.3rem;
            font-weight: 800;
            margin: 0 0 8px 0;
            line-height: 1.15;
        }}
        .hero-subtitle {{
            color: #C9DAF5;
            font-size: 1.02rem;
            max-width: 720px;
        }}

        .insight-card {{
            background-color: {COLORS['primary_light']};
            border-left: 4px solid {COLORS['primary']};
            border-radius: 10px;
            padding: 14px 20px 14px 16px;
            color: {COLORS['primary_dark']};
            font-size: 0.95rem;
            margin: 8px 0 18px 0;
            display: flex;
            align-items: flex-start;
            gap: 10px;
        }}

        /* Sidebar section badge (pill), same style language as before */
        .sidebar-pill {{
            display: inline-block;
            background-color: rgba(255,255,255,0.12);
            color: #FFFFFF;
            font-weight: 700;
            font-size: 0.95rem;
            padding: 7px 16px;
            border-radius: 999px;
            margin-bottom: 4px;
        }}

        div[data-baseweb="tab-list"] {{ gap: 6px; }}
        button[data-baseweb="tab"] {{
            background-color: {COLORS['card_bg']};
            border-radius: 8px 8px 0 0;
        }}

        hr {{ border-color: {COLORS['grid']}; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(kicker: str, title: str, subtitle: str = ""):
    """Dark-navy gradient hero card at the top of every page (replaces the old plain header)."""
    st.markdown(
        f"""
        <div class="hero-card">
            <span class="hero-kicker">{kicker}</span>
            <div class="hero-title">{title}</div>
            {f'<div class="hero-subtitle">{subtitle}</div>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_badge(text: str):
    """Consistent light pill heading used at the top of every sidebar section."""
    st.markdown(f"<span class='sidebar-pill'>{text}</span>", unsafe_allow_html=True)


def blue_shades(n: int) -> list:
    """Return n distinct blue shades (dark navy -> light sky blue), theme-matched,
    for coloring pie/bar slices per-category (e.g. one shade per country)."""
    import plotly.colors as pc
    scale = ["#0B1F4D", "#1E3A8A", "#1E40AF", "#2563EB", "#3B82F6",
             "#60A5FA", "#93C5FD", "#BFDBFE"]
    if n <= len(scale):
        # spread evenly across the scale rather than just taking the first n
        idx = [round(i * (len(scale) - 1) / max(n - 1, 1)) for i in range(n)]
        return [scale[i] for i in idx]
    return pc.sample_colorscale(
        [[i / (len(scale) - 1), c] for i, c in enumerate(scale)],
        [i / (n - 1) for i in range(n)],
    )


def chip_list(items: list, kind: str = "positive"):
    """Render a list of country names as colored pill/chip badges.
    kind: 'positive' (green, e.g. newly entered) or 'negative' (red, e.g. dropped out)."""
    if not items:
        st.markdown(
            f"<span style='color:{COLORS['text_muted']}; font-size:0.9rem;'>None</span>",
            unsafe_allow_html=True,
        )
        return
    bg, fg = ("#DCFCE7", "#15803D") if kind == "positive" else ("#FEE2E2", "#B91C1C")
    chips = "".join(
        f"<span style='display:inline-block; background-color:{bg}; color:{fg}; "
        f"font-weight:700; font-size:0.85rem; padding:6px 14px; border-radius:999px; "
        f"margin:4px 6px 4px 0;'>{c}</span>"
        for c in sorted(items)
    )
    st.markdown(f"<div>{chips}</div>", unsafe_allow_html=True)


def insight(text: str):
    st.markdown(
        f"<div class='insight-card'><span style='font-size:1.1rem;line-height:1;'>💡</span>"
        f"<span>{text}</span></div>",
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df.columns = ["Country"] + YEAR_COLS
    for c in YEAR_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # computed columns
    df["avg_rate"] = df[YEAR_COLS].mean(axis=1, skipna=True)
    df["max_rate"] = df[YEAR_COLS].max(axis=1, skipna=True)
    df["min_rate"] = df[YEAR_COLS].min(axis=1, skipna=True)
    df["max_year"] = df[YEAR_COLS].idxmax(axis=1)
    df["min_year"] = df[YEAR_COLS].idxmin(axis=1)
    df["std_dev"] = df[YEAR_COLS].std(axis=1, skipna=True)
    df["net_change"] = df["2025"] - df["2019"]

    def band(x):
        if pd.isna(x):
            return "No data"
        if x < 0.20:
            return "Low (0-20%)"
        if x < 0.40:
            return "Moderate (20-40%)"
        if x < 0.60:
            return "High (40-60%)"
        return "Very High (60%+)"

    df["risk_band_2025"] = df["2025"].apply(band)
    df["Region"] = df["Country"].map(REGION_MAP).fillna("Other")
    return df


REGION_MAP = {
    'Afghanistan': 'Asia',
    'Albania': 'Europe',
    'Algeria': 'Africa',
    'Andorra': 'Europe',
    'Angola': 'Africa',
    'Antigua And Barbuda': 'North America',
    'Argentina': 'South America',
    'Armenia': 'Asia',
    'Australia': 'Oceania',
    'Austria': 'Europe',
    'Azerbaijan': 'Asia',
    'Bahamas': 'North America',
    'Bahrain': 'Asia',
    'Bangladesh': 'Asia',
    'Barbados': 'North America',
    'Belarus': 'Europe',
    'Belgium': 'Europe',
    'Belize': 'North America',
    'Benin': 'Africa',
    'Bhutan': 'Asia',
    'Bolivia': 'South America',
    'Bosnia And Herzegovina': 'Europe',
    'Botswana': 'Africa',
    'Brazil': 'South America',
    'Brunei': 'Asia',
    'Bulgaria': 'Europe',
    'Burkina Faso': 'Africa',
    'Burma': 'Asia',
    'Burundi': 'Africa',
    'Cabo Verde': 'Africa',
    'Cambodia': 'Asia',
    'Cameroon': 'Africa',
    'Canada': 'North America',
    'Central African Republic': 'Africa',
    'Chad': 'Africa',
    'Chile': 'South America',
    'China': 'Asia',
    'Colombia': 'South America',
    'Comoros': 'Africa',
    'Democratic Republic Of The Congo': 'Africa',
    'Republic Of The Congo': 'Africa',
    'Costa Rica': 'North America',
    "Cote D'Ivoire": 'Africa',
    'Croatia': 'Europe',
    'Cuba': 'North America',
    'Cyprus': 'Asia',
    'Czech Republic': 'Europe',
    'Denmark': 'Europe',
    'Djibouti': 'Africa',
    'Dominica': 'North America',
    'Dominican Republic': 'North America',
    'Ecuador': 'South America',
    'Egypt': 'Africa',
    'El Salvador': 'North America',
    'Equatorial Guinea': 'Africa',
    'Eritrea': 'Africa',
    'Estonia': 'Europe',
    'Eswatini': 'Africa',
    'Ethiopia': 'Africa',
    'Federated States Of Micronesia': 'Oceania',
    'Fiji': 'Oceania',
    'Finland': 'Europe',
    'France': 'Europe',
    'Gabon': 'Africa',
    'Gambia': 'Africa',
    'Georgia': 'Asia',
    'Germany': 'Europe',
    'Ghana': 'Africa',
    'Great Britain And Northern Ireland': 'Europe',
    'Greece': 'Europe',
    'Grenada': 'North America',
    'Guatemala': 'North America',
    'Guinea': 'Africa',
    'Guinea - Bissau': 'Africa',
    'Guyana': 'South America',
    'Haiti': 'North America',
    'Honduras': 'North America',
    'Hungary': 'Europe',
    'Iceland': 'Europe',
    'India': 'Asia',
    'Indonesia': 'Asia',
    'Iran': 'Asia',
    'Iraq': 'Asia',
    'Ireland': 'Europe',
    'Israel': 'Asia',
    'Italy': 'Europe',
    'Jamaica': 'North America',
    'Japan': 'Asia',
    'Jordan': 'Asia',
    'Kazakhstan': 'Asia',
    'Kenya': 'Africa',
    'Kiribati': 'Oceania',
    'North Korea': 'Asia',
    'South Korea': 'Asia',
    'Kuwait': 'Asia',
    'Kyrgyzstan': 'Asia',
    'Laos': 'Asia',
    'Latvia': 'Europe',
    'Lebanon': 'Asia',
    'Lesotho': 'Africa',
    'Liberia': 'Africa',
    'Libya': 'Africa',
    'Liechtenstein': 'Europe',
    'Lithuania': 'Europe',
    'Luxembourg': 'Europe',
    'Madagascar': 'Africa',
    'Malawi': 'Africa',
    'Malaysia': 'Asia',
    'Maldives': 'Asia',
    'Mali': 'Africa',
    'Malta': 'Europe',
    'Marshall Islands': 'Oceania',
    'Mauritania': 'Africa',
    'Mauritius': 'Africa',
    'Mexico': 'North America',
    'Moldova': 'Europe',
    'Monaco': 'Europe',
    'Mongolia': 'Asia',
    'Montenegro': 'Europe',
    'Morocco': 'Africa',
    'Mozambique': 'Africa',
    'Namibia': 'Africa',
    'Nauru': 'Oceania',
    'Nepal': 'Asia',
    'Netherlands': 'Europe',
    'New Zealand': 'Oceania',
    'Nicaragua': 'North America',
    'Niger': 'Africa',
    'Nigeria': 'Africa',
    'North Macedonia': 'Europe',
    'Norway': 'Europe',
    'Oman': 'Asia',
    'Pakistan': 'Asia',
    'Palau': 'Oceania',
    'Panama': 'North America',
    'Papua New Guinea': 'Oceania',
    'Paraguay': 'South America',
    'Peru': 'South America',
    'Philippines': 'Asia',
    'Poland': 'Europe',
    'Portugal': 'Europe',
    'Qatar': 'Asia',
    'Romania': 'Europe',
    'Russia': 'Europe',
    'Rwanda': 'Africa',
    'Samoa': 'Oceania',
    'San Marino': 'Europe',
    'Sao Tome And Principe': 'Africa',
    'Saudi Arabia': 'Asia',
    'Senegal': 'Africa',
    'Serbia': 'Europe',
    'Seychelles': 'Africa',
    'Sierra Leone': 'Africa',
    'Singapore': 'Asia',
    'Slovakia': 'Europe',
    'Slovenia': 'Europe',
    'Solomon Islands': 'Oceania',
    'Somalia': 'Africa',
    'South Africa': 'Africa',
    'South Sudan': 'Africa',
    'Spain': 'Europe',
    'Sri Lanka': 'Asia',
    'St. Kitts And Nevis': 'North America',
    'St. Lucia': 'North America',
    'St. Vincent And The Grenadines': 'North America',
    'Sudan': 'Africa',
    'Suriname': 'South America',
    'Sweden': 'Europe',
    'Switzerland': 'Europe',
    'Syria': 'Asia',
    'Tajikistan': 'Asia',
    'Tanzania': 'Africa',
    'Thailand': 'Asia',
    'Timor-Leste': 'Asia',
    'Togo': 'Africa',
    'Tonga': 'Oceania',
    'Trinidad And Tobago': 'North America',
    'Tunisia': 'Africa',
    'Turkey': 'Asia',
    'Turkmenistan': 'Asia',
    'Tuvalu': 'Oceania',
    'Uganda': 'Africa',
    'Ukraine': 'Europe',
    'United Arab Emirates': 'Asia',
    'Uruguay': 'South America',
    'Uzbekistan': 'Asia',
    'Vanuatu': 'Oceania',
    'Vatican City': 'Europe',
    'Venezuela': 'South America',
    'Vietnam': 'Asia',
    'Yemen': 'Asia',
    'Zambia': 'Africa',
    'Zimbabwe': 'Africa',
    'Hong Kong S. A. R.': 'Asia',
    'Kosovo': 'Europe',
    'Macau S.A.R.': 'Asia',
    'Palestinian Authority Travel Document': 'Asia',
    'Taiwan': 'Asia',
    'Western Sahara': 'Africa',
}


ISO_OVERRIDES = {
    "United States": "USA", "Russia": "RUS", "South Korea": "KOR",
    "North Korea": "PRK", "Iran": "IRN", "Syria": "SYR", "Vietnam": "VNM",
    "Laos": "LAO", "Ivory Coast": "CIV", "Cape Verde": "CPV",
    "Democratic Republic Of The Congo": "COD", "Republic Of The Congo": "COG",
    "Congo": "COG", "Czech Republic": "CZE", "Czechia": "CZE",
    "Macau S.A.R.": "MAC", "Hong Kong S.A.R.": "HKG", "Hong Kong": "HKG",
    "Taiwan": "TWN", "Brunei": "BRN", "Eswatini": "SWZ", "Swaziland": "SWZ",
    "Burma": "MMR", "Myanmar": "MMR", "Micronesia": "FSM",
    "Bosnia And Herzegovina": "BIH", "Antigua And Barbuda": "ATG",
    "Trinidad And Tobago": "TTO", "St. Kitts And Nevis": "KNA",
    "St. Lucia": "LCA", "St. Vincent And The Grenadines": "VCT",
    "Sao Tome And Principe": "STP", "United Arab Emirates": "ARE",
    "Palestinian Authority Travel Document": "PSE",
    "Western Sahara": "ESH", "Kosovo": "XKX",
    "Guinea - Bissau": "GNB", "Guinea-Bissau": "GNB",
    "Turkey": "TUR", "Turkiye": "TUR",
    "Hong Kong S. A. R.": "HKG", "Hong Kong S.A.R.": "HKG",
}


@st.cache_data
def get_iso_map(countries: list) -> dict:
    import pycountry
    out = {}
    for c in countries:
        if c in ISO_OVERRIDES:
            out[c] = ISO_OVERRIDES[c]
            continue
        try:
            out[c] = pycountry.countries.search_fuzzy(c)[0].alpha_3
        except Exception:
            out[c] = None
    return out
