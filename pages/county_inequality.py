"""
Page 2: County-Level Inequality Heatmap
Choropleth + clustering of Kenya counties by poverty & development metrics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
from utils.ml_models import cluster_counties, compute_regional_stats


CLUSTER_COLORS = {
    "🌿 Emerging (Low Poverty)":  "#27AE60",
    "📈 Developing":              "#2ECC71",
    "⚡ Transitioning":           "#F39C12",
    "⚠️ Vulnerable":              "#E67E22",
    "🔴 Critical Need":           "#E74C3C",
}

METRIC_CONFIG = {
    "Poverty_Rate":       {"label": "Poverty Rate (%)",        "colorscale": "Reds",   "icon": "🏚️"},
    "Unemployment_Rate":  {"label": "Unemployment Rate (%)",   "colorscale": "Oranges","icon": "👷"},
    "Mobile_Penetration": {"label": "Mobile Penetration (%)",  "colorscale": "Greens", "icon": "📱"},
    "Electricity_Access": {"label": "Electricity Access (%)",  "colorscale": "YlOrBr", "icon": "⚡"},
    "HDI_Score":          {"label": "HDI Score",               "colorscale": "Blues",  "icon": "🌐"},
}


def _make_bubble_map(df: pd.DataFrame, metric: str, cfg: dict) -> folium.Map:
    """Create a Folium bubble map for Kenya counties."""
    m = folium.Map(
        location=[0.0236, 37.9062],
        zoom_start=6,
        tiles="CartoDB dark_matter"
    )

    vals    = df[metric]
    min_v, max_v = vals.min(), vals.max()

    for _, row in df.iterrows():
        val     = row[metric]
        norm    = (val - min_v) / (max_v - min_v + 1e-9)
        radius  = 8 + norm * 28

        # Color by cluster
        c_label = row.get("Cluster_Label", "⚡ Transitioning")
        color   = CLUSTER_COLORS.get(c_label, "#3498DB")

        popup_html = f"""
        <div style='font-family:Arial; min-width:180px; background:#1C2833;
                    color:white; padding:10px; border-radius:8px;'>
            <b style='font-size:14px'>📍 {row['County']}</b><br>
            <hr style='border-color:#2C3E50; margin:5px 0'>
            <span style='color:#AED6F1'>Region:</span> {row['Region']}<br>
            <span style='color:#AED6F1'>Cluster:</span> {c_label}<br>
            <hr style='border-color:#2C3E50; margin:5px 0'>
            🏚️ Poverty: <b>{row['Poverty_Rate']:.1f}%</b><br>
            👷 Unemployment: <b>{row['Unemployment_Rate']:.1f}%</b><br>
            📱 Mobile: <b>{row['Mobile_Penetration']:.1f}%</b><br>
            ⚡ Electricity: <b>{row['Electricity_Access']:.1f}%</b><br>
            🌐 HDI: <b>{row['HDI_Score']:.3f}</b><br>
            👥 Population: <b>{row['Population_2019']:,}</b>
        </div>
        """
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.75,
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=f"{row['County']}: {val:.1f} {cfg['label']}"
        ).add_to(m)

    return m


def render(data: dict):
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1A5276 0%, #154360 100%);
                padding: .8rem 1.5rem; border-radius: 12px; margin-bottom: 1rem;'>
        <h2 style='color:white; margin:0; font-size:1.4rem;'>🗺️ County Inequality & Opportunity Map</h2>
        <p style='color:#AED6F1; margin:.2rem 0 0; font-size:.85rem;'>
            Kenya 47 Counties · KNBS 2019 Census · KMeans Clustering · Interactive Map
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ Page Guide & Stakeholder Notes", expanded=False):
        st.markdown("""
        **What this page shows:**
        Socioeconomic data for all 47 Kenya counties from the KNBS 2019 Census, visualised as:
        - An **interactive Folium map** with colour-coded county polygons
        - A **KMeans clustering** analysis grouping counties into 5 development tiers
        - **Bubble charts** and **bar rankings** for cross-county comparisons

        **How to read the cluster tiers:**
        | Tier | Counties | Characteristics |
        |------|----------|----------------|
        | 🌿 Emerging | Nairobi, Mombasa, Kisumu | Low poverty, high mobile/electricity |
        | 📈 Developing | Most Central + Rift Valley | Moderate development |
        | ⚡ Transitioning | Western, Nyanza | Mixed indicators |
        | ⚠️ Vulnerable | Coast + parts of Eastern | High unemployment, low HDI |
        | 🔴 Critical Need | Wajir, Mandera, Turkana | Extreme poverty (>70%), low services |

        **For stakeholders:**
        - 🏛️ *Government / CRA*: The 5-tier clustering directly maps to equitable revenue allocation
          priorities. Tier 5 counties need 3–4× per capita transfers to reach baseline services.
        - 🌍 *NGOs / UNICEF / UNHCR*: NE Kenya cluster shows acute humanitarian need —
          Wajir, Mandera, Garissa require emergency development programming.
        - 📈 *County Governors*: Compare your county's HDI, mobile penetration, and electricity
          access against peers. Use the 'County Comparison' page for detailed benchmarking.
        - 💡 *Key insight*: Kenya's Gini coefficient (40.8) understates the **spatial inequality**
          between Nairobi (HDI ~0.75) and Turkana (HDI ~0.35) — a 2× development gap.
        """)

    county_df = data["county"].copy()

    # ── Sidebar ─────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🗂️ Map Controls")
        metric = st.selectbox(
            "Metric to Display",
            list(METRIC_CONFIG.keys()),
            format_func=lambda x: f"{METRIC_CONFIG[x]['icon']} {METRIC_CONFIG[x]['label']}",
            key="county_metric"
        )
        n_clusters = st.slider("Number of Clusters", 3, 6, 5, key="county_clusters")
        region_filter = st.multiselect(
            "Filter by Region",
            sorted(county_df["Region"].unique()),
            default=[],
            key="county_region"
        )

    cfg = METRIC_CONFIG[metric]

    # Run clustering
    county_df = cluster_counties(county_df, n_clusters=n_clusters)

    if region_filter:
        display_df = county_df[county_df["Region"].isin(region_filter)]
    else:
        display_df = county_df

    # ── KPI row ─────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🏚️ Avg Poverty", f"{county_df['Poverty_Rate'].mean():.1f}%",
              f"Max: {county_df['Poverty_Rate'].max():.1f}%")
    k2.metric("👷 Avg Unemployment", f"{county_df['Unemployment_Rate'].mean():.1f}%",
              f"Max: {county_df['Unemployment_Rate'].max():.1f}%")
    k3.metric("📱 Avg Mobile", f"{county_df['Mobile_Penetration'].mean():.1f}%",
              f"Min: {county_df['Mobile_Penetration'].min():.1f}%")
    k4.metric("🌐 Avg HDI", f"{county_df['HDI_Score'].mean():.3f}",
              f"Min: {county_df['HDI_Score'].min():.3f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Interactive Folium Map ───────────────────────────────────────
    st.markdown(f"### 🗺️ Interactive Map — {cfg['icon']} {cfg['label']}")
    st.caption("🖱️ Click any bubble for detailed county statistics")

    folium_map = _make_bubble_map(display_df, metric, cfg)
    st_folium(folium_map, width=None, height=500, returned_objects=[])

    # ── Cluster legend ──────────────────────────────────────────────
    st.markdown("#### 🏷️ Cluster Legend")
    legend_cols = st.columns(len(CLUSTER_COLORS))
    for i, (label, color) in enumerate(CLUSTER_COLORS.items()):
        count = len(county_df[county_df["Cluster_Label"] == label])
        legend_cols[i].markdown(f"""
        <div style='background:#1C2833; border-left:4px solid {color};
                    padding:.6rem .8rem; border-radius:8px; text-align:center;'>
            <div style='color:white; font-size:.85rem'>{label}</div>
            <div style='color:{color}; font-weight:bold'>{count} counties</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Bar chart: Top/Bottom 10 ─────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(f"#### 🔝 Top 10 — Highest {cfg['label']}")
        top10 = display_df.nlargest(10, metric)[["County", metric, "Cluster_Label"]].reset_index(drop=True)
        colors = [CLUSTER_COLORS.get(c, "#3498DB") for c in top10["Cluster_Label"]]
        fig_top = go.Figure(go.Bar(
            x=top10[metric], y=top10["County"],
            orientation="h",
            marker_color=colors,
            text=[f"{v:.1f}" for v in top10[metric]],
            textposition="outside"
        ))
        fig_top.update_layout(
            plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
            font=dict(color="white", size=11),
            height=360, margin=dict(l=10, r=50, t=20, b=20),
            xaxis=dict(gridcolor="#2C3E50"),
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig_top, use_container_width=True)

    with col_b:
        st.markdown(f"#### 🔻 Top 10 — Lowest {cfg['label']}")
        bot10 = display_df.nsmallest(10, metric)[["County", metric, "Cluster_Label"]].reset_index(drop=True)
        colors_b = [CLUSTER_COLORS.get(c, "#3498DB") for c in bot10["Cluster_Label"]]
        fig_bot = go.Figure(go.Bar(
            x=bot10[metric], y=bot10["County"],
            orientation="h",
            marker_color=colors_b,
            text=[f"{v:.1f}" for v in bot10[metric]],
            textposition="outside"
        ))
        fig_bot.update_layout(
            plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
            font=dict(color="white", size=11),
            height=360, margin=dict(l=10, r=50, t=20, b=20),
            xaxis=dict(gridcolor="#2C3E50"),
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig_bot, use_container_width=True)

    # ── Regional summary ─────────────────────────────────────────────
    st.markdown("### 🌍 Regional Summary")
    regional = compute_regional_stats(county_df)
    fig_reg = px.bar(
        regional.sort_values("Avg_Poverty", ascending=False),
        x="Region", y=["Avg_Poverty", "Avg_Unemployment"],
        barmode="group",
        color_discrete_sequence=["#E74C3C", "#F39C12"],
        title="Average Poverty & Unemployment by Region",
        labels={"value": "Rate (%)", "variable": "Indicator"}
    )
    fig_reg.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white"), height=380,
        legend=dict(bgcolor="#1C2833", font=dict(color="white")),
        title_font=dict(color="white", size=16),
        xaxis=dict(gridcolor="#2C3E50"),
        yaxis=dict(gridcolor="#2C3E50"),
    )
    st.plotly_chart(fig_reg, use_container_width=True)

    # ── Scatter: Poverty vs Mobile penetration ───────────────────────
    st.markdown("### 📱 Does Mobile Penetration Reduce Poverty?")
    fig_sc = px.scatter(
        display_df, x="Mobile_Penetration", y="Poverty_Rate",
        size="Population_2019", color="Cluster_Label",
        color_discrete_map=CLUSTER_COLORS,
        hover_name="County",
        hover_data={"HDI_Score": True, "Electricity_Access": True,
                    "Population_2019": ":,"},
        trendline="ols",
        title="Mobile Penetration vs Poverty Rate (bubble = population)",
        labels={"Mobile_Penetration": "Mobile Penetration (%)",
                "Poverty_Rate": "Poverty Rate (%)"}
    )
    fig_sc.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white"), height=420,
        legend=dict(bgcolor="#1C2833", font=dict(color="white"), title="Cluster"),
        title_font=dict(color="white", size=16),
        xaxis=dict(gridcolor="#2C3E50"),
        yaxis=dict(gridcolor="#2C3E50"),
    )
    st.plotly_chart(fig_sc, use_container_width=True)

    # ── Data table ───────────────────────────────────────────────────
    with st.expander("📋 Full County Data Table"):
        show = display_df[["County", "Region", "Cluster_Label", "Poverty_Rate",
                            "Unemployment_Rate", "Mobile_Penetration",
                            "Electricity_Access", "HDI_Score", "Population_2019"]].copy()
        show = show.rename(columns={
            "Cluster_Label": "Cluster", "Poverty_Rate": "Poverty (%)",
            "Unemployment_Rate": "Unemp (%)", "Mobile_Penetration": "Mobile (%)",
            "Electricity_Access": "Electricity (%)", "Population_2019": "Pop (2019)"
        })
        st.dataframe(show.reset_index(drop=True), use_container_width=True)
        csv = show.to_csv(index=False).encode()
        st.download_button("⬇️ Download County CSV", csv, "kenya_county_data.csv", "text/csv")
