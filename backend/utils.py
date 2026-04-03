import requests

from bs4 import BeautifulSoup


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
