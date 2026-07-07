"""Text normalization utilities for OCR output."""

import re


def normalize_ocr_text(text: str) -> str:
    """Clean OCR output into math-friendly text."""
    replacements = {
        "×": "*",
        "÷": "/",
        "−": "-",
        "–": "-",
        "—": "-",
        "²": "**2",
        "³": "**3",
        "√": "sqrt",
        "π": "pi",
        "∞": "oo",
        "≤": "<=",
        "≥": ">=",
        "≠": "!=",
        "≈": "~",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace(" ", "")
    text = re.sub(r"(\d)x", r"\1*x", text)
    text = re.sub(r"\)x", r")*x", text)
    text = re.sub(r"x(\d)", r"x*\1", text)
    text = re.sub(r"(\d)\(", r"\1*(", text)
    return text
