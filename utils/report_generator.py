"""
PDF Report Generator
Generates a one-page executive summary PDF using ReportLab.
Author: Stephen Muema
"""

import io
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False


def generate_executive_summary(data: dict) -> bytes:
    """
    Generate a PDF executive summary of Kenya Economic Pulse data.
    Returns bytes that can be served as a download.
    Falls back gracefully if ReportLab is not installed.
    """
    if not REPORTLAB_OK:
        return b""

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontSize=20,
        textColor=colors.HexColor("#1B4F72"),
        spaceAfter=12
    )
    h2_style = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#2980B9"),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2C3E50")
    )

    story = []

    # ── Title ──────────────────────────────────────────────────────────────
    story.append(Paragraph("🇰🇪 Kenya Economic Pulse", title_style))
    story.append(Paragraph(
        f"Executive Summary — Generated {datetime.now().strftime('%B %d, %Y')}",
        body_style
    ))
    story.append(Spacer(1, 0.4*cm))

    # ── Key KPIs ──────────────────────────────────────────────────────────
    story.append(Paragraph("Key Economic Indicators (2023)", h2_style))

    macro = data.get("macro", None)
    mm    = data.get("mobile_money", None)
    yu    = data.get("youth_unemp", None)

    try:
        gdp_val  = float(macro["GDP Growth (%)"].dropna().iloc[-1]) if macro is not None else 4.8
        inf_val  = float(macro["Inflation Rate (%)"].dropna().iloc[-1]) if macro is not None else 7.8
        pov_val  = float(mm["Poverty_Rate_National"].iloc[-1]) if mm is not None else 33.5
        yu_val   = float(yu["Youth_Unemployment_Pct"].iloc[-1]) if yu is not None else 61.5
        mpesa_u  = float(mm["MPesa_Users_M"].iloc[-1]) if mm is not None else 41.0
        fin_inc  = float(mm["Financial_Inclusion_Pct"].iloc[-1]) if mm is not None else 85.1
    except Exception:
        gdp_val, inf_val, pov_val, yu_val, mpesa_u, fin_inc = 4.8, 7.8, 33.5, 61.5, 41.0, 85.1

    kpi_data = [
        ["Indicator", "Value", "Status"],
        ["GDP Growth Rate", f"{gdp_val:.1f}%", "Positive" if gdp_val > 0 else "Negative"],
        ["Inflation Rate", f"{inf_val:.1f}%", "High" if inf_val > 7 else "Moderate"],
        ["National Poverty Rate", f"{pov_val:.1f}%", "Improving" if pov_val < 40 else "Critical"],
        ["Youth Unemployment", f"{yu_val:.1f}%", "Critical (4.5× global avg)"],
        ["M-Pesa Users", f"{mpesa_u:.0f}M", "Strong"],
        ["Financial Inclusion", f"{fin_inc:.1f}%", "Excellent"],
    ]
    kpi_table = Table(kpi_data, colWidths=[6*cm, 3*cm, 5*cm])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#1B4F72")),
        ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.HexColor("#EBF5FB"), colors.HexColor("#D6EAF8")]),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#AED6F1")),
        ("TOPPADDING",  (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.3*cm))

    # ── Key Findings ──────────────────────────────────────────────────────
    story.append(Paragraph("Key Findings", h2_style))
    findings = [
        "M-Pesa is Kenya's most powerful poverty reduction tool — ML model R² = 0.904.",
        "NE Kenya remains in a development crisis: Wajir (82%), Mandera (76%), Turkana (79%) poverty.",
        "Financial inclusion rose from 26.4% (2006) to 85.1% (2023) — a 58.7pp improvement.",
        f"Youth unemployment ({yu_val:.1f}%) is 4.5× the global average of 13.6% (ILO 2023).",
        "47% of Kenyans lack electricity — off-grid solar is the fastest solution for rural areas.",
        "Remittances ($4.2B) now exceed tea and tourism as Kenya's largest forex earner.",
    ]
    for f in findings:
        story.append(Paragraph(f"• {f}", body_style))
    story.append(Spacer(1, 0.3*cm))

    # ── Policy Recommendations ────────────────────────────────────────────
    story.append(Paragraph("Policy Recommendations", h2_style))
    recommendations = [
        "Prioritise mobile financial services expansion to NE counties (Wajir, Mandera, Turkana).",
        "Increase TVET and digital skills investment — university enrollment is the top unemployment driver.",
        "Accelerate rural electrification via off-grid solar programmes.",
        "Scale M-Pesa agent network to underserved regions (mobile penetration < 40%).",
        "Introduce progressive taxation measures to address Gini index of 40.8.",
        "Attract FDI in ICT and green energy sectors to create formal employment for youth.",
    ]
    for r in recommendations:
        story.append(Paragraph(f"• {r}", body_style))
    story.append(Spacer(1, 0.5*cm))

    # ── Footer ───────────────────────────────────────────────────────────
    story.append(Paragraph(
        "Kenya Economic Pulse | Built by Stephen Muema | "
        "muemastephenportfolio.netlify.app | musyokas753@gmail.com",
        ParagraphStyle("footer", parent=styles["BodyText"],
                       fontSize=8, textColor=colors.grey)
    ))

    doc.build(story)
    return buf.getvalue()
