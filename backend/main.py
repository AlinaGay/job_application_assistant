# main.py

import os
import shutil

# from dotenv import load_dotenv
# load_dotenv()

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

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
