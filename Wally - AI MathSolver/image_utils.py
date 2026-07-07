"""OpenCV image preprocessing for math problem photos."""

from __future__ import annotations

import cv2
import numpy as np


def load_image(file_bytes: bytes) -> np.ndarray:
    """Load image bytes into a BGR numpy array."""
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode image. Please upload a valid image file.")
    return image


def remove_shadows(gray: np.ndarray) -> np.ndarray:
    """Reduce shadows using morphological background estimation."""
    dilated = cv2.dilate(gray, np.ones((7, 7), np.uint8))
    bg = cv2.medianBlur(dilated, 21)
    diff = 255 - cv2.absdiff(gray, bg)
    return cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX)


def improve_contrast(gray: np.ndarray) -> np.ndarray:
    """Apply CLAHE for better OCR contrast."""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


def auto_rotate(image: np.ndarray) -> np.ndarray:
    """Deskew image based on detected text contours."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) < 10:
        return image
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = 90 + angle
    elif angle > 45:
        angle = angle - 90
    if abs(angle) < 0.5:
        return image
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        image, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )


def detect_and_crop(image: np.ndarray) -> np.ndarray:
    """Detect the main content region and crop to it."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return image
    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    if w * h < 0.05 * image.shape[0] * image.shape[1]:
        return image
    pad = 10
    x = max(0, x - pad)
    y = max(0, y - pad)
    w = min(image.shape[1] - x, w + 2 * pad)
    h = min(image.shape[0] - y, h + 2 * pad)
    return image[y : y + h, x : x + w]


def preprocess_for_ocr(image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Full preprocessing pipeline.
    Returns (color_cropped_image, binary_for_ocr).
    """
    rotated = auto_rotate(image)
    cropped = detect_and_crop(rotated)
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    gray = remove_shadows(gray)
    gray = improve_contrast(gray)
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    return cropped, binary
