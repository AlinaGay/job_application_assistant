# config.py
"""Configuration constants for the RAG pipeline.

Centralizes model names and chunking parameters
so they can be changed in one place.
"""

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama3.1:8b"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
