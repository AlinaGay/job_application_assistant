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


def fill_template(file_path: str, data: dict, output_path: str,
                  multiline: bool = True):
    """Replace {{PLACEHOLDER}} patterns in a DOCX with actual content."""
    doc = Document(file_path)
    paragraphs = list(_iter_all_paragraphs(doc))

    for paragraph in paragraphs:
        if "{{" in paragraph.text:
            _replace_in_paragraph(paragraph, data, multiline)

    doc.save(output_path)


def _iter_all_paragraphs(doc):
    """Yield all paragraphs from the document and its tables."""
    for paragraph in doc.paragraphs:
        yield paragraph
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    yield paragraph


def _replace_in_paragraph(paragraph, data: dict, multiline: bool):
    """Replace all placeholders in a single paragraph."""
    for key, value in data.items():
        placeholder = "{{" + key + "}}"
        if placeholder not in paragraph.text:
            continue

        lines = value.split("\n") if multiline else [value]
        _replace_text(paragraph, placeholder, lines[0])

        for line in reversed(lines[1:]):
            _insert_paragraph_after(paragraph, line)


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


def _insert_paragraph_after(paragraph, text: str):
    """Copy paragraph formatting and insert a new paragraph with text."""
    new_para = copy.deepcopy(paragraph._p)
    runs = new_para.findall(f".//{NAMESPACE}r")

    if runs:
        first_text = runs[0].find(f"{NAMESPACE}t")
        if first_text is not None:
            first_text.text = text
        for run in runs[1:]:
            text_elem = run.find(f"{NAMESPACE}t")
            if text_elem is not None:
                text_elem.text = ""

    paragraph._p.addnext(new_para)
