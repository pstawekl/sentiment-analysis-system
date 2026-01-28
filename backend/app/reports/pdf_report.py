"""
Generowanie raportu PDF z analizy sentymentu opinii.
Wykorzystuje ReportLab do budowy dokumentu: nagłówek, podsumowanie, lista opinii.
"""

from datetime import datetime
from io import BytesIO
from typing import Any, Dict

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

# Maksymalna długość fragmentu opinii w tabeli (znaki)
MAX_REVIEW_SNIPPET_LEN = 400


def _truncate_text(text: str, max_len: int = MAX_REVIEW_SNIPPET_LEN) -> str:
    """Skraca tekst do max_len znaków; dodaje '...' jeśli obcięty."""
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def build_report_pdf(df: pd.DataFrame, eda_stats: Dict[str, Any]) -> bytes:
    """
    Buduje raport PDF zawierający podsumowanie i wszystkie opinie z analizą.

    Args:
        df: DataFrame z kolumnami review_text, polarity, sentiment_label, word_count (opcjonalnie review_length).
        eda_stats: Słownik ze statystykami EDA (total_reviews, positive_count, negative_count, itd.).

    Returns:
        bytes: Zawartość pliku PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=12,
        alignment=1,
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=12,
    )
    normal_style = styles["Normal"]

    story = []

    # --- Strona tytułowa / nagłówek ---
    story.append(Paragraph("Raport analizy sentymentu opinii", title_style))
    story.append(
        Paragraph(
            f"Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            normal_style,
        )
    )
    story.append(Spacer(1, 0.5 * cm))

    # --- Sekcja podsumowania ---
    story.append(Paragraph("Podsumowanie", heading_style))
    total = eda_stats.get("total_reviews", 0)
    pos_count = eda_stats.get("positive_count", 0)
    neg_count = eda_stats.get("negative_count", 0)
    pos_pct = eda_stats.get("positive_percentage", 0.0)
    neg_pct = eda_stats.get("negative_percentage", 0.0)
    avg_polarity = eda_stats.get("average_polarity", 0.0)
    avg_length = eda_stats.get("average_review_length", 0.0)
    avg_words = eda_stats.get("average_word_count", 0.0)

    summary_data = [
        ["Liczba opinii", str(total)],
        ["Opinie pozytywne", f"{pos_count} ({pos_pct:.1f}%)"],
        ["Opinie negatywne", f"{neg_count} ({neg_pct:.1f}%)"],
        ["Średnia polaryzacja", f"{avg_polarity:.4f}"],
        ["Średnia długość opinii (znaki)", f"{avg_length:.1f}"],
        ["Średnia liczba słów w opinii", f"{avg_words:.1f}"],
    ]
    summary_table = Table(summary_data, colWidths=[*([None] * 2)])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 0.8 * cm))

    # --- Lista opinii i analiza ---
    story.append(Paragraph("Lista opinii i wyniki analizy", heading_style))

    # Nagłówki tabeli
    table_header = ["Lp.", "Opinia (fragment)",
                    "Polaryzacja", "Sentyment", "Słowa"]
    table_data = [table_header]

    required_cols = ["review_text", "polarity", "sentiment_label"]
    if not all(c in df.columns for c in required_cols):
        story.append(
            Paragraph(
                "Brak wymaganych kolumn w danych (review_text, polarity, sentiment_label).",
                normal_style,
            )
        )
    else:
        word_col = "word_count" if "word_count" in df.columns else None
        for idx, row in df.iterrows():
            lp = len(table_data)
            text = _truncate_text(row["review_text"])
            polarity = row["polarity"]
            label = row["sentiment_label"]
            words = row[word_col] if word_col is not None else ""
            table_data.append(
                [str(lp), text, f"{float(polarity):.4f}",
                 str(label), str(words)]
            )

        col_widths = [1.2 * cm, None, 2.2 * cm, 2.2 * cm, 1.2 * cm]
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (0, -1), "CENTER"),
                    ("ALIGN", (2, 0), (2, -1), "CENTER"),
                    ("ALIGN", (3, 0), (3, -1), "CENTER"),
                    ("ALIGN", (4, 0), (4, -1), "CENTER"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                     [colors.white, colors.lightgrey]),
                ]
            )
        )
        story.append(t)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
