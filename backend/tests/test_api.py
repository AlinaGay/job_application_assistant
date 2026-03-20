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
