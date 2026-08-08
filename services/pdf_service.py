"""Generates a PDF report for a single detection using ReportLab."""
import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_report(detection: dict, before_path: str, after_path: str,
                     result_path: str, output_path: str) -> str:
    """detection: dict-like row with title, change_percent, num_regions (optional),
    encroachment_flag, latitude, longitude, created_at."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], fontSize=20)
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                             leftMargin=2 * cm, rightMargin=2 * cm,
                             topMargin=2 * cm, bottomMargin=2 * cm)

    story = []
    story.append(Paragraph("AI Encroachment Detection Report", title_style))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 0.8 * cm))

    status = "ENCROACHMENT DETECTED" if detection.get("encroachment_flag") else "No significant change"
    status_color = colors.red if detection.get("encroachment_flag") else colors.green

    summary_data = [
        ["Title", detection.get("title") or "Untitled"],
        ["Change detected", f"{detection.get('change_percent', 0)}%"],
        ["Status", status],
        ["Location",
         f"{detection.get('latitude')}, {detection.get('longitude')}"
         if detection.get("latitude") is not None else "Not provided"],
        ["Date", str(detection.get("created_at", ""))],
    ]
    table = Table(summary_data, colWidths=[4 * cm, 11 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f0f0")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (1, 2), (1, 2), status_color),
        ("FONTNAME", (1, 2), (1, 2), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 1 * cm))

    story.append(Paragraph("Before", styles["Heading3"]))
    story.append(RLImage(before_path, width=15 * cm, height=9 * cm, kind="proportional"))
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("After", styles["Heading3"]))
    story.append(RLImage(after_path, width=15 * cm, height=9 * cm, kind="proportional"))
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Detected Changes (highlighted)", styles["Heading3"]))
    story.append(RLImage(result_path, width=15 * cm, height=9 * cm, kind="proportional"))

    doc.build(story)
    return output_path