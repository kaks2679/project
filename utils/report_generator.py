"""
PDF + HTML Executive Summary Report Generator
Kenya Economic Pulse — Stephen Muema, Data Scientist
"""

import io
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepTogether, Image
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.platypus.flowables import HRFlowable
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics import renderPDF
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False


# ── Brand colour palette ──────────────────────────────────────────────
NAVY        = colors.HexColor("#1B4F72")   # primary brand navy
NAVY_DARK   = colors.HexColor("#0D2635")   # deep navy for rule
BLUE        = colors.HexColor("#2980B9")   # accent blue
BLUE_LIGHT  = colors.HexColor("#5DADE2")   # light blue
TEAL        = colors.HexColor("#0E6655")   # teal accent
GREEN       = colors.HexColor("#1E8449")   # good/positive
GREEN_LIGHT = colors.HexColor("#27AE60")
RED         = colors.HexColor("#C0392B")   # bad/critical
ORANGE      = colors.HexColor("#D35400")   # warning
AMBER       = colors.HexColor("#F39C12")
LIGHT_BG    = colors.HexColor("#EBF5FB")   # row bg 1
ALT_BG      = colors.HexColor("#D6EAF8")   # row bg 2
RULE_COLOR  = colors.HexColor("#2980B9")   # horizontal rule
SECTION_BG  = colors.HexColor("#F2F9FF")   # section shading
GREY_LIGHT  = colors.HexColor("#BDC3C7")
GREY_TXT    = colors.HexColor("#566573")
DARK_TEXT   = colors.HexColor("#1C2833")
WHITE       = colors.white
OFF_WHITE   = colors.HexColor("#FAFAFA")


def _safe_kpis(data: dict) -> dict:
    """Extract KPI values safely with fallbacks."""
    macro  = data.get("macro")
    mm     = data.get("mobile_money")
    yu     = data.get("youth_unemp")
    try:
        gdp_val = float(macro["GDP Growth (%)"].dropna().iloc[-1])          if macro is not None else 4.8
        inf_val = float(macro["Inflation Rate (%)"].dropna().iloc[-1])      if macro is not None else 7.8
        unemp   = float(macro["Unemployment Rate (%)"].dropna().iloc[-1])   if macro is not None else 5.7
        gini    = float(macro["Gini Index (Inequality)"].dropna().iloc[-1]) if macro is not None else 40.8
    except Exception:
        gdp_val, inf_val, unemp, gini = 4.8, 7.8, 5.7, 40.8
    try:
        pov_val = float(mm["Poverty_Rate_National"].iloc[-1])   if mm is not None else 33.5
        mpesa_u = float(mm["MPesa_Users_M"].iloc[-1])           if mm is not None else 41.0
        fin_inc = float(mm["Financial_Inclusion_Pct"].iloc[-1]) if mm is not None else 85.1
        remit   = float(mm["Remittances_B_USD"].iloc[-1])       if mm is not None else 4.2
    except Exception:
        pov_val, mpesa_u, fin_inc, remit = 33.5, 41.0, 85.1, 4.2
    try:
        yu_val  = float(yu["Youth_Unemployment_Pct"].iloc[-1])  if yu is not None else 61.5
    except Exception:
        yu_val = 61.5
    return dict(gdp_val=gdp_val, inf_val=inf_val, unemp=unemp, gini=gini,
                pov_val=pov_val, mpesa_u=mpesa_u, fin_inc=fin_inc,
                remit=remit, yu_val=yu_val)


def _logo_squares(size: float = 11) -> Drawing:
    """Render two navy squares — the Kenya Economic Pulse logo mark."""
    gap   = size * 0.3
    total = size * 2 + gap
    d = Drawing(total, size)
    for x in (0, size + gap):
        r = Rect(x, 0, size, size, fillColor=NAVY, strokeColor=None)
        d.add(r)
    return d


def generate_executive_summary(data: dict) -> bytes:
    """
    Generate a polished PDF executive summary.
    Header matches the reference design: centered logo squares + title + subtitle + rule.
    """
    if not REPORTLAB_OK:
        return b""

    kpi = _safe_kpis(data)
    now_full  = datetime.now().strftime("%d %B %Y")
    now_short = datetime.now().strftime("%Y%m%d")

    buf = io.BytesIO()
    PAGE_W, PAGE_H = A4
    LEFT = RIGHT = 2.2 * cm
    TOP  = 2 * cm
    BOT  = 1.8 * cm

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=LEFT, rightMargin=RIGHT,
        topMargin=TOP, bottomMargin=BOT,
        title="Kenya Economic Pulse — Executive Summary",
        author="Stephen Muema, Data Scientist",
        subject="Kenya Economic Analysis 2023",
    )

    CONTENT_W = PAGE_W - LEFT - RIGHT   # ≈ 17.1 cm
    styles = getSampleStyleSheet()

    # ── Define all paragraph styles once ─────────────────────────────
    def _ps(name, **kw):
        return ParagraphStyle(name, parent=styles["Normal"], **kw)

    # Cover title styles
    cover_title = _ps("CoverTitle",
                      fontName="Helvetica-Bold", fontSize=24,
                      textColor=NAVY, alignment=TA_CENTER,
                      spaceBefore=0, spaceAfter=4, leading=28)
    cover_sub   = _ps("CoverSub",
                      fontName="Helvetica", fontSize=11,
                      textColor=GREY_TXT, alignment=TA_CENTER,
                      spaceAfter=4, leading=15)
    cover_meta  = _ps("CoverMeta",
                      fontName="Helvetica", fontSize=9,
                      textColor=GREY_TXT, alignment=TA_CENTER,
                      spaceAfter=0, leading=13)

    # Section heading
    h2_s = _ps("H2s",
               fontName="Helvetica-Bold", fontSize=12,
               textColor=NAVY, spaceBefore=10, spaceAfter=5,
               leftIndent=0, borderPad=0,
               backColor=None)
    h3_s = _ps("H3s",
               fontName="Helvetica-Bold", fontSize=10,
               textColor=BLUE, spaceBefore=6, spaceAfter=3)
    h3_teal = _ps("H3t",
                  fontName="Helvetica-Bold", fontSize=10,
                  textColor=TEAL, spaceBefore=6, spaceAfter=3)

    # Body
    body_s = _ps("Bodys",
                 fontName="Helvetica", fontSize=9,
                 textColor=DARK_TEXT, leading=14)
    bullet_s = _ps("Bullets",
                   fontName="Helvetica", fontSize=9,
                   textColor=DARK_TEXT, leading=14,
                   leftIndent=12, spaceAfter=3)
    small_s = _ps("Smalls",
                  fontName="Helvetica", fontSize=8,
                  textColor=GREY_TXT, leading=11)
    footer_s = _ps("Footers",
                   fontName="Helvetica", fontSize=7.5,
                   textColor=GREY_TXT, alignment=TA_CENTER, leading=11)

    # KPI cell style
    kpi_label_s = _ps("KPILabel",
                      fontName="Helvetica", fontSize=8,
                      textColor=GREY_TXT, alignment=TA_CENTER, leading=10)
    kpi_value_s = _ps("KPIValue",
                      fontName="Helvetica-Bold", fontSize=16,
                      textColor=NAVY, alignment=TA_CENTER, leading=19)
    kpi_status_s = _ps("KPIStat",
                       fontName="Helvetica-Oblique", fontSize=8,
                       alignment=TA_CENTER, leading=10)

    story = []

    # ══════════════════════════════════════════════════════════════════
    # ① COVER HEADER — exactly like the reference PDF
    #    [logo squares]  Kenya Economic Pulse  (centered block)
    #    Executive Summary Report
    #    Generated: DD Month YYYY | Prepared by: Stephen Muema, Data Scientist
    #    ─────────────────────────────────────────────────────────── (blue rule)
    # ══════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 0.6 * cm))

    # Logo mark row (two navy squares, centered via 3-col table)
    logo = _logo_squares(10)
    logo_row = Table([[logo]], colWidths=[CONTENT_W])
    logo_row.setStyle(TableStyle([
        ("ALIGN",  (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(logo_row)
    story.append(Spacer(1, 0.3 * cm))

    # Main title
    story.append(Paragraph("Kenya Economic Pulse", cover_title))
    story.append(Paragraph("Executive Summary Report", cover_sub))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        f"Generated: {now_full}&nbsp;&nbsp;|&nbsp;&nbsp;"
        "Prepared by: Stephen Muema, Data Scientist",
        cover_meta
    ))
    story.append(Spacer(1, 0.5 * cm))

    # Blue horizontal rule (full width, 1.5 pt, matching reference)
    story.append(HRFlowable(width="100%", thickness=1.5,
                            color=RULE_COLOR, spaceAfter=10))
    story.append(Spacer(1, 0.1 * cm))

    # ══════════════════════════════════════════════════════════════════
    # ② SECTION HEADER HELPER
    # ══════════════════════════════════════════════════════════════════
    def section_header(text: str) -> list:
        """Returns a compact navy-accent section heading with thin rule."""
        return [
            Paragraph(text, h2_s),
            HRFlowable(width="100%", thickness=0.6, color=BLUE_LIGHT, spaceAfter=4),
        ]

    # ══════════════════════════════════════════════════════════════════
    # ③ KPI DASHBOARD — 4-column × 2-row card grid
    # ══════════════════════════════════════════════════════════════════
    for fl in section_header("1. Kenya at a Glance — 2023 Snapshot"):
        story.append(fl)

    def _status_color(flag: str) -> colors.Color:
        lf = flag.lower()
        if any(w in lf for w in ("good", "strong", "excellent", "record", "improving", "positive", "growing")):
            return GREEN
        if any(w in lf for w in ("critical", "high", "stuck", "warn", "watch")):
            return RED
        if any(w in lf for w in ("easing", "moderate", "stable", "stagnant")):
            return AMBER
        return GREY_TXT

    def _kpi_card(label: str, value: str, trend: str, status: str) -> list:
        sc = _status_color(status)
        status_style = ParagraphStyle(
            f"st_{label}", parent=kpi_status_s, textColor=sc)
        trend_style  = ParagraphStyle(
            f"tr_{label}", parent=small_s, alignment=TA_CENTER, textColor=BLUE)
        return [
            Paragraph(label,  kpi_label_s),
            Paragraph(value,  kpi_value_s),
            Paragraph(trend,  trend_style),
            Paragraph(status, status_style),
        ]

    kpi_items = [
        ("GDP Growth",        f"{kpi['gdp_val']:.1f}%",
         "› Stable",          "Good" if kpi['gdp_val'] > 3 else "Watch"),
        ("Inflation Rate",    f"{kpi['inf_val']:.1f}%",
         "↓ Easing",          "High" if kpi['inf_val'] > 7 else "Good"),
        ("National Poverty",  f"{kpi['pov_val']:.1f}%",
         "↓ Improving",       "High"),
        ("Youth Unemployment",f"{kpi['yu_val']:.1f}%",
         "→ Stuck",           "Critical"),
        ("M-Pesa Users",      f"{kpi['mpesa_u']:.0f}M+",
         "› Growing",         "Good"),
        ("Financial Inclusion",f"{kpi['fin_inc']:.1f}%",
         "› Growing",         "Excellent"),
        ("Remittances",       f"USD {kpi['remit']:.1f}B",
         "› Record",          "Good"),
        ("Gini Index",        f"{kpi['gini']:.1f}",
         "→ Stagnant",        "High"),
    ]

    CARD_W = CONTENT_W / 4
    kpi_rows_data = []
    for i in range(0, len(kpi_items), 4):
        row_cells = []
        for label, value, trend, status in kpi_items[i:i+4]:
            row_cells.append(_kpi_card(label, value, trend, status))
        kpi_rows_data.append(row_cells)

    kpi_tbl = Table(kpi_rows_data, colWidths=[CARD_W] * 4,
                    rowHeights=[2.6 * cm] * len(kpi_rows_data))
    kpi_style = [
        ("GRID",          (0, 0), (-1, -1), 0.5, GREY_LIGHT),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [OFF_WHITE, LIGHT_BG]),
        # Top accent line per cell — navy stripe on top
        ("LINEABOVE",     (0, 0), (-1, 0),  2, NAVY),
        ("LINEABOVE",     (0, 1), (-1, 1),  2, NAVY),
    ]
    kpi_tbl.setStyle(TableStyle(kpi_style))
    story.append(kpi_tbl)
    story.append(Spacer(1, 0.4 * cm))

    # ══════════════════════════════════════════════════════════════════
    # ④ ML FINDINGS — two-column: bullet findings | county snapshot
    # ══════════════════════════════════════════════════════════════════
    for fl in section_header("2. Machine Learning Findings"):
        story.append(fl)

    ml_intro = (
        "The following findings are derived from Gradient Boosting and Random Forest models "
        "trained on 17 years of Kenya economic data (2007–2023):"
    )
    story.append(Paragraph(ml_intro, body_s))
    story.append(Spacer(1, 0.2 * cm))

    findings_ml = [
        ("<b>Mobile Money is the #1 poverty lever</b> — "
         "M-Pesa user growth explains <b>90.4%</b> of national poverty variance (R²=0.904, GBM model)."),
        ("<b>Financial inclusion 26.4% → 85.1%</b> (2006–2023) — "
         "a 58.7 pp improvement. Kenya leads Sub-Saharan Africa."),
        (f"<b>Youth unemployment ({kpi['yu_val']:.1f}%)</b> is 4.5× the global average (ILO 13.6%). "
         "TVET investment is the fastest lever."),
        ("<b>NE Kenya in crisis</b> — Wajir 82%, Turkana 79%, Mandera 76% poverty. "
         "Requires emergency county-level transfers."),
        ("<b>47% lack electricity</b> — off-grid solar deployment is the fastest "
         "path to 100% by 2030."),
        (f"<b>Remittances (${kpi['remit']:.1f}B)</b> now exceed tea + tourism as "
         "Kenya's largest forex earner."),
    ]

    # County snapshot table
    county_df = data.get("county")
    if county_df is not None:
        top3  = county_df.nlargest(3,  "Poverty_Rate")[["County", "Poverty_Rate"]].values.tolist()
        bot3  = county_df.nsmallest(3, "Poverty_Rate")[["County", "Poverty_Rate"]].values.tolist()
        c_rows = (
            [["County", "Poverty Rate", "Status"]] +
            [[r[0], f"{r[1]:.1f}%", "Most Deprived"] for r in top3] +
            [["—", "—", "—"]] +
            [[r[0], f"{r[1]:.1f}%", "Best Performing"] for r in bot3]
        )
    else:
        c_rows = [["County", "Poverty Rate", "Status"], ["N/A", "N/A", "N/A"]]

    cty_tbl = Table(c_rows, colWidths=[3.5*cm, 2.5*cm, 3.2*cm])
    cty_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [LIGHT_BG, ALT_BG]),
        ("GRID",          (0, 0), (-1, -1), 0.4, GREY_LIGHT),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        # colour for top-3 and bottom-3 county name cells
        ("TEXTCOLOR",     (0, 1), (0, 3),  RED),
        ("TEXTCOLOR",     (0, 5), (0, 7),  GREEN),
    ]))

    find_block = (
        [Paragraph(f"• {f}", bullet_s) for f in findings_ml]
    )
    cty_block  = [
        Paragraph("County Poverty Snapshot", h3_teal),
        Spacer(1, 0.1*cm),
        cty_tbl,
    ]

    two_col = Table(
        [[find_block, cty_block]],
        colWidths=[CONTENT_W * 0.57, CONTENT_W * 0.43]
    )
    two_col.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (0, 0),   0),
        ("RIGHTPADDING", (0, 0), (0, 0),   10),
        ("LEFTPADDING",  (1, 0), (1, 0),   8),
    ]))
    story.append(two_col)
    story.append(Spacer(1, 0.35 * cm))

    # ══════════════════════════════════════════════════════════════════
    # ⑤ POLICY RECOMMENDATIONS
    # ══════════════════════════════════════════════════════════════════
    for fl in section_header("3. Policy Recommendations"):
        story.append(fl)

    recs = [
        ("Expand Mobile Financial Services",
         "Roll out M-Pesa agent network to NE counties (Wajir, Mandera, Turkana) "
         "where mobile penetration is below 40%. Each 10 pp gain reduces poverty ~2 pp."),
        ("Scale TVET & Digital Skills",
         "University over-enrollment drives youth unemployment. Redirect 1% GDP to TVET — "
         "projected to reduce youth unemployment by 4–6 pp by 2028."),
        ("Accelerate Rural Electrification",
         "Deploy off-grid solar at scale. The national 100% electrification target requires "
         "an additional 25 pp in 8 years — achievable with public-private solar partnerships."),
        ("Attract ICT & Green Energy FDI",
         "Both sectors create high-quality formal jobs for youth. Target FDI 1.5% of GDP "
         "(current 0.5%). Tax incentives for ICT parks in Tier-4 and Tier-5 counties."),
        ("Progressive Fiscal Redistribution",
         "Gini index of 40.8 requires structural tax reform: progressive income tax, "
         "VAT exemptions on basic goods, and expanded cash-transfer programmes."),
        ("Formalise Diaspora Remittances",
         f"Reduce transfer fees from ~8% to <3% on ${kpi['remit']:.1f}B annual inflow. "
         "Formalisation and diaspora bonds could unlock an additional $1B+ in development finance."),
    ]

    REC_ICON_W = 0.7 * cm
    REC_BODY_W = CONTENT_W - REC_ICON_W - 0.3 * cm

    tag_colors = [NAVY, BLUE, TEAL, GREEN, AMBER, RED]
    rec_rows = []
    for i, (title, body) in enumerate(recs):
        tag_bg   = tag_colors[i % len(tag_colors)]
        tag_cell = Paragraph(
            f"<b>{i+1}</b>",
            _ps(f"rcn_{i}", fontName="Helvetica-Bold", fontSize=9,
                textColor=WHITE, alignment=TA_CENTER)
        )
        body_cell = [
            Paragraph(f"<b>{title}</b>",
                      ParagraphStyle(f"rct_{i}", fontName="Helvetica-Bold", fontSize=9,
                                     textColor=NAVY, spaceAfter=2, leading=12)),
            Paragraph(body, ParagraphStyle(f"rcb_{i}", parent=body_s, spaceAfter=0)),
        ]
        rec_rows.append([tag_cell, body_cell])

    rec_tbl = Table(rec_rows, colWidths=[REC_ICON_W, REC_BODY_W])
    rec_style = [
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (0, -1),  4),
        ("RIGHTPADDING",  (0, 0), (0, -1),  4),
        ("LEFTPADDING",   (1, 0), (1, -1),  8),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [LIGHT_BG, OFF_WHITE]),
        ("GRID",          (0, 0), (-1, -1), 0.3, GREY_LIGHT),
    ]
    # Add numbered-tag background per row
    for i, (_, _) in enumerate(recs):
        rec_style.append(("BACKGROUND", (0, i), (0, i), tag_colors[i % len(tag_colors)]))
    rec_tbl.setStyle(TableStyle(rec_style))
    story.append(rec_tbl)
    story.append(Spacer(1, 0.45 * cm))

    # ══════════════════════════════════════════════════════════════════
    # ⑥ FOOTER — rule + credits
    # ══════════════════════════════════════════════════════════════════
    story.append(HRFlowable(width="100%", thickness=0.8, color=RULE_COLOR, spaceAfter=6))
    story.append(Paragraph(
        "<b>Kenya Economic Pulse</b>  ·  Stephen Muema, Data Scientist &amp; ML Engineer  ·  "
        "muemastephenportfolio.netlify.app  ·  musyokas753@gmail.com",
        footer_s
    ))
    story.append(Spacer(1, 0.1 * cm))
    story.append(Paragraph(
        "Data Sources: World Bank Open API  ·  KNBS 2019 Census  ·  CBK Annual Reports  ·  "
        "ILO Labour Statistics  ·  FinAccess Survey 2021  ·  KIHBS 2021",
        footer_s
    ))

    doc.build(story)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════
# HTML FALLBACK — styled to match the same brand identity
# ══════════════════════════════════════════════════════════════════════

def generate_html_summary(data: dict) -> str:
    """
    Polished HTML report — same brand identity as the PDF.
    Works without ReportLab. Open in any browser or email client.
    """
    kpi = _safe_kpis(data)
    now = datetime.now().strftime("%d %B %Y")

    def status_badge(text: str, good: bool | None = None) -> str:
        if good is True:
            bg, fg = "#D5F5E3", "#1E8449"
        elif good is False:
            bg, fg = "#FDEDEC", "#C0392B"
        else:
            bg, fg = "#FEF9E7", "#D35400"
        return (f"<span style='background:{bg}; color:{fg}; padding:2px 8px; "
                f"border-radius:12px; font-size:.8rem; font-weight:600;'>{text}</span>")

    kpi_cards = [
        ("GDP Growth",         f"{kpi['gdp_val']:.1f}%",  "› Stable",
         status_badge("Good" if kpi['gdp_val'] > 3 else "Watch",
                      kpi['gdp_val'] > 3)),
        ("Inflation Rate",     f"{kpi['inf_val']:.1f}%",  "↓ Easing",
         status_badge("High" if kpi['inf_val'] > 7 else "Moderate",
                      kpi['inf_val'] <= 7)),
        ("Poverty Rate",       f"{kpi['pov_val']:.1f}%",  "↓ Improving",
         status_badge("High", False)),
        ("Youth Unemployment", f"{kpi['yu_val']:.1f}%",   "→ Stuck",
         status_badge("Critical", False)),
        ("M-Pesa Users",       f"{kpi['mpesa_u']:.0f}M+", "› Growing",
         status_badge("Good", True)),
        ("Financial Inclusion",f"{kpi['fin_inc']:.1f}%",  "› Growing",
         status_badge("Excellent", True)),
        ("Remittances",        f"USD {kpi['remit']:.1f}B","› Record",
         status_badge("Good", True)),
        ("Gini Index",         f"{kpi['gini']:.1f}",      "→ Stagnant",
         status_badge("High", False)),
    ]

    cards_html = ""
    for label, value, trend, badge in kpi_cards:
        cards_html += f"""
        <div class='kpi-card'>
            <div class='kpi-label'>{label}</div>
            <div class='kpi-value'>{value}</div>
            <div class='kpi-trend'>{trend}</div>
            <div style='margin-top:4px'>{badge}</div>
        </div>"""

    recs_list = [
        ("Expand Mobile Financial Services",
         f"Roll out M-Pesa agent network to NE counties where mobile penetration &lt;40%. "
         "Each 10 pp gain reduces poverty ~2 pp."),
        ("Scale TVET &amp; Digital Skills",
         "Redirect 1% GDP to vocational training — projected to cut youth unemployment 4–6 pp by 2028."),
        ("Accelerate Rural Electrification",
         "Deploy off-grid solar to close the 25 pp gap to 100% electrification by 2030."),
        ("Attract ICT &amp; Green Energy FDI",
         "Target FDI of 1.5% GDP (from 0.5%). Tax incentives for ICT parks in lagging counties."),
        ("Progressive Fiscal Redistribution",
         "Reform income tax, extend VAT exemptions on basics, expand cash-transfer programmes."),
        ("Formalise Diaspora Remittances",
         f"Reduce transfer fees &lt;3% on ${kpi['remit']:.1f}B inflow. Diaspora bonds could unlock $1B+ more."),
    ]
    recs_html = "".join(
        f"<div class='rec'><span class='rec-num'>{i+1}</span>"
        f"<div><b>{t}</b><br/><span style='color:#566573;font-size:.88rem'>{b}</span></div></div>"
        for i, (t, b) in enumerate(recs_list)
    )

    return f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>Kenya Economic Pulse — Executive Summary</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Segoe UI', Arial, sans-serif;
    background: #f5f7fa;
    color: #1C2833;
    padding: 2rem 1rem;
  }}
  .page {{
    max-width: 900px;
    margin: 0 auto;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 20px rgba(0,0,0,.08);
    overflow: hidden;
  }}

  /* ── HEADER ── */
  .header {{
    padding: 2.5rem 2rem 1.5rem;
    text-align: center;
    background: white;
    border-bottom: 2px solid #2980B9;
  }}
  .logo-squares {{
    display: inline-flex;
    gap: 4px;
    margin-bottom: .8rem;
  }}
  .logo-sq {{
    width: 14px; height: 14px;
    background: #1B4F72;
    border-radius: 1px;
  }}
  .header h1 {{
    font-size: 1.9rem;
    font-weight: 700;
    color: #1B4F72;
    letter-spacing: -.3px;
    margin-bottom: .25rem;
  }}
  .header .subtitle {{
    font-size: 1rem;
    color: #566573;
    margin-bottom: .35rem;
  }}
  .header .meta {{
    font-size: .83rem;
    color: #7F8C8D;
  }}

  /* ── CONTENT ── */
  .content {{ padding: 1.5rem 2rem; }}

  /* ── SECTION ── */
  .section {{ margin-bottom: 1.6rem; }}
  .section-title {{
    font-size: 1rem;
    font-weight: 700;
    color: #1B4F72;
    padding: .35rem 0 .35rem 0;
    border-bottom: 1.5px solid #5DADE2;
    margin-bottom: .9rem;
  }}

  /* ── KPI CARDS ── */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: .6rem;
    margin-bottom: 1rem;
  }}
  .kpi-card {{
    background: #FAFAFA;
    border: 1px solid #D5D8DC;
    border-top: 3px solid #1B4F72;
    border-radius: 4px;
    padding: .7rem .5rem;
    text-align: center;
  }}
  .kpi-label  {{ font-size: .73rem; color: #7F8C8D; margin-bottom: .25rem; }}
  .kpi-value  {{ font-size: 1.3rem; font-weight: 700; color: #1B4F72; margin-bottom: .15rem; }}
  .kpi-trend  {{ font-size: .75rem; color: #2980B9; font-style: italic; }}

  /* ── ML FINDINGS ── */
  .two-col {{ display: grid; grid-template-columns: 1fr .72fr; gap: 1.2rem; }}
  .findings ul {{ padding-left: 1.1rem; }}
  .findings li {{ font-size: .9rem; line-height: 1.65; margin-bottom: .4rem; color: #1C2833; }}

  /* ── COUNTY TABLE ── */
  .cty-table {{ width: 100%; border-collapse: collapse; font-size: .83rem; }}
  .cty-table th {{ background: #1B4F72; color: white; padding: 6px 10px; text-align:left; }}
  .cty-table td {{ padding: 5px 10px; border: 1px solid #D5D8DC; }}
  .cty-table tr:nth-child(even) td {{ background: #EBF5FB; }}
  .red  {{ color: #C0392B; font-weight:600; }}
  .green{{ color: #1E8449; font-weight:600; }}

  /* ── RECOMMENDATIONS ── */
  .rec {{
    display: flex;
    gap: .8rem;
    align-items: flex-start;
    padding: .65rem .8rem;
    margin-bottom: .4rem;
    border-radius: 4px;
    background: #F2F9FF;
    border: 1px solid #D6EAF8;
  }}
  .rec-num {{
    min-width: 22px; height: 22px;
    background: #1B4F72; color: white;
    border-radius: 50%;
    font-size: .8rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }}

  /* ── FOOTER ── */
  .footer {{
    background: #F2F9FF;
    border-top: 1px solid #D6EAF8;
    padding: .9rem 2rem;
    font-size: .75rem;
    color: #7F8C8D;
    text-align: center;
    line-height: 1.7;
  }}
  .footer a {{ color: #2980B9; text-decoration: none; }}

  @media(max-width:600px) {{
    .kpi-grid {{ grid-template-columns: repeat(2,1fr); }}
    .two-col  {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
<div class='page'>

  <!-- HEADER -->
  <div class='header'>
    <div class='logo-squares'>
      <div class='logo-sq'></div>
      <div class='logo-sq'></div>
    </div>
    <h1>Kenya Economic Pulse</h1>
    <div class='subtitle'>Executive Summary Report</div>
    <div class='meta'>Generated: {now}&nbsp;&nbsp;|&nbsp;&nbsp;Prepared by: Stephen Muema, Data Scientist</div>
  </div>

  <div class='content'>

    <!-- KPI SECTION -->
    <div class='section'>
      <div class='section-title'>1. Kenya at a Glance — 2023 Snapshot</div>
      <div class='kpi-grid'>{cards_html}</div>
    </div>

    <!-- ML FINDINGS + COUNTY SNAPSHOT -->
    <div class='section'>
      <div class='section-title'>2. Machine Learning Findings</div>
      <p style='font-size:.88rem; color:#566573; margin-bottom:.7rem;'>
        Derived from Gradient Boosting and Random Forest models trained on 17 years of Kenya data (2007–2023):
      </p>
      <div class='two-col'>
        <div class='findings'>
          <ul>
            <li><b>Mobile Money is the #1 poverty lever</b> — M-Pesa explains <b>90.4%</b> of national poverty variance (R²=0.904).</li>
            <li><b>Financial inclusion 26.4% → 85.1%</b> (2006–2023) — Kenya leads Sub-Saharan Africa.</li>
            <li><b>Youth unemployment ({kpi['yu_val']:.1f}%)</b> is 4.5× the global average. TVET is the fastest fix.</li>
            <li><b>NE Kenya in crisis</b> — Wajir 82%, Turkana 79%, Mandera 76% poverty.</li>
            <li><b>47% lack electricity</b> — off-grid solar is fastest path to 100% by 2030.</li>
            <li><b>Remittances (${kpi['remit']:.1f}B)</b> now exceed tea + tourism as Kenya's top forex earner.</li>
          </ul>
        </div>
        <div>
          <p style='font-size:.83rem; font-weight:600; color:#0E6655; margin-bottom:.5rem;'>County Poverty Snapshot</p>
          <table class='cty-table'>
            <tr><th>County</th><th>Poverty Rate</th><th>Status</th></tr>
            {"".join(f"<tr><td class='red'>{r[0]}</td><td>{r[1]:.1f}%</td><td>Most Deprived</td></tr>" for r in (data.get('county').nlargest(3,'Poverty_Rate')[['County','Poverty_Rate']].values.tolist() if data.get('county') is not None else []))}
            <tr><td colspan='3' style='text-align:center;color:#AAB7B8;'>— — —</td></tr>
            {"".join(f"<tr><td class='green'>{r[0]}</td><td>{r[1]:.1f}%</td><td>Best Performing</td></tr>" for r in (data.get('county').nsmallest(3,'Poverty_Rate')[['County','Poverty_Rate']].values.tolist() if data.get('county') is not None else []))}
          </table>
        </div>
      </div>
    </div>

    <!-- RECOMMENDATIONS -->
    <div class='section'>
      <div class='section-title'>3. Policy Recommendations</div>
      {recs_html}
    </div>

  </div><!-- /content -->

  <!-- FOOTER -->
  <div class='footer'>
    <b>Kenya Economic Pulse</b> &nbsp;·&nbsp; Stephen Muema, Data Scientist &amp; ML Engineer &nbsp;·&nbsp;
    <a href='https://muemastephenportfolio.netlify.app/'>muemastephenportfolio.netlify.app</a>
    &nbsp;·&nbsp; musyokas753@gmail.com<br>
    Data: World Bank Open API &nbsp;·&nbsp; KNBS 2019 Census &nbsp;·&nbsp; CBK Annual Reports
    &nbsp;·&nbsp; ILO Labour Statistics &nbsp;·&nbsp; FinAccess Survey 2021 &nbsp;·&nbsp; KIHBS 2021
  </div>

</div>
</body></html>"""
