"""
Page 6: County Comparison Tool
Multi-county socioeconomic comparison (up to 5 counties) — radar, heatmap, bar charts.
Author: Stephen Muema
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


# ── Metric definitions ────────────────────────────────────────────────
METRICS = {
    "Poverty_Rate":       {"label": "Poverty Rate (%)",       "icon": "🏚️",  "good": "low",     "unit": "%"},
    "Unemployment_Rate":  {"label": "Unemployment Rate (%)",  "icon": "👷",  "good": "low",     "unit": "%"},
    "Mobile_Penetration": {"label": "Mobile Penetration (%)", "icon": "📱",  "good": "high",    "unit": "%"},
    "Electricity_Access": {"label": "Electricity Access (%)", "icon": "⚡",  "good": "high",    "unit": "%"},
    "HDI_Score":          {"label": "HDI Score",              "icon": "📚",  "good": "high",    "unit": ""},
    "Population_2019":    {"label": "Population (2019)",      "icon": "👥",  "good": "neutral", "unit": ""},
}

# County palette — up to 5 colours
COUNTY_COLORS = ["#2980B9", "#27AE60", "#E74C3C", "#F39C12", "#8E44AD"]
COUNTY_FILLS  = [
    "rgba(41,128,185,.2)",   # blue
    "rgba(39,174,96,.2)",    # green
    "rgba(231,76,60,.2)",    # red
    "rgba(243,156,18,.2)",   # orange
    "rgba(142,68,173,.2)",   # purple
]


def _normalise(val, col_data, good):
    mn, mx = float(col_data.min()), float(col_data.max())
    span   = mx - mn + 1e-9
    norm   = (val - mn) / span * 100
    return round(100 - norm if good == "low" else norm, 1)


def _fmt(val, metric):
    if metric == "Population_2019":
        return f"{int(val):,}"
    if metric == "HDI_Score":
        return f"{val:.3f}"
    return f"{val:.1f}%"


def render(data: dict):
    # ── Compact header ─────────────────────────────────────────────────
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1B2631 0%, #21618C 100%);
                padding: .8rem 1.5rem; border-radius: 12px; margin-bottom: 1rem;'>
        <h2 style='color:white; margin:0; font-size:1.4rem;'>⚖️ County Comparison Tool</h2>
        <p style='color:#AED6F1; margin:.2rem 0 0; font-size:.85rem;'>
            Compare up to 5 Kenya counties side-by-side across all socioeconomic dimensions
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Stakeholder context ───────────────────────────────────────────
    with st.expander("ℹ️ About this page & how to read the results", expanded=False):
        st.markdown("""
        **Purpose:** Select 2–5 counties to compare their socioeconomic performance across poverty,
        unemployment, mobile penetration, electricity access, and Human Development Index (HDI).

        **How to interpret results:**
        - **Radar chart** — each axis is normalised 0–100 where 100 = *best* performance.
          A larger polygon = stronger overall development.
        - **Heatmap** — raw values at a glance; red = worst, green = best in each row.
        - **Bar chart** — grouped bars for direct metric-by-metric comparison.
        - **Ranking table** — all 47 counties ranked; your selections highlighted.

        **Stakeholder notes:**
        - 🏛️ *Policy makers*: Compare a target county against national leaders to identify gaps.
        - 📈 *Investors*: High HDI + growing mobile penetration = investable market.
        - 🎓 *Researchers*: Use the ranking table & download CSV for statistical analysis.
        """)

    county_df = data["county"].copy()

    # ── Add Cluster_Label if missing ──────────────────────────────────
    if "Cluster_Label" not in county_df.columns:
        county_df["Cluster_Label"] = "N/A"

    counties_list = sorted(county_df["County"].unique().tolist())

    # ── County selector (up to 5) ─────────────────────────────────────
    st.markdown("#### 🗂️ Select Counties to Compare (2 – 5)")
    col_s1, col_s2 = st.columns([3, 2])
    with col_s1:
        selected = st.multiselect(
            "Choose counties:",
            counties_list,
            default=["Nairobi", "Turkana"] if "Nairobi" in counties_list else counties_list[:2],
            max_selections=5,
            key="cmp_multi"
        )
    with col_s2:
        if len(selected) < 2:
            st.warning("⚠️ Select at least 2 counties to enable comparison.")
            return
        if len(selected) > 5:
            st.error("Max 5 counties. Please remove some.")
            return
        st.markdown(f"""
        <div style='background:#1C2833; padding:.7rem 1rem; border-radius:8px;
                    border-left:3px solid #3498DB; font-size:.82rem; color:#AAB7B8;'>
            Comparing <b style='color:white'>{len(selected)}</b> counties across
            <b style='color:white'>6</b> socioeconomic metrics
        </div>
        """, unsafe_allow_html=True)

    rows = {c: county_df[county_df["County"] == c].iloc[0] for c in selected}

    # ════════════════════════════════════════════════════════════════
    # SECTION 1 — COUNTY HEADER CARDS
    # ════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("#### 🏷️ Selected Counties")
    hdr_cols = st.columns(len(selected))
    for i, (c, col) in enumerate(zip(selected, hdr_cols)):
        row = rows[c]
        col.markdown(f"""
        <div style='background:linear-gradient(135deg,{COUNTY_COLORS[i]}22,{COUNTY_COLORS[i]}44);
                    padding:.7rem; border-radius:10px; text-align:center;
                    border:1px solid {COUNTY_COLORS[i]};'>
            <div style='color:{COUNTY_COLORS[i]}; font-size:1.1rem; font-weight:bold'>{c}</div>
            <div style='color:#AAB7B8; font-size:.72rem;'>{row["Region"]} Region</div>
            <div style='color:#566573; font-size:.7rem; margin-top:.2rem;'>HDI {row.get("HDI_Score",0):.3f}</div>
        </div>
        """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # SECTION 2 — METRIC COMPARISON HEATMAP + RADAR (2-col layout)
    # ════════════════════════════════════════════════════════════════
    st.markdown("---")
    col_radar, col_heat = st.columns([1, 1])

    # ── Radar chart ──────────────────────────────────────────────────
    radar_keys   = ["Poverty_Rate", "Unemployment_Rate", "Mobile_Penetration",
                    "Electricity_Access", "HDI_Score"]
    radar_labels = ["Poverty\n(inv.)", "Unemployment\n(inv.)", "Mobile\nPenetration",
                    "Electricity\nAccess", "HDI Score"]

    with col_radar:
        st.markdown("##### 🕸️ Development Radar (0–100, higher = better)")
        fig_radar = go.Figure()
        for i, c in enumerate(selected):
            row   = rows[c]
            vals  = [_normalise(float(row[m]), county_df[m], METRICS[m]["good"]) for m in radar_keys]
            vals_c = vals + [vals[0]]
            lbls_c = radar_labels + [radar_labels[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals_c, theta=lbls_c,
                fill="toself", name=c,
                line=dict(color=COUNTY_COLORS[i], width=2),
                fillcolor=COUNTY_FILLS[i]
            ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="#1C2833",
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="#2C3E50",
                                tickfont=dict(color="#AAB7B8", size=8), ticksuffix=" pts"),
                angularaxis=dict(gridcolor="#2C3E50", tickfont=dict(color="white", size=9))
            ),
            paper_bgcolor="#0E1117",
            font=dict(color="white"),
            legend=dict(bgcolor="#1C2833", font=dict(color="white", size=10),
                        orientation="h", y=-0.15, x=0.5, xanchor="center"),
            height=380,
            margin=dict(l=20, r=20, t=20, b=60)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # ── Metric heatmap ────────────────────────────────────────────────
    with col_heat:
        st.markdown("##### 🌡️ Metric Heatmap (raw values)")
        hm_metrics = [m for m in METRICS if m in county_df.columns]
        hm_labels  = [METRICS[m]["label"] for m in hm_metrics]
        hm_data    = np.array([
            [float(rows[c][m]) if m != "Population_2019"
             else float(rows[c][m]) / 1e6   # convert to millions for readability
             for m in hm_metrics]
            for c in selected
        ])
        # Normalise each metric 0-1 for colour (direction-aware)
        hm_norm = np.zeros_like(hm_data)
        for j, m in enumerate(hm_metrics):
            col_vals = county_df[m].values.astype(float)
            mn, mx   = col_vals.min(), col_vals.max()
            span     = mx - mn + 1e-9
            norm     = (hm_data[:, j] - mn) / span
            hm_norm[:, j] = norm if METRICS[m]["good"] == "high" else 1 - norm

        text_matrix = [
            [_fmt(float(rows[c][m]), m) + (" M" if m == "Population_2019" else "")
             for m in hm_metrics]
            for c in selected
        ]
        fig_hm = go.Figure(go.Heatmap(
            z=hm_norm,
            x=hm_labels,
            y=selected,
            text=text_matrix,
            texttemplate="%{text}",
            colorscale="RdYlGn",
            showscale=False,
            hovertemplate="<b>%{y}</b> — %{x}<br>Value: %{text}<extra></extra>"
        ))
        fig_hm.update_layout(
            plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
            font=dict(color="white", size=10),
            height=380,
            xaxis=dict(tickangle=-25, side="bottom", tickfont=dict(size=9)),
            yaxis=dict(tickfont=dict(size=10)),
            margin=dict(l=10, r=10, t=10, b=60)
        )
        st.plotly_chart(fig_hm, use_container_width=True)

    # ════════════════════════════════════════════════════════════════
    # SECTION 3 — GROUPED BAR CHART
    # ════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("##### 📊 Grouped Bar: Metric-by-Metric")
    bar_metrics = [m for m in METRICS if m != "Population_2019" and m in county_df.columns]
    bar_labels  = [METRICS[m]["label"] for m in bar_metrics]

    fig_bar = go.Figure()
    for i, c in enumerate(selected):
        vals = [float(rows[c][m]) for m in bar_metrics]
        fig_bar.add_trace(go.Bar(
            name=c, x=bar_labels, y=vals,
            marker_color=COUNTY_COLORS[i],
            opacity=0.85,
            text=[f"{v:.1f}" for v in vals],
            textposition="outside",
            textfont=dict(size=9)
        ))
    fig_bar.update_layout(
        barmode="group",
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white"), height=360,
        legend=dict(bgcolor="#1C2833", font=dict(color="white", size=10),
                    orientation="h", y=1.1, x=0),
        xaxis=dict(gridcolor="#2C3E50", tickangle=-15, tickfont=dict(size=9)),
        yaxis=dict(gridcolor="#2C3E50", title="Value"),
        margin=dict(l=10, r=10, t=50, b=30)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ════════════════════════════════════════════════════════════════
    # SECTION 4 — SCORE SUMMARY TABLE
    # ════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("##### 🏆 Overall Development Score & County Rankings")

    # Compute composite score (avg of normalised metrics, excluding population)
    score_metrics = [m for m in METRICS if m != "Population_2019" and m in county_df.columns]
    score_data = {}
    for c in selected:
        score = np.mean([_normalise(float(rows[c][m]), county_df[m], METRICS[m]["good"]) for m in score_metrics])
        score_data[c] = round(score, 1)

    score_df = pd.DataFrame([
        {"County": c,
         "Region": rows[c]["Region"],
         "Dev. Score /100": score_data[c],
         **{METRICS[m]["label"]: _fmt(float(rows[c][m]), m) for m in score_metrics}}
        for c in sorted(score_data, key=lambda x: score_data[x], reverse=True)
    ])
    st.dataframe(score_df.set_index("County"), use_container_width=True)

    # ── Insight box ────────────────────────────────────────────────────
    best_c  = max(score_data, key=score_data.get)
    worst_c = min(score_data, key=score_data.get)
    diff    = score_data[best_c] - score_data[worst_c]
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#0B3D6E,#1A5276); padding:1rem 1.5rem;
                border-radius:10px; border-left:4px solid #3498DB; margin-top:.5rem;'>
        <p style='color:#AED6F1; font-size:.78rem; margin:0 0 .3rem;'>🔍 Key Insight</p>
        <p style='color:white; font-size:.92rem; margin:0; line-height:1.7;'>
            Among selected counties, <b>{best_c}</b> leads with a composite score of
            <b>{score_data[best_c]:.0f}/100</b> while <b>{worst_c}</b> lags at
            <b>{score_data[worst_c]:.0f}/100</b> — a gap of <b>{diff:.0f} points</b>.
            This reflects Kenya's significant <b>intra-national development inequality</b>.
            Targeted interventions in the lowest-scoring counties can dramatically shift these numbers.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # SECTION 5 — ALL COUNTIES RANKED (collapsible)
    # ════════════════════════════════════════════════════════════════
    with st.expander("📋 All 47 Counties Ranked"):
        rank_by = st.selectbox(
            "Rank by:",
            [METRICS[m]["label"] for m in METRICS if m in county_df.columns],
            key="rank_metric_v2"
        )
        col_name = next((k for k, v in METRICS.items() if v["label"] == rank_by), None)
        if col_name:
            ascending = (METRICS[col_name]["good"] == "low")
            ranked = county_df[["County", "Region", col_name]].sort_values(
                col_name, ascending=ascending
            ).reset_index(drop=True)
            ranked.index += 1
            ranked.columns = ["County", "Region", rank_by]

            def _highlight(row):
                if row["County"] in selected:
                    idx = selected.index(row["County"])
                    c   = COUNTY_COLORS[idx]
                    # Convert hex to rgb for lighter bg
                    return [f"background-color: {c}33; border-left: 3px solid {c}"] * len(row)
                return [""] * len(row)

            st.dataframe(ranked.style.apply(_highlight, axis=1), use_container_width=True)

        # Download
        dl_df = county_df[["County","Region"] + list(METRICS.keys())].copy()
        st.download_button(
            "⬇️ Download All County Data (CSV)",
            dl_df.to_csv(index=False).encode(),
            "kenya_county_comparison.csv",
            "text/csv"
        )
