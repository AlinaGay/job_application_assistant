# Job Application Assistant

AI-powered cover letter generator that crafts personalized, authentic cover letters by analyzing your resume, personal motivation, company info, and job description.

Built with a RAG (Retrieval-Augmented Generation) pipeline — the agent autonomously searches your documents to find the most relevant experience and stories for each application.

## Demo



https://github.com/user-attachments/assets/64dab58f-dacf-4c34-8cf3-0d698948a441






## How It Works

```
React (frontend)          FastAPI (backend)           RAG Pipeline
─────────────────         ──────────────────          ─────────────────
Upload Resume    ──────►  /upload_resume/    ──────►  PDF → Chunks → FAISS
Upload About Me  ──────►  /upload_about_me/  ──────►  PDF/TXT → Chunks → FAISS
Company Info     ──────►  /generate/         ──────►  Agent retrieves context
Job Description  ──────►                              from both stores → LLM
                                                      generates cover letter
Download PDF     ◄──────  /download_pdf/     ◄──────  Clean text → Styled PDF
```

The ReAct agent decides which tools to call and what to search for — it may query the resume for skills, then the about_me document for motivation, and combine everything into a tailored letter.

## Features

- **Document Upload** — upload resume (PDF) and personal motivation file (PDF/TXT)
- **URL Scraping** — paste a link to company page or job posting, and the app extracts text automatically. Falls back to manual input if scraping fails
- **RAG-based Generation** — agent searches uploaded documents for relevant context using FAISS vector similarity search
- **PDF Export** — download the cover letter as a styled PDF with EB Garamond font
- **Copy to Clipboard** — one-click copy of the generated text

## Tech Stack

**Frontend:** React, Vite

**Backend:** FastAPI, Uvicorn

**AI/ML:** LangChain, LangGraph, Ollama (Llama 3.1:8b), HuggingFace Embeddings (all-MiniLM-L6-v2), FAISS

**Other:** BeautifulSoup (web scraping), ReportLab (PDF generation)

## Project Structure

```
job_application_assistant/
├── backend/
│   ├── fonts/                 # EB Garamond font files
│   ├── uploads/               # Uploaded documents (gitignored)
│   ├── main.py                # FastAPI endpoints
│   ├── rag.py                 # RAG pipeline, agent, tools
│   ├── prompts.py             # LLM prompt templates
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   ├── DataInput.jsx
│   │   │   └── CoverLetterResult.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- [Ollama](https://ollama.ai/) installed

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/job-application-assistant.git
cd job-application-assistant
```

### 2. Start Ollama and pull the model

```bash
ollama serve
```

In a separate terminal:

```bash
ollama pull llama3.1:8b
```

### 3. Set up the backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Start the backend

```bash
uvicorn main:app --reload
```

Backend runs at http://localhost:8000. API docs at http://localhost:8000/docs.

### 5. Set up and start the frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:5173.

### Summary — 3 terminals running

| Terminal | Command | URL |
|----------|---------|-----|
| 1 | `ollama serve` | localhost:11434 |
| 2 | `uvicorn main:app --reload` | localhost:8000 |
| 3 | `npm run dev` | localhost:5173 |

## Usage

1. Open http://localhost:5173
2. Upload your **resume** (PDF)
3. Upload your **About Me** file (PDF or TXT) — personal motivation, stories, values
4. Add **company info** — paste text or load from URL
5. Add **job description** — paste text or load from URL
6. Click **Generate Cover Letter**
7. Copy the result or **Download as PDF**

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload_resume/` | Upload and index resume |
| POST | `/upload_about_me/` | Upload and index about_me file |
| POST | `/scrape/` | Extract text from URL |
| POST | `/generate/` | Generate cover letter |
| POST | `/download_pdf/` | Download letter as PDF |
| POST | `/upload_template/` | Upload a DOCX resume template |
| POST | `/fill_template//` | Fill the uploaded DOCX template |
| POST | `/download_filled_resume/` | Download the filled resume DOCX |

## License

MIT
