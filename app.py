"""
Kenya Economic Pulse — Main Streamlit Application
10-page interactive data science dashboard for Kenya economic analysis.
Author: Stephen Muema | Data Scientist & ML Engineer
Portfolio: https://muemastephenportfolio.netlify.app/
GitHub:    https://github.com/kaks2679/project
Version:   2.2.0  |  April 2026
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# ── Page config (MUST be first Streamlit call) ──────────────────────
st.set_page_config(
    page_title="Kenya Economic Pulse | Stephen Muema",
    page_icon="🇰🇪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help":    "https://github.com/kaks2679/project",
        "Report a bug":"mailto:stephenmuema@proton.me",
        "About":       "Kenya Economic Pulse v2.2 — Built by Stephen Muema, Data Scientist",
    }
)

# ── Global CSS styles ────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D1B2A 0%, #1B2838 100%);
        border-right: 1px solid #2C3E50;
    }
    [data-testid="stSidebar"] * { color: #ECF0F1 !important; }

    [data-testid="stMetric"] {
        background: #1C2833;
        border-radius: 10px;
        padding: 12px 16px;
        border: 1px solid #2C3E50;
    }
    [data-testid="stMetricLabel"] { color: #AAB7B8 !important; font-size: .85rem; }
    [data-testid="stMetricValue"] { color: #ECF0F1 !important; }

    .streamlit-expanderHeader { color: #AED6F1 !important; }

    .stTabs [data-baseweb="tab-list"]  { background: #1C2833; border-radius: 10px; padding: 4px; }
    .stTabs [data-baseweb="tab"]       { color: #AAB7B8 !important; border-radius: 8px; padding: 8px 16px; }
    .stTabs [aria-selected="true"]     { background: #2980B9 !important; color: white !important; }

    .stDownloadButton button {
        background: #2980B9 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
    }

    ::-webkit-scrollbar        { width: 6px; }
    ::-webkit-scrollbar-track  { background: #0E1117; }
    ::-webkit-scrollbar-thumb  { background: #2C3E50; border-radius: 3px; }

    div[data-testid="stRadio"] > label { color: #AAB7B8 !important; font-size: .9rem; }
    div[data-testid="stRadio"] > div > label { color: #ECF0F1 !important; }
</style>
""", unsafe_allow_html=True)

# ── Page imports (after set_page_config) ────────────────────────────
from utils.data_fetcher import get_all_data
from pages import (
    economic_indicators,
    county_inequality,
    mobile_money,
    youth_unemployment,
    forecaster,
    county_comparison,
    policy_simulator,
    anomaly_detection,
    nlq_engine,
    developer,
)

# ── Navigation pages ─────────────────────────────────────────────────
PAGES = [
    "🏠 Overview",
    "📊 Economic Indicators",
    "🗺️ County Inequality Map",
    "💚 M-Pesa Impact Predictor",
    "🎓 Youth Unemployment",
    "🔮 Economic Forecaster",
    "⚖️ County Comparison",
    "🏛️ Policy Simulator",
    "🔍 Anomaly Detection",
    "💬 NL Query Engine",
    "👨‍💻 Developer / About",
]

# ── Data loading with caching ────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_data():
    return get_all_data()


# ── Overview page ────────────────────────────────────────────────────
def render_overview(data: dict):
    macro  = data["macro"]
    mm     = data["mobile_money"]
    yu     = data["youth_unemp"]
    county = data["county"]

    # Hero banner
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1B2631 0%, #154360 50%, #0E6655 100%);
                padding: 3rem 2rem; border-radius: 20px; margin-bottom: 2rem; text-align:center;'>
        <div style='font-size:4rem'>🇰🇪</div>
        <h1 style='color:white; font-size:2.8rem; margin:.5rem 0;'>Kenya Economic Pulse</h1>
        <p style='color:#AED6F1; font-size:1.15rem; max-width:750px; margin:.5rem auto 1.5rem;'>
            Real-time economic intelligence for Kenya — powered by World Bank data,
            KNBS Census, CBK mobile money statistics, and machine learning.
        </p>
        <div style='display:flex; justify-content:center; gap:.8rem; flex-wrap:wrap;'>
            <span style='background:rgba(255,255,255,.12); color:white; padding:.4rem 1rem;
                         border-radius:20px; font-size:.85rem;'>📊 10 Interactive Dashboards</span>
            <span style='background:rgba(255,255,255,.12); color:white; padding:.4rem 1rem;
                         border-radius:20px; font-size:.85rem;'>🤖 7 ML Models</span>
            <span style='background:rgba(255,255,255,.12); color:white; padding:.4rem 1rem;
                         border-radius:20px; font-size:.85rem;'>🗺️ 47 County Analysis</span>
            <span style='background:rgba(255,255,255,.12); color:white; padding:.4rem 1rem;
                         border-radius:20px; font-size:.85rem;'>💬 NL Query Engine</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI strip
    st.markdown("### 🌍 Kenya at a Glance")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    last_mm  = mm.iloc[-1]
    last_yu  = yu.iloc[-1]
    gdp_val  = macro["GDP Growth (%)"].dropna().iloc[-1] if "GDP Growth (%)" in macro.columns else 4.8
    inf_val  = macro["Inflation Rate (%)"].dropna().iloc[-1] if "Inflation Rate (%)" in macro.columns else 7.8

    kpis = [
        ("🇰🇪 Population",   "56.4M",                                   "#3498DB"),
        ("📈 GDP Growth",     f"{gdp_val:.1f}%",                         "#27AE60"),
        ("💸 Inflation",      f"{inf_val:.1f}%",                         "#E74C3C"),
        ("📱 M-Pesa Users",   f"{last_mm['MPesa_Users_M']:.0f}M",        "#8E44AD"),
        ("🎓 Youth Unemp.",   f"{last_yu['Youth_Unemployment_Pct']:.1f}%","#F39C12"),
        ("🏚️ Poverty Rate",  f"{last_mm['Poverty_Rate_National']:.1f}%", "#E67E22"),
    ]
    for col, (lbl, val, color) in zip([c1, c2, c3, c4, c5, c6], kpis):
        col.markdown(f"""
        <div style='background:#1C2833; padding:1rem; border-radius:10px;
                    border-top:3px solid {color}; text-align:center; min-height:90px;'>
            <div style='color:#AAB7B8; font-size:.75rem; margin-bottom:.3rem'>{lbl}</div>
            <div style='color:{color}; font-size:1.4rem; font-weight:bold'>{val}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick charts: 2-column layout
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 📈 GDP Growth vs Poverty (2007–2023)")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        if not macro.empty and "GDP Growth (%)" in macro.columns:
            mac_trim = macro[macro["Year"] >= 2007].copy()
            gdp_vals = mac_trim["GDP Growth (%)"].fillna(0)
            fig.add_trace(go.Bar(
                x=mac_trim["Year"], y=gdp_vals,
                name="GDP Growth (%)",
                marker_color=["#27AE60" if v >= 0 else "#E74C3C" for v in gdp_vals],
                opacity=0.75
            ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=mm["Year"], y=mm["Poverty_Rate_National"],
            name="Poverty Rate (%)", mode="lines+markers",
            line=dict(color="#E74C3C", width=2.5), marker=dict(size=6)
        ), secondary_y=True)
        fig.update_layout(
            plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
            font=dict(color="white"), height=340,
            legend=dict(bgcolor="#1C2833", font=dict(color="white"), x=0, y=1.1, orientation="h"),
            hovermode="x unified",
            xaxis=dict(gridcolor="#2C3E50"),
            margin=dict(l=10, r=10, t=30, b=20)
        )
        fig.update_yaxes(gridcolor="#2C3E50", secondary_y=False, title_text="GDP Growth (%)")
        fig.update_yaxes(gridcolor="#2C3E50", secondary_y=True,  title_text="Poverty (%)")
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("#### 📱 Mobile Financial Inclusion Rise")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=mm["Year"], y=mm["Financial_Inclusion_Pct"],
            fill="tozeroy",
            fillcolor="rgba(52,152,219,0.2)",
            line=dict(color="#3498DB", width=2.5),
            name="Financial Inclusion (%)"
        ))
        fig2.add_trace(go.Scatter(
            x=mm["Year"], y=mm["MPesa_Users_M"] * 2,
            line=dict(color="#27AE60", width=2, dash="dot"),
            name="M-Pesa Users (×2 scaled)"
        ))
        fig2.update_layout(
            plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
            font=dict(color="white"), height=340,
            legend=dict(bgcolor="#1C2833", font=dict(color="white"), x=0, y=1.1, orientation="h"),
            hovermode="x unified",
            xaxis=dict(gridcolor="#2C3E50"),
            yaxis=dict(gridcolor="#2C3E50"),
            margin=dict(l=10, r=10, t=30, b=20)
        )
        st.plotly_chart(fig2, use_container_width=True)

    # County snapshot
    st.markdown("#### 🗺️ County Poverty Snapshot — Top 10 vs Bottom 10")
    top_poor = county.nlargest(10, "Poverty_Rate")[["County", "Poverty_Rate", "Region"]]
    top_rich = county.nsmallest(10, "Poverty_Rate")[["County", "Poverty_Rate", "Region"]]
    snap_df  = pd.concat([
        top_poor.assign(Type="Highest Poverty"),
        top_rich.assign(Type="Lowest Poverty")
    ])
    fig_snap = px.bar(
        snap_df, x="County", y="Poverty_Rate", color="Type",
        color_discrete_map={"Highest Poverty": "#E74C3C", "Lowest Poverty": "#27AE60"},
        barmode="group",
        labels={"Poverty_Rate": "Poverty Rate (%)"},
    )
    fig_snap.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white"), height=360,
        legend=dict(bgcolor="#1C2833", font=dict(color="white")),
        xaxis=dict(gridcolor="#2C3E50", tickangle=-30),
        yaxis=dict(gridcolor="#2C3E50"),
        margin=dict(l=10, r=10, t=20, b=10)
    )
    st.plotly_chart(fig_snap, use_container_width=True)

    # Youth unemployment trend
    st.markdown("#### 🎓 Youth Unemployment Trend (2005–2023)")
    fig_yu = go.Figure()
    fig_yu.add_trace(go.Scatter(
        x=yu["Year"], y=yu["Youth_Unemployment_Pct"],
        fill="tozeroy",
        fillcolor="rgba(142,68,173,0.2)",
        line=dict(color="#8E44AD", width=2.5),
        mode="lines+markers",
        name="Youth Unemployment (%)",
        marker=dict(size=7)
    ))
    fig_yu.add_hline(
        y=13.6, line_dash="dash", line_color="#27AE60",
        annotation_text="🌍 Global avg: 13.6%",
        annotation_font_color="#27AE60"
    )
    fig_yu.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white"), height=300,
        legend=dict(bgcolor="#1C2833", font=dict(color="white")),
        hovermode="x unified",
        xaxis=dict(gridcolor="#2C3E50"),
        yaxis=dict(gridcolor="#2C3E50", title="Youth Unemployment (%)"),
        margin=dict(l=10, r=10, t=20, b=20)
    )
    st.plotly_chart(fig_yu, use_container_width=True)

    # About project box
    st.markdown("""
    <div style='background:#1C2833; padding:1.5rem 2rem; border-radius:12px;
                border:1px solid #2C3E50; margin-top:1rem;'>
        <h3 style='color:#3498DB; margin-top:0'>🔬 About This Project</h3>
        <p style='color:#AAB7B8; line-height:1.8;'>
            <b style='color:white'>Kenya Economic Pulse</b> is an end-to-end data science portfolio
            combining open-source datasets with machine learning to answer Kenya's most pressing
            economic questions using Python, Streamlit, and real data.
        </p>
        <div style='display:grid; grid-template-columns:1fr 1fr 1fr; gap:.8rem; margin-top:1rem;'>
            <div style='background:#0E1117; padding:.8rem 1rem; border-radius:8px; border-left:3px solid #3498DB;'>
                <b style='color:white'>📊 Economic Indicators</b>
                <p style='color:#7F8C8D; font-size:.85rem; margin:.3rem 0 0'>20+ macro indicators + 5yr Holt-Winters forecasting</p>
            </div>
            <div style='background:#0E1117; padding:.8rem 1rem; border-radius:8px; border-left:3px solid #27AE60;'>
                <b style='color:white'>🗺️ County Inequality Map</b>
                <p style='color:#7F8C8D; font-size:.85rem; margin:.3rem 0 0'>47 counties clustered by KMeans into 5 development tiers</p>
            </div>
            <div style='background:#0E1117; padding:.8rem 1rem; border-radius:8px; border-left:3px solid #8E44AD;'>
                <b style='color:white'>💚 M-Pesa Impact Model</b>
                <p style='color:#7F8C8D; font-size:.85rem; margin:.3rem 0 0'>Gradient Boosting R²=0.904 proving mobile money reduces poverty</p>
            </div>
            <div style='background:#0E1117; padding:.8rem 1rem; border-radius:8px; border-left:3px solid #F39C12;'>
                <b style='color:white'>🔮 Economic Forecaster</b>
                <p style='color:#7F8C8D; font-size:.85rem; margin:.3rem 0 0'>Holt-Winters + ARIMA(2,1,2) with confidence intervals</p>
            </div>
            <div style='background:#0E1117; padding:.8rem 1rem; border-radius:8px; border-left:3px solid #E74C3C;'>
                <b style='color:white'>🔍 Anomaly Detection</b>
                <p style='color:#7F8C8D; font-size:.85rem; margin:.3rem 0 0'>Isolation Forest detecting economic shocks (2008, 2020…)</p>
            </div>
            <div style='background:#0E1117; padding:.8rem 1rem; border-radius:8px; border-left:3px solid #1ABC9C;'>
                <b style='color:white'>💬 NL Query Engine</b>
                <p style='color:#7F8C8D; font-size:.85rem; margin:.3rem 0 0'>Ask plain-English questions — get instant data-backed answers</p>
            </div>
        </div>
        <p style='color:#566573; font-size:.82rem; margin:1rem 0 0;'>
            🛠️ Stack: Python · Streamlit · Scikit-learn · Plotly · Folium · Statsmodels · World Bank API · KNBS · CBK
        </p>
    </div>
    """, unsafe_allow_html=True)


# ── Sidebar navigation ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:1rem 0;'>
        <div style='font-size:3rem'>🇰🇪</div>
        <h2 style='color:#3498DB; margin:.3rem 0; font-size:1.2rem'>Kenya Economic Pulse</h2>
        <p style='color:#7F8C8D; font-size:.75rem; margin:0'>by Stephen Muema · v2.2.0</p>
        <hr style='border-color:#2C3E50; margin:.8rem 0'>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "📌 Navigate",
        PAGES,
        key="nav_page"
    )

    st.markdown("<hr style='border-color:#2C3E50'>", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#1C2833; padding:.8rem; border-radius:8px; font-size:.78rem;'>
        <b style='color:#3498DB'>📡 Data Sources</b><br>
        <span style='color:#AAB7B8'>
        • World Bank Open API<br>
        • KNBS 2019 Census<br>
        • CBK Annual Reports<br>
        • ILO Labour Statistics<br>
        • FinAccess Survey 2021<br>
        • KIHBS 2021
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center; font-size:.74rem; color:#566573;'>
        Built with ❤️ by<br>
        <a href='https://muemastephenportfolio.netlify.app/'
           style='color:#3498DB; text-decoration:none;'>Stephen Muema</a><br>
        Data Scientist &amp; ML Engineer<br>
        Nairobi, Kenya 🇰🇪<br><br>
        <a href='https://github.com/kaks2679/project'
           style='color:#566573; text-decoration:none;'>🐙 GitHub Repo</a>
    </div>
    """, unsafe_allow_html=True)


# ── Load data ────────────────────────────────────────────────────────
with st.spinner("🔄 Loading Kenya economic data..."):
    data = load_data()


# ── Route pages ──────────────────────────────────────────────────────
if page == "🏠 Overview":
    render_overview(data)
elif page == "📊 Economic Indicators":
    economic_indicators.render(data)
elif page == "🗺️ County Inequality Map":
    county_inequality.render(data)
elif page == "💚 M-Pesa Impact Predictor":
    mobile_money.render(data)
elif page == "🎓 Youth Unemployment":
    youth_unemployment.render(data)
elif page == "🔮 Economic Forecaster":
    forecaster.render(data)
elif page == "⚖️ County Comparison":
    county_comparison.render(data)
elif page == "🏛️ Policy Simulator":
    policy_simulator.render(data)
elif page == "🔍 Anomaly Detection":
    anomaly_detection.render(data)
elif page == "💬 NL Query Engine":
    nlq_engine.render(data)
elif page == "👨‍💻 Developer / About":
    developer.render(data)
