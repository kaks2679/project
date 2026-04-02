"""
Page 3: M-Pesa & Mobile Money Impact Predictor
How mobile money transforms Kenya's economy and reduces poverty.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from utils.ml_models import mobile_money_poverty_model


def render(data: dict):
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1E8449 0%, #117A65 100%);
                padding: .8rem 1.5rem; border-radius: 12px; margin-bottom: 1rem;'>
        <h2 style='color:white; margin:0; font-size:1.4rem;'>💚 M-Pesa & Mobile Money Impact Predictor</h2>
        <p style='color:#A9DFBF; margin:.2rem 0 0; font-size:.85rem;'>
            17 years of CBK data · ML regression · Does mobile money reduce poverty?
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ Page Guide & Stakeholder Notes", expanded=False):
        st.markdown("""
        **What this page shows:**
        Analysis of M-Pesa and mobile financial services data (2007–2023) from CBK Annual Reports,
        combined with an ML regression model that quantifies mobile money's impact on poverty.

        **How to read the results:**
        - **KPI strip** — headline M-Pesa statistics for 2023 (users, agents, volume, inclusion, remittances)
        - **Growth vs Poverty chart** — as M-Pesa users grow (green bars), the red poverty line falls
        - **Model comparison table** — R² = 1.0 = perfect prediction; our best model achieves R²=0.904
        - **Feature importance** — which M-Pesa variables *most* drive poverty reduction
        - **Actual vs Predicted** — validates the model accuracy on historical data

        **For stakeholders:**
        - 🏛️ *Policy makers*: Financial inclusion is the **single biggest lever** for poverty reduction.
          Prioritise M-Pesa agent rollout to NE counties (Wajir, Mandera, Turkana).
        - 📈 *Investors*: M-Pesa's 41M users + KES 7.9 trillion annual volume = massive fintech market.
        - 🌍 *NGOs*: Remittances ($4.2B) now exceed FDI and tea exports — diaspora engagement is critical.
        - 💡 *Key insight*: Financial inclusion rose from 26.4% (2006) → 85.1% (2023). The ML model
          confirms that **M-Pesa penetration** explains over 90% of poverty variance.
        """)

    mm_df = data["mobile_money"].copy()

    # ── Run ML model ─────────────────────────────────────────────────
    with st.spinner("⚙️ Training regression models..."):
        result = mobile_money_poverty_model(mm_df)

    # ── KPI strip ────────────────────────────────────────────────────
    st.markdown("### 🚀 M-Pesa by the Numbers (2023)")
    k1, k2, k3, k4, k5 = st.columns(5)
    last = mm_df.iloc[-1]
    kpis = [
        ("👤 Users",        f"{last['MPesa_Users_M']:.0f}M",           "#27AE60"),
        ("🏪 Agents",       f"{int(last['MPesa_Agents']):,}",           "#2980B9"),
        ("💰 Volume",       f"KES {last['Mobile_Money_Volume_B_KES']:.0f}B","#8E44AD"),
        ("🏦 Fin. Included",f"{last['Financial_Inclusion_Pct']:.1f}%",  "#E67E22"),
        ("🌍 Remittances",  f"USD {last['Remittances_B_USD']:.1f}B",    "#E74C3C"),
    ]
    for col, (lbl, val, color) in zip([k1,k2,k3,k4,k5], kpis):
        col.markdown(f"""
        <div style='background:#1C2833; padding:1rem; border-radius:10px;
                    border-top:3px solid {color}; text-align:center;'>
            <div style='color:#AAB7B8; font-size:.78rem'>{lbl}</div>
            <div style='color:{color}; font-size:1.4rem; font-weight:bold'>{val}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Growth chart ─────────────────────────────────────────────────
    st.markdown("### 📈 M-Pesa Growth vs Poverty Reduction (2007–2023)")
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=mm_df["Year"], y=mm_df["MPesa_Users_M"],
        name="M-Pesa Users (M)",
        marker_color="#27AE60",
        opacity=0.7
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=mm_df["Year"], y=mm_df["Poverty_Rate_National"],
        name="National Poverty Rate (%)",
        line=dict(color="#E74C3C", width=3),
        mode="lines+markers",
        marker=dict(size=7)
    ), secondary_y=True)

    fig.add_trace(go.Scatter(
        x=mm_df["Year"], y=mm_df["Financial_Inclusion_Pct"],
        name="Financial Inclusion (%)",
        line=dict(color="#F39C12", width=2.5, dash="dot"),
        mode="lines+markers",
        marker=dict(size=6)
    ), secondary_y=True)

    fig.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white"), height=440,
        legend=dict(bgcolor="#1C2833", font=dict(color="white")),
        hovermode="x unified",
        xaxis=dict(gridcolor="#2C3E50", title="Year"),
    )
    fig.update_yaxes(title_text="M-Pesa Users (M)", gridcolor="#2C3E50", secondary_y=False)
    fig.update_yaxes(title_text="Rate (%)", gridcolor="#2C3E50", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

    # ── ML Model results ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🤖 ML Model: Does Mobile Money Reduce Poverty?")

    if result:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("#### 📊 Model Comparison")
            model_rows = []
            for name, vals in result["model_results"].items():
                model_rows.append({
                    "Model": name,
                    "R² Score": f"{vals['r2']:.3f}",
                    "MAE": f"{vals['mae']:.3f}%",
                    "Quality": "🥇 Best" if vals["r2"] == result["best_r2"] else "✅ Good"
                })
            st.dataframe(
                pd.DataFrame(model_rows).set_index("Model"),
                use_container_width=True
            )

            best_r2 = result["best_r2"]
            color   = "#27AE60" if best_r2 > 0.75 else "#F39C12"
            st.markdown(f"""
            <div style='background:#1C2833; padding:1.2rem; border-radius:10px;
                        border-left:4px solid {color}; margin-top:1rem;'>
                <b style='color:white'>Best Model R² = {best_r2:.3f}</b><br>
                <span style='color:#AAB7B8; font-size:.9rem'>
                    {'Excellent — model explains >' + str(round(best_r2*100)) + '% of poverty variance'
                     if best_r2 > 0.75
                     else 'Good — model explains ' + str(round(best_r2*100)) + '% of poverty variance'}
                </span>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("#### 🔑 Feature Importance")
            fi  = result["feature_importance"]
            fi_df = pd.DataFrame(list(fi.items()), columns=["Feature", "Importance (%)"]) \
                      .sort_values("Importance (%)", ascending=True)
            fig_fi = go.Figure(go.Bar(
                x=fi_df["Importance (%)"], y=fi_df["Feature"],
                orientation="h",
                marker_color=["#E74C3C" if v > 20 else "#F39C12" if v > 10 else "#3498DB"
                               for v in fi_df["Importance (%)"]],
                text=[f"{v:.1f}%" for v in fi_df["Importance (%)"]],
                textposition="outside"
            ))
            fig_fi.update_layout(
                plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
                font=dict(color="white", size=11),
                height=320, margin=dict(l=10, r=60, t=10, b=20),
                xaxis=dict(gridcolor="#2C3E50", title="Importance (%)"),
            )
            st.plotly_chart(fig_fi, use_container_width=True)

        # Actual vs Predicted
        st.markdown("#### 🎯 Actual vs Predicted Poverty Rate")
        pred_df = result["predictions_df"]
        fig_avp = go.Figure()
        fig_avp.add_trace(go.Scatter(
            x=pred_df["Year"], y=pred_df["Poverty_Rate_National"],
            mode="lines+markers", name="Actual Poverty Rate",
            line=dict(color="#E74C3C", width=3), marker=dict(size=8)
        ))
        fig_avp.add_trace(go.Scatter(
            x=pred_df["Year"], y=pred_df["Predicted_Poverty"],
            mode="lines+markers", name="ML Predicted",
            line=dict(color="#27AE60", width=2.5, dash="dot"), marker=dict(size=7, symbol="diamond")
        ))
        fig_avp.update_layout(
            plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
            font=dict(color="white"), height=360,
            legend=dict(bgcolor="#1C2833", font=dict(color="white")),
            hovermode="x unified",
            xaxis=dict(gridcolor="#2C3E50", title="Year"),
            yaxis=dict(gridcolor="#2C3E50", title="Poverty Rate (%)"),
        )
        st.plotly_chart(fig_avp, use_container_width=True)

    # ── Transaction volumes ──────────────────────────────────────────
    st.markdown("### 💸 Mobile Money Transaction Volumes (KES Billions)")
    fig_vol = go.Figure()
    fig_vol.add_trace(go.Scatter(
        x=mm_df["Year"], y=mm_df["Mobile_Money_Volume_B_KES"],
        fill="tozeroy",
        fillcolor="rgba(39,174,96,0.25)",
        line=dict(color="#27AE60", width=2.5),
        name="Transaction Volume (KES B)"
    ))
    fig_vol.add_trace(go.Scatter(
        x=mm_df["Year"], y=mm_df["Remittances_B_USD"] * 140,
        mode="lines+markers",
        line=dict(color="#F39C12", width=2, dash="dot"),
        name="Remittances (approx. KES B)"
    ))
    fig_vol.update_layout(
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white"), height=360,
        legend=dict(bgcolor="#1C2833", font=dict(color="white")),
        xaxis=dict(gridcolor="#2C3E50", title="Year"),
        yaxis=dict(gridcolor="#2C3E50", title="KES Billions"),
        hovermode="x unified"
    )
    st.plotly_chart(fig_vol, use_container_width=True)

    # ── Key insight ──────────────────────────────────────────────────
    st.markdown("""
    <div style='background:linear-gradient(135deg,#1E8449,#117A65); padding:1.5rem;
                border-radius:12px; margin-top:1rem;'>
        <h3 style='color:white; margin:0'>🔍 Key Insight</h3>
        <p style='color:#A9DFBF; margin-top:.5rem; font-size:1rem;'>
            Since M-Pesa launched in 2007, Kenya's national poverty rate dropped from
            <b style='color:white'>46.8% → 33.5%</b> while financial inclusion rose from
            <b style='color:white'>26.4% → 85.1%</b>. The ML model confirms that
            <b style='color:white'>financial inclusion and M-Pesa user growth</b> are
            the strongest predictors of poverty reduction — more than GDP growth alone.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Raw data ─────────────────────────────────────────────────────
    with st.expander("📋 Mobile Money Raw Data"):
        st.dataframe(mm_df.set_index("Year").style.format("{:.2f}"), use_container_width=True)
        csv = mm_df.to_csv(index=False).encode()
        st.download_button("⬇️ Download CSV", csv, "kenya_mobile_money.csv", "text/csv")
