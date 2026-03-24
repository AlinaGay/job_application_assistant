import os
import pytest
from rag import (
    clean_cover_letter,
    process_about_me,
    process_resume,
    scrape_url
)


def test_process_resume(tmp_path):
    """Test that resume is indexed and returns chunk count."""
    test_file = tmp_path/"test.txt"
    test_file.write_text("Python developer with 5 years of experience in Django and FastAPI.")

    chunks = process_resume(str(test_file))
    assert chunks > 0


def test_process_about_me(tmp_path):
    """Test that about_me file is indexed and returns chunk count."""
    test_file = tmp_path/"about_me.txt"
    test_file.write_text("I am passionate about building products that help people.")

    chunks = process_about_me(str(test_file))
    assert chunks > 0


def test_scrape_url_valid():
    """Test scraping a known public page."""
    text = scrape_url("https://example.com")
    assert text is not None
    assert len(text) > 0


def test_scrape_url_invalid():
    """Test scraping an invalid URL returns error string."""
    result = scrape_url("https://this-does-not-exist-99999.com")
    assert result is None or "error" in result.lower()
