import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_upload_resume_success():
    """Test that a PDF file uploads successfully."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with open("tests/fixtures/test_resume.pdf", "rb") as f:
            response = await client.post(
                "/upload_resume/",
                files={"file": ("resume.pdf", f, "application/pdf")},
            )
    assert response.status_code == 200
    assert response.json()["filename"] == "resume.pdf"
    assert "chunks" in response.json()


@pytest.mark.asyncio
async def test_upload_resume_no_file():
    """Test that request without file returns 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/upload_resume/")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_without_resume():
    """Test that generation fails if no resume uploaded."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/generate/",
            data={
                "company_text": "Test company",
                "job_text": "Test job",
            },
        )
    assert response.status_code == 200
    assert "upload" in response.json()["cover_letter"].lower()


@pytest.mark.asyncio
async def test_scrape_invalid_url():
    """Test that scraping an invalid URL returns failure."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/scrape/",
            data={"url": "http://localhost:99999/nonexistent"},
        )
    assert response.status_code == 200
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_download_pdf():
    """Test that PDF is generated and returned."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/download_pdf/",
            data={"cover_letter": "Dear Receiver,\n\nTest letter.\n\nKind regards, Alina"},
        )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
