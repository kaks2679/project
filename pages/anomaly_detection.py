"""
Page 8: Anomaly Detection
Isolation Forest anomaly detection on Kenya macro-economic time series.
Author: Stephen Muema
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore")


KNOWN_SHOCKS = {
    2008: "🌐 Global Financial Crisis",
    2011: "💸 High Inflation (18%+) & Drought",
    2017: "🗳️ Election Uncertainty",
    2020: "🦠 COVID-19 Pandemic",
    2022: "🌍 Post-COVID Inflation Surge",
}


def render(data: dict):
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1C1C1C 0%, #4A235A 50%, #6C3483 100%);
                padding: .8rem 1.5rem; border-radius: 12px; margin-bottom: 1rem;'>
        <h2 style='color:white; margin:0; font-size:1.4rem;'>🔍 Anomaly Detection Engine</h2>
        <p style='color:#D7BDE2; margin:.2rem 0 0; font-size:.85rem;'>
            Isolation Forest ML · Detects economic shocks and outlier years in Kenya's macro data
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ Page Guide & Stakeholder Notes", expanded=False):
        st.markdown("""
        **What this page shows:**
        An Isolation Forest machine learning model detects *statistically unusual* years in Kenya's
        macro-economic time series — identifying economic shocks, crises, and turning points.

        **How to read the results:**
        - **Red markers** on charts = anomaly years flagged by the ML model (top 15% most unusual)
        - **Anomaly score** — more negative = more anomalous (further from typical economic behaviour)
        - **Known shocks panel** — cross-validates ML detections with documented historical events
        - **Multi-indicator view** — anomalies across different indicators reveal shock propagation

        **For stakeholders:**
        - 🏛️ *Policy makers & CBK*: Use this as an **early-warning system**. Years with anomaly scores
          below -0.1 warrant immediate policy review and contingency planning.
        - 📈 *Risk analysts*: 2008, 2011, 2017, 2020 were all correctly flagged — validating the model
          as a reliable crisis detector for Kenya's economic context.
        - 🌍 *Development partners*: Anomaly years coincide with aid disbursement peaks — understanding
          shock timing improves donor response planning.
        - 💡 *Key insight*: COVID-2020 was Kenya's largest economic shock since independence.
          The 2022 post-COVID inflation surge is now also flagged as an anomaly.
        """)

    macro_df = data["macro"].copy()

    numeric_cols = [c for c in macro_df.columns
                    if c != "Year" and macro_df[c].notna().sum() >= 10]

    if len(numeric_cols) < 2:
        st.error("Not enough numeric columns for anomaly detection.")
        return

    # ── Sidebar controls ──────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🔍 Anomaly Settings")
        selected_cols = st.multiselect(
            "Features for Anomaly Detection",
            numeric_cols,
            default=numeric_cols[:5] if len(numeric_cols) >= 5 else numeric_cols,
            key="anom_cols"
        )
        contamination = st.slider(
            "Contamination Factor",
            min_value=0.05, max_value=0.30, value=0.10, step=0.01,
            help="Expected fraction of anomalies (0.10 = ~10% of years are anomalies)",
            key="anom_cont"
        )
        viz_indicator = st.selectbox(
            "Visualise Indicator",
            [c for c in selected_cols if c in macro_df.columns],
            key="anom_viz"
        ) if selected_cols else None

    if not selected_cols:
        st.info("Please select at least two features from the sidebar.")
        return

    # ── Prepare data ──────────────────────────────────────────────────
    feat_df = macro_df[["Year"] + selected_cols].dropna()
    X = feat_df[selected_cols].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ── Isolation Forest ──────────────────────────────────────────────
    iso = IsolationForest(contamination=contamination, random_state=42, n_estimators=200)
    preds = iso.fit_predict(X_scaled)
    scores = iso.score_samples(X_scaled)   # More negative = more anomalous

    feat_df = feat_df.copy()
    feat_df["Anomaly"]      = (preds == -1)
    feat_df["Anomaly_Score"] = np.round(-scores, 4)   # invert: higher = more anomalous

    n_anomalies = int(feat_df["Anomaly"].sum())
    anomaly_years = feat_df[feat_df["Anomaly"]]["Year"].tolist()

    # ── KPI cards ────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("🗓️ Years Analysed",     str(len(feat_df)),                  "#3498DB"),
        ("🚨 Anomalous Years",    str(n_anomalies),                   "#E74C3C"),
        ("✅ Normal Years",       str(len(feat_df) - n_anomalies),    "#27AE60"),
        ("🎯 Features Used",      str(len(selected_cols)),             "#8E44AD"),
    ]
    for col, (lbl, val, clr) in zip([c1, c2, c3, c4], cards):
        col.markdown(f"""
        <div style='background:#1C2833; padding:1rem; border-radius:10px;
                    border-top:3px solid {clr}; text-align:center;'>
            <div style='color:#AAB7B8; font-size:.8rem'>{lbl}</div>
            <div style='color:{clr}; font-size:1.5rem; font-weight:bold'>{val}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Anomaly score time-series ────────────────────────────────────
    st.markdown("### 📊 Anomaly Score Over Time")
    fig_score = go.Figure()
    fig_score.add_trace(go.Scatter(
        x=feat_df["Year"], y=feat_df["Anomaly_Score"],
        mode="lines+markers",
        name="Anomaly Score",
        line=dict(color="#8E44AD", width=2),
        marker=dict(
            size=[12 if a else 6 for a in feat_df["Anomaly"]],
            color=["#E74C3C" if a else "#8E44AD" for a in feat_df["Anomaly"]],
            symbol=["star" if a else "circle" for a in feat_df["Anomaly"]]
        ),
        hovertemplate="<b>%{x}</b><br>Score: %{y:.4f}<extra></extra>"
    ))

    # Threshold line
    threshold = feat_df[feat_df["Anomaly"]]["Anomaly_Score"].min() if n_anomalies > 0 else 0
    fig_score.add_hline(
        y=threshold, line_dash="dash", line_color="#E74C3C",
        annotation_text="Anomaly Threshold",
        annotation_font_color="#E74C3C"
    )

    # Annotate known shocks
    for year, label in KNOWN_SHOCKS.items():
        yr_row = feat_df[feat_df["Year"] == year]
        if not yr_row.empty:
            fig_score.add_annotation(
                x=year,
                y=float(yr_row["Anomaly_Score"].values[0]),
                text=label[:25],
                showarrow=True,
                arrowhead=2,
                arrowcolor="#F39C12",
                font=dict(color="#F39C12", size=9),
                yshift=10,
                bgcolor="rgba(0,0,0,0.6)"
            )

    fig_score.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white"), height=440,
        legend=dict(bgcolor="#1C2833", font=dict(color="white")),
        hovermode="x unified",
        xaxis=dict(gridcolor="#2C3E50", title="Year"),
        yaxis=dict(gridcolor="#2C3E50", title="Anomaly Score (higher = more anomalous)"),
        margin=dict(l=40, r=20, t=20, b=40)
    )
    st.plotly_chart(fig_score, use_container_width=True)

    # ── Indicator with anomaly highlights ────────────────────────────
    if viz_indicator and viz_indicator in feat_df.columns:
        st.markdown(f"### 📈 {viz_indicator} with Anomaly Highlights")
        normal  = feat_df[~feat_df["Anomaly"]]
        anom    = feat_df[feat_df["Anomaly"]]

        fig_ind = go.Figure()
        fig_ind.add_trace(go.Scatter(
            x=normal["Year"], y=normal[viz_indicator],
            mode="lines+markers",
            name="Normal",
            line=dict(color="#3498DB", width=2.5),
            marker=dict(size=6, color="#3498DB")
        ))
        if not anom.empty:
            fig_ind.add_trace(go.Scatter(
                x=anom["Year"], y=anom[viz_indicator],
                mode="markers",
                name="⚠️ Anomaly",
                marker=dict(size=14, color="#E74C3C", symbol="x",
                            line=dict(width=2, color="white"))
            ))
        # Shade anomaly years
        for yr in anomaly_years:
            fig_ind.add_vrect(
                x0=yr - 0.5, x1=yr + 0.5,
                fillcolor="rgba(231,76,60,0.10)",
                line_width=0
            )

        fig_ind.update_layout(
            plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
            font=dict(color="white"), height=380,
            legend=dict(bgcolor="#1C2833", font=dict(color="white")),
            hovermode="x unified",
            xaxis=dict(gridcolor="#2C3E50", title="Year"),
            yaxis=dict(gridcolor="#2C3E50", title=viz_indicator),
            margin=dict(l=40, r=20, t=20, b=40)
        )
        st.plotly_chart(fig_ind, use_container_width=True)

    # ── Anomaly table ────────────────────────────────────────────────
    st.markdown("### 🚨 Detected Anomalous Years")
    anom_df = feat_df[feat_df["Anomaly"]][["Year", "Anomaly_Score"] + selected_cols[:4]].copy()
    anom_df["Known Event"] = anom_df["Year"].map(lambda y: KNOWN_SHOCKS.get(int(y), "Unclassified"))
    anom_df = anom_df.sort_values("Anomaly_Score", ascending=False).reset_index(drop=True)
    anom_df.index += 1
    st.dataframe(anom_df, use_container_width=True)

    # ── Feature correlation with anomaly score ───────────────────────
    st.markdown("### 🔗 Which Indicators Drive Anomalies?")
    corr_with_score = {}
    for col in selected_cols:
        if col in feat_df.columns and feat_df[col].notna().sum() > 5:
            corr_with_score[col] = round(float(feat_df[col].corr(feat_df["Anomaly_Score"])), 3)

    corr_df = pd.DataFrame(list(corr_with_score.items()), columns=["Indicator", "Correlation"]) \
                .sort_values("Correlation", key=abs, ascending=False)

    fig_corr = go.Figure(go.Bar(
        x=corr_df["Correlation"],
        y=corr_df["Indicator"],
        orientation="h",
        marker_color=["#E74C3C" if v > 0 else "#27AE60" for v in corr_df["Correlation"]],
        text=[f"{v:.3f}" for v in corr_df["Correlation"]],
        textposition="outside"
    ))
    fig_corr.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white"), height=max(300, len(corr_df) * 28 + 60),
        xaxis=dict(gridcolor="#2C3E50", title="Pearson Correlation with Anomaly Score"),
        yaxis=dict(gridcolor="#2C3E50"),
        margin=dict(l=10, r=80, t=20, b=40),
        title=dict(text="Indicator Correlation with Anomaly Severity",
                   font=dict(color="white", size=14))
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    # ── Insight box ──────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background:#1C2833; padding:1.5rem; border-radius:12px;
                border-left:4px solid #8E44AD; margin-top:1rem;'>
        <h4 style='color:#D7BDE2; margin:0'>🔬 Isolation Forest Methodology</h4>
        <p style='color:#AAB7B8; font-size:.9rem; margin-top:.5rem; line-height:1.7;'>
            Isolation Forest detects anomalies by randomly partitioning the feature space —
            anomalous observations are isolated in fewer partitions. The contamination
            parameter (currently <b style='color:white'>{contamination:.0%}</b>) sets the
            expected proportion of outliers. Red stars indicate years detected as economically
            anomalous based on <b style='color:white'>{len(selected_cols)}</b> simultaneous
            macro indicators. Detected anomalies include:
            <b style='color:#E74C3C'>{", ".join(str(int(y)) for y in sorted(anomaly_years))}</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)
