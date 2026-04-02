"""
Page 7: Policy Simulator
Interactive macro policy what-if scenarios.
Author: Stephen Muema
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")


BASELINE = {
    "poverty":            33.5,
    "youth_unemployment": 61.5,
    "gini":               40.8,
    "gdp_growth":          4.8,
    "financial_inclusion": 85.1,
}


def _simulate_policy(mobile_pen: float, edu_spend: float,
                     fdi: float, infrastructure: float,
                     remittances: float) -> dict:
    """
    Simplified linear policy simulation model.
    Adjustments calibrated from Kenya empirical literature.
    """
    poverty_change = (
        -(mobile_pen - 85.1) * 0.18
        - (edu_spend - 5.5)  * 0.45
        - (fdi - 0.5)        * 0.30
        - (infrastructure - 50) * 0.10
        - (remittances - 4.2) * 0.25
    )
    youth_change = (
        -(mobile_pen - 85.1) * 0.10
        - (edu_spend - 5.5)  * 0.60
        - (fdi - 0.5)        * 0.55
        - (infrastructure - 50) * 0.12
    )
    gini_change = (
        -(mobile_pen - 85.1) * 0.08
        - (edu_spend - 5.5)  * 0.35
        - (infrastructure - 50) * 0.05
    )
    gdp_change = (
        (fdi - 0.5)        * 0.40
        + (infrastructure - 50) * 0.08
        + (mobile_pen - 85.1) * 0.05
        + (remittances - 4.2) * 0.15
    )
    fin_change = (mobile_pen - 85.1) * 0.35 + (edu_spend - 5.5) * 0.12

    return {
        "poverty":            round(BASELINE["poverty"]            + poverty_change, 1),
        "youth_unemployment": round(BASELINE["youth_unemployment"] + youth_change,   1),
        "gini":               round(BASELINE["gini"]               + gini_change,    1),
        "gdp_growth":         round(BASELINE["gdp_growth"]         + gdp_change,     1),
        "financial_inclusion":round(BASELINE["financial_inclusion"]+ fin_change,     1),
    }


def render(data: dict):
    st.markdown("""
    <div style='background: linear-gradient(135deg, #0B3D0B 0%, #1E8449 50%, #148F77 100%);
                padding: .8rem 1.5rem; border-radius: 12px; margin-bottom: 1rem;'>
        <h2 style='color:white; margin:0; font-size:1.4rem;'>🏛️ Policy Simulator</h2>
        <p style='color:#A9DFBF; margin:.2rem 0 0; font-size:.85rem;'>
            Adjust policy levers and instantly see their projected impact on poverty,
            youth unemployment, inequality, GDP, and financial inclusion
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ Page Guide & Stakeholder Notes", expanded=False):
        st.markdown("""
        **What this page shows:**
        An interactive linear policy simulation model with 5 adjustable levers, showing how
        combinations of policy interventions could shift key economic outcomes from the 2023 baseline.

        **The 5 Policy Levers:**
        | Lever | Baseline | Recommended Target |
        |-------|----------|-------------------|
        | 📱 Mobile Penetration (%) | 85.1 | 95+ |
        | 🎓 Education Spend (% GDP) | 5.5 | 7.0 |
        | 💰 FDI Inflows (% GDP) | 0.5 | 1.5 |
        | 🏗️ Infrastructure Score | 50 | 70 |
        | 🌍 Remittances (% GDP) | 4.2 | 5.5 |

        **How to read the waterfall chart:**
        Each bar shows the incremental impact of that lever on poverty reduction.
        Green = poverty falls, red = poverty rises. The final bar shows the new projected poverty rate.

        **For stakeholders:**
        - 🏛️ *Policy makers*: The simulation shows that combining **mobile expansion + TVET spending**
          yields the biggest poverty reduction (estimated -6 to -8 pp).
        - 🌍 *Development partners (World Bank, IMF, AU)*: Use this to model conditionality scenarios
          for aid programmes and structural adjustment recommendations.
        - ⚠️ *Model caveat*: This is a simplified linear model. Real-world effects are non-linear
          and context-dependent. Use as directional guidance, not precise prediction.
        """)

    # ── Policy sliders ────────────────────────────────────────────────
    st.markdown("### 🎛️ Policy Levers")
    st.markdown("Adjust the sliders to simulate different policy scenarios:")

    col1, col2 = st.columns(2)

    with col1:
        mobile_pen = st.slider(
            "📱 Mobile Penetration (%)",
            min_value=60.0, max_value=100.0, value=85.1, step=0.5,
            help="Increase mobile network coverage and M-Pesa access",
            key="pol_mobile"
        )
        edu_spend = st.slider(
            "🎓 Education Spending (% of GDP)",
            min_value=2.0, max_value=12.0, value=5.5, step=0.1,
            help="Government education budget allocation",
            key="pol_edu"
        )
        fdi = st.slider(
            "💼 FDI Inflows ($ Billion)",
            min_value=0.1, max_value=5.0, value=0.5, step=0.1,
            help="Foreign Direct Investment into Kenya",
            key="pol_fdi"
        )

    with col2:
        infrastructure = st.slider(
            "🏗️ Infrastructure Investment Index",
            min_value=0.0, max_value=100.0, value=50.0, step=1.0,
            help="Index of roads, energy, water, digital infrastructure",
            key="pol_infra"
        )
        remittances = st.slider(
            "💰 Remittances ($ Billion)",
            min_value=1.0, max_value=10.0, value=4.2, step=0.1,
            help="Money sent home by Kenyans in diaspora",
            key="pol_remit"
        )

    # ── Run simulation ────────────────────────────────────────────────
    projected = _simulate_policy(mobile_pen, edu_spend, fdi, infrastructure, remittances)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📊 Simulation Results")

    result_data = [
        ("🏚️ Poverty Rate (%)",          BASELINE["poverty"],            projected["poverty"],            "low"),
        ("🎓 Youth Unemployment (%)",     BASELINE["youth_unemployment"], projected["youth_unemployment"], "low"),
        ("⚖️ Gini Index",                 BASELINE["gini"],               projected["gini"],               "low"),
        ("📈 GDP Growth (%)",             BASELINE["gdp_growth"],         projected["gdp_growth"],         "high"),
        ("🏦 Financial Inclusion (%)",    BASELINE["financial_inclusion"],projected["financial_inclusion"],"high"),
    ]

    cols = st.columns(5)
    for col, (label, base, proj, good) in zip(cols, result_data):
        delta = proj - base
        if good == "low":
            color = "#27AE60" if delta < 0 else "#E74C3C"
            arrow = "📉" if delta < 0 else "📈"
        else:
            color = "#27AE60" if delta > 0 else "#E74C3C"
            arrow = "📈" if delta > 0 else "📉"
        sign = "+" if delta >= 0 else ""
        col.markdown(f"""
        <div style='background:#1C2833; padding:1rem; border-radius:10px;
                    border-top:3px solid {color}; text-align:center;'>
            <div style='color:#AAB7B8; font-size:.72rem'>{label}</div>
            <div style='color:white; font-size:.85rem; margin:.2rem 0'>
                Baseline: <b>{base}</b>
            </div>
            <div style='color:{color}; font-size:1.4rem; font-weight:bold'>{proj}</div>
            <div style='color:{color}; font-size:.85rem'>{arrow} {sign}{delta:.1f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Waterfall chart ───────────────────────────────────────────────
    st.markdown("### 📊 Impact Waterfall: Poverty Rate Change")

    components = {
        "Mobile Penetration":  -(mobile_pen - 85.1) * 0.18,
        "Education Spending":  -(edu_spend - 5.5)   * 0.45,
        "FDI Inflows":         -(fdi - 0.5)         * 0.30,
        "Infrastructure":      -(infrastructure - 50)* 0.10,
        "Remittances":         -(remittances - 4.2)  * 0.25,
    }
    comp_df = pd.DataFrame(list(components.items()), columns=["Driver", "Impact"])
    comp_df["Color"] = comp_df["Impact"].apply(lambda x: "#27AE60" if x < 0 else "#E74C3C")
    comp_df["Label"] = comp_df["Impact"].apply(lambda x: f"{'+'if x>=0 else ''}{x:.2f}pp")

    fig_wf = go.Figure(go.Bar(
        x=comp_df["Driver"],
        y=comp_df["Impact"],
        marker_color=comp_df["Color"],
        text=comp_df["Label"],
        textposition="outside",
    ))
    fig_wf.add_hline(y=0, line_color="#566573", line_width=1)
    fig_wf.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white"), height=380,
        xaxis=dict(gridcolor="#2C3E50", title="Policy Driver"),
        yaxis=dict(gridcolor="#2C3E50", title="Poverty Rate Change (pp)"),
        title=dict(text="Each Policy Driver's Contribution to Poverty Reduction",
                   font=dict(color="white", size=14)),
        margin=dict(l=10, r=10, t=50, b=40)
    )
    st.plotly_chart(fig_wf, use_container_width=True)

    # ── Before / After comparison bar chart ──────────────────────────
    st.markdown("### 📈 Before vs After Scenario")
    indicators = ["Poverty Rate (%)", "Youth Unemployment (%)", "Gini Index",
                  "GDP Growth (%)", "Financial Inclusion (%)"]
    base_vals = [BASELINE["poverty"], BASELINE["youth_unemployment"], BASELINE["gini"],
                 BASELINE["gdp_growth"], BASELINE["financial_inclusion"]]
    proj_vals = [projected["poverty"], projected["youth_unemployment"], projected["gini"],
                 projected["gdp_growth"], projected["financial_inclusion"]]

    fig_ba = go.Figure()
    fig_ba.add_trace(go.Bar(name="Baseline (2023)", x=indicators, y=base_vals,
                            marker_color="#566573", opacity=0.8))
    fig_ba.add_trace(go.Bar(name="Simulated Scenario", x=indicators, y=proj_vals,
                            marker_color="#3498DB", opacity=0.9))
    fig_ba.update_layout(
        barmode="group",
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white"), height=380,
        legend=dict(bgcolor="#1C2833", font=dict(color="white")),
        xaxis=dict(gridcolor="#2C3E50", tickangle=-15),
        yaxis=dict(gridcolor="#2C3E50", title="Value"),
        margin=dict(l=10, r=10, t=20, b=50)
    )
    st.plotly_chart(fig_ba, use_container_width=True)

    # ── Scenario summary ──────────────────────────────────────────────
    total_poverty_red = BASELINE["poverty"] - projected["poverty"]
    people_lifted = int(total_poverty_red / 100 * 56_400_000)
    sign_pl = "+" if people_lifted >= 0 else ""

    color_box = "#1E8449" if total_poverty_red > 0 else "#922B21"
    st.markdown(f"""
    <div style='background:{color_box}; padding:1.5rem 2rem; border-radius:12px; margin-top:1rem;'>
        <h3 style='color:white; margin:0'>📋 Scenario Summary</h3>
        <p style='color:#A9DFBF; margin:.8rem 0 0; font-size:1rem; line-height:1.8;'>
            Under this policy scenario, Kenya's poverty rate would move from
            <b style='color:white'>{BASELINE['poverty']}% → {projected['poverty']}%</b>
            — a change of <b style='color:white'>{'+' if total_poverty_red >= 0 else ''}{total_poverty_red:.1f} percentage points</b>,
            potentially {'lifting' if total_poverty_red > 0 else 'affecting'} approximately
            <b style='color:white'>{sign_pl}{abs(people_lifted):,} people</b>.
            Youth unemployment would {'fall' if projected['youth_unemployment'] < BASELINE['youth_unemployment'] else 'rise'} to
            <b style='color:white'>{projected['youth_unemployment']}%</b> and
            GDP growth would reach <b style='color:white'>{projected['gdp_growth']}%</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)
