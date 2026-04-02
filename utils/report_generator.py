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
        HRFlowable, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus.flowables import HRFlowable
    from reportlab.graphics.shapes import Drawing, Rect, Line, String
    from reportlab.graphics import renderPDF
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False


# ── Brand colour palette ──────────────────────────────────────────────
NAVY        = colors.HexColor("#1B4F72")   # primary brand navy
NAVY_DARK   = colors.HexColor("#0D2635")   # deep navy
BLUE        = colors.HexColor("#2980B9")   # accent blue
BLUE_LIGHT  = colors.HexColor("#AED6F1")   # light blue tint
TEAL        = colors.HexColor("#0E6655")   # teal accent
GREEN       = colors.HexColor("#1E8449")   # positive
GREEN_LIGHT = colors.HexColor("#27AE60")
RED         = colors.HexColor("#C0392B")   # critical
ORANGE      = colors.HexColor("#D35400")   # warning
AMBER       = colors.HexColor("#F39C12")
LIGHT_BG    = colors.HexColor("#EBF5FB")   # row alternating
ALT_BG      = colors.HexColor("#D6EAF8")
RULE_COLOR  = colors.HexColor("#2980B9")   # horizontal rule
SECTION_BG  = colors.HexColor("#F8FBFF")   # section shading
GREY_LIGHT  = colors.HexColor("#D5D8DC")
GREY_TXT    = colors.HexColor("#566573")
DARK_TEXT   = colors.HexColor("#1C2833")
WHITE       = colors.white
OFF_WHITE   = colors.HexColor("#FAFAFA")
HEADER_BG   = colors.HexColor("#F0F7FF")   # very pale blue header bg


def _safe_kpis(data: dict) -> dict:
    """Extract KPI values safely with fallbacks."""
    macro = data.get("macro")
    mm    = data.get("mobile_money")
    yu    = data.get("youth_unemp")
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
        yu_val = float(yu["Youth_Unemployment_Pct"].iloc[-1])   if yu is not None else 61.5
    except Exception:
        yu_val = 61.5
    return dict(gdp_val=gdp_val, inf_val=inf_val, unemp=unemp, gini=gini,
                pov_val=pov_val, mpesa_u=mpesa_u, fin_inc=fin_inc,
                remit=remit, yu_val=yu_val)


def _logo_mark(sq: float = 10) -> Drawing:
    """
    Two filled navy squares side-by-side — the Kenya Economic Pulse logo mark.
    Rendered as a small inline Drawing to sit left of the title.
    """
    gap   = sq * 0.35
    total = sq * 2 + gap
    d = Drawing(total, sq)
    d.add(Rect(0,           0, sq, sq, fillColor=NAVY, strokeColor=None))
    d.add(Rect(sq + gap,    0, sq, sq, fillColor=BLUE, strokeColor=None))
    return d


def generate_executive_summary(data: dict) -> bytes:
    """
    Generate a polished PDF executive summary.
    Header: inline logo-mark + bold title (matching reference design).
    """
    if not REPORTLAB_OK:
        return b""

    kpi      = _safe_kpis(data)
    now_full = datetime.now().strftime("%d %B %Y")

    buf     = io.BytesIO()
    PAGE_W, PAGE_H = A4
    LEFT    = RIGHT = 2.0 * cm
    TOP     = 1.8 * cm
    BOT     = 1.5 * cm

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=LEFT, rightMargin=RIGHT,
        topMargin=TOP,   bottomMargin=BOT,
        title="Kenya Economic Pulse — Executive Summary",
        author="Stephen Muema, Data Scientist",
        subject="Kenya Economic Analysis 2023",
    )
    CONTENT_W = PAGE_W - LEFT - RIGHT   # ≈ 17.1 cm
    styles    = getSampleStyleSheet()

    # ── Paragraph style factory ───────────────────────────────────────
    def _ps(name, **kw):
        return ParagraphStyle(name, parent=styles["Normal"], **kw)

    # Header text styles
    title_s  = _ps("Title",
                   fontName="Helvetica-Bold", fontSize=22,
                   textColor=NAVY, leading=26, alignment=TA_LEFT,
                   spaceBefore=0, spaceAfter=0)
    sub_s    = _ps("Sub",
                   fontName="Helvetica", fontSize=10.5,
                   textColor=GREY_TXT, leading=14, alignment=TA_LEFT,
                   spaceBefore=2, spaceAfter=0)
    meta_s   = _ps("Meta",
                   fontName="Helvetica", fontSize=8.5,
                   textColor=GREY_TXT, leading=12, alignment=TA_LEFT,
                   spaceBefore=2, spaceAfter=0)

    # Section headings
    h2_s     = _ps("H2",
                   fontName="Helvetica-Bold", fontSize=11,
                   textColor=NAVY, spaceBefore=10, spaceAfter=4)
    h3_teal  = _ps("H3T",
                   fontName="Helvetica-Bold", fontSize=9.5,
                   textColor=TEAL, spaceBefore=6, spaceAfter=3)

    # Body
    body_s   = _ps("Body",
                   fontName="Helvetica", fontSize=8.5,
                   textColor=DARK_TEXT, leading=13)
    bullet_s = _ps("Bullet",
                   fontName="Helvetica", fontSize=8.5,
                   textColor=DARK_TEXT, leading=13,
                   leftIndent=10, spaceAfter=3)
    small_s  = _ps("Small",
                   fontName="Helvetica", fontSize=7.5,
                   textColor=GREY_TXT, leading=11)
    footer_s = _ps("Footer",
                   fontName="Helvetica", fontSize=7,
                   textColor=GREY_TXT, alignment=TA_CENTER, leading=11)

    # KPI cell styles
    kpi_label_s  = _ps("KPILbl",
                        fontName="Helvetica", fontSize=7.5,
                        textColor=GREY_TXT, alignment=TA_CENTER, leading=9)
    kpi_value_s  = _ps("KPIVal",
                        fontName="Helvetica-Bold", fontSize=15,
                        textColor=NAVY, alignment=TA_CENTER, leading=18)
    kpi_trend_s  = _ps("KPITrn",
                        fontName="Helvetica-Oblique", fontSize=7.5,
                        textColor=BLUE, alignment=TA_CENTER, leading=9)

    story = []

    # ══════════════════════════════════════════════════════════════════
    # ① HEADER BLOCK — matches reference PDF exactly
    #
    #  ┌──────────────────────────────────────────────────────────┐
    #  │  [■ ■]  Kenya Economic Pulse                             │
    #  │         Executive Summary Report                         │
    #  │         Generated: DD Month YYYY  |  Prepared by: ...    │
    #  └──────────────────────────────────────────────────────────┘
    #                ─────────────────────── (blue rule)
    #
    # The logo mark (two squares) sits in a left column; the text
    # block sits in the right column — exactly like the reference.
    # ══════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 0.3 * cm))

    LOGO_COL  = 1.0 * cm
    TEXT_COL  = CONTENT_W - LOGO_COL - 0.3 * cm
    logo_draw = _logo_mark(10)

    # Build text column as nested table so all three lines align cleanly
    text_block = Table(
        [
            [Paragraph("Kenya Economic Pulse", title_s)],
            [Paragraph("Executive Summary Report", sub_s)],
            [Paragraph(
                f"Generated: {now_full}&nbsp;&nbsp;|&nbsp;&nbsp;"
                "Prepared by: Stephen Muema, Data Scientist",
                meta_s
            )],
        ],
        colWidths=[TEXT_COL]
    )
    text_block.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
    ]))

    # Outer row: logo | text
    header_row = Table(
        [[logo_draw, text_block]],
        colWidths=[LOGO_COL + 0.5 * cm, TEXT_COL - 0.5 * cm]
    )
    header_row.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (0, 0), (0, 0),   "LEFT"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    story.append(header_row)
    story.append(Spacer(1, 0.55 * cm))

    # Thick navy + thin blue double rule
    story.append(HRFlowable(width="100%", thickness=2.5,
                            color=NAVY, spaceAfter=2))
    story.append(HRFlowable(width="100%", thickness=0.8,
                            color=RULE_COLOR, spaceAfter=8))
    story.append(Spacer(1, 0.15 * cm))

    # ══════════════════════════════════════════════════════════════════
    # ② SECTION HEADER HELPER
    # ══════════════════════════════════════════════════════════════════
    def section_header(text: str) -> list:
        """Navy bold heading + thin blue underline."""
        return [
            Paragraph(text, h2_s),
            HRFlowable(width="100%", thickness=0.5,
                       color=BLUE_LIGHT, spaceAfter=5),
        ]

    # ══════════════════════════════════════════════════════════════════
    # ③ KPI DASHBOARD — 4-column × 2-row card grid
    # ══════════════════════════════════════════════════════════════════
    for fl in section_header("1.  Kenya at a Glance — 2023 Snapshot"):
        story.append(fl)

    def _status_color(flag: str) -> colors.Color:
        lf = flag.lower()
        if any(w in lf for w in ("good", "strong", "excellent", "record",
                                  "improving", "positive", "growing")):
            return GREEN
        if any(w in lf for w in ("critical", "high", "stuck", "warn")):
            return RED
        if any(w in lf for w in ("easing", "moderate", "stable", "stagnant")):
            return AMBER
        return GREY_TXT

    def _kpi_card(label, value, trend, status):
        sc = _status_color(status)
        st_style = ParagraphStyle(
            f"KS_{label}", parent=small_s,
            textColor=sc, alignment=TA_CENTER,
            fontName="Helvetica-BoldOblique")
        tr_style = ParagraphStyle(
            f"KT_{label}", parent=styles["Normal"],
            fontName=kpi_trend_s.fontName, fontSize=kpi_trend_s.fontSize,
            textColor=kpi_trend_s.textColor, alignment=kpi_trend_s.alignment,
            leading=kpi_trend_s.leading)
        return [
            Paragraph(label,  kpi_label_s),
            Paragraph(value,  kpi_value_s),
            Paragraph(trend,  tr_style),
            Paragraph(status, st_style),
        ]

    kpi_items = [
        ("GDP Growth",         f"{kpi['gdp_val']:.1f}%",
         "› Stable",           "Good" if kpi['gdp_val'] > 3 else "Watch"),
        ("Inflation Rate",     f"{kpi['inf_val']:.1f}%",
         "↓ Easing",           "High" if kpi['inf_val'] > 7 else "Moderate"),
        ("National Poverty",   f"{kpi['pov_val']:.1f}%",
         "↓ Improving",        "High"),
        ("Youth Unemployment", f"{kpi['yu_val']:.1f}%",
         "→ Stuck",            "Critical"),
        ("M-Pesa Users",       f"{kpi['mpesa_u']:.0f}M+",
         "› Growing",          "Excellent"),
        ("Fin. Inclusion",     f"{kpi['fin_inc']:.1f}%",
         "› Growing",          "Excellent"),
        ("Remittances",        f"${kpi['remit']:.1f}B",
         "› Record",           "Good"),
        ("Gini Index",         f"{kpi['gini']:.1f}",
         "→ Stagnant",         "High"),
    ]

    CARD_W    = CONTENT_W / 4
    kpi_rows  = []
    for i in range(0, len(kpi_items), 4):
        row_cells = [_kpi_card(*item) for item in kpi_items[i:i+4]]
        kpi_rows.append(row_cells)

    kpi_tbl = Table(kpi_rows,
                    colWidths=[CARD_W] * 4,
                    rowHeights=[2.4 * cm] * len(kpi_rows))
    kpi_tbl.setStyle(TableStyle([
        ("GRID",           (0, 0), (-1, -1), 0.4, GREY_LIGHT),
        ("ALIGN",          (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",     (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
        ("LEFTPADDING",    (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [OFF_WHITE, LIGHT_BG]),
        # Navy accent bar on top of both rows
        ("LINEABOVE",      (0, 0), (-1, 0),  2.5, NAVY),
        ("LINEABOVE",      (0, 1), (-1, 1),  2.5, NAVY),
    ]))
    story.append(kpi_tbl)
    story.append(Spacer(1, 0.35 * cm))

    # ══════════════════════════════════════════════════════════════════
    # ④ ML FINDINGS — two-column layout
    # ══════════════════════════════════════════════════════════════════
    for fl in section_header("2.  Machine Learning Findings"):
        story.append(fl)

    story.append(Paragraph(
        "Derived from Gradient Boosting &amp; Random Forest models trained on "
        "17 years of Kenya economic data (2007–2023):",
        body_s
    ))
    story.append(Spacer(1, 0.15 * cm))

    findings = [
        ("<b>Mobile Money is the #1 poverty lever</b> — M-Pesa explains "
         "<b>90.4 %</b> of national poverty variance (R²=0.904, GBM)."),
        (f"<b>Financial inclusion 26.4 % → {kpi['fin_inc']:.1f} %</b> (2006–2023). "
         "Kenya leads Sub-Saharan Africa."),
        (f"<b>Youth unemployment ({kpi['yu_val']:.1f} %)</b> is 4.5× the ILO global "
         "average (13.6 %). TVET investment is the fastest lever."),
        ("<b>NE Kenya in crisis</b> — Wajir 82 %, Turkana 79 %, Mandera 76 % poverty. "
         "Requires emergency county-level transfers."),
        ("<b>47 % lack electricity</b> — off-grid solar is the fastest path "
         "to 100 % electrification by 2030."),
        (f"<b>Remittances (${kpi['remit']:.1f}B)</b> now exceed tea + tourism as "
         "Kenya's largest forex earner."),
    ]

    # County snapshot table
    county_df = data.get("county")
    if county_df is not None:
        top3 = county_df.nlargest(3,  "Poverty_Rate")[["County", "Poverty_Rate"]].values.tolist()
        bot3 = county_df.nsmallest(3, "Poverty_Rate")[["County", "Poverty_Rate"]].values.tolist()
        c_rows = (
            [["County", "Pov. Rate", "Status"]] +
            [[r[0], f"{r[1]:.1f}%", "Most Deprived"]  for r in top3] +
            [["—",   "—",           "—"]] +
            [[r[0], f"{r[1]:.1f}%", "Best Performing"] for r in bot3]
        )
    else:
        c_rows = [["County", "Pov. Rate", "Status"], ["N/A", "N/A", "N/A"]]

    cty_tbl = Table(c_rows, colWidths=[3.2 * cm, 2.3 * cm, 3.0 * cm])
    cty_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 7.5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [LIGHT_BG, ALT_BG]),
        ("GRID",          (0, 0), (-1, -1), 0.3, GREY_LIGHT),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("TEXTCOLOR",     (0, 1), (0, 3),   RED),
        ("TEXTCOLOR",     (0, 5), (0, 7),   GREEN),
    ]))

    find_block = [Paragraph(f"• {f}", bullet_s) for f in findings]
    cty_block  = [
        Paragraph("County Poverty Snapshot", h3_teal),
        Spacer(1, 0.1 * cm),
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
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
    ]))
    story.append(two_col)
    story.append(Spacer(1, 0.3 * cm))

    # ══════════════════════════════════════════════════════════════════
    # ⑤ POLICY RECOMMENDATIONS
    # ══════════════════════════════════════════════════════════════════
    for fl in section_header("3.  Policy Recommendations"):
        story.append(fl)

    recs = [
        ("Expand Mobile Financial Services",
         "Roll out M-Pesa agent network to NE counties (Wajir, Mandera, Turkana) "
         "where penetration is below 40 %. Each 10 pp gain reduces poverty ~2 pp."),
        ("Scale TVET & Digital Skills",
         "Redirect 1 % of GDP to vocational training — projected to cut youth "
         "unemployment by 4–6 pp by 2028."),
        ("Accelerate Rural Electrification",
         "Deploy off-grid solar at scale. 25 pp gap to 100 % electrification is "
         "achievable by 2030 via public-private solar partnerships."),
        ("Attract ICT & Green Energy FDI",
         "Target FDI of 1.5 % GDP (currently 0.5 %). Tax incentives for ICT parks "
         "in lagging Tier-4 and Tier-5 counties."),
        ("Progressive Fiscal Redistribution",
         "Gini 40.8 demands structural reform: progressive income tax, VAT exemptions "
         "on basic goods, expanded cash-transfer programmes."),
        ("Formalise Diaspora Remittances",
         f"Reduce transfer fees from ~8 % to &lt;3 % on ${kpi['remit']:.1f}B inflow. "
         "Diaspora bonds could unlock an additional $1B+ in development finance."),
    ]

    ICON_W = 0.65 * cm
    BODY_W = CONTENT_W - ICON_W - 0.2 * cm
    tag_colors = [NAVY, BLUE, TEAL, GREEN, AMBER, RED]
    rec_rows   = []
    for i, (title, body) in enumerate(recs):
        tag_cell = Paragraph(
            f"<b>{i+1}</b>",
            _ps(f"rn{i}", fontName="Helvetica-Bold", fontSize=8.5,
                textColor=WHITE, alignment=TA_CENTER)
        )
        body_cell = [
            Paragraph(f"<b>{title}</b>",
                      _ps(f"rt{i}", fontName="Helvetica-Bold", fontSize=8.5,
                          textColor=NAVY, spaceAfter=2, leading=11)),
            Paragraph(body, _ps(f"rb{i}", fontName="Helvetica", fontSize=8.5,
                                         textColor=DARK_TEXT, leading=13, spaceAfter=0)),
        ]
        rec_rows.append([tag_cell, body_cell])

    rec_tbl = Table(rec_rows, colWidths=[ICON_W, BODY_W])
    rec_style = [
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (0, -1),  5),
        ("RIGHTPADDING",  (0, 0), (0, -1),  5),
        ("LEFTPADDING",   (1, 0), (1, -1),  8),
        ("RIGHTPADDING",  (1, 0), (1, -1),  4),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [LIGHT_BG, OFF_WHITE]),
        ("GRID",          (0, 0), (-1, -1), 0.3, GREY_LIGHT),
    ]
    for i in range(len(recs)):
        rec_style.append(("BACKGROUND", (0, i), (0, i),
                          tag_colors[i % len(tag_colors)]))
    rec_tbl.setStyle(TableStyle(rec_style))
    story.append(rec_tbl)
    story.append(Spacer(1, 0.4 * cm))

    # ══════════════════════════════════════════════════════════════════
    # ⑥ FOOTER
    # ══════════════════════════════════════════════════════════════════
    story.append(HRFlowable(width="100%", thickness=1.2,
                            color=NAVY, spaceAfter=2))
    story.append(HRFlowable(width="100%", thickness=0.5,
                            color=RULE_COLOR, spaceAfter=6))
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
# HTML FALLBACK — same brand identity as the PDF
# ══════════════════════════════════════════════════════════════════════

def generate_html_summary(data: dict) -> str:
    """
    Polished HTML executive summary — matches PDF brand identity.
    Header: inline logo squares LEFT of bold title (reference design).
    """
    kpi = _safe_kpis(data)
    now = datetime.now().strftime("%d %B %Y")

    def badge(text: str, good=None) -> str:
        if good is True:
            bg, fg = "#D5F5E3", "#1E8449"
        elif good is False:
            bg, fg = "#FDEDEC", "#C0392B"
        else:
            bg, fg = "#FEF9E7", "#D35400"
        return (f"<span style='background:{bg};color:{fg};padding:2px 7px;"
                f"border-radius:10px;font-size:.75rem;font-weight:600'>{text}</span>")

    kpi_cards_cfg = [
        ("GDP Growth",         f"{kpi['gdp_val']:.1f}%",  "› Stable",
         badge("Good" if kpi['gdp_val'] > 3 else "Watch", kpi['gdp_val'] > 3)),
        ("Inflation Rate",     f"{kpi['inf_val']:.1f}%",  "↓ Easing",
         badge("High" if kpi['inf_val'] > 7 else "Moderate", kpi['inf_val'] <= 7)),
        ("Poverty Rate",       f"{kpi['pov_val']:.1f}%",  "↓ Improving",
         badge("High", False)),
        ("Youth Unemployment", f"{kpi['yu_val']:.1f}%",   "→ Stuck",
         badge("Critical", False)),
        ("M-Pesa Users",       f"{kpi['mpesa_u']:.0f}M+", "› Growing",
         badge("Excellent", True)),
        ("Fin. Inclusion",     f"{kpi['fin_inc']:.1f}%",  "› Growing",
         badge("Excellent", True)),
        ("Remittances",        f"${kpi['remit']:.1f}B",   "› Record",
         badge("Good", True)),
        ("Gini Index",         f"{kpi['gini']:.1f}",      "→ Stagnant",
         badge("High", False)),
    ]

    cards_html = ""
    for label, value, trend, bdg in kpi_cards_cfg:
        cards_html += f"""
        <div class='kpi-card'>
            <div class='kpi-label'>{label}</div>
            <div class='kpi-value'>{value}</div>
            <div class='kpi-trend'>{trend}</div>
            <div style='margin-top:5px'>{bdg}</div>
        </div>"""

    recs_list = [
        ("Expand Mobile Financial Services",
         f"Roll out M-Pesa agent network to NE counties where penetration &lt;40%. "
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
        f"<div><b>{t}</b><br/>"
        f"<span style='color:#566573;font-size:.86rem'>{b}</span></div></div>"
        for i, (t, b) in enumerate(recs_list)
    )

    # County snapshot rows
    county_df = data.get("county")
    if county_df is not None:
        top3 = county_df.nlargest(3,  "Poverty_Rate")[["County", "Poverty_Rate"]].values.tolist()
        bot3 = county_df.nsmallest(3, "Poverty_Rate")[["County", "Poverty_Rate"]].values.tolist()
        c_rows_html  = "".join(
            f"<tr><td class='red'>{r[0]}</td><td>{r[1]:.1f}%</td>"
            f"<td>Most Deprived</td></tr>" for r in top3)
        c_rows_html += "<tr><td colspan='3' style='text-align:center;color:#AAB7B8;'>— — —</td></tr>"
        c_rows_html += "".join(
            f"<tr><td class='green'>{r[0]}</td><td>{r[1]:.1f}%</td>"
            f"<td>Best Performing</td></tr>" for r in bot3)
    else:
        c_rows_html = "<tr><td colspan='3'>Data unavailable</td></tr>"

    return f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width,initial-scale=1.0'>
<title>Kenya Economic Pulse — Executive Summary</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Segoe UI',Arial,sans-serif;background:#f0f4f8;color:#1C2833;padding:2rem 1rem}}
  .page{{max-width:920px;margin:0 auto;background:white;border-radius:8px;
         box-shadow:0 3px 24px rgba(0,0,0,.1);overflow:hidden}}

  /* ── HEADER ── */
  .header{{
    padding:2rem 2.2rem 1.4rem;
    background:white;
    border-bottom:none;
  }}
  .header-inner{{
    display:flex;
    align-items:center;
    gap:.9rem;
    padding-bottom:1.1rem;
  }}
  .logo-wrap{{display:flex;gap:5px;flex-shrink:0}}
  .logo-sq{{width:13px;height:13px;border-radius:1px}}
  .logo-sq.navy{{background:#1B4F72}}
  .logo-sq.blue{{background:#2980B9}}
  .header-text h1{{
    font-size:1.75rem;font-weight:700;color:#1B4F72;
    letter-spacing:-.3px;line-height:1.1;margin-bottom:.2rem
  }}
  .header-text .subtitle{{font-size:.97rem;color:#566573;margin-bottom:.2rem}}
  .header-text .meta{{font-size:.8rem;color:#7F8C8D}}
  .rule-double{{
    border:none;
    border-top: 3px solid #1B4F72;
    margin-bottom:2px;
  }}
  .rule-thin{{
    border:none;
    border-top: 1px solid #2980B9;
    margin-bottom:0;
  }}

  /* ── CONTENT ── */
  .content{{padding:1.4rem 2.2rem}}
  .section{{margin-bottom:1.5rem}}
  .section-title{{
    font-size:.95rem;font-weight:700;color:#1B4F72;
    padding:.3rem 0 .35rem;
    border-bottom:1px solid #AED6F1;
    margin-bottom:.85rem
  }}

  /* ── KPI GRID ── */
  .kpi-grid{{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:.5rem;
    margin-bottom:.8rem
  }}
  .kpi-card{{
    background:#FAFAFA;
    border:1px solid #D5D8DC;
    border-top:3px solid #1B4F72;
    border-radius:4px;
    padding:.65rem .45rem;
    text-align:center
  }}
  .kpi-label{{font-size:.7rem;color:#7F8C8D;margin-bottom:.2rem}}
  .kpi-value{{font-size:1.25rem;font-weight:700;color:#1B4F72;margin-bottom:.1rem}}
  .kpi-trend{{font-size:.72rem;color:#2980B9;font-style:italic}}

  /* ── TWO COLUMN ── */
  .two-col{{display:grid;grid-template-columns:1fr .72fr;gap:1.2rem}}
  .findings ul{{padding-left:1rem}}
  .findings li{{font-size:.87rem;line-height:1.6;margin-bottom:.35rem;color:#1C2833}}

  /* ── COUNTY TABLE ── */
  .cty-h{{font-size:.82rem;font-weight:600;color:#0E6655;margin-bottom:.5rem}}
  .cty-table{{width:100%;border-collapse:collapse;font-size:.8rem}}
  .cty-table th{{background:#1B4F72;color:white;padding:5px 9px;text-align:left}}
  .cty-table td{{padding:4px 9px;border:1px solid #D5D8DC}}
  .cty-table tr:nth-child(even) td{{background:#EBF5FB}}
  .red{{color:#C0392B;font-weight:600}}
  .green{{color:#1E8449;font-weight:600}}

  /* ── RECS ── */
  .rec{{
    display:flex;gap:.75rem;align-items:flex-start;
    padding:.6rem .75rem;margin-bottom:.35rem;
    border-radius:4px;background:#F8FBFF;
    border:1px solid #D6EAF8
  }}
  .rec-num{{
    min-width:22px;height:22px;
    background:#1B4F72;color:white;
    border-radius:50%;font-size:.78rem;font-weight:700;
    display:flex;align-items:center;justify-content:center;flex-shrink:0
  }}

  /* ── FOOTER ── */
  .footer{{
    background:#F0F7FF;border-top:1px solid #D6EAF8;
    padding:.85rem 2.2rem;font-size:.72rem;
    color:#7F8C8D;text-align:center;line-height:1.7
  }}
  .footer a{{color:#2980B9;text-decoration:none}}

  @media(max-width:600px){{
    .kpi-grid{{grid-template-columns:repeat(2,1fr)}}
    .two-col{{grid-template-columns:1fr}}
  }}
</style>
</head>
<body>
<div class='page'>

  <!-- HEADER — logo inline LEFT of title, matching reference PDF -->
  <div class='header'>
    <div class='header-inner'>
      <div class='logo-wrap'>
        <div class='logo-sq navy'></div>
        <div class='logo-sq blue'></div>
      </div>
      <div class='header-text'>
        <h1>Kenya Economic Pulse</h1>
        <div class='subtitle'>Executive Summary Report</div>
        <div class='meta'>Generated: {now}&nbsp;&nbsp;|&nbsp;&nbsp;Prepared by: Stephen Muema, Data Scientist</div>
      </div>
    </div>
    <hr class='rule-double'>
    <hr class='rule-thin'>
  </div>

  <div class='content'>

    <!-- KPI SNAPSHOT -->
    <div class='section'>
      <div class='section-title'>1.  Kenya at a Glance — 2023 Snapshot</div>
      <div class='kpi-grid'>{cards_html}</div>
    </div>

    <!-- ML FINDINGS + COUNTY SNAPSHOT -->
    <div class='section'>
      <div class='section-title'>2.  Machine Learning Findings</div>
      <p style='font-size:.85rem;color:#566573;margin-bottom:.7rem'>
        Derived from Gradient Boosting &amp; Random Forest models trained on 17 years of Kenya data (2007–2023):
      </p>
      <div class='two-col'>
        <div class='findings'>
          <ul>
            <li><b>Mobile Money is the #1 poverty lever</b> — M-Pesa explains <b>90.4%</b> of national poverty variance (R²=0.904).</li>
            <li><b>Financial inclusion 26.4% → {kpi['fin_inc']:.1f}%</b> (2006–2023). Kenya leads Sub-Saharan Africa.</li>
            <li><b>Youth unemployment ({kpi['yu_val']:.1f}%)</b> is 4.5× the ILO global average. TVET is the fastest fix.</li>
            <li><b>NE Kenya in crisis</b> — Wajir 82%, Turkana 79%, Mandera 76% poverty.</li>
            <li><b>47% lack electricity</b> — off-grid solar is fastest path to 100% by 2030.</li>
            <li><b>Remittances (${kpi['remit']:.1f}B)</b> now exceed tea + tourism as Kenya's top forex earner.</li>
          </ul>
        </div>
        <div>
          <div class='cty-h'>County Poverty Snapshot</div>
          <table class='cty-table'>
            <tr><th>County</th><th>Pov. Rate</th><th>Status</th></tr>
            {c_rows_html}
          </table>
        </div>
      </div>
    </div>

    <!-- RECOMMENDATIONS -->
    <div class='section'>
      <div class='section-title'>3.  Policy Recommendations</div>
      {recs_html}
    </div>

  </div><!-- /content -->

  <!-- FOOTER -->
  <div class='footer'>
    <b>Kenya Economic Pulse</b> &nbsp;·&nbsp; Stephen Muema, Data Scientist &amp; ML Engineer
    &nbsp;·&nbsp; <a href='https://muemastephenportfolio.netlify.app/'>muemastephenportfolio.netlify.app</a>
    &nbsp;·&nbsp; musyokas753@gmail.com<br>
    Data: World Bank Open API &nbsp;·&nbsp; KNBS 2019 Census &nbsp;·&nbsp; CBK Annual Reports
    &nbsp;·&nbsp; ILO Labour Statistics &nbsp;·&nbsp; FinAccess Survey 2021 &nbsp;·&nbsp; KIHBS 2021
  </div>

</div>
</body></html>"""
