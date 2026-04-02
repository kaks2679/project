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
from datetime import datetime

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

    # Hero banner — compact
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1B2631 0%, #154360 50%, #0E6655 100%);
                padding: 1.2rem 1.8rem; border-radius: 14px; margin-bottom: 1.2rem;
                display:flex; align-items:center; gap:1rem; flex-wrap:wrap;'>
        <div style='font-size:2.4rem; line-height:1'>🇰🇪</div>
        <div style='flex:1; min-width:200px;'>
            <h1 style='color:white; font-size:1.6rem; margin:0; font-weight:700;'>Kenya Economic Pulse</h1>
            <p style='color:#AED6F1; font-size:.85rem; margin:.2rem 0 .5rem;'>
                Real-time economic intelligence — World Bank · KNBS · CBK · Machine Learning
            </p>
            <div style='display:flex; gap:.5rem; flex-wrap:wrap;'>
                <span style='background:rgba(255,255,255,.12); color:white; padding:.25rem .75rem;
                             border-radius:20px; font-size:.75rem;'>📊 10 Dashboards</span>
                <span style='background:rgba(255,255,255,.12); color:white; padding:.25rem .75rem;
                             border-radius:20px; font-size:.75rem;'>🤖 7 ML Models</span>
                <span style='background:rgba(255,255,255,.12); color:white; padding:.25rem .75rem;
                             border-radius:20px; font-size:.75rem;'>🗺️ 47 Counties</span>
                <span style='background:rgba(255,255,255,.12); color:white; padding:.25rem .75rem;
                             border-radius:20px; font-size:.75rem;'>💬 NLQ Engine</span>
            </div>
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

    # ── Report download ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📥 Download Executive Summary Report")
    rpt_col1, rpt_col2, rpt_col3 = st.columns([2, 2, 3])
    with rpt_col1:
        try:
            from utils.report_generator import generate_executive_summary, REPORTLAB_OK
            if REPORTLAB_OK:
                with st.spinner("Generating PDF…"):
                    pdf_bytes = generate_executive_summary(data)
                if pdf_bytes:
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"Kenya_Economic_Pulse_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        help="Full executive summary with KPIs, findings & policy recommendations"
                    )
            else:
                st.info("Install `reportlab` for PDF reports")
        except Exception as e:
            st.warning(f"PDF unavailable: {e}")
    with rpt_col2:
        try:
            from utils.report_generator import generate_html_summary
            html_report = generate_html_summary(data)
            st.download_button(
                label="🌐 Download HTML Report",
                data=html_report.encode(),
                file_name=f"Kenya_Economic_Pulse_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                help="Executive summary as a styled HTML file (open in any browser)"
            )
        except Exception as e:
            st.warning(f"HTML report error: {e}")
    with rpt_col3:
        st.markdown("""
        <div style='background:#1C2833; padding:.7rem 1rem; border-radius:8px;
                    border-left:3px solid #3498DB; font-size:.82rem; color:#AAB7B8;'>
            <b style='color:white'>Report includes:</b> KPI dashboard · Key findings ·
            County snapshot (top/bottom poverty) · 6 policy recommendations · Data sources
        </div>
        """, unsafe_allow_html=True)

    # ── Stakeholder insights ─────────────────────────────────────────
    st.markdown("---")
    st.markdown("""
    <div style='background:#1C2833; padding:1.2rem 1.5rem; border-radius:12px;
                border:1px solid #2C3E50; margin-bottom:1rem;'>
        <h3 style='color:#3498DB; margin-top:0; font-size:1.1rem;'>💡 Stakeholder Insights & Dashboard Guide</h3>
        <div style='display:grid; grid-template-columns:1fr 1fr; gap:.8rem; margin-top:.8rem;'>
            <div style='background:#0E1117; padding:.7rem 1rem; border-radius:8px; border-left:3px solid #3498DB;'>
                <b style='color:#3498DB; font-size:.85rem;'>🏛️ Policy Makers & Government</b>
                <p style='color:#AAB7B8; font-size:.8rem; margin:.3rem 0 0; line-height:1.6;'>
                    Use <b>Policy Simulator</b> to model interventions (mobile expansion, education spend, FDI).
                    <b>County Inequality Map</b> identifies which counties need emergency support.
                    <b>Anomaly Detection</b> flags economic shocks for early response.
                </p>
            </div>
            <div style='background:#0E1117; padding:.7rem 1rem; border-radius:8px; border-left:3px solid #27AE60;'>
                <b style='color:#27AE60; font-size:.85rem;'>📈 Investors & Financial Analysts</b>
                <p style='color:#AAB7B8; font-size:.8rem; margin:.3rem 0 0; line-height:1.6;'>
                    <b>Economic Indicators</b> page shows GDP, inflation, debt trends with 5-year forecasts.
                    <b>Economic Forecaster</b> provides ARIMA + Holt-Winters projections with confidence intervals.
                    <b>M-Pesa Impact</b> quantifies digital finance market opportunity.
                </p>
            </div>
            <div style='background:#0E1117; padding:.7rem 1rem; border-radius:8px; border-left:3px solid #F39C12;'>
                <b style='color:#F39C12; font-size:.85rem;'>🎓 Researchers & Academics</b>
                <p style='color:#AAB7B8; font-size:.8rem; margin:.3rem 0 0; line-height:1.6;'>
                    <b>County Comparison</b> enables side-by-side multi-county research across 6 socioeconomic dimensions.
                    <b>NL Query Engine</b> provides instant data answers. All CSV datasets are freely downloadable
                    from each page.
                </p>
            </div>
            <div style='background:#0E1117; padding:.7rem 1rem; border-radius:8px; border-left:3px solid #E74C3C;'>
                <b style='color:#E74C3C; font-size:.85rem;'>📰 Journalists & Civil Society</b>
                <p style='color:#AAB7B8; font-size:.8rem; margin:.3rem 0 0; line-height:1.6;'>
                    <b>Youth Unemployment</b> page shows the 61.5% crisis with scenario modelling.
                    <b>County Inequality Map</b> exposes the NE Kenya development gap.
                    Download the <b>Executive Summary PDF</b> above for briefing documents.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # About project box
    with st.expander("🔬 About This Project & Tech Stack"):
        st.markdown("""
        **Kenya Economic Pulse** is an end-to-end data science portfolio combining open-source datasets
        with machine learning to answer Kenya's most pressing economic questions.

        | Page | What it does |
        |------|-------------|
        | 📊 Economic Indicators | 20+ macro indicators · Holt-Winters + ARIMA forecasts |
        | 🗺️ County Inequality Map | 47 counties · KMeans clustering · Folium choropleth |
        | 💚 M-Pesa Impact Predictor | GBM regression R²=0.904 · Feature importance |
        | 🎓 Youth Unemployment | ML forecast · Scenario simulator |
        | 🔮 Economic Forecaster | Holt-Winters + ARIMA(2,1,2) · Confidence intervals |
        | ⚖️ County Comparison | Up to 5 counties · Radar + bar charts |
        | 🏛️ Policy Simulator | 5-lever what-if · Waterfall chart |
        | 🔍 Anomaly Detection | Isolation Forest · Known economic shocks |
        | 💬 NL Query Engine | Plain-English questions · 16 topic patterns |
        | 👨‍💻 Developer / About | Full methodology + data sources |

        **Stack:** Python · Streamlit · Scikit-learn · Plotly · Folium · Statsmodels ·
        World Bank API · KNBS · CBK · ReportLab
        """)


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
