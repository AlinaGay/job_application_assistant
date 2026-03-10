# main.py

import os
import shutil

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from rag import process_resume, generate_cover_letter


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


@app.post("/generate/")
async def generate(
    company_text: str = Form(...),
    about_me_text: str = Form(...)
):
    letter = generate_cover_letter(company_text, about_me_text)
    return {"cover_letter": letter}
