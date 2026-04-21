# utils.py
"""Utility functions for web scraping and cover letter text processing."""

import copy
import re
import requests

from bs4 import BeautifulSoup
from docx import Document

from config import NAMESPACE, PLACEHOLDER_PATTERN


def scrape_url(url: str):
    """Fetch and extract text content from a web page by URL."""
    try:
        headers = {"User-Agent": "CoverLetterApp/1.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        return text[:5000] if len(text) > 100 else None
    except Exception:
        return None


def clean_cover_letter(text: str) -> str:
    """Remove service text before and after the actual letter.

    Extracts only the content between 'Dear...' and 'Kind regards, Alina',
    stripping any LLM commentary or metadata.
    """
    start_markers = ["Dear"]
    for marker in start_markers:
        idx = text.find(marker)
        if idx != -1:
            text = text[idx:]
            break

    end_markers = ["Kind regards, Alina", "Kind regards,\nAlina"]
    for marker in end_markers:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx + len(marker)]
            break

    return text.strip()


def find_placeholder(file_path: str) -> list:
    """Find all {{PLACEHOLDER}} patterns in a DOCX file."""
    doc = Document(file_path)
    plaseholders = set()

    for paragraph in _iter_all_paragraphs(doc):
        plaseholders.update(PLACEHOLDER_PATTERN.findall(paragraph.text))

    return sorted(plaseholders)


def fill_template(file_path: str, data: dict, output_path: str):
    """Replace {{PLACEHOLDER}} patterns in a DOCX with actual content."""
    doc = Document(file_path)
    pass


def _iter_all_paragraphs(doc):
    """Yield all paragraphs from the document and its tables."""
    for paragraph in doc.paragraphs:
        yield paragraph
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    yield paragraph


def _replace_text(paragraph, placeholder: str, replacement: str):
    """Replace placeholder text, preserving formatting."""
    for run in paragraph.runs:
        if placeholder in run.text:
            run.text = run.text.replace(placeholder, replacement)
            return
    if placeholder in paragraph.text and paragraph.runs:
        paragraph.runs[0].text = paragraph.text.replace(
            placeholder, replacement)
        for run in paragraph.runs[1:]:
            run.text = ""
