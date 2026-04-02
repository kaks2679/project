"""
Page 10: Developer / About Page
Project information, methodology, data sources, and author profile.
Author: Stephen Muema
"""

import streamlit as st
import pandas as pd


def render(data: dict):
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1A1A2E 0%, #16213E 50%, #0F3460 100%);
                padding: 3rem 2rem; border-radius: 20px; margin-bottom: 2rem; text-align:center;'>
        <div style='font-size:4rem'>🇰🇪</div>
        <h1 style='color:white; font-size:2.5rem; margin:.5rem 0'>Kenya Economic Pulse</h1>
        <p style='color:#AED6F1; font-size:1.1rem; margin:.3rem 0'>
            End-to-End Data Science Portfolio Project
        </p>
        <div style='display:flex; justify-content:center; gap:1rem; flex-wrap:wrap; margin-top:1.5rem;'>
            <span style='background:rgba(255,255,255,.1); color:#AED6F1; padding:.4rem 1rem;
                         border-radius:20px; font-size:.85rem;'>v2.2.0</span>
            <span style='background:rgba(255,255,255,.1); color:#AED6F1; padding:.4rem 1rem;
                         border-radius:20px; font-size:.85rem;'>April 2026</span>
            <span style='background:rgba(255,255,255,.1); color:#AED6F1; padding:.4rem 1rem;
                         border-radius:20px; font-size:.85rem;'>MIT License</span>
            <span style='background:rgba(255,255,255,.1); color:#AED6F1; padding:.4rem 1rem;
                         border-radius:20px; font-size:.85rem;'>Python 3.10+</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Author card ───────────────────────────────────────────────────
    st.markdown("### 👤 About the Author")
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown("""
        <div style='background:#1C2833; padding:2rem; border-radius:16px; text-align:center;
                    border:1px solid #2C3E50;'>
            <div style='font-size:5rem'>👨‍💻</div>
            <h2 style='color:white; margin:.5rem 0; font-size:1.4rem'>Stephen Muema</h2>
            <p style='color:#3498DB; font-size:.9rem; margin:.2rem 0'>Data Scientist & ML Engineer</p>
            <p style='color:#7F8C8D; font-size:.85rem; margin:.2rem 0'>📍 Nairobi, Kenya 🇰🇪</p>
            <hr style='border-color:#2C3E50; margin:.8rem 0'>
            <a href='https://muemastephenportfolio.netlify.app/' target='_blank'
               style='color:#3498DB; text-decoration:none; font-size:.85rem;'>🌐 Portfolio</a><br><br>
            <a href='https://github.com/kaks2679' target='_blank'
               style='color:#AAB7B8; text-decoration:none; font-size:.85rem;'>🐙 GitHub</a><br><br>
            <a href='mailto:stephenmuema@proton.me'
               style='color:#AAB7B8; text-decoration:none; font-size:.85rem;'>📧 Email</a>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div style='background:#1C2833; padding:2rem; border-radius:16px; border:1px solid #2C3E50;'>
            <h3 style='color:#3498DB; margin-top:0'>About This Project</h3>
            <p style='color:#AAB7B8; line-height:1.8; font-size:.95rem;'>
                <b style='color:white'>Kenya Economic Pulse</b> is a production-quality, end-to-end
                data science portfolio built to demonstrate mastery across the full ML pipeline:
                data acquisition, cleaning, feature engineering, ML modelling, forecasting,
                anomaly detection, and interactive visualisation.
            </p>
            <p style='color:#AAB7B8; line-height:1.8; font-size:.95rem;'>
                The project answers three core economic questions using data and ML:
            </p>
            <ol style='color:#AAB7B8; line-height:2; font-size:.92rem;'>
                <li>Does <b style='color:white'>M-Pesa mobile money</b> reduce poverty?
                    <span style='color:#27AE60'>(R² = 0.904 ✓)</span></li>
                <li>Can we <b style='color:white'>cluster Kenya's counties</b> by development level?
                    <span style='color:#27AE60'>(KMeans k=5 ✓)</span></li>
                <li>What policies best reduce <b style='color:white'>youth unemployment</b>?
                    <span style='color:#27AE60'>(GBM model ✓)</span></li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 10 Dashboard Pages ────────────────────────────────────────────
    st.markdown("### 📋 Dashboard Pages (10 Total)")
    pages = [
        ("🏠", "Overview",                     "Kenya at a glance — KPI strip, GDP/poverty charts, county snapshot"),
        ("📊", "Economic Indicators",           "20+ macro indicators with correlation heatmap and OLS scatter"),
        ("🗺️", "County Inequality Map",         "KMeans clustering, Folium bubble map, regional comparisons"),
        ("💚", "M-Pesa Impact Predictor",       "Ridge/GBM/RF regression proving mobile money reduces poverty"),
        ("🎓", "Youth Unemployment Forecaster", "GBM forecasting with interactive scenario simulator"),
        ("🔮", "Economic Forecaster",           "Holt-Winters + ARIMA(2,1,2) with confidence intervals"),
        ("⚖️", "County Comparison",             "Side-by-side radar chart + bar chart for any two counties"),
        ("🏛️", "Policy Simulator",              "5-lever policy simulation with waterfall impact chart"),
        ("🔍", "Anomaly Detection",             "Isolation Forest detecting economic shocks (2008, 2020…)"),
        ("💬", "NL Query Engine",               "Ask plain-English questions, get data-backed chart answers"),
    ]
    cols = st.columns(2)
    for i, (icon, name, desc) in enumerate(pages):
        col = cols[i % 2]
        col.markdown(f"""
        <div style='background:#1C2833; padding:1rem; border-radius:10px; margin-bottom:.6rem;
                    border-left:3px solid #3498DB;'>
            <b style='color:white'>{icon} {name}</b>
            <p style='color:#7F8C8D; font-size:.82rem; margin:.3rem 0 0'>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ML models ─────────────────────────────────────────────────────
    st.markdown("### 🤖 Machine Learning Models")
    ml_data = {
        "Model":        ["Gradient Boosting",    "Random Forest",    "Ridge Regression",
                         "KMeans Clustering",    "Holt-Winters ES",  "ARIMA(2,1,2)",
                         "Isolation Forest"],
        "Task":         ["Poverty prediction",   "Poverty prediction","Poverty prediction",
                         "County segmentation",  "Economic forecasting","Economic forecasting",
                         "Anomaly detection"],
        "Performance":  ["R² = 0.904",           "R² = 0.882",       "R² = 0.871",
                         "Silhouette > 0.58",    "MAE < 0.8pp",      "95% CI forecasts",
                         "Contamination=10%"],
        "Library":      ["sklearn",              "sklearn",          "sklearn",
                         "sklearn",              "statsmodels",      "statsmodels",
                         "sklearn"],
    }
    st.dataframe(pd.DataFrame(ml_data), use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Data sources ──────────────────────────────────────────────────
    st.markdown("### 📡 Data Sources")
    sources = [
        ("🌐 World Bank Open Data", "https://data.worldbank.org/country/KE",
         "Macro indicators: GDP growth, inflation, unemployment, Gini, remittances, electricity, literacy"),
        ("📊 KNBS 2019 Census", "https://www.knbs.or.ke/2019-kenya-population-and-housing-census/",
         "47-county population, poverty rates, unemployment from Kenya National Bureau of Statistics"),
        ("🏦 Central Bank of Kenya", "https://www.centralbank.go.ke/annual-reports/",
         "M-Pesa agent/user counts, mobile money volumes, financial inclusion surveys"),
        ("👷 ILO Labour Statistics", "https://ilostat.ilo.org/data/",
         "Youth unemployment rates (ages 15–24), sector employment shares"),
        ("💳 FinAccess Survey", "https://www.knbs.or.ke/finaccess-household-survey/",
         "Financial inclusion percentages, rural/urban banking gaps"),
        ("📈 KIHBS 2021", "https://www.knbs.or.ke/kenya-integrated-household-budget-survey-kihbs-2021/",
         "Household income, expenditure, poverty headcount ratios by county"),
    ]
    for name, url, desc in sources:
        st.markdown(f"""
        <div style='background:#1C2833; padding:.8rem 1rem; border-radius:8px;
                    margin-bottom:.5rem; border-left:3px solid #27AE60;'>
            <a href='{url}' target='_blank' style='color:#3498DB; font-weight:bold;
               text-decoration:none; font-size:.9rem'>{name}</a>
            <p style='color:#7F8C8D; font-size:.82rem; margin:.2rem 0 0'>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tech stack ────────────────────────────────────────────────────
    st.markdown("### 🛠️ Technology Stack")
    tech = {
        "Category": ["Frontend", "Data Processing", "Machine Learning",
                     "Visualisation", "Mapping", "Forecasting", "Notebooks"],
        "Tools": ["Streamlit 1.32+", "Pandas, NumPy, PyArrow",
                  "Scikit-learn (GB, RF, Ridge, KMeans, IsolationForest)",
                  "Plotly 5.18+, Altair 5", "Folium, streamlit-folium",
                  "Statsmodels (Holt-Winters, ARIMA)", "Jupyter 4, nbformat, nbconvert"],
    }
    st.dataframe(pd.DataFrame(tech), use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Project structure ─────────────────────────────────────────────
    st.markdown("### 📁 Project Structure")
    st.code("""
kenya-economic-pulse/
├── app.py                          # Main Streamlit application (10 pages)
├── requirements.txt                # Python dependencies
├── .streamlit/config.toml          # Streamlit dark theme config
├── data/                           # CSV data files (6 datasets)
│   ├── kenya_macro_indicators.csv  # 24×16 World Bank macro data
│   ├── kenya_county_data.csv       # 47 counties × 12 features
│   ├── kenya_mobile_money.csv      # M-Pesa 2007–2023 (17×8)
│   ├── kenya_youth_unemployment.csv# Youth unemp 2005–2023 (19×8)
│   ├── kenya_sector_employment.csv # Sector shares 2010–2023 (14×10)
│   └── kenya_regional_stats.csv    # 8 regions × 8 aggregates
├── pages/                          # 10 Streamlit page modules
│   ├── economic_indicators.py      # Page 1
│   ├── county_inequality.py        # Page 2
│   ├── mobile_money.py             # Page 3
│   ├── youth_unemployment.py       # Page 4
│   ├── forecaster.py               # Page 5
│   ├── county_comparison.py        # Page 6
│   ├── policy_simulator.py         # Page 7
│   ├── anomaly_detection.py        # Page 8
│   ├── nlq_engine.py               # Page 9
│   └── developer.py                # Page 10
├── utils/                          # Utility modules
│   ├── data_fetcher.py             # World Bank API + fallback data
│   ├── ml_models.py                # All ML model functions
│   └── report_generator.py        # PDF report generation
├── src/                            # Source modules
│   ├── data/loader.py, validator.py
│   ├── features/engineering.py
│   ├── models/regression.py, clustering.py, forecasting.py
│   └── visualization/charts.py
└── notebooks/
    ├── kenya_economic_pulse_analysis.ipynb  # Full DS pipeline notebook
    └── build_notebook.py                    # Notebook builder script
    """, language="")

    # ── Key findings ──────────────────────────────────────────────────
    st.markdown("### 🔑 Key Findings")
    findings = [
        ("💚", "M-Pesa Effect",    "Mobile money penetration is the #1 predictor of poverty reduction "
                                    "(GBM R²=0.904). Since 2007, financial inclusion rose 26.4%→85.1% "
                                    "as poverty fell 46.8%→33.5%."),
        ("🗺️", "County Gap",       "Extreme regional inequality: Wajir (82.4%) vs Kiambu (13.2%) — "
                                    "a 69pp poverty gap. North-Eastern counties are in critical need."),
        ("🎓", "Youth Crisis",     "Youth unemployment at 61.5% — 4.5× the global average. "
                                    "Education spending and FDI are the strongest policy levers."),
        ("📈", "Growth Resilient", "Kenya grew ~5.2% average 2000–2023 despite COVID, elections, drought. "
                                    "Services & ICT now drive 35%+ of GDP."),
        ("⚡", "Power Divide",     "Electricity access ranges from 10.8% (Turkana) to 92.4% (Nairobi). "
                                    "Rural electrification is key to reducing inequality."),
        ("💰", "Diaspora Power",   "Diaspora remittances hit USD 4.2B in 2023 — larger than FDI inflows — "
                                    "providing critical household income support."),
    ]
    cols = st.columns(2)
    for i, (icon, title, text) in enumerate(findings):
        cols[i % 2].markdown(f"""
        <div style='background:#1C2833; padding:1rem; border-radius:10px; margin-bottom:.6rem;
                    border-left:3px solid #27AE60;'>
            <b style='color:white'>{icon} {title}</b>
            <p style='color:#AAB7B8; font-size:.83rem; margin:.3rem 0 0; line-height:1.6'>{text}</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────
    st.markdown("""
    <div style='text-align:center; padding:2rem; color:#566573; margin-top:2rem;
                border-top:1px solid #2C3E50;'>
        <p style='margin:0; font-size:.85rem;'>
            Built with ❤️ by
            <a href='https://muemastephenportfolio.netlify.app/' target='_blank'
               style='color:#3498DB; text-decoration:none;'>Stephen Muema</a>
            · Data Scientist & ML Engineer · Nairobi, Kenya 🇰🇪
        </p>
        <p style='margin:.4rem 0 0; font-size:.8rem;'>
            <a href='https://github.com/kaks2679/project' target='_blank'
               style='color:#566573; text-decoration:none;'>GitHub Repository</a>
            · MIT License · v2.2.0 · April 2026
        </p>
    </div>
    """, unsafe_allow_html=True)
