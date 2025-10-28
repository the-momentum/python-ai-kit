import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import pypdf

def get_pdf_path() -> Path | str:
    load_dotenv()
    return os.getenv("PDF_PATH")


def get_pdf_text(pdf_path: Path | str) -> dict[str, Any]:
    reader = pypdf.PdfReader(pdf_path)
    pages_text = [page.extract_text() for page in reader.pages]
    return {
        "page_number": len(reader.pages),
        "pages": pages_text,
    }
