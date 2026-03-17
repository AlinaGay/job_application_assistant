# main.py

import os
import shutil

from reportlab.lib import pagesizes
from reportlab.lib import styles

# from dotenv import load_dotenv
# load_dotenv()

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from rag import (
    generate_cover_letter,
    process_about_me,
    process_resume,
    scrape_url
)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=["Content-Disposition"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")


@app.post("/upload_resume/")
async def upload_resume(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    chunks_count = process_resume(file_path)
    return {"filename": file.filename, "chunks": chunks_count}


@app.post("/upload_about_me/")
async def upload_about_me(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    chunks_count = process_about_me(file_path)
    return {"filename": file.filename, "chunks": chunks_count}


@app.post("/scrape/")
async def scrape(url: str = Form(...)):
    text = scrape_url(url)
    if text:
        return {"success": True, "text": text}
    return {"success": False, "text": ""}


@app.post("/generate/")
async def generate(
    company_text: str = Form(...),
    job_text: str = Form(...),
):
    letter = generate_cover_letter(company_text, job_text)
    return {"cover_letter": letter}


@app.post("/download_pdf/")
async def download_pdf(cover_letter: str = Form(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    pdf_path = os.path.join(UPLOAD_DIR, "cover_letter.pdf")

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    for line in cover_letter.split("\n"):
        if line.strip():
            story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 6))
        else:
            story.append(Spacer(1, 12))

    doc.build(story)
    return FileResponse(pdf_path, filename="cover_letter.pdf", media_type="application/pdf")
