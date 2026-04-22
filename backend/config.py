# config.py
"""Configuration constants for the RAG pipeline.

Centralizes model names and chunking parameters
so they can be changed in one place.
"""

import re


EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama3.1:8b"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

PLACEHOLDER_PATTERN = re.compile(r"\{\{(\w+)\}\}")
NAMESPACE = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
