"""PDF generation for the Twitter Digest."""

import logging
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    PageBreak,
)

from .models import DailyDigest

logger = logging.getLogger(__name__)


def markdown_to_paragraphs(markdown_text: str, styles: dict) -> list:
    """Convert markdown text to ReportLab Paragraph objects."""
    elements = []
    lines = markdown_text.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            elements.append(Spacer(1, 6))
            i += 1
            continue

        if line.startswith("# "):
            text = line[2:]
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(text, styles["Heading1"]))
            elements.append(Spacer(1, 8))

        elif line.startswith("## "):
            text = line[3:]
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(text, styles["Heading2"]))
            elements.append(Spacer(1, 6))

        elif line.startswith("### "):
            text = line[4:]
            elements.append(Spacer(1, 8))
            elements.append(Paragraph(text, styles["Heading3"]))
            elements.append(Spacer(1, 4))

        elif line.startswith("- ") or line.startswith("* "):
            text = line[2:]
            text = format_inline_markdown(text)
            elements.append(Paragraph(f"• {text}", styles["Bullet"]))

        elif re.match(r"^\d+\.\s", line):
            text = re.sub(r"^\d+\.\s", "", line)
            text = format_inline_markdown(text)
            elements.append(Paragraph(f"• {text}", styles["Bullet"]))

        elif line.startswith("---") or line.startswith("***"):
            elements.append(Spacer(1, 12))

        else:
            text = format_inline_markdown(line)
            elements.append(Paragraph(text, styles["Normal"]))

        i += 1

    return elements


def format_inline_markdown(text: str) -> str:
    """Convert inline markdown to ReportLab XML tags."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.+?)__", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"_(.+?)_", r"<i>\1</i>", text)
    text = re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", text)
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    return text


def create_styles() -> dict:
    """Create custom styles for the PDF."""
    base_styles = getSampleStyleSheet()

    styles = {
        "Title": ParagraphStyle(
            "Title",
            parent=base_styles["Title"],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor("#1a1a2e"),
        ),
        "Heading1": ParagraphStyle(
            "Heading1",
            parent=base_styles["Heading1"],
            fontSize=18,
            spaceAfter=12,
            textColor=colors.HexColor("#16213e"),
        ),
        "Heading2": ParagraphStyle(
            "Heading2",
            parent=base_styles["Heading2"],
            fontSize=14,
            spaceAfter=8,
            textColor=colors.HexColor("#0f3460"),
        ),
        "Heading3": ParagraphStyle(
            "Heading3",
            parent=base_styles["Heading3"],
            fontSize=12,
            spaceAfter=6,
            textColor=colors.HexColor("#1a1a2e"),
        ),
        "Normal": ParagraphStyle(
            "Normal",
            parent=base_styles["Normal"],
            fontSize=10,
            spaceAfter=6,
            leading=14,
        ),
        "Bullet": ParagraphStyle(
            "Bullet",
            parent=base_styles["Normal"],
            fontSize=10,
            leftIndent=20,
            spaceAfter=4,
            leading=14,
        ),
        "Date": ParagraphStyle(
            "Date",
            parent=base_styles["Normal"],
            fontSize=12,
            textColor=colors.HexColor("#666666"),
            spaceAfter=20,
        ),
    }

    return styles


def build_pdf(
    digest: DailyDigest,
    output_path: str,
    title: str = "Twitter Morning Digest",
) -> str:
    """
    Build a PDF from the daily digest.

    Returns the path to the generated PDF.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = create_styles()
    elements = []

    elements.append(Paragraph(title, styles["Title"]))
    date_str = digest.date.strftime("%A, %B %d, %Y")
    elements.append(Paragraph(date_str, styles["Date"]))

    if digest.handles:
        handles_text = ", ".join(f"@{h.handle}" for h in digest.handles)
        elements.append(Paragraph(f"<b>Tracking:</b> {handles_text}", styles["Normal"]))
        elements.append(Spacer(1, 20))

    if digest.raw_markdown:
        md_elements = markdown_to_paragraphs(digest.raw_markdown, styles)
        elements.extend(md_elements)
    else:
        elements.append(Paragraph("No content available.", styles["Normal"]))

    try:
        doc.build(elements)
        logger.info(f"PDF generated: {output_path}")
        return str(path)
    except Exception as e:
        logger.error(f"Error building PDF: {e}")
        raise


def build_pdf_bytes(
    digest: DailyDigest,
    title: str = "Twitter Morning Digest",
) -> bytes:
    """Build PDF and return as bytes (useful for email attachment)."""
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = create_styles()
    elements = []

    elements.append(Paragraph(title, styles["Title"]))
    date_str = digest.date.strftime("%A, %B %d, %Y")
    elements.append(Paragraph(date_str, styles["Date"]))

    if digest.handles:
        handles_text = ", ".join(f"@{h.handle}" for h in digest.handles)
        elements.append(Paragraph(f"<b>Tracking:</b> {handles_text}", styles["Normal"]))
        elements.append(Spacer(1, 20))

    if digest.raw_markdown:
        md_elements = markdown_to_paragraphs(digest.raw_markdown, styles)
        elements.extend(md_elements)
    else:
        elements.append(Paragraph("No content available.", styles["Normal"]))

    doc.build(elements)
    return buffer.getvalue()
