"""OCR text extraction from math problem images."""

from __future__ import annotations

import cv2
import numpy as np

from image_utils import preprocess_for_ocr
from models import OCRResult
from text_utils import normalize_ocr_text

_reader = None


def _get_reader():
    """Lazy-load EasyOCR to avoid slow startup on import."""
    global _reader
    if _reader is None:
        import easyocr

        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


def extract_text_from_image(image: np.ndarray) -> OCRResult:
    """Run preprocessing and OCR on an image."""
    cropped, binary = preprocess_for_ocr(image)
    reader = _get_reader()
    results = reader.readtext(binary, detail=1)
    if not results:
        results = reader.readtext(cropped, detail=1)

    lines = []
    confidences = []
    for _bbox, text, conf in results:
        cleaned = text.strip()
        if cleaned:
            lines.append(cleaned)
            confidences.append(conf)

    raw = " ".join(lines)
    normalized = normalize_ocr_text(raw)
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

    return OCRResult(
        raw_text=normalized or raw,
        confidence=avg_conf,
        cropped_image=cropped,
    )


def extract_text_from_bytes(file_bytes: bytes) -> OCRResult:
    """Load image bytes and extract text."""
    from image_utils import load_image

    image = load_image(file_bytes)
    return extract_text_from_image(image)
