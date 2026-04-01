# 🇰🇪 Kenya Economic Pulse

> **A full end-to-end Data Science project by Stephen Muema — Data Scientist & ML Engineer**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://kenya-economic-pulse.streamlit.app)

---

## 📊 Overview

**Kenya Economic Pulse** is an interactive data science dashboard that answers Kenya's most important economic questions using real data, machine learning, and stunning visualizations.

### 🔍 4 Interactive Modules

| Module | Description |
|--------|-------------|
| 📊 **Economic Indicators** | 20+ macro indicators (GDP, inflation, unemployment) with 5-year Holt-Winters forecasting |
| 🗺️ **County Inequality Map** | All 47 counties analyzed and clustered by poverty, HDI, mobile penetration using KMeans |
| 💚 **M-Pesa Impact Predictor** | Gradient Boosting regression proving mobile money reduces poverty |
| 🎓 **Youth Unemployment Forecaster** | ML model + interactive scenario simulator for policy decisions |

---

## 🛠️ Tech Stack

```
Language:      Python 3.10+
Dashboard:     Streamlit
ML Models:     Scikit-learn (KMeans, GBM, Random Forest, Ridge)
Forecasting:   Statsmodels (Holt-Winters, ARIMA)
Visualization: Plotly, Folium, Streamlit-Folium
Data APIs:     World Bank (wbgapi)
Data Sources:  KNBS 2019 Census, CBK Annual Reports, ILO, FinAccess 2021
```

---

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/kaks2679/project.git
cd project

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

---

## 📡 Data Sources

- **World Bank Open Data API** — GDP, inflation, unemployment, poverty, remittances
- **Kenya National Bureau of Statistics (KNBS)** — 2019 Census county-level data
- **Central Bank of Kenya (CBK)** — Mobile money & financial inclusion statistics
- **International Labour Organization (ILO)** — Youth unemployment benchmarks
- **FinAccess Survey 2021** — Financial inclusion data

---

## 🌟 Key Insights

- 📱 **M-Pesa launched in 2007** — Kenya's financial inclusion rose from 26% → 85%
- 🏚️ **Poverty dropped** from 46.8% (2007) → 33.5% (2023) — ML confirms mobile money as key driver
- 🎓 **Youth unemployment at 61.5%** — 4.5× the global average of 13.6%
- 🗺️ **NE Kenya** (Wajir, Mandera, Turkana) has 70–82% poverty vs Nairobi at 17%
- 📈 **ICT sector employment** grew from 1.2% → 6.8% (2010–2023)

---

## 👤 Author

**Stephen Muema**
- 🌐 Portfolio: [muemastephenportfolio.netlify.app](https://muemastephenportfolio.netlify.app)
- 💼 LinkedIn: [Stephen Muema](https://www.linkedin.com/in/stephen-muema-617339359)
- 🐙 GitHub: [@Kaks753](https://github.com/Kaks753)
- 📧 Email: musyokas753@gmail.com
- 📍 Nairobi, Kenya 🇰🇪

---

## 📄 License

MIT License — Free to use, learn from, and build upon.
