"""Application configuration exposed as module-level constants.

Use environment variables to override defaults.
"""
import os
from pathlib import Path

# Gemini / Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Directory where PDF templates are stored (absolute)
PDF_TEMPLATE_DIR = Path(os.getenv("PDF_TEMPLATE_DIR", "")) if os.getenv("PDF_TEMPLATE_DIR") else (Path(__file__).parent / "pdf_templates")
try:
    # Ensure Path object
    if not isinstance(PDF_TEMPLATE_DIR, Path):
        PDF_TEMPLATE_DIR = Path(PDF_TEMPLATE_DIR)
    PDF_TEMPLATE_DIR = PDF_TEMPLATE_DIR.resolve()
except Exception:
    PDF_TEMPLATE_DIR = Path(__file__).parent / "pdf_templates"

# Model selection
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-pro")

__all__ = ["GEMINI_API_KEY", "PDF_TEMPLATE_DIR", "MODEL_NAME"]
