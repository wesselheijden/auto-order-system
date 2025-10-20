"""OCR helpers wrapping pytesseract."""
from __future__ import annotations

from pathlib import Path
from typing import Union

from PIL import Image
import pytesseract


class OCRFailure(RuntimeError):
    """Raised when OCR extraction fails."""


def extract_text_from_image(path: Union[str, Path], lang: str = "eng+nld") -> str:
    """Return text extracted from an image using Tesseract."""

    image_path = Path(path)
    try:
        with Image.open(image_path) as image:
            text = pytesseract.image_to_string(image, lang=lang)
    except pytesseract.TesseractNotFoundError as exc:  # type: ignore[attr-defined]
        raise OCRFailure(
            "Tesseract executable not found. Install Tesseract OCR and ensure it is on the PATH."
        ) from exc
    except OSError as exc:  # Pillow errors
        raise OCRFailure(f"Failed to open image {image_path}: {exc}") from exc
    return text
