"""
Page 9: Natural Language Query Engine
Ask plain-English questions about Kenya's economy — answered with data + charts.
Author: Stephen Muema
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re
import warnings
warnings.filterwarnings("ignore")


# ── Keyword routing ──────────────────────────────────────────────────
QUESTION_PATTERNS = [
    # GDP
    (r"gdp.*growth|growth.*gdp|economy.*grow",               "gdp_growth"),
    (r"gdp.*capita|income.*per.*person",                     "gdp_capita"),
    # Poverty
    (r"poor(?:est)?|poverty|destitut",                       "poverty"),
    # Inflation
    (r"inflat|price.*rise|cost.*living",                     "inflation"),
    # Unemployment
    (r"unemploy|jobless|job.*market",                        "unemployment"),
    (r"youth.*unemploy|unemploy.*youth|young.*job",          "youth_unemp"),
    # Mobile / M-Pesa
    (r"mpesa|mobile.*money|m-pesa|financial.*inclus",        "mpesa"),
    (r"mobile.*penetr|phone.*access|sim.*card",              "mobile_pen"),
    # County
    (r"county|count(?:ies)?|region|province|local",          "counties"),
    # Gini / inequality
    (r"gini|inequalit|wealth.*gap|rich.*poor",               "gini"),
    # Electricity
    (r"electric|power|energy.*access",                       "electricity"),
    # Remittances
    (r"remit|diaspora|sent.*home",                           "remittances"),
    # Sector
    (r"agric|farm|sector.*employ|employ.*sector",            "sector"),
    # Forecast
    (r"forecast|predict|future|next.*year|project",          "forecast"),
    # Best / worst county
    (r"best.*county|lowest.*poverty|richest.*county",        "best_county"),
    (r"worst.*county|highest.*poverty|poorest.*county",      "worst_county"),
]

EXAMPLE_QUESTIONS = [
    "What is Kenya's current GDP growth?",
    "Which county has the highest poverty rate?",
    "How has M-Pesa reduced poverty?",
    "What is the youth unemployment rate?",
    "Show me inflation trends over time",
    "Which counties have the best electricity access?",
    "What is the Gini coefficient trend?",
    "Forecast GDP growth for the next 5 years",
    "What is the remittances contribution to GDP?",
    "Show sector employment breakdown",
]


def _classify(question: str) -> str:
    q = question.lower()
    for pattern, topic in QUESTION_PATTERNS:
        if re.search(pattern, q):
            return topic
    return "general"


def _answer(topic: str, data: dict) -> dict:
    """Return dict with answer text, optional dataframe, optional figure."""
    macro  = data["macro"]
    county = data["county"]
    mm     = data["mobile_money"]
    yu     = data["youth_unemp"]
    sector = data["sector_employ"]

    if topic == "gdp_growth":
        col = "GDP Growth (%)"
        if col in macro.columns:
            last = macro[col].dropna().iloc[-1]
            yr   = int(macro["Year"].iloc[macro[col].dropna().index[-1]])
            avg  = macro[col].dropna().mean()
            text = (f"Kenya's GDP growth in **{yr}** was **{last:.1f}%**. "
                    f"The historical average (2000–2023) is **{avg:.1f}%**. "
                    f"Kenya's economy has grown at ~5% annually, driven by services, ICT, and agriculture.")
            fig  = go.Figure(go.Bar(
                x=macro["Year"], y=macro[col].fillna(0),
                marker_color=["#27AE60" if v >= 0 else "#E74C3C" for v in macro[col].fillna(0)],
                name="GDP Growth (%)"
            ))
            fig.update_layout(**_dark_layout("Kenya GDP Growth Rate (%)", "Year", "Growth (%)"))
            return {"text": text, "fig": fig}

    elif topic == "gdp_capita":
        col = "GDP per Capita (constant USD)"
        if col in macro.columns:
            s = macro[["Year", col]].dropna()
            last = s[col].iloc[-1]; yr = int(s["Year"].iloc[-1])
            text = (f"Kenya's GDP per capita was **USD {last:,.0f}** in **{yr}** (constant 2015 USD). "
                    f"It has grown from ~USD 400 in 2000, reflecting economic transformation.")
            fig = go.Figure(go.Scatter(x=s["Year"], y=s[col], fill="tozeroy",
                                       fillcolor="rgba(52,152,219,0.2)",
                                       line=dict(color="#3498DB", width=2.5), name=col))
            fig.update_layout(**_dark_layout("GDP per Capita (constant USD)", "Year", "USD"))
            return {"text": text, "fig": fig}

    elif topic == "poverty":
        col_mm  = "Poverty_Rate_National"
        col_cty = "Poverty_Rate"
        last_pov = mm[col_mm].iloc[-1]
        poorest  = county.nlargest(5, col_cty)[["County", col_cty, "Region"]]
        text = (f"Kenya's national poverty rate is **{last_pov:.1f}%** (2023). "
                f"Down from ~47% in 2007 when M-Pesa launched. "
                f"The 5 poorest counties by headcount ratio are shown below.")
        fig = go.Figure(go.Bar(
            x=poorest["County"], y=poorest[col_cty],
            marker_color="#E74C3C",
            text=[f"{v:.1f}%" for v in poorest[col_cty]], textposition="outside"
        ))
        fig.update_layout(**_dark_layout("Top 5 Poorest Counties", "County", "Poverty Rate (%)"))
        return {"text": text, "fig": fig, "df": poorest}

    elif topic == "inflation":
        col = "Inflation Rate (%)"
        if col in macro.columns:
            last = macro[col].dropna().iloc[-1]; yr = int(macro["Year"].iloc[macro[col].dropna().index[-1]])
            peak = macro[col].max(); peak_yr = int(macro.loc[macro[col].idxmax(), "Year"])
            text = (f"Kenya's inflation rate was **{last:.1f}%** in **{yr}**. "
                    f"The peak was **{peak:.1f}%** in **{peak_yr}** (drought + global commodity prices). "
                    f"CBK targets inflation at 5% ± 2.5 pp.")
            fig = go.Figure(go.Scatter(
                x=macro["Year"], y=macro[col].fillna(0),
                fill="tozeroy", fillcolor="rgba(231,76,60,0.15)",
                line=dict(color="#E74C3C", width=2.5), name=col
            ))
            fig.add_hline(y=5, line_dash="dash", line_color="#27AE60",
                          annotation_text="CBK Target 5%", annotation_font_color="#27AE60")
            fig.update_layout(**_dark_layout("Kenya Inflation Rate (%)", "Year", "Inflation (%)"))
            return {"text": text, "fig": fig}

    elif topic == "unemployment":
        col = "Unemployment Rate (%)"
        if col in macro.columns:
            last = macro[col].dropna().iloc[-1]
            text = (f"Kenya's unemployment rate is **{last:.1f}%**. "
                    f"However, this underestimates underemployment and informal sector challenges. "
                    f"Youth unemployment (15–24) is much higher at ~61.5%.")
            fig = go.Figure(go.Scatter(x=macro["Year"], y=macro[col].fillna(0),
                                       fill="tozeroy", fillcolor="rgba(243,156,18,0.15)",
                                       line=dict(color="#F39C12", width=2.5), name=col))
            fig.update_layout(**_dark_layout("Unemployment Rate (%)", "Year", "Rate (%)"))
            return {"text": text, "fig": fig}

    elif topic == "youth_unemp":
        last = yu["Youth_Unemployment_Pct"].iloc[-1]
        yr   = int(yu["Year"].iloc[-1])
        text = (f"Kenya's **youth unemployment rate** (ages 15–24) was **{last:.1f}%** in **{yr}**. "
                f"This is nearly 5× the global average of ~13.6%. "
                f"Key drivers: skills mismatch, population growth, limited formal-sector jobs.")
        fig = go.Figure(go.Scatter(
            x=yu["Year"], y=yu["Youth_Unemployment_Pct"],
            fill="tozeroy", fillcolor="rgba(142,68,173,0.2)",
            line=dict(color="#8E44AD", width=2.5), mode="lines+markers", name="Youth Unemp (%)"
        ))
        fig.add_hline(y=13.6, line_dash="dash", line_color="#27AE60",
                      annotation_text="Global avg 13.6%", annotation_font_color="#27AE60")
        fig.update_layout(**_dark_layout("Youth Unemployment (%) 2005–2023", "Year", "Rate (%)"))
        return {"text": text, "fig": fig}

    elif topic == "mpesa":
        last = mm.iloc[-1]
        text = (f"M-Pesa has **{last['MPesa_Users_M']:.0f}M users** and **{int(last['MPesa_Agents']):,} agents** (2023). "
                f"Financial inclusion rose from **26.4% (2007) → {last['Financial_Inclusion_Pct']:.1f}% (2023)**. "
                f"ML models confirm M-Pesa is the **#1 predictor** of poverty reduction in Kenya (R²=0.904).")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=mm["Year"], y=mm["MPesa_Users_M"],
                                  fill="tozeroy", fillcolor="rgba(39,174,96,0.2)",
                                  line=dict(color="#27AE60", width=2.5), name="M-Pesa Users (M)"))
        fig.add_trace(go.Scatter(x=mm["Year"], y=mm["Financial_Inclusion_Pct"],
                                  line=dict(color="#F39C12", width=2.5, dash="dot"),
                                  name="Financial Inclusion (%)"))
        fig.update_layout(**_dark_layout("M-Pesa Growth & Financial Inclusion", "Year", "Value"))
        return {"text": text, "fig": fig}

    elif topic == "mobile_pen":
        top5 = county.nlargest(5, "Mobile_Penetration")[["County", "Mobile_Penetration"]]
        bot5 = county.nsmallest(5, "Mobile_Penetration")[["County", "Mobile_Penetration"]]
        text = (f"Mobile penetration varies widely across Kenya's 47 counties — from "
                f"**{county['Mobile_Penetration'].min():.1f}%** to **{county['Mobile_Penetration'].max():.1f}%**. "
                f"Urban counties like Nairobi lead at 98.2%.")
        fig = go.Figure(go.Bar(
            x=top5["County"].tolist() + ["…"] + bot5["County"].tolist(),
            y=top5["Mobile_Penetration"].tolist() + [np.nan] + bot5["Mobile_Penetration"].tolist(),
            marker_color=["#27AE60"]*5 + ["gray"] + ["#E74C3C"]*5,
            name="Mobile Penetration (%)"
        ))
        fig.update_layout(**_dark_layout("Mobile Penetration: Top 5 vs Bottom 5 Counties", "County", "%"))
        return {"text": text, "fig": fig}

    elif topic == "counties":
        text = "Kenya has **47 counties**. Here is a ranked overview by poverty rate."
        ranked = county[["County", "Poverty_Rate", "Unemployment_Rate",
                         "Mobile_Penetration", "Electricity_Access", "HDI_Score", "Region"]] \
                    .sort_values("Poverty_Rate").reset_index(drop=True)
        ranked.index += 1
        fig = go.Figure(go.Bar(
            x=county.sort_values("Poverty_Rate")["County"],
            y=county.sort_values("Poverty_Rate")["Poverty_Rate"],
            marker_color=county.sort_values("Poverty_Rate")["Poverty_Rate"],
            marker_colorscale="RdYlGn_r",
            name="Poverty Rate (%)"
        ))
        fig.update_layout(**_dark_layout("All 47 Counties by Poverty Rate", "County", "Poverty Rate (%)"),
                          xaxis_tickangle=-45)
        return {"text": text, "fig": fig, "df": ranked.head(20)}

    elif topic == "gini":
        col = "Gini Index (Inequality)"
        if col in macro.columns:
            s = macro[["Year", col]].dropna()
            last = float(s[col].iloc[-1]); yr = int(s["Year"].iloc[-1])
            text = (f"Kenya's Gini Index was **{last:.1f}** in **{yr}** — moderately high inequality. "
                    f"For reference, 0 = perfect equality, 100 = maximum inequality. "
                    f"Kenya's inequality is driven by urban–rural gaps and regional disparities.")
            fig = go.Figure(go.Scatter(x=s["Year"], y=s[col], fill="tozeroy",
                                       fillcolor="rgba(231,76,60,0.15)",
                                       line=dict(color="#E74C3C", width=2.5), name=col))
            fig.add_hline(y=40, line_dash="dash", line_color="#F39C12",
                          annotation_text="Sub-Saharan avg ~43",
                          annotation_font_color="#F39C12")
            fig.update_layout(**_dark_layout("Gini Index Trend", "Year", "Gini Index"))
            return {"text": text, "fig": fig}

    elif topic == "electricity":
        col = "Electricity_Access"
        top5 = county.nlargest(5, col)[["County", col, "Region"]]
        text = (f"Electricity access ranges from **{county[col].min():.1f}%** to "
                f"**{county[col].max():.1f}%** across counties. "
                f"The national target is 100% by 2030 under Kenya's Big 4 Agenda.")
        fig = go.Figure(go.Bar(
            x=county.sort_values(col, ascending=False).head(15)["County"],
            y=county.sort_values(col, ascending=False).head(15)[col],
            marker_color="#F39C12", name="Electricity Access (%)"
        ))
        fig.update_layout(**_dark_layout("Top 15 Counties by Electricity Access", "County", "%"),
                          xaxis_tickangle=-30)
        return {"text": text, "fig": fig}

    elif topic == "remittances":
        col = "Remittances_B_USD"
        last = mm[col].iloc[-1]; first = mm[col].iloc[0]
        text = (f"Kenyan diaspora remittances reached **USD {last:.1f}B** in 2023 — "
                f"up from USD {first:.1f}B in 2007. Remittances now exceed FDI inflows "
                f"and are a critical buffer against poverty.")
        fig = go.Figure(go.Bar(x=mm["Year"], y=mm[col], marker_color="#3498DB", name="Remittances ($B)"))
        fig.update_layout(**_dark_layout("Kenyan Diaspora Remittances ($B)", "Year", "USD Billions"))
        return {"text": text, "fig": fig}

    elif topic == "sector":
        text = "Kenya's employment is shifting from agriculture towards services and ICT."
        cols = [c for c in sector.columns if c != "Year"]
        fig = go.Figure()
        colors = ["#27AE60","#3498DB","#E74C3C","#F39C12","#8E44AD","#1ABC9C","#E67E22","#95A5A6","#566573"]
        for i, c in enumerate(cols):
            fig.add_trace(go.Scatter(x=sector["Year"], y=sector[c], stackgroup="one",
                                      name=c, line=dict(color=colors[i % len(colors)])))
        fig.update_layout(**_dark_layout("Kenya Sector Employment Share (%) 2010–2023", "Year", "Share (%)"))
        return {"text": text, "fig": fig, "df": sector.set_index("Year")}

    elif topic in ("best_county", "worst_county"):
        ascending = (topic == "best_county")
        top10 = county.nsmallest(10, "Poverty_Rate") if ascending else county.nlargest(10, "Poverty_Rate")
        label = "Lowest (Best)" if ascending else "Highest (Worst)"
        text  = f"The 10 counties with **{label}** poverty rates:"
        fig = go.Figure(go.Bar(
            x=top10["County"], y=top10["Poverty_Rate"],
            marker_color="#27AE60" if ascending else "#E74C3C",
            text=[f"{v:.1f}%" for v in top10["Poverty_Rate"]], textposition="outside"
        ))
        fig.update_layout(**_dark_layout(f"Counties — {label} Poverty Rate", "County", "Poverty Rate (%)"))
        return {"text": text, "fig": fig, "df": top10[["County","Poverty_Rate","Region"]]}

    elif topic == "forecast":
        from utils.ml_models import forecast_indicator
        col = "GDP Growth (%)"
        if col in macro.columns:
            s = macro.set_index("Year")[col].dropna()
            fc_df = forecast_indicator(s, list(s.index), forecast_years=5)
            fc_part = fc_df[fc_df["Is_Forecast"]] if not fc_df.empty else pd.DataFrame()
            text = (f"Based on Holt-Winters Exponential Smoothing, Kenya's GDP growth is "
                    f"projected to remain around **{fc_part['Value'].mean():.1f}%** over 2024–2028.")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=list(s.index), y=s.values,
                                      line=dict(color="#3498DB", width=2.5), name="Historical"))
            if not fc_part.empty:
                cx = [int(s.index[-1])] + list(fc_part["Year"])
                cy = [float(s.iloc[-1])] + list(fc_part["Value"])
                fig.add_trace(go.Scatter(x=cx, y=cy, line=dict(color="#F39C12", width=2.5, dash="dot"),
                                          name="Forecast", marker=dict(size=7, symbol="diamond")))
            fig.update_layout(**_dark_layout("GDP Growth Forecast (Holt-Winters)", "Year", "Growth (%)"))
            return {"text": text, "fig": fig}

    # Fallback
    return {
        "text": ("I couldn't find a specific answer for that query. "
                 "Try asking about: **GDP growth, poverty, inflation, unemployment, M-Pesa, "
                 "counties, inequality, electricity, remittances, sector employment**, or **forecast**.")
    }


def _dark_layout(title: str, xtitle: str = "", ytitle: str = "") -> dict:
    return dict(
        title=dict(text=title, font=dict(color="white", size=15)),
        plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
        font=dict(color="white"), height=380,
        legend=dict(bgcolor="#1C2833", font=dict(color="white")),
        hovermode="x unified",
        xaxis=dict(gridcolor="#2C3E50", title=xtitle),
        yaxis=dict(gridcolor="#2C3E50", title=ytitle),
        margin=dict(l=40, r=20, t=50, b=40)
    )


def render(data: dict):
    # ── Compact header ────────────────────────────────────────────────
    st.markdown("""
    <div style='background: linear-gradient(135deg, #0D1B2A 0%, #1B2838 50%, #1C4E80 100%);
                padding: 1rem 1.5rem; border-radius: 12px; margin-bottom: 1.2rem;
                display:flex; align-items:center; gap:1rem;'>
        <div>
            <h2 style='color:white; margin:0; font-size:1.4rem;'>💬 Natural Language Query Engine</h2>
            <p style='color:#AED6F1; margin:.2rem 0 0; font-size:.85rem;'>
                Ask any question about Kenya's economy in plain English — get instant data-backed answers
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stakeholder context ───────────────────────────────────────────
    with st.expander("ℹ️ How to use this page", expanded=False):
        st.markdown("""
        **Who is this for?**
        Policy makers, investors, researchers, and journalists who need quick, accurate answers
        about Kenya's economy without writing code or navigating multiple dashboards.

        **How it works:**
        Type any plain-English question. The engine classifies your intent across 16 topic areas,
        queries the live datasets, and returns a written summary + interactive chart.

        **Supported topics:**
        GDP growth · Poverty · Inflation · Unemployment · Youth unemployment ·
        M-Pesa/Mobile money · Mobile penetration · Counties · Gini/Inequality ·
        Electricity access · Remittances · Sector employment · Economic forecasts ·
        Best/worst counties
        """)

    # ── Session state for question (enables button clicks) ────────────
    if "nlq_active_question" not in st.session_state:
        st.session_state["nlq_active_question"] = ""

    # ── Search bar ────────────────────────────────────────────────────
    typed = st.text_input(
        "🔍 Ask a question about Kenya's economy:",
        value=st.session_state["nlq_active_question"],
        placeholder="e.g. What is Kenya's poverty rate?  |  Which county is poorest?  |  Show M-Pesa growth",
        key="nlq_text_input"
    )
    # Sync typed input back to state
    if typed != st.session_state["nlq_active_question"]:
        st.session_state["nlq_active_question"] = typed

    # ── Example question buttons ──────────────────────────────────────
    st.markdown("<p style='color:#AAB7B8; font-size:.82rem; margin:.4rem 0 .2rem;'>💡 <b>Quick questions — click to try:</b></p>", unsafe_allow_html=True)

    # Row 1: first 5
    cols_r1 = st.columns(5)
    for i, (col, q) in enumerate(zip(cols_r1, EXAMPLE_QUESTIONS[:5])):
        label = q[:26] + "…" if len(q) > 26 else q
        if col.button(label, key=f"nlq_btn_{i}", use_container_width=True):
            st.session_state["nlq_active_question"] = q
            st.rerun()

    # Row 2: next 5
    cols_r2 = st.columns(5)
    for i, (col, q) in enumerate(zip(cols_r2, EXAMPLE_QUESTIONS[5:])):
        label = q[:26] + "…" if len(q) > 26 else q
        if col.button(label, key=f"nlq_btn_{i+5}", use_container_width=True):
            st.session_state["nlq_active_question"] = q
            st.rerun()

    st.markdown("<hr style='border-color:#2C3E50; margin:.6rem 0;'>", unsafe_allow_html=True)

    question = st.session_state["nlq_active_question"]

    if not question or question.strip() == "":
        st.markdown("""
        <div style='background:#1C2833; padding:1.5rem; border-radius:12px; text-align:center;'>
            <div style='font-size:2.5rem'>🇰🇪</div>
            <h3 style='color:#3498DB; margin:.4rem 0 .3rem'>Kenya Economic Intelligence</h3>
            <p style='color:#7F8C8D; font-size:.9rem; max-width:600px; margin:0 auto;'>
                Type a question above or click an example button to get instant, data-backed answers
                about Kenya's macro economy, 47 counties, M-Pesa, youth unemployment, and more.
            </p>
            <div style='display:flex; flex-wrap:wrap; gap:.5rem; justify-content:center; margin-top:1rem;'>
                <span style='background:#0E1117; color:#3498DB; padding:.3rem .8rem; border-radius:20px; font-size:.78rem; border:1px solid #2C3E50;'>📊 6 Datasets</span>
                <span style='background:#0E1117; color:#27AE60; padding:.3rem .8rem; border-radius:20px; font-size:.78rem; border:1px solid #2C3E50;'>🗺️ 47 Counties</span>
                <span style='background:#0E1117; color:#F39C12; padding:.3rem .8rem; border-radius:20px; font-size:.78rem; border:1px solid #2C3E50;'>🤖 16 Topics</span>
                <span style='background:#0E1117; color:#8E44AD; padding:.3rem .8rem; border-radius:20px; font-size:.78rem; border:1px solid #2C3E50;'>⚡ Instant Answers</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Classify and answer ───────────────────────────────────────────
    topic = _classify(question)
    with st.spinner("🧠 Analysing query..."):
        result = _answer(topic, data)

    # Answer box
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#0B3D6E,#1A5276); padding:1.2rem 1.5rem;
                border-radius:12px; border-left:4px solid #3498DB; margin-bottom:.8rem;'>
        <p style='color:#AED6F1; font-size:.75rem; margin:0 0 .3rem;'>
            🎯 Detected topic: <b style='color:white'>{topic.replace("_"," ").title()}</b>
        </p>
        <p style='color:white; font-size:1rem; margin:0; line-height:1.7;'>{result["text"]}</p>
    </div>
    """, unsafe_allow_html=True)

    if "fig" in result and result["fig"] is not None:
        st.plotly_chart(result["fig"], use_container_width=True)

    if "df" in result and result["df"] is not None:
        with st.expander("📋 View Data Table"):
            st.dataframe(result["df"], use_container_width=True)

    # ── Clear button ──────────────────────────────────────────────────
    col_clr, _ = st.columns([1, 4])
    if col_clr.button("🗑️ Clear / New Question", key="nlq_clear"):
        st.session_state["nlq_active_question"] = ""
        st.rerun()

    # ── History ───────────────────────────────────────────────────────
    if "nlq_history" not in st.session_state:
        st.session_state["nlq_history"] = []
    if question and question not in st.session_state["nlq_history"]:
        st.session_state["nlq_history"].insert(0, question)
        st.session_state["nlq_history"] = st.session_state["nlq_history"][:8]

    if len(st.session_state["nlq_history"]) > 1:
        with st.expander("📖 Recent Questions (click to reuse)"):
            for q in st.session_state["nlq_history"][1:]:
                if st.button(f"↩️ {q}", key=f"hist_{hash(q)}", use_container_width=True):
                    st.session_state["nlq_active_question"] = q
                    st.rerun()
