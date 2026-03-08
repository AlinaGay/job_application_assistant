import os
import requests

from bs4 import BeutifulSoap
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import FAISS


embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

vector_store = None


def process_resume(file_path: str) -> int:
    global vector_store

    loader = PyPDFLoader(file_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    )
    chunks = splitter.split_documents(docs)
    vector_store = FAISS.from_documents(chunks, embeddings)

    return len(chunks)
