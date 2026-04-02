# 🇰🇪 Kenya Economic Pulse

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.2.0-blue.svg)](https://github.com/kaks2679/project)

> **End-to-end data science portfolio project** — 10-page interactive Streamlit dashboard exploring Kenya's economy using World Bank data, KNBS Census, CBK mobile money statistics, and machine learning.

**Author:** [Stephen Muema](https://muemastephenportfolio.netlify.app/) | Data Scientist & ML Engineer | Nairobi, Kenya 🇰🇪

---

## 🚀 Live Demo

```bash
git clone https://github.com/kaks2679/project.git
cd project
pip install -r requirements.txt
streamlit run app.py
```

---

## 📋 Dashboard Pages (10 Total)

| # | Page | Description |
|---|------|-------------|
| 1 | 🏠 **Overview** | Kenya at a glance — 6 KPI cards, GDP/poverty chart, county snapshot, youth unemployment trend |
| 2 | 📊 **Economic Indicators** | 20+ macro indicators with correlation heatmap, OLS scatter, 5-yr Holt-Winters forecasts |
| 3 | 🗺️ **County Inequality Map** | KMeans k=5 clustering, interactive Folium bubble map, regional bar charts |
| 4 | 💚 **M-Pesa Impact Predictor** | Ridge/GBM/RF regression proving mobile money reduces poverty (R²=0.904) |
| 5 | 🎓 **Youth Unemployment** | GBM forecaster + interactive scenario simulator with GDP/FDI/Education sliders |
| 6 | 🔮 **Economic Forecaster** | Holt-Winters + ARIMA(2,1,2) with 80% CI band, multi-indicator forecast table |
| 7 | ⚖️ **County Comparison** | Side-by-side radar chart + bar chart for any two counties |
| 8 | 🏛️ **Policy Simulator** | 5-lever policy simulation with waterfall impact chart and scenario summary |
| 9 | 🔍 **Anomaly Detection** | Isolation Forest detecting economic shocks (2008 GFC, 2020 COVID...) |
| 10 | 💬 **NL Query Engine** | Ask plain-English questions → instant data-backed chart answers |

---

## 🤖 Machine Learning Models

| Model | Task | Performance |
|-------|------|-------------|
| Gradient Boosting | Poverty prediction | R² = 0.904 |
| Random Forest | Poverty prediction | R² = 0.882 |
| Ridge Regression | Poverty prediction | R² = 0.871 |
| KMeans (k=5) | County segmentation | Silhouette > 0.58 |
| Holt-Winters ES | Economic forecasting | MAE < 0.8pp |
| ARIMA(2,1,2) | Economic forecasting | 95% CI forecasts |
| Isolation Forest | Anomaly detection | Contamination=10% |

---

## 📡 Data Sources

| Dataset | Source | Coverage |
|---------|--------|----------|
| Macro Indicators | [World Bank Open Data](https://data.worldbank.org/country/KE) | 2000–2023, 16 indicators |
| County Data | [KNBS 2019 Census](https://www.knbs.or.ke/2019-kenya-population-and-housing-census/) | All 47 counties, 12 features |
| Mobile Money | [CBK Annual Reports](https://www.centralbank.go.ke/annual-reports/) | 2007–2023, M-Pesa & inclusion |
| Youth Unemployment | [ILO ILOSTAT](https://ilostat.ilo.org/data/) | 2005–2023 |
| Sector Employment | [KNBS Labour Survey](https://www.knbs.or.ke/) | 2010–2023, 9 sectors |
| Financial Inclusion | [FinAccess Survey](https://www.knbs.or.ke/finaccess-household-survey/) | Household survey data |

---

## 🛠️ Technology Stack

```
Frontend:       Streamlit 1.32+
Data:           Pandas 2.1+, NumPy 1.26+, PyArrow 14+
ML Models:      Scikit-learn 1.4+ (GBM, RF, Ridge, KMeans, IsolationForest)
Forecasting:    Statsmodels 0.14+ (Holt-Winters, ARIMA)
Visualisation:  Plotly 5.18+, Altair 5
Mapping:        Folium 0.16+, streamlit-folium 0.18+
PDF Reports:    ReportLab 4.0+
Notebooks:      Jupyter 4.0+, nbformat 5.9+, nbconvert 7.14+
API:            wbgapi 1.0+ (World Bank)
```

---

## 📁 Project Structure

```
kenya-economic-pulse/
├── app.py                              # Main Streamlit app (10 pages, full routing)
├── requirements.txt                    # All Python dependencies
├── .streamlit/config.toml              # Dark theme configuration
│
├── data/                               # 6 CSV data files
│   ├── kenya_macro_indicators.csv      # 24 rows × 16 cols (World Bank)
│   ├── kenya_county_data.csv           # 47 rows × 12 cols (KNBS)
│   ├── kenya_mobile_money.csv          # 17 rows × 8 cols (CBK)
│   ├── kenya_youth_unemployment.csv    # 19 rows × 8 cols (ILO)
│   ├── kenya_sector_employment.csv     # 14 rows × 10 cols (KNBS)
│   └── kenya_regional_stats.csv        # 8 rows × 8 cols (aggregated)
│
├── pages/                              # 10 Streamlit page modules
│   ├── economic_indicators.py          # Page 2: Macro dashboard
│   ├── county_inequality.py            # Page 3: Map + clustering
│   ├── mobile_money.py                 # Page 4: M-Pesa ML model
│   ├── youth_unemployment.py           # Page 5: Youth GBM model
│   ├── forecaster.py                   # Page 6: HW + ARIMA forecasts
│   ├── county_comparison.py            # Page 7: Side-by-side comparison
│   ├── policy_simulator.py             # Page 8: Policy what-if
│   ├── anomaly_detection.py            # Page 9: Isolation Forest
│   ├── nlq_engine.py                   # Page 10: NL query engine
│   └── developer.py                    # Page 11: About / developer info
│
├── utils/                              # Utility modules
│   ├── data_fetcher.py                 # World Bank API + fallback datasets
│   ├── ml_models.py                    # All ML model functions
│   └── report_generator.py            # PDF report generation
│
├── src/                                # Modular source code
│   ├── data/
│   │   ├── loader.py                   # Dataset loading functions
│   │   └── validator.py                # Data validation utilities
│   ├── features/
│   │   └── engineering.py              # Feature engineering
│   ├── models/
│   │   ├── regression.py               # Regression models
│   │   ├── clustering.py               # KMeans clustering
│   │   └── forecasting.py              # Time-series forecasting
│   └── visualization/
│       └── charts.py                   # Plotly chart builders
│
└── notebooks/
    ├── kenya_economic_pulse_analysis.ipynb  # Executed DS pipeline (29 cells)
    └── build_notebook.py                    # Notebook builder script
```

---

## 🔑 Key Findings

| Finding | Detail |
|---------|--------|
| 💚 **M-Pesa Effect** | GBM R²=0.904 confirms financial inclusion is #1 predictor of poverty. Poverty fell 46.8%→33.5% since 2007 as inclusion rose 26.4%→85.1% |
| 🗺️ **County Gap** | 69pp poverty gap: Wajir (82.4%) vs Kiambu (13.2%). North-Eastern counties in critical need tier |
| 🎓 **Youth Crisis** | 61.5% youth unemployment — 4.5× the global average (13.6%). Education spending is #1 policy lever |
| 📈 **Growth Resilient** | Kenya averaged ~5.2% GDP growth 2000–2023 despite COVID, elections, drought |
| ⚡ **Power Divide** | Electricity access: 10.8% (Turkana) to 92.4% (Nairobi). 11M+ Kenyans off-grid |
| 💰 **Diaspora Power** | Remittances hit USD 4.2B (2023) — now larger than FDI inflows |

---

## ⚡ Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/kaks2679/project.git
cd project
pip install -r requirements.txt
```

### 2. Run Dashboard
```bash
streamlit run app.py
```
The app will open at `http://localhost:8501`.

### 3. Run Jupyter Notebook
```bash
cd notebooks
jupyter lab kenya_economic_pulse_analysis.ipynb
```

### 4. Rebuild Notebook
```bash
cd notebooks
python build_notebook.py          # Re-generate notebook structure
jupyter nbconvert --execute ...   # Re-execute cells
```

---

## ☁️ Deploy to Streamlit Cloud

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select `app.py` as the main file
5. Click **Deploy** — live in ~2 minutes!

---

## 📓 Jupyter Notebook

The notebook `notebooks/kenya_economic_pulse_analysis.ipynb` contains:

| Section | Content |
|---------|---------|
| 1. Environment | Package install + imports |
| 2. Data Loading | All 6 CSV datasets |
| 3. Data Cleaning | Missing values, validation, interpolation |
| 4. EDA | 5 charts: macro trends, correlation matrix, M-Pesa, county inequality, youth unemployment |
| 5. ML Models | Poverty regression (GBM R²=0.904), KMeans clustering, youth unemployment GBM, Holt-Winters forecasting, Isolation Forest |
| 6. Policy Simulation | 4 policy scenarios comparison |
| 7. Conclusions | Key findings + 5 policy recommendations |
| 8. Appendix | Data source URLs and citations |

**Total: 29 cells (20 code + 9 markdown) | Executed clean with 0 errors**

---

## 👤 Author

**Stephen Muema** | Data Scientist & ML Engineer

- 🌐 Portfolio: [muemastephenportfolio.netlify.app](https://muemastephenportfolio.netlify.app/)
- 🐙 GitHub: [github.com/kaks2679](https://github.com/kaks2679)
- 📧 Email: stephenmuema@proton.me
- 📍 Location: Nairobi, Kenya 🇰🇪

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Kenya Economic Pulse v2.2.0 · April 2026 · Built with Python & Streamlit*
