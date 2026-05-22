# config.py
"""Configuration constants for the RAG pipeline.

Centralizes model names and chunking parameters
so they can be changed in one place.
"""

import re
import os


EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama3.1:8b"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

PLACEHOLDER_PATTERN = re.compile(r"\{\{(\w+)\}\}")
NAMESPACE = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

CORS_ORIGINS = ["http://localhost:5173"]

GITHUB = "https://api.github.com"
