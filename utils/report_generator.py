"""
PDF + HTML Report Generator
Generates an executive summary report (PDF via ReportLab or HTML fallback).
Author: Stephen Muema
"""

import io
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepTogether
    )
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False


# ── Colour palette ────────────────────────────────────────────────────
NAVY      = colors.HexColor("#1B2631")
BLUE      = colors.HexColor("#2980B9")
TEAL      = colors.HexColor("#0E6655")
GREEN     = colors.HexColor("#1E8449")
RED       = colors.HexColor("#C0392B")
ORANGE    = colors.HexColor("#D35400")
LIGHT_BG  = colors.HexColor("#EBF5FB")
ALT_BG    = colors.HexColor("#D6EAF8")
GRID      = colors.HexColor("#AED6F1")
GREY_TXT  = colors.HexColor("#566573")
DARK_TEXT = colors.HexColor("#1C2833")
WHITE     = colors.white


def _safe_kpis(data: dict):
    """Extract KPI values safely."""
    macro = data.get("macro")
    mm    = data.get("mobile_money")
    yu    = data.get("youth_unemp")
    county = data.get("county")
    try:
        gdp_val  = float(macro["GDP Growth (%)"].dropna().iloc[-1])       if macro  is not None else 4.8
        inf_val  = float(macro["Inflation Rate (%)"].dropna().iloc[-1])   if macro  is not None else 7.8
        pov_val  = float(mm["Poverty_Rate_National"].iloc[-1])            if mm     is not None else 33.5
        yu_val   = float(yu["Youth_Unemployment_Pct"].iloc[-1])           if yu     is not None else 61.5
        mpesa_u  = float(mm["MPesa_Users_M"].iloc[-1])                    if mm     is not None else 41.0
        fin_inc  = float(mm["Financial_Inclusion_Pct"].iloc[-1])          if mm     is not None else 85.1
        remit    = float(mm["Remittances_B_USD"].iloc[-1])                if mm     is not None else 4.2
        unemp    = float(macro["Unemployment Rate (%)"].dropna().iloc[-1]) if macro is not None else 5.7
    except Exception:
        gdp_val, inf_val, pov_val, yu_val = 4.8, 7.8, 33.5, 61.5
        mpesa_u, fin_inc, remit, unemp    = 41.0, 85.1, 4.2, 5.7
    return dict(gdp_val=gdp_val, inf_val=inf_val, pov_val=pov_val,
                yu_val=yu_val, mpesa_u=mpesa_u, fin_inc=fin_inc,
                remit=remit, unemp=unemp)


def generate_executive_summary(data: dict) -> bytes:
    """
    Generate a PDF executive summary of Kenya Economic Pulse data.
    Returns PDF bytes.  Falls back to empty bytes if ReportLab missing.
    """
    if not REPORTLAB_OK:
        return b""

    kpi = _safe_kpis(data)
    now = datetime.now().strftime("%B %d, %Y")
    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=1.8*cm, bottomMargin=1.8*cm,
        title="Kenya Economic Pulse — Executive Summary",
        author="Stephen Muema"
    )

    styles = getSampleStyleSheet()

    # ── Custom styles ─────────────────────────────────────────────────
    title_s = ParagraphStyle("KEPTitle", parent=styles["Title"],
                             fontSize=22, textColor=NAVY,
                             spaceAfter=4, spaceBefore=0)
    sub_s   = ParagraphStyle("KEPSub",   parent=styles["Normal"],
                             fontSize=10, textColor=GREY_TXT,
                             spaceAfter=10)
    h2_s    = ParagraphStyle("KEPH2",    parent=styles["Heading2"],
                             fontSize=13, textColor=BLUE,
                             spaceBefore=12, spaceAfter=5,
                             borderPad=2)
    h3_s    = ParagraphStyle("KEPH3",    parent=styles["Heading3"],
                             fontSize=11, textColor=TEAL,
                             spaceBefore=8, spaceAfter=4)
    body_s  = ParagraphStyle("KEPBody",  parent=styles["BodyText"],
                             fontSize=9.5, leading=14,
                             textColor=DARK_TEXT)
    bullet_s = ParagraphStyle("KEPBullet", parent=body_s,
                              leftIndent=14, spaceAfter=4,
                              bulletIndent=4)
    footer_s = ParagraphStyle("KEPFoot", parent=styles["Normal"],
                              fontSize=7.5, textColor=GREY_TXT,
                              alignment=1)

    story = []

    # ══════════════════════════════════════════════════════════════════
    # HEADER BLOCK
    # ══════════════════════════════════════════════════════════════════
    # Title table with accent stripe
    hdr_data = [[
        Paragraph("<b>🇰🇪  Kenya Economic Pulse</b>", title_s),
        Paragraph(f"<i>Executive Summary</i><br/>Generated: {now}", sub_s)
    ]]
    hdr_tbl = Table(hdr_data, colWidths=[11*cm, 6*cm])
    hdr_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",    (0, 0), (-1, 0), WHITE),
        ("TOPPADDING",   (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING",(0, 0), (-1, 0), 10),
        ("LEFTPADDING",  (0, 0), (0, 0),  14),
        ("VALIGN",       (0, 0), (-1, 0), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,0),(0,0), [NAVY]),
    ]))
    story.append(hdr_tbl)
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE))
    story.append(Spacer(1, 0.3*cm))

    # ══════════════════════════════════════════════════════════════════
    # KPI DASHBOARD — 4-column grid
    # ══════════════════════════════════════════════════════════════════
    story.append(Paragraph("📊 Key Economic Indicators — 2023", h2_s))

    def kpi_cell(icon, label, value, status, color):
        return Paragraph(
            f"<b>{icon} {label}</b><br/>"
            f"<font size=14><b>{value}</b></font><br/>"
            f"<font color='{color}'>{status}</font>",
            ParagraphStyle("kc", parent=styles["Normal"],
                           fontSize=9, leading=13, alignment=1)
        )

    kpi_cells = [
        kpi_cell("📈", "GDP Growth",      f"{kpi['gdp_val']:.1f}%",
                 "▲ Positive" if kpi['gdp_val'] > 0 else "▼ Negative",
                 "#1E8449" if kpi['gdp_val'] > 0 else "#C0392B"),
        kpi_cell("💸", "Inflation",       f"{kpi['inf_val']:.1f}%",
                 "⚠ High" if kpi['inf_val'] > 7 else "✓ Moderate",
                 "#D35400" if kpi['inf_val'] > 7 else "#1E8449"),
        kpi_cell("🏚", "Poverty Rate",    f"{kpi['pov_val']:.1f}%",
                 "↓ Improving",  "#1E8449"),
        kpi_cell("👷", "Unemployment",   f"{kpi['unemp']:.1f}%",
                 "Stable",       "#2980B9"),
        kpi_cell("📱", "M-Pesa Users",   f"{kpi['mpesa_u']:.0f}M",
                 "✓ Strong",    "#1E8449"),
        kpi_cell("🏦", "Fin. Inclusion", f"{kpi['fin_inc']:.1f}%",
                 "✓ Excellent", "#1E8449"),
        kpi_cell("🎓", "Youth Unemp.",   f"{kpi['yu_val']:.1f}%",
                 "⚠ Critical",  "#C0392B"),
        kpi_cell("🌍", "Remittances",    f"${kpi['remit']:.1f}B",
                 "↑ Record",    "#1E8449"),
    ]
    # 4 per row
    kpi_rows = [kpi_cells[i:i+4] for i in range(0, len(kpi_cells), 4)]
    kpi_tbl = Table(kpi_rows, colWidths=[4.25*cm]*4, rowHeights=[2.4*cm]*len(kpi_rows))
    kpi_colors = [LIGHT_BG, ALT_BG]
    kpi_tbl.setStyle(TableStyle([
        ("GRID",          (0, 0), (-1, -1), 0.5, GRID),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [LIGHT_BG, ALT_BG]),
        ("ROUNDEDCORNERS",(0, 0), (-1, -1), 4),
    ]))
    story.append(kpi_tbl)
    story.append(Spacer(1, 0.4*cm))

    # ══════════════════════════════════════════════════════════════════
    # TWO COLUMN: Findings + County Snapshot
    # ══════════════════════════════════════════════════════════════════
    story.append(HRFlowable(width="100%", thickness=1, color=GRID))
    story.append(Spacer(1, 0.2*cm))

    findings = [
        "M-Pesa is Kenya's #1 poverty-reduction tool — ML Gradient Boosting R² = <b>0.904</b>.",
        "Financial inclusion rose from <b>26.4% (2006) → 85.1% (2023)</b> — a 58.7 pp improvement.",
        f"Youth unemployment ({kpi['yu_val']:.1f}%) is <b>4.5× the global average</b> of 13.6% (ILO).",
        "NE Kenya in crisis: Wajir (82%), Mandera (76%), Turkana (79%) poverty rates.",
        "47% of Kenyans lack electricity — off-grid solar is fastest rural solution.",
        f"Diaspora remittances (<b>${kpi['remit']:.1f}B</b>) exceed tea + tourism combined.",
    ]

    county_df = data.get("county")
    if county_df is not None:
        top3p  = county_df.nlargest(3, "Poverty_Rate")[["County", "Poverty_Rate"]].values.tolist()
        bot3p  = county_df.nsmallest(3, "Poverty_Rate")[["County", "Poverty_Rate"]].values.tolist()
        cty_rows = (
            [["County", "Poverty Rate"]] +
            [[f"⬆ {r[0]}", f"{r[1]:.1f}%"] for r in top3p] +
            [["—", "—"]] +
            [[f"⬇ {r[0]}", f"{r[1]:.1f}%"] for r in bot3p]
        )
    else:
        cty_rows = [["County", "Poverty Rate"], ["N/A", "N/A"]]

    cty_tbl = Table(cty_rows, colWidths=[5*cm, 2.5*cm])
    cty_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [LIGHT_BG, ALT_BG]),
        ("GRID",          (0, 0), (-1, -1), 0.5, GRID),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("TEXTCOLOR",     (0, 1), (0, 3), RED),
        ("TEXTCOLOR",     (0, 5), (0, 7), GREEN),
    ]))

    findings_block = [Paragraph("📌 Key Findings", h3_s)] + \
                     [Paragraph(f"• {f}", bullet_s) for f in findings]
    county_block   = [Paragraph("🗺️ County Snapshot", h3_s),
                      Paragraph("Top 3 vs Bottom 3 by Poverty Rate:", body_s),
                      Spacer(1, 0.15*cm),
                      cty_tbl]

    two_col = Table(
        [[findings_block, county_block]],
        colWidths=[11*cm, 7*cm]
    )
    two_col.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 12),
        ("LEFTPADDING",  (1, 0), (1, 0), 8),
    ]))
    story.append(two_col)
    story.append(Spacer(1, 0.3*cm))

    # ══════════════════════════════════════════════════════════════════
    # POLICY RECOMMENDATIONS
    # ══════════════════════════════════════════════════════════════════
    story.append(HRFlowable(width="100%", thickness=1, color=GRID))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("🏛️ Policy Recommendations", h2_s))

    recs = [
        ("📱 Expand Mobile Coverage",
         "Prioritise M-Pesa agent network rollout to NE counties (Wajir, Mandera, Turkana) "
         "where mobile penetration remains below 40%."),
        ("🎓 TVET & Digital Skills",
         "University enrollment is the top driver of youth unemployment. "
         "Scale Technical and Vocational Education and Training (TVET) programmes nationwide."),
        ("⚡ Rural Electrification",
         "Accelerate off-grid solar programmes. The national 100% electrification target requires "
         "25 additional percentage points by 2030."),
        ("💰 FDI in ICT & Green Energy",
         "Attract FDI into formal-sector ICT and renewable energy — both create high-quality "
         "youth employment and reduce carbon intensity."),
        ("⚖️ Progressive Redistribution",
         "Address Gini index of 40.8 through progressive tax reforms and "
         "targeted cash-transfer programmes for the bottom quintile."),
        ("🌍 Diaspora Remittances",
         f"Formalise and reduce costs of diaspora remittance channels to protect "
         f"the ${kpi['remit']:.1f}B annual inflow and maximise developmental impact."),
    ]

    rec_rows = []
    for icon_title, body in recs:
        rec_rows.append([
            Paragraph(f"<b>{icon_title}</b>", h3_s),
            Paragraph(body, body_s)
        ])
    rec_tbl = Table(rec_rows, colWidths=[4.5*cm, 12.5*cm])
    rec_tbl.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [LIGHT_BG, colors.white]),
        ("GRID",          (0, 0), (-1, -1), 0.4, GRID),
    ]))
    story.append(rec_tbl)
    story.append(Spacer(1, 0.4*cm))

    # ══════════════════════════════════════════════════════════════════
    # FOOTER
    # ══════════════════════════════════════════════════════════════════
    story.append(HRFlowable(width="100%", thickness=1, color=GRID))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "Kenya Economic Pulse  ·  Author: Stephen Muema, Data Scientist & ML Engineer  ·  "
        "muemastephenportfolio.netlify.app  ·  musyokas753@gmail.com  ·  "
        "Data: World Bank API · KNBS 2019 Census · CBK Annual Reports · ILO · FinAccess 2021",
        footer_s
    ))

    doc.build(story)
    return buf.getvalue()


def generate_html_summary(data: dict) -> str:
    """
    Fallback HTML report when ReportLab is unavailable.
    Returns an HTML string suitable for st.download_button.
    """
    kpi = _safe_kpis(data)
    now = datetime.now().strftime("%B %d, %Y")

    rows = [
        ("GDP Growth Rate",    f"{kpi['gdp_val']:.1f}%",  "Positive" if kpi['gdp_val'] > 0 else "Negative"),
        ("Inflation Rate",     f"{kpi['inf_val']:.1f}%",  "High" if kpi['inf_val'] > 7 else "Moderate"),
        ("Poverty Rate",       f"{kpi['pov_val']:.1f}%",  "Improving"),
        ("Unemployment",       f"{kpi['unemp']:.1f}%",    "Stable"),
        ("M-Pesa Users",       f"{kpi['mpesa_u']:.0f}M",  "Strong"),
        ("Financial Inclusion",f"{kpi['fin_inc']:.1f}%",  "Excellent"),
        ("Youth Unemployment", f"{kpi['yu_val']:.1f}%",   "Critical"),
        ("Remittances",        f"${kpi['remit']:.1f}B",   "Record High"),
    ]
    tr_html = "".join(
        f"<tr style='background:{'#EBF5FB' if i%2==0 else '#D6EAF8'}'>"
        f"<td>{r[0]}</td><td><b>{r[1]}</b></td><td>{r[2]}</td></tr>"
        for i, r in enumerate(rows)
    )

    return f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'>
<title>Kenya Economic Pulse — Executive Summary</title>
<style>
  body {{ font-family: Arial, sans-serif; max-width:900px; margin:2rem auto; color:#1C2833; }}
  h1   {{ color:#1B2631; border-bottom:3px solid #2980B9; padding-bottom:.5rem; }}
  h2   {{ color:#2980B9; margin-top:1.5rem; }}
  table{{ border-collapse:collapse; width:100%; margin:.8rem 0; }}
  th   {{ background:#1B4F72; color:white; padding:8px 12px; text-align:left; }}
  td   {{ padding:7px 12px; border:1px solid #AED6F1; }}
  .footer{{ font-size:.8rem; color:#7F8C8D; margin-top:2rem; border-top:1px solid #AED6F1; padding-top:.8rem; }}
  .rec  {{ background:#EBF5FB; border-left:4px solid #2980B9; padding:.6rem 1rem; margin:.5rem 0; border-radius:4px; }}
</style>
</head><body>
<h1>🇰🇪 Kenya Economic Pulse — Executive Summary</h1>
<p>Generated: {now} &nbsp;·&nbsp; Author: Stephen Muema</p>
<h2>📊 Key Economic Indicators (2023)</h2>
<table><tr><th>Indicator</th><th>Value</th><th>Status</th></tr>{tr_html}</table>
<h2>📌 Key Findings</h2>
<ul>
  <li>M-Pesa is Kenya's #1 poverty-reduction tool — ML model R² = <b>0.904</b></li>
  <li>Financial inclusion rose from <b>26.4% → 85.1%</b> (2006–2023)</li>
  <li>Youth unemployment ({kpi['yu_val']:.1f}%) is <b>4.5× the global average</b></li>
  <li>NE Kenya in crisis: Wajir (82%), Mandera (76%), Turkana (79%)</li>
  <li>47% of Kenyans lack electricity access</li>
  <li>Diaspora remittances (${kpi['remit']:.1f}B) exceed tea + tourism</li>
</ul>
<h2>🏛️ Policy Recommendations</h2>
<div class='rec'>📱 <b>Expand Mobile Coverage</b> — Roll out M-Pesa agents to NE counties below 40% mobile penetration</div>
<div class='rec'>🎓 <b>TVET &amp; Digital Skills</b> — Scale vocational training to address skills mismatch driving youth unemployment</div>
<div class='rec'>⚡ <b>Rural Electrification</b> — Accelerate off-grid solar to reach 100% electrification by 2030</div>
<div class='rec'>💰 <b>FDI in ICT &amp; Green Energy</b> — Attract investment in formal-sector jobs for youth</div>
<div class='rec'>⚖️ <b>Progressive Redistribution</b> — Address Gini 40.8 via targeted cash transfers and tax reform</div>
<div class='rec'>🌍 <b>Diaspora Remittances</b> — Formalise channels and reduce fees to protect the ${kpi['remit']:.1f}B inflow</div>
<p class='footer'>Kenya Economic Pulse · muemastephenportfolio.netlify.app · musyokas753@gmail.com · 
Data: World Bank API · KNBS 2019 Census · CBK Annual Reports · ILO · FinAccess 2021</p>
</body></html>"""
