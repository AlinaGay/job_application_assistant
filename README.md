# Job Application Assistant

AI-powered toolkit for crafting personalized job application materials. Combines two workflows in one app:

- **Cover Letter Generator** — RAG-based agent that writes tailored cover letters from your resume, personal motivation, company info, and job description.
- **CV Customizer** — agentic resume template filler that uses GitHub MCP tools to pull real project data and tailors a DOCX resume to a specific job description.

Both workflows are powered by autonomous agents that decide which tools to call and what context to retrieve for each application.

## Demo

https://github.com/user-attachments/assets/64dab58f-dacf-4c34-8cf3-0d698948a441

## Architecture

React (frontend)          FastAPI (backend)           AI Pipeline
─────────────────         ──────────────────          ─────────────────────────
┌─ Cover Letter Flow ─┐
Upload Resume    ──────►  /upload_resume/    ──────►  │ PDF → FAISS index   │
Upload About Me  ──────►  /upload_about_me/  ──────►  │ PDF → FAISS index   │
Company + Job    ──────►  /generate/         ──────►  │ ReAct agent →       │
│ retrieve + LLM      │
└─────────────────────┘
┌─ CV Customizer ─────┐
Upload Template  ──────►  /upload_template/  ──────►  │ DOCX → placeholders │
Job Description  ──────►  /fill_template/    ──────►  │ Agent with tools:   │
│ • retrieve_resume   │
│ • GitHub MCP tools  │
│ → structured JSON   │
└─────────────────────┘
Download PDF     ◄──────  /download_pdf/     ◄──────  ReportLab
Download DOCX    ◄──────  /download_filled_resume/    docx-template


### Cover Letter Pipeline
The ReAct agent autonomously decides which document to query — it may pull skills from the resume, motivation from About Me, then combine everything into a grounded letter.

### CV Customizer Pipeline
The agent calls a combination of local RAG (`retrieve_resume`) and **GitHub MCP tools** (`repos_list`, `get_readme`, `get_repo_languages`) to assemble a project-backed EXPERIENCE section, then fills DOCX placeholders with structured JSON output.

## Features

- **Cover Letter Generation** — RAG-based, with citations grounded in your documents.
- **CV Customization** — fills a DOCX template with AI-generated content tailored to a job description, with EXPERIENCE backed by real GitHub projects via MCP.
- **GitHub Integration via MCP** — FastMCP server exposes GitHub API as tools the agent can call autonomously.
- **Document Upload** — resume (PDF), motivation file (PDF/TXT), DOCX template.
- **URL Scraping** — paste a link to a company page or job posting; falls back to manual input on failure.
- **PDF Export** — styled output with EB Garamond font.
- **Copy to Clipboard** — one-click copy of generated text.

## Tech Stack

**Frontend:** React, Vite

**Backend:** FastAPI, Uvicorn

**AI/ML:** LangChain, LangGraph, Ollama (Llama 3.1:8b), HuggingFace Embeddings (all-MiniLM-L6-v2), FAISS

**Tool integration:** FastMCP (Model Context Protocol server for GitHub tools)

**Other:** BeautifulSoup (web scraping), ReportLab (PDF), docx-template (DOCX filling)

## Architecture Decisions

- **Two FAISS stores instead of one** — separate indexes for resume (skills/experience) and About Me (motivation/values) keep retrieval focused and prevent cross-contamination of top-k results.
- **Local Ollama instead of API** — privacy by default (resume is personal data) and zero cost during iteration. Trade-off is quality and latency; production version would use Azure OpenAI with private endpoints.
- **MCP for GitHub instead of direct API calls** — standardized tool interface that the LLM can invoke via tool calling, decoupled from business logic. Same MCP server could be reused by any MCP-compatible client.
- **Structured output via Pydantic** — agent returns a JSON object validated against a schema, eliminating fragile regex parsing.
- **ReAct agent with LangGraph** — explicit state graph for tool-calling decisions; easier to debug and extend than a fixed chain.

## Project Structure

job_application_assistant/
├── backend/
│   ├── fonts/                 # EB Garamond font files
│   ├── uploads/               # Uploaded documents (gitignored)
│   ├── main.py                # FastAPI endpoints + lifespan
│   ├── rag.py                 # RAG pipelines, ReAct agent, tool wiring
│   ├── mcp_server.py          # FastMCP server exposing GitHub tools
│   ├── prompts.py             # LLM prompt templates (cover letter + template fill)
│   ├── utils.py               # PDF cleaning, scraping, placeholder discovery
│   ├── config.py              # App configuration (env vars)
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   ├── DataInput.jsx
│   │   │   ├── CoverLetterResult.jsx
│   │   │   └── TemplateUpload.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
└── README.md

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- [Ollama](https://ollama.ai/) installed
- GitHub Personal Access Token (for the MCP server, read-only `public_repo` scope is enough)

### 1. Clone the repository

\`\`\`bash
git clone https://github.com/YOUR_USERNAME/job-application-assistant.git
cd job-application-assistant
\`\`\`

### 2. Configure environment

Create `backend/.env`:

\`\`\`
GITHUB_TOKEN=ghp_your_token_here
GITHUB_USERNAME=your_github_handle
\`\`\`

### 3. Start Ollama and pull the model

\`\`\`bash
ollama serve
\`\`\`

In a separate terminal:

\`\`\`bash
ollama pull llama3.1:8b
\`\`\`

### 4. Set up the backend

\`\`\`bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

### 5. Start the backend

\`\`\`bash
uvicorn main:app --reload
\`\`\`

Backend runs at http://localhost:8000. API docs at http://localhost:8000/docs.

The MCP server starts automatically inside the backend lifespan — no separate process needed.

### 6. Set up and start the frontend

In a new terminal:

\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

Frontend runs at http://localhost:5173.

### Summary — 3 terminals running

| Terminal | Command | URL |
|----------|---------|-----|
| 1 | `ollama serve` | localhost:11434 |
| 2 | `uvicorn main:app --reload` | localhost:8000 |
| 3 | `npm run dev` | localhost:5173 |

## Usage

### Generate a Cover Letter

1. Open http://localhost:5173
2. Upload your **resume** (PDF)
3. Upload your **About Me** file (PDF or TXT) — personal motivation, stories, values
4. Add **company info** — paste text or load from URL
5. Add **job description** — paste text or load from URL
6. Click **Generate Cover Letter**
7. Copy the result or **Download as PDF**

### Customize a CV from a Template

1. Upload a **DOCX template** with placeholders like `{{ JOB_POSITION }}`, `{{ SUMMARY }}`, `{{ EXPERIENCE }}`
2. Provide the target **job description**
3. Click **Fill Template** — the agent calls `retrieve_resume` for personal context and GitHub MCP tools for project data
4. **Download** the filled DOCX

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload_resume/` | Upload and index resume |
| POST | `/upload_about_me/` | Upload and index About Me file |
| POST | `/scrape/` | Extract text from URL |
| POST | `/generate/` | Generate cover letter |
| POST | `/download_pdf/` | Download cover letter as PDF |
| POST | `/upload_template/` | Upload a DOCX resume template |
| POST | `/fill_template/` | Fill the uploaded DOCX template using AI + MCP tools |
| POST | `/download_filled_resume/` | Download the filled resume DOCX |

Interactive docs at http://localhost:8000/docs.

## Roadmap

- [ ] Hybrid search (BM25 + dense) for better retrieval on technical terms.
- [ ] Cross-encoder re-ranking on top-k results.
- [ ] Evaluation pipeline using RAGAS (faithfulness, context recall).
- [ ] Streaming responses to the frontend.
- [ ] Persist FAISS indexes between sessions.
- [ ] Multi-user support with per-user vector stores.

## License

MIT
