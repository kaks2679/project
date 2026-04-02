"""
Page 4: Youth Unemployment Forecaster & Scenario Simulator
Predict youth unemployment under custom macro-economic scenarios.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from utils.ml_models import youth_unemployment_model, simulate_scenario


def render(data: dict):
    st.markdown("""
    <div style='background: linear-gradient(135deg, #6C3483 0%, #4A235A 100%);
                padding: .8rem 1.5rem; border-radius: 12px; margin-bottom: 1rem;'>
        <h2 style='color:white; margin:0; font-size:1.4rem;'>🎓 Youth Unemployment Forecaster</h2>
        <p style='color:#D7BDE2; margin:.2rem 0 0; font-size:.85rem;'>
            ML Prediction · 5-Year Forecast · Interactive Scenario Simulator
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ Page Guide & Stakeholder Notes", expanded=False):
        st.markdown("""
        **What this page shows:**
        Kenya's youth unemployment (ages 15–24) from 2005–2023, with a Gradient Boosting ML model
        for 5-year forecasting and an interactive policy scenario simulator.

        **How to read the results:**
        - **KPI cards** — current rate, change since 2005, ML forecast 2028, global average benchmark
        - **Historical + forecast chart** — red = actual, purple = ML fit, orange = 5yr projection
        - **Sector employment stacked chart** — shifting from agriculture towards services/ICT
        - **Scenario simulator** — adjust GDP growth, FDI, university enrollment to see the modelled impact

        **For stakeholders:**
        - 🏛️ *Policy makers*: Youth unemployment at 61.5% is a **national emergency**. Each 1% GDP growth
          reduces youth unemployment by ~0.8 pp. TVET investment yields the fastest returns.
        - 📈 *Investors*: A young, growing workforce is Kenya's competitive advantage. ICT and green
          energy sectors offer the highest youth employment multipliers.
        - 🎓 *Researchers*: Use the scenario simulator to test the macro-economic levers identified in
          the ILO Kenya Employment Report (2022).
        - 💡 *Key insight*: Without intervention, youth unemployment is forecast to remain above 58%
          by 2028. Targeted FDI + skills training could reduce it below 50% by 2030.
        """)

    yu_df = data["youth_unemp"].copy()
    se_df = data["sector_employ"].copy()

    # ── Train model ──────────────────────────────────────────────────
    with st.spinner("⚙️ Training youth unemployment model..."):
        result = youth_unemployment_model(yu_df)

    # ── Key stats ────────────────────────────────────────────────────
    last_val  = yu_df["Youth_Unemployment_Pct"].iloc[-1]
    first_val = yu_df["Youth_Unemployment_Pct"].iloc[0]
    change    = round(last_val - first_val, 1)
    forecast_2028 = result["forecast_values"][-1] if result else last_val

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f"""
    <div style='background:#1C2833; padding:1.2rem; border-radius:10px;
                border-top:3px solid #E74C3C; text-align:center;'>
        <div style='color:#AAB7B8; font-size:.8rem'>Current (2023)</div>
        <div style='color:#E74C3C; font-size:1.6rem; font-weight:bold'>{last_val:.1f}%</div>
    </div>""", unsafe_allow_html=True)
    k2.markdown(f"""
    <div style='background:#1C2833; padding:1.2rem; border-radius:10px;
                border-top:3px solid #F39C12; text-align:center;'>
        <div style='color:#AAB7B8; font-size:.8rem'>Change since 2005</div>
        <div style='color:#F39C12; font-size:1.6rem; font-weight:bold'>{change:+.1f}%</div>
    </div>""", unsafe_allow_html=True)
    k3.markdown(f"""
    <div style='background:#1C2833; padding:1.2rem; border-radius:10px;
                border-top:3px solid #8E44AD; text-align:center;'>
        <div style='color:#AAB7B8; font-size:.8rem'>ML Forecast (2028)</div>
        <div style='color:#8E44AD; font-size:1.6rem; font-weight:bold'>{forecast_2028:.1f}%</div>
    </div>""", unsafe_allow_html=True)
    k4.markdown(f"""
    <div style='background:#1C2833; padding:1.2rem; border-radius:10px;
                border-top:3px solid #2980B9; text-align:center;'>
        <div style='color:#AAB7B8; font-size:.8rem'>Global Average (ILO)</div>
        <div style='color:#2980B9; font-size:1.6rem; font-weight:bold'>13.6%</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Historical + Forecast chart ──────────────────────────────────
    st.markdown("### 📊 Historical Trend + 5-Year ML Forecast")

    fig_hist = go.Figure()

    # Historical
    fig_hist.add_trace(go.Scatter(
        x=yu_df["Year"], y=yu_df["Youth_Unemployment_Pct"],
        mode="lines+markers", name="Actual",
        line=dict(color="#E74C3C", width=3), marker=dict(size=8),
        hovertemplate="<b>Actual</b><br>Year: %{x}<br>%{y:.1f}%<extra></extra>"
    ))
    # ML fitted
    fig_hist.add_trace(go.Scatter(
        x=yu_df["Year"], y=result["historical_preds"],
        mode="lines", name="ML Fitted",
        line=dict(color="#F39C12", width=2, dash="dot"),
        hovertemplate="<b>ML Fitted</b><br>Year: %{x}<br>%{y:.1f}%<extra></extra>"
    ))
    # Forecast
    connector_x = [yu_df["Year"].iloc[-1]] + result["forecast_years"]
    connector_y = [float(yu_df["Youth_Unemployment_Pct"].iloc[-1])] + list(result["forecast_values"])
    fig_hist.add_trace(go.Scatter(
        x=connector_x, y=connector_y,
        mode="lines+markers", name="Forecast (2024–2028)",
        line=dict(color="#8E44AD", width=2.5, dash="dot"),
        marker=dict(size=9, symbol="diamond", color="#8E44AD"),
        hovertemplate="<b>Forecast</b><br>Year: %{x}<br>%{y:.1f}%<extra></extra>"
    ))
    # Global benchmark
    fig_hist.add_hline(
        y=13.6, line_dash="dash", line_color="#27AE60",
        annotation_text="🌍 Global avg: 13.6%",
        annotation_font_color="#27AE60"
    )

    fig_hist.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white"), height=440,
        legend=dict(bgcolor="#1C2833", font=dict(color="white")),
        hovermode="x unified",
        xaxis=dict(gridcolor="#2C3E50", title="Year"),
        yaxis=dict(gridcolor="#2C3E50", title="Youth Unemployment (%)"),
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # ── Feature importance ───────────────────────────────────────────
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown("### 🔑 Key Drivers of Youth Unemployment")
        fi    = result["feature_importance"]
        fi_df = pd.DataFrame(list(fi.items()), columns=["Factor", "Importance (%)"]) \
                  .sort_values("Importance (%)", ascending=True)
        fig_fi = go.Figure(go.Bar(
            x=fi_df["Importance (%)"], y=fi_df["Factor"],
            orientation="h",
            marker_color=["#E74C3C" if v > 25 else "#F39C12" if v > 15 else "#3498DB"
                           for v in fi_df["Importance (%)"]],
            text=[f"{v:.1f}%" for v in fi_df["Importance (%)"]],
            textposition="outside"
        ))
        fig_fi.update_layout(
            plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
            font=dict(color="white", size=11),
            height=300, margin=dict(l=10, r=70, t=10, b=20),
            xaxis=dict(gridcolor="#2C3E50"),
        )
        st.plotly_chart(fig_fi, use_container_width=True)

    with col_b:
        st.markdown("### 📉 Unemployment vs GDP Growth Correlation")
        fig_gdp = px.scatter(
            yu_df, x="GDP_Growth", y="Youth_Unemployment_Pct",
            color="Year", size_max=12,
            color_continuous_scale="Plasma",
            trendline="ols",
            labels={"GDP_Growth": "GDP Growth (%)",
                    "Youth_Unemployment_Pct": "Youth Unemployment (%)"},
            hover_data={"Year": True}
        )
        fig_gdp.update_layout(
            plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
            font=dict(color="white"), height=300,
            xaxis=dict(gridcolor="#2C3E50"),
            yaxis=dict(gridcolor="#2C3E50"),
            margin=dict(l=10, r=10, t=10, b=20),
            coloraxis_colorbar=dict(title="Year", tickfont=dict(color="white"),
                                    title_font=dict(color="white"))
        )
        st.plotly_chart(fig_gdp, use_container_width=True)

    # ── 🔮 SCENARIO SIMULATOR ────────────────────────────────────────
    st.markdown("---")
    st.markdown("""
    <div style='background:#1C2833; padding:1.5rem; border-radius:12px; margin-bottom:1rem;'>
        <h2 style='color:#8E44AD; margin:0'>🔮 Scenario Simulator</h2>
        <p style='color:#AAB7B8; margin:.5rem 0 0'>
            Adjust macro-economic levers and predict youth unemployment in real time.
        </p>
    </div>
    """, unsafe_allow_html=True)

    sim_col1, sim_col2 = st.columns([1, 1])

    with sim_col1:
        gdp_growth   = st.slider("📈 GDP Growth (%)",        -3.0, 12.0, 5.0, 0.5, key="sim_gdp")
        fdi          = st.slider("🌍 FDI Inflows (USD B)",    0.1, 3.0,  0.7, 0.1, key="sim_fdi")
        univ_enroll  = st.slider("🎓 University Enrollment (K)", 100, 600, 450, 10, key="sim_uni")

    with sim_col2:
        internet_pct = st.slider("🌐 Internet Users (%)",    30.0, 100.0, 91.0, 1.0, key="sim_int")
        inflation    = st.slider("💸 Inflation Rate (%)",      2.0,  20.0,  7.8, 0.5, key="sim_inf")

    scenario_pred = simulate_scenario(
        result, gdp_growth, fdi, univ_enroll, internet_pct, inflation
    )

    baseline = float(yu_df["Youth_Unemployment_Pct"].iloc[-1])
    diff     = scenario_pred - baseline
    color    = "#27AE60" if diff < 0 else "#E74C3C"
    arrow    = "🔻" if diff < 0 else "🔺"

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#6C3483,#4A235A); padding:2rem;
                border-radius:16px; text-align:center; margin-top:1rem;'>
        <div style='color:#D7BDE2; font-size:1rem'>Predicted Youth Unemployment</div>
        <div style='color:white; font-size:3.5rem; font-weight:bold; margin:.3rem 0'>{scenario_pred}%</div>
        <div style='color:{color}; font-size:1.2rem'>
            {arrow} {abs(diff):.1f}% {'improvement' if diff < 0 else 'worsening'} vs current baseline ({baseline:.1f}%)
        </div>
        <div style='color:#AAB7B8; font-size:.85rem; margin-top:.8rem'>
            {'✅ This scenario would put Kenya closer to the global average (13.6%)' if scenario_pred < baseline
             else '⚠️ This scenario worsens youth unemployment — policy attention needed'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Gauge chart
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=scenario_pred,
        delta={"reference": baseline, "valueformat": ".1f",
               "increasing": {"color": "#E74C3C"},
               "decreasing": {"color": "#27AE60"}},
        number={"suffix": "%", "font": {"color": "white", "size": 36}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "white",
                     "tickfont": {"color": "white"}},
            "bar": {"color": color},
            "bgcolor": "#1C2833",
            "bordercolor": "#2C3E50",
            "steps": [
                {"range": [0, 25],  "color": "#1E8449"},
                {"range": [25, 50], "color": "#F39C12"},
                {"range": [50, 75], "color": "#E67E22"},
                {"range": [75, 100],"color": "#E74C3C"},
            ],
            "threshold": {
                "line": {"color": "white", "width": 4},
                "thickness": 0.75, "value": 13.6
            }
        },
        title={"text": "Youth Unemployment Predictor", "font": {"color": "white", "size": 14}}
    ))
    fig_gauge.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white"), height=320,
        margin=dict(l=30, r=30, t=40, b=20)
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    # ── Sector employment chart ──────────────────────────────────────
    st.markdown("### 🏭 Kenya Employment by Sector (2010–2023)")
    sector_cols = ["Agriculture", "Manufacturing", "ICT_Services",
                   "Finance_Banking", "Trade_Retail", "Tourism_Hospitality",
                   "Construction", "Education_Health", "Other"]
    palette     = px.colors.qualitative.Plotly

    fig_sec = go.Figure()
    for i, sec in enumerate(sector_cols):
        fig_sec.add_trace(go.Scatter(
            x=se_df["Year"], y=se_df[sec],
            mode="lines+markers", name=sec,
            stackgroup="one",
            line=dict(color=palette[i % len(palette)]),
            hovertemplate=f"<b>{sec}</b><br>Year: %{{x}}<br>%{{y:.1f}}%<extra></extra>"
        ))

    fig_sec.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white"), height=440,
        legend=dict(bgcolor="#1C2833", font=dict(color="white"),
                    orientation="h", yanchor="bottom", y=1.02, xanchor="left"),
        hovermode="x unified",
        xaxis=dict(gridcolor="#2C3E50", title="Year"),
        yaxis=dict(gridcolor="#2C3E50", title="Employment Share (%)", range=[0, 100]),
    )
    st.plotly_chart(fig_sec, use_container_width=True)

    # ── Internet vs Unemployment ─────────────────────────────────────
    st.markdown("### 🌐 Internet Access vs Youth Unemployment")
    fig_int = make_subplots(specs=[[{"secondary_y": True}]])
    fig_int.add_trace(go.Scatter(
        x=yu_df["Year"], y=yu_df["Internet_Users_Pct"],
        mode="lines+markers", name="Internet Users (%)",
        line=dict(color="#3498DB", width=2.5), marker=dict(size=7)
    ), secondary_y=False)
    fig_int.add_trace(go.Scatter(
        x=yu_df["Year"], y=yu_df["Youth_Unemployment_Pct"],
        mode="lines+markers", name="Youth Unemployment (%)",
        line=dict(color="#E74C3C", width=2.5), marker=dict(size=7)
    ), secondary_y=True)
    fig_int.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white"), height=360,
        legend=dict(bgcolor="#1C2833", font=dict(color="white")),
        hovermode="x unified",
        xaxis=dict(gridcolor="#2C3E50", title="Year"),
    )
    fig_int.update_yaxes(title_text="Internet Users (%)", gridcolor="#2C3E50", secondary_y=False)
    fig_int.update_yaxes(title_text="Youth Unemployment (%)", gridcolor="#2C3E50", secondary_y=True)
    st.plotly_chart(fig_int, use_container_width=True)

    with st.expander("📋 Youth Unemployment Raw Data"):
        st.dataframe(yu_df.set_index("Year").style.format("{:.2f}"), use_container_width=True)
        csv = yu_df.to_csv(index=False).encode()
        st.download_button("⬇️ Download CSV", csv, "kenya_youth_unemployment.csv", "text/csv")
