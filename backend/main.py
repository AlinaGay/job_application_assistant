# main.py

import os
import shutil

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from rag import (
    generate_cover_letter,
    process_about_me,
    process_resume
)
from utils import clean_cover_letter, scrape_url


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")


@app.post("/upload_resume/")
async def upload_resume(file: UploadFile = File(...)):
    """Save uploaded resume PDF and index it into the RAG vector store."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    chunks_count = process_resume(file_path)
    return {"filename": file.filename, "chunks": chunks_count}


@app.post("/upload_about_me/")
async def upload_about_me(file: UploadFile = File(...)):
    """Save uploaded about_me file (PDF or TXT) and index it into the RAG vector store."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    chunks_count = process_about_me(file_path)
    return {"filename": file.filename, "chunks": chunks_count}


@app.post("/scrape/")
async def scrape(url: str = Form(...)):
    """Attempt to extract text content from a web page by URL."""
    text = scrape_url(url)
    if text:
        return {"success": True, "text": text}
    return {"success": False, "text": ""}


@app.post("/generate/")
async def generate(
    company_text: str = Form(...),
    job_text: str = Form(...),
):
    """Generate a cover letter based on company info and job description.

    Requires resume and about_me to be uploaded first.
    The agent retrieves relevant context from both vector stores.
    """
    letter = generate_cover_letter(company_text, job_text)
    return {"cover_letter": letter}


@app.post("/download_pdf/")
async def download_pdf(cover_letter: str = Form(...)):
    """Convert the generated cover letter to a styled PDF with EB Garamond font.

    Cleans the letter text (removes LLM commentary) before rendering.
    Returns the PDF file for download.
    """
    cleaned_letter = clean_cover_letter(cover_letter)

    font_dir = os.path.join(BASE_DIR, "fonts")
    pdfmetrics.registerFont(TTFont("EBGaramond", os.path.join(font_dir, "EBGaramond-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("EBGaramond-Bold", os.path.join(font_dir, "EBGaramond-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("EBGaramond-Italic", os.path.join(font_dir, "EBGaramond-Italic.ttf")))

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    pdf_path = os.path.join(UPLOAD_DIR, "cover_letter.pdf")

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=72,
        rightMargin=72,
        topMargin=72,
        bottomMargin=72,
    )
    style = ParagraphStyle(
        "CoverLetter",
        fontName="EBGaramond",
        fontSize=12,
        leading=18,
        spaceAfter=6,
    )
    story = []

    for line in cleaned_letter.split("\n"):
        if line.strip():
            story.append(Paragraph(line, style))
            story.append(Spacer(1, 6))
        else:
            story.append(Spacer(1, 12))

    doc.build(story)
    return FileResponse(pdf_path, filename="cover_letter.pdf", media_type="application/pdf")
