# 🌐 Visa Refusal Dashboard

Interactive Streamlit dashboard visualizing US B-Visa refusal rates across 199 countries from 2019–2025.

## Features
- **World Map** — Choropleth view of refusal rates by country for the selected year
- **Distribution Histogram** — Click a bar to see which countries fall in that refusal-rate range
- **KPI Cards** — Global average, highest/lowest refusal rate, countries covered
- **Risk-Band Composition** — Countries grouped into Low / Moderate / High / Very High refusal bands
- **Year Selector** — Slide through 2019–2025 in the sidebar

## Project Structure
```
├── app.py              # Main dashboard (Overview page)
├── utils.py            # Shared helpers (data loading, theming, charts)
├── pages/               # Additional Streamlit pages (Rankings, Country Spotlight, etc.)
├── requirements.txt
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data
Refusal rate data covers 199 countries across years 2019–2025, sourced from US B-Visa refusal statistics.

## Tech Stack
- Streamlit
- Plotly (Express & Graph Objects)
- Pandas
