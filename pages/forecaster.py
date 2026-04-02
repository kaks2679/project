"""
Page 5: Economic Forecaster
Advanced ARIMA + Holt-Winters time-series forecasting dashboard.
Author: Stephen Muema
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from utils.ml_models import forecast_indicator, arima_forecast
import warnings
warnings.filterwarnings("ignore")


FORECASTABLE = [
    "GDP Growth (%)",
    "Inflation Rate (%)",
    "Unemployment Rate (%)",
    "Poverty Headcount Ratio (%)",
    "Access to Electricity (%)",
    "Mobile Subscriptions (per 100)",
    "GDP per Capita (constant USD)",
    "Remittances (% of GDP)",
    "Government Debt (% of GDP)",
]


def render(data: dict):
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1A1A2E 0%, #16213E 50%, #0F3460 100%);
                padding: .8rem 1.5rem; border-radius: 12px; margin-bottom: 1rem;'>
        <h2 style='color:white; margin:0; font-size:1.4rem;'>🔮 Economic Forecaster</h2>
        <p style='color:#AED6F1; margin:.2rem 0 0; font-size:.85rem;'>
            Holt-Winters Exponential Smoothing · ARIMA(2,1,2) · 5–10 Year Projections
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ Page Guide & Stakeholder Notes", expanded=False):
        st.markdown("""
        **What this page shows:**
        Two complementary time-series forecasting models applied to Kenya's macro indicators:
        - **Holt-Winters** (exponential smoothing) — best for smooth trend + seasonal patterns
        - **ARIMA(2,1,2)** — best for capturing autocorrelation and irregular fluctuations

        **How to read the results:**
        - **Solid line** = historical data (World Bank 2000–2023)
        - **Dashed orange line** = Holt-Winters point forecast
        - **Shaded confidence band** (ARIMA) = 95% interval — reality should fall within this range
        - **Error metrics**: RMSE = root mean squared error (lower = better), MAPE = % error

        **For stakeholders:**
        - 🏛️ *Policy makers*: GDP growth forecast ~5% through 2028 if current trends hold.
          Inflation forecast shows gradual convergence to CBK's 5% target by 2026.
        - 📈 *Investors*: GDP per capita forecast shows continued growth — Kenya remains one of
          East Africa's most investable frontier markets.
        - ⚠️ *Important caveat*: Forecasts assume no major shocks (pandemics, droughts, elections).
          Use the Anomaly Detection page to assess historical shock frequency.
        - 💡 *Key insight*: The widening ARIMA confidence bands beyond 2026 reflect genuine
          uncertainty — do not treat point forecasts as certainties.
        """)

    macro_df = data["macro"].copy()

    # ── Sidebar controls ─────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🔮 Forecast Settings")
        indicator = st.selectbox(
            "Select Indicator to Forecast",
            [c for c in FORECASTABLE if c in macro_df.columns],
            key="fc_indicator"
        )
        horizon = st.slider("Forecast Horizon (Years)", 3, 10, 5, key="fc_horizon")
        model_choice = st.radio(
            "Forecast Model",
            ["Holt-Winters", "ARIMA(2,1,2)", "Both"],
            key="fc_model",
            index=2
        )

    if indicator not in macro_df.columns:
        st.warning(f"Indicator '{indicator}' not available in current dataset.")
        return

    series = macro_df.set_index("Year")[indicator].dropna()
    years  = list(series.index)

    # ── KPI cards ────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    current_val = float(series.iloc[-1])
    min_val     = float(series.min())
    max_val     = float(series.max())
    trend_val   = float(series.diff().mean())

    cards = [
        ("📌 Latest Value",  f"{current_val:.2f}",                                         "#3498DB"),
        ("📉 Historical Min",f"{min_val:.2f}",                                              "#E74C3C"),
        ("📈 Historical Max",f"{max_val:.2f}",                                              "#27AE60"),
        ("➡️ Avg Trend/yr",  f"{'+' if trend_val >= 0 else ''}{trend_val:.2f}",            "#F39C12"),
    ]
    for col, (lbl, val, clr) in zip([c1, c2, c3, c4], cards):
        col.markdown(f"""
        <div style='background:#1C2833; padding:1rem; border-radius:10px;
                    border-top:3px solid {clr}; text-align:center;'>
            <div style='color:#AAB7B8; font-size:.8rem'>{lbl}</div>
            <div style='color:{clr}; font-size:1.4rem; font-weight:bold'>{val}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Main forecast chart ──────────────────────────────────────────
    fig = go.Figure()

    # Historical data
    fig.add_trace(go.Scatter(
        x=years, y=series.values,
        mode="lines+markers",
        name="Historical",
        line=dict(color="#3498DB", width=3),
        marker=dict(size=6),
        hovertemplate="<b>%{x}</b>: %{y:.2f}<extra>Historical</extra>"
    ))

    # Holt-Winters forecast
    if model_choice in ("Holt-Winters", "Both"):
        fc_df = forecast_indicator(series, years, forecast_years=horizon)
        if not fc_df.empty:
            fc_part = fc_df[fc_df["Is_Forecast"]]
            # Connector from last historical point
            connect_x = [int(years[-1])] + list(fc_part["Year"])
            connect_y = [float(series.iloc[-1])] + list(fc_part["Value"])
            fig.add_trace(go.Scatter(
                x=connect_x, y=connect_y,
                mode="lines+markers",
                name="Holt-Winters Forecast",
                line=dict(color="#F39C12", width=2.5, dash="dot"),
                marker=dict(size=7, symbol="diamond"),
                hovertemplate="<b>%{x}</b>: %{y:.2f}<extra>HW Forecast</extra>"
            ))

    # ARIMA forecast
    if model_choice in ("ARIMA(2,1,2)", "Both"):
        arima_fc, conf_int = arima_forecast(series, steps=horizon)
        if arima_fc is not None:
            fc_years = list(range(int(years[-1]) + 1, int(years[-1]) + 1 + horizon))
            connect_x = [int(years[-1])] + fc_years
            connect_y = [float(series.iloc[-1])] + list(arima_fc)
            fig.add_trace(go.Scatter(
                x=connect_x, y=connect_y,
                mode="lines+markers",
                name="ARIMA Forecast",
                line=dict(color="#E74C3C", width=2.5, dash="dash"),
                marker=dict(size=7, symbol="circle"),
                hovertemplate="<b>%{x}</b>: %{y:.2f}<extra>ARIMA Forecast</extra>"
            ))
            # Confidence interval band
            if conf_int is not None:
                try:
                    lo = list(conf_int.iloc[:, 0])
                    hi = list(conf_int.iloc[:, 1])
                    fig.add_trace(go.Scatter(
                        x=fc_years + fc_years[::-1],
                        y=hi + lo[::-1],
                        fill="toself",
                        fillcolor="rgba(231,76,60,0.12)",
                        line=dict(color="rgba(0,0,0,0)"),
                        name="ARIMA 80% CI",
                        showlegend=True,
                        hoverinfo="skip"
                    ))
                except Exception:
                    pass

    # Shade forecast region
    if years:
        fig.add_vrect(
            x0=int(years[-1]), x1=int(years[-1]) + horizon,
            fillcolor="rgba(255,255,255,0.03)",
            line_width=0,
            annotation_text="Forecast Zone",
            annotation_position="top left",
            annotation_font_color="#566573"
        )

    fig.update_layout(
        title=dict(text=f"Forecast: {indicator}", font=dict(size=18, color="white")),
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font=dict(color="white"),
        legend=dict(bgcolor="#1C2833", font=dict(color="white")),
        hovermode="x unified",
        xaxis=dict(gridcolor="#2C3E50", title="Year"),
        yaxis=dict(gridcolor="#2C3E50", title=indicator),
        height=500,
        margin=dict(l=40, r=20, t=60, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Multi-indicator forecast comparison ──────────────────────────
    st.markdown("### 📊 Multi-Indicator Forecast Table")
    avail = [c for c in FORECASTABLE if c in macro_df.columns]

    forecast_rows = []
    for ind in avail[:6]:
        s = macro_df.set_index("Year")[ind].dropna()
        y = list(s.index)
        fc = forecast_indicator(s, y, forecast_years=5)
        if not fc.empty:
            fc_vals = fc[fc["Is_Forecast"]]["Value"].values
            current = float(s.iloc[-1])
            proj_5  = float(fc_vals[-1]) if len(fc_vals) else np.nan
            change  = proj_5 - current
            forecast_rows.append({
                "Indicator": ind,
                "Current (2023)": round(current, 2),
                "Forecast (2028)": round(proj_5, 2),
                "Change": round(change, 2),
                "Direction": "📈 Up" if change > 0 else "📉 Down"
            })

    if forecast_rows:
        fc_table_df = pd.DataFrame(forecast_rows).set_index("Indicator")
        st.dataframe(fc_table_df, use_container_width=True)

    # ── Historical decomposition: rolling mean + std ─────────────────
    st.markdown(f"### 📉 Historical Trend Analysis: {indicator}")
    roll_df = pd.DataFrame({
        "Year": years,
        "Value": series.values,
        "Rolling_Mean": pd.Series(series.values).rolling(window=3, center=True).mean().values,
        "Rolling_Std":  pd.Series(series.values).rolling(window=3, center=True).std().values,
    })

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=roll_df["Year"], y=roll_df["Value"],
        mode="lines+markers",
        name="Actual",
        line=dict(color="#3498DB", width=2),
        marker=dict(size=5)
    ))
    fig2.add_trace(go.Scatter(
        x=roll_df["Year"], y=roll_df["Rolling_Mean"],
        mode="lines",
        name="3-Year Rolling Mean",
        line=dict(color="#F39C12", width=2.5, dash="dot")
    ))
    # std band
    fig2.add_trace(go.Scatter(
        x=list(roll_df["Year"]) + list(roll_df["Year"][::-1]),
        y=list(roll_df["Rolling_Mean"].fillna(0) + roll_df["Rolling_Std"].fillna(0)) +
          list((roll_df["Rolling_Mean"].fillna(0) - roll_df["Rolling_Std"].fillna(0))[::-1]),
        fill="toself",
        fillcolor="rgba(243,156,18,0.1)",
        line=dict(color="rgba(0,0,0,0)"),
        name="±1 Std Dev Band",
        showlegend=True,
        hoverinfo="skip"
    ))
    fig2.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white"), height=360,
        legend=dict(bgcolor="#1C2833", font=dict(color="white")),
        hovermode="x unified",
        xaxis=dict(gridcolor="#2C3E50", title="Year"),
        yaxis=dict(gridcolor="#2C3E50", title=indicator),
        margin=dict(l=40, r=20, t=20, b=40)
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── Raw data download ─────────────────────────────────────────────
    with st.expander("📋 Raw & Forecast Data"):
        display = pd.DataFrame({"Year": years, indicator: series.values})
        st.dataframe(display.set_index("Year"), use_container_width=True)
        csv = display.to_csv(index=False).encode()
        st.download_button("⬇️ Download CSV", csv, f"kenya_{indicator.replace(' ','_')}_forecast.csv", "text/csv")
