"""
Page 6: County Comparison Tool
Side-by-side socioeconomic comparison of any two Kenya counties.
Author: Stephen Muema
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


METRICS = {
    "Poverty_Rate":       {"label": "Poverty Rate (%)",       "icon": "🏚️",  "good": "low"},
    "Unemployment_Rate":  {"label": "Unemployment Rate (%)",  "icon": "👷",  "good": "low"},
    "Mobile_Penetration": {"label": "Mobile Penetration (%)", "icon": "📱",  "good": "high"},
    "Electricity_Access": {"label": "Electricity Access (%)", "icon": "⚡",  "good": "high"},
    "HDI_Score":          {"label": "HDI Score",              "icon": "📚",  "good": "high"},
    "Population_2019":    {"label": "Population (2019)",      "icon": "👥",  "good": "neutral"},
}


def render(data: dict):
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1B2631 0%, #21618C 100%);
                padding: 2rem; border-radius: 16px; margin-bottom: 2rem;'>
        <h1 style='color:white; margin:0; font-size:2rem;'>⚖️ County Comparison Tool</h1>
        <p style='color:#AED6F1; margin-top:.5rem; font-size:1rem;'>
            Compare any two Kenya counties side-by-side across all socioeconomic dimensions
        </p>
    </div>
    """, unsafe_allow_html=True)

    county_df = data["county"].copy()
    counties  = sorted(county_df["County"].unique().tolist())

    # ── County selector ───────────────────────────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        county_a = st.selectbox("🔵 Select County A", counties,
                                index=counties.index("Nairobi") if "Nairobi" in counties else 0,
                                key="cmp_a")
    with col_b:
        county_b = st.selectbox("🔴 Select County B", counties,
                                index=counties.index("Turkana") if "Turkana" in counties else 1,
                                key="cmp_b")

    if county_a == county_b:
        st.warning("Please select two different counties to compare.")
        return

    row_a = county_df[county_df["County"] == county_a].iloc[0]
    row_b = county_df[county_df["County"] == county_b].iloc[0]

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Side-by-side KPI cards ────────────────────────────────────────
    st.markdown("### 📊 Head-to-Head Comparison")
    header_a, header_b = st.columns(2)
    with header_a:
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#1B4F72,#2980B9);
                    padding:1rem; border-radius:10px; text-align:center;'>
            <h2 style='color:white; margin:0'>{county_a}</h2>
            <p style='color:#AED6F1; margin:.3rem 0 0; font-size:.9rem'>{row_a['Region']} Region · Cluster: {row_a.get('Cluster_Label','N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
    with header_b:
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#641E16,#E74C3C);
                    padding:1rem; border-radius:10px; text-align:center;'>
            <h2 style='color:white; margin:0'>{county_b}</h2>
            <p style='color:#FADBD8; margin:.3rem 0 0; font-size:.9rem'>{row_b['Region']} Region · Cluster: {row_b.get('Cluster_Label','N/A')}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    for metric, meta in METRICS.items():
        if metric not in county_df.columns:
            continue
        val_a = row_a[metric]
        val_b = row_b[metric]

        if metric == "Population_2019":
            fmt_a = f"{int(val_a):,}"
            fmt_b = f"{int(val_b):,}"
        elif metric == "HDI_Score":
            fmt_a = f"{val_a:.3f}"
            fmt_b = f"{val_b:.3f}"
        else:
            fmt_a = f"{val_a:.1f}%"
            fmt_b = f"{val_b:.1f}%"

        # Determine winner
        if meta["good"] == "high":
            winner = "A" if val_a > val_b else "B"
        elif meta["good"] == "low":
            winner = "A" if val_a < val_b else "B"
        else:
            winner = "tie"

        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            bg_a = "#1A5276" if winner == "A" else "#1C2833"
            border_a = "#27AE60" if winner == "A" else "#2C3E50"
            st.markdown(f"""
            <div style='background:{bg_a}; padding:.8rem 1rem; border-radius:8px;
                        border:1px solid {border_a}; text-align:center;'>
                <span style='color:#AAB7B8; font-size:.8rem'>{meta["icon"]} {meta["label"]}</span><br>
                <span style='color:{"#27AE60" if winner=="A" else "white"}; font-size:1.4rem; font-weight:bold'>{fmt_a}</span>
                {"<span style='color:#27AE60; font-size:.7rem;'> ✓ Better</span>" if winner=="A" else ""}
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style='text-align:center; padding:.8rem 0;'>
                <span style='color:#566573; font-size:1.5rem'>⚡</span><br>
                <span style='color:#AAB7B8; font-size:.75rem'>vs</span>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            bg_b = "#7B241C" if winner == "B" else "#1C2833"
            border_b = "#27AE60" if winner == "B" else "#2C3E50"
            st.markdown(f"""
            <div style='background:{bg_b}; padding:.8rem 1rem; border-radius:8px;
                        border:1px solid {border_b}; text-align:center;'>
                <span style='color:#AAB7B8; font-size:.8rem'>{meta["icon"]} {meta["label"]}</span><br>
                <span style='color:{"#27AE60" if winner=="B" else "white"}; font-size:1.4rem; font-weight:bold'>{fmt_b}</span>
                {"<span style='color:#27AE60; font-size:.7rem;'> ✓ Better</span>" if winner=="B" else ""}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Radar chart ───────────────────────────────────────────────────
    st.markdown("### 🕸️ Radar Chart: Multi-Dimensional Comparison")
    radar_metrics = ["Poverty_Rate", "Unemployment_Rate", "Mobile_Penetration",
                     "Electricity_Access", "HDI_Score"]
    radar_labels  = [METRICS[m]["label"].replace(" (%)", "").replace(" (2019)", "") for m in radar_metrics]

    def normalise(series_vals, metric_name):
        """Normalise 0–100 for radar; invert low-is-good metrics."""
        col_data = county_df[metric_name]
        mn, mx = col_data.min(), col_data.max()
        norm = [(v - mn) / (mx - mn + 1e-9) * 100 for v in series_vals]
        if METRICS[metric_name]["good"] == "low":
            norm = [100 - v for v in norm]
        return norm

    vals_a = normalise([row_a[m] for m in radar_metrics], "Poverty_Rate")
    vals_b = normalise([row_b[m] for m in radar_metrics], "Poverty_Rate")

    # Re-normalise each metric individually
    vals_a = []
    vals_b = []
    for m in radar_metrics:
        col_data = county_df[m]
        mn, mx = float(col_data.min()), float(col_data.max())
        span = mx - mn + 1e-9
        na = (float(row_a[m]) - mn) / span * 100
        nb = (float(row_b[m]) - mn) / span * 100
        if METRICS[m]["good"] == "low":
            na, nb = 100 - na, 100 - nb
        vals_a.append(round(na, 1))
        vals_b.append(round(nb, 1))

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=vals_a + [vals_a[0]],
        theta=radar_labels + [radar_labels[0]],
        fill="toself",
        name=county_a,
        line=dict(color="#2980B9", width=2),
        fillcolor="rgba(41,128,185,0.2)"
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=vals_b + [vals_b[0]],
        theta=radar_labels + [radar_labels[0]],
        fill="toself",
        name=county_b,
        line=dict(color="#E74C3C", width=2),
        fillcolor="rgba(231,76,60,0.2)"
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="#1C2833",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#2C3E50",
                            tickfont=dict(color="#AAB7B8"), ticksuffix=" pts"),
            angularaxis=dict(gridcolor="#2C3E50", tickfont=dict(color="white"))
        ),
        paper_bgcolor="#0E1117",
        font=dict(color="white"),
        legend=dict(bgcolor="#1C2833", font=dict(color="white")),
        height=450,
        title=dict(text=f"Development Score Radar: {county_a} vs {county_b}",
                   font=dict(color="white", size=16))
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ── Bar chart comparison ──────────────────────────────────────────
    st.markdown("### 📊 Bar Chart Comparison")
    bar_metrics = [m for m in radar_metrics if m != "Population_2019"]
    bar_df = pd.DataFrame({
        "Metric": [METRICS[m]["label"] for m in bar_metrics] * 2,
        "Value":  [float(row_a[m]) for m in bar_metrics] + [float(row_b[m]) for m in bar_metrics],
        "County": [county_a] * len(bar_metrics) + [county_b] * len(bar_metrics)
    })
    fig_bar = px.bar(
        bar_df, x="Metric", y="Value", color="County", barmode="group",
        color_discrete_map={county_a: "#2980B9", county_b: "#E74C3C"},
        labels={"Value": "Value", "Metric": "Indicator"}
    )
    fig_bar.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white"), height=380,
        legend=dict(bgcolor="#1C2833", font=dict(color="white")),
        xaxis=dict(gridcolor="#2C3E50", tickangle=-15),
        yaxis=dict(gridcolor="#2C3E50"),
        margin=dict(l=10, r=10, t=20, b=10)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── All counties ranked by metric ─────────────────────────────────
    st.markdown("### 🏆 All Counties Ranked")
    rank_by = st.selectbox("Rank by:", [METRICS[m]["label"] for m in METRICS if m in county_df.columns],
                           key="rank_metric")
    # reverse lookup
    col_name = next((k for k, v in METRICS.items() if v["label"] == rank_by), None)
    if col_name:
        ranked = county_df[["County", "Region", col_name]].sort_values(
            col_name, ascending=(METRICS[col_name]["good"] == "low")
        ).reset_index(drop=True)
        ranked.index += 1
        ranked.columns = ["County", "Region", rank_by]

        # Highlight selected counties
        def highlight_selected(row):
            if row["County"] == county_a:
                return ["background-color: #1A5276"] * len(row)
            if row["County"] == county_b:
                return ["background-color: #7B241C"] * len(row)
            return [""] * len(row)

        st.dataframe(ranked.style.apply(highlight_selected, axis=1), use_container_width=True)
