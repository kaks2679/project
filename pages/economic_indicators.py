"""
Page 1: Economic Indicators Dashboard
Interactive macro-economic time-series with forecasting.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from utils.ml_models import forecast_indicator, arima_forecast


COLORS = {
    "primary":   "#1B4F72",
    "secondary": "#2ECC71",
    "accent":    "#E74C3C",
    "warning":   "#F39C12",
    "bg":        "#0E1117",
    "card":      "#1C2833",
    "forecast":  "#F39C12",
    "historical":"#3498DB",
}

INDICATOR_META = {
    "GDP Growth (%)":            {"icon": "📈", "good": "high", "unit": "%",     "desc": "Annual GDP growth rate"},
    "Inflation Rate (%)":        {"icon": "💸", "good": "low",  "unit": "%",     "desc": "Consumer price inflation"},
    "Unemployment Rate (%)":     {"icon": "👷", "good": "low",  "unit": "%",     "desc": "Total unemployment rate"},
    "Gini Index (Inequality)":   {"icon": "⚖️", "good": "low",  "unit": "",      "desc": "0 = perfect equality, 100 = max inequality"},
    "Poverty Headcount Ratio (%)":{"icon": "🏚️","good": "low",  "unit": "%",     "desc": "Population below national poverty line"},
    "Youth Unemployment (%)":    {"icon": "🎓", "good": "low",  "unit": "%",     "desc": "Unemployment among 15–24 year olds"},
    "Remittances (% of GDP)":    {"icon": "💰", "good": "high", "unit": "% GDP", "desc": "Money sent by Kenyans in diaspora"},
    "Mobile Subscriptions (per 100)":{"icon": "📱","good":"high","unit": "/100",  "desc": "Mobile connections per 100 people"},
    "Access to Electricity (%)": {"icon": "⚡", "good": "high", "unit": "%",     "desc": "Population with electricity access"},
    "GDP per Capita (constant USD)":{"icon":"💵","good": "high", "unit": "USD",   "desc": "GDP per person (constant 2015 USD)"},
}


def render(data: dict):
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1B4F72 0%, #2980B9 100%);
                padding: .8rem 1.5rem; border-radius: 12px; margin-bottom: 1rem;'>
        <h2 style='color:white; margin:0; font-size:1.4rem;'>📊 Kenya Economic Indicators</h2>
        <p style='color:#AED6F1; margin:.2rem 0 0; font-size:.85rem;'>
            Real macro-economic data · World Bank API · 2000–2028 Forecast
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ Page Guide & Stakeholder Notes", expanded=False):
        st.markdown("""
        **What this page shows:**
        20+ macro-economic indicators for Kenya (2000–2023) sourced from the World Bank API,
        with optional 5-year Holt-Winters forecasts.

        **How to read the charts:**
        - **KPI cards** — latest value + year-on-year change (🔺 up, 🔻 down, ✅ good, ❌ bad)
        - **Trend chart** — select multiple indicators to compare on the same axis
        - **Correlation matrix** — Pearson r: values near +1 / -1 indicate strong relationships
        - **GDP vs Poverty scatter** — downward OLS trendline confirms economic growth reduces poverty

        **For stakeholders:**
        - 📈 *Investors*: Watch GDP growth (target >5%), inflation (<7%), and government debt trends.
        - 🏛️ *Policy makers*: Poverty Headcount Ratio and Gini Index measure distributional impact of policy.
        - 🎓 *Researchers*: Use the data table + CSV download for econometric analysis.
        - 💡 *Key insight*: Kenya's GDP per capita grew from ~$400 (2000) to ~$1,800 (2023) yet
          poverty headcount remains ~33% — highlighting growth-inequality decoupling.
        """)

    macro_df = data["macro"]
    if macro_df.empty:
        st.error("Could not load macro data. Please refresh.")
        return

    # ── Sidebar controls ────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### ⚙️ Dashboard Controls")
        year_range = st.slider(
            "Year Range",
            int(macro_df["Year"].min()),
            int(macro_df["Year"].max()),
            (2005, int(macro_df["Year"].max())),
            key="econ_years"
        )
        show_forecast = st.toggle("Show 5-Year Forecast", value=True, key="econ_fc")
        selected_indicators = st.multiselect(
            "Compare Indicators",
            [c for c in macro_df.columns if c != "Year"],
            default=["GDP Growth (%)", "Inflation Rate (%)", "Unemployment Rate (%)"],
            key="econ_sel"
        )

    filtered = macro_df[
        (macro_df["Year"] >= year_range[0]) &
        (macro_df["Year"] <= year_range[1])
    ].copy()

    # ── KPI cards ───────────────────────────────────────────────────
    kpi_cols = st.columns(4)
    kpi_indicators = [
        "GDP Growth (%)", "Inflation Rate (%)",
        "Unemployment Rate (%)", "Poverty Headcount Ratio (%)"
    ]
    for i, col in enumerate(kpi_cols):
        ind = kpi_indicators[i]
        if ind in filtered.columns:
            vals  = filtered[ind].dropna()
            last  = vals.iloc[-1] if len(vals) else 0
            prev  = vals.iloc[-2] if len(vals) > 1 else last
            delta = round(last - prev, 2)
            meta  = INDICATOR_META.get(ind, {"icon": "📊", "good": "high", "unit": "%"})
            good  = meta["good"]
            arrow = "🔺" if delta > 0 else "🔻" if delta < 0 else "➡️"
            color = "#2ECC71" if (
                (good == "high" and delta >= 0) or (good == "low" and delta <= 0)
            ) else "#E74C3C"
            col.markdown(f"""
            <div style='background:{COLORS["card"]}; padding:1.2rem; border-radius:12px;
                        border-left:4px solid {color}; text-align:center;'>
                <div style='font-size:1.8rem'>{meta['icon']}</div>
                <div style='color:#AAB7B8; font-size:.75rem; margin:.3rem 0'>{ind}</div>
                <div style='color:white; font-size:1.6rem; font-weight:bold'>{last:.1f}{meta['unit']}</div>
                <div style='color:{color}; font-size:.85rem'>{arrow} {abs(delta):.2f} vs prev year</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Main trend chart ─────────────────────────────────────────────
    if selected_indicators:
        fig = go.Figure()
        palette = px.colors.qualitative.Plotly

        for idx, ind in enumerate(selected_indicators):
            if ind not in filtered.columns:
                continue
            series = filtered.set_index("Year")[ind].dropna()
            years  = list(series.index)
            color  = palette[idx % len(palette)]

            # Historical line
            fig.add_trace(go.Scatter(
                x=years, y=series.values,
                mode="lines+markers",
                name=ind,
                line=dict(color=color, width=2.5),
                marker=dict(size=5),
                hovertemplate=f"<b>{ind}</b><br>Year: %{{x}}<br>Value: %{{y:.2f}}<extra></extra>"
            ))

            # Forecast overlay
            if show_forecast:
                all_years = list(macro_df["Year"].dropna().astype(int))
                fc_df = forecast_indicator(
                    macro_df.set_index("Year")[ind],
                    all_years, forecast_years=5
                )
                if not fc_df.empty:
                    fc_part = fc_df[fc_df["Is_Forecast"]]
                    hist_end = series.dropna()
                    if len(hist_end) > 0:
                        connector_x = [int(hist_end.index[-1])] + list(fc_part["Year"])
                        connector_y = [float(hist_end.iloc[-1])] + list(fc_part["Value"])
                    else:
                        connector_x = list(fc_part["Year"])
                        connector_y = list(fc_part["Value"])
                    fig.add_trace(go.Scatter(
                        x=connector_x, y=connector_y,
                        mode="lines+markers",
                        name=f"{ind} (Forecast)",
                        line=dict(color=color, width=2, dash="dot"),
                        marker=dict(size=6, symbol="diamond"),
                        opacity=0.75,
                        hovertemplate=f"<b>{ind} – Forecast</b><br>Year: %{{x}}<br>%{{y:.2f}}<extra></extra>"
                    ))

        fig.update_layout(
            title=dict(text="Kenya Economic Indicators Trend", font=dict(size=20, color="white")),
            plot_bgcolor="#0E1117",
            paper_bgcolor="#0E1117",
            font=dict(color="white"),
            legend=dict(bgcolor="#1C2833", bordercolor="#2C3E50", borderwidth=1,
                        font=dict(color="white")),
            hovermode="x unified",
            xaxis=dict(gridcolor="#2C3E50", title="Year"),
            yaxis=dict(gridcolor="#2C3E50", title="Value"),
            height=480,
            margin=dict(l=40, r=20, t=60, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Correlation heatmap ──────────────────────────────────────────
    st.markdown("### 🔗 Indicator Correlation Matrix")
    corr_cols = [c for c in macro_df.columns if c != "Year" and macro_df[c].notna().sum() > 5]
    if len(corr_cols) >= 3:
        corr_df   = macro_df[corr_cols].corr().round(2)
        fig_corr  = px.imshow(
            corr_df,
            color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1,
            title="Pearson Correlation Between Economic Indicators",
            text_auto=True,
            aspect="auto"
        )
        fig_corr.update_layout(
            plot_bgcolor="#0E1117",
            paper_bgcolor="#0E1117",
            font=dict(color="white", size=10),
            height=480,
            title_font=dict(color="white", size=16),
            coloraxis_colorbar=dict(title="r", tickfont=dict(color="white"), title_font=dict(color="white"))
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    # ── GDP vs Poverty scatter ───────────────────────────────────────
    if "GDP per Capita (constant USD)" in macro_df.columns and "Poverty Headcount Ratio (%)" in macro_df.columns:
        st.markdown("### 💵 GDP per Capita vs Poverty Rate")
        scat_df = macro_df[["Year", "GDP per Capita (constant USD)", "Poverty Headcount Ratio (%)"]].dropna()
        fig_s = px.scatter(
            scat_df,
            x="GDP per Capita (constant USD)",
            y="Poverty Headcount Ratio (%)",
            color="Year",
            size_max=12,
            color_continuous_scale="Viridis",
            trendline="ols",
            title="As GDP per Capita rises → Poverty falls",
            labels={"GDP per Capita (constant USD)": "GDP per Capita (USD)",
                    "Poverty Headcount Ratio (%)": "Poverty Rate (%)"}
        )
        fig_s.update_layout(
            plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
            font=dict(color="white"), height=400,
            title_font=dict(color="white", size=16),
            xaxis=dict(gridcolor="#2C3E50"),
            yaxis=dict(gridcolor="#2C3E50"),
        )
        st.plotly_chart(fig_s, use_container_width=True)

    # ── Data table ───────────────────────────────────────────────────
    with st.expander("📋 View Raw Data Table"):
        show_cols = ["Year"] + [c for c in filtered.columns if c != "Year"]
        st.dataframe(
            filtered[show_cols].set_index("Year").style
              .format("{:.2f}", na_rep="N/A")
              .background_gradient(cmap="Blues", axis=0),
            use_container_width=True
        )
        csv = filtered.to_csv(index=False).encode()
        st.download_button("⬇️ Download CSV", csv, "kenya_macro_data.csv", "text/csv")
