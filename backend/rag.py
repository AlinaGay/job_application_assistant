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


def generate_cover_letter(about_me_text: str, job_text) -> str:
    if not vector_store:
        return "Please, upload information about you."

    query = f"Experience, skills and values for job position: {job_text[:200]}"
    docs = vector_store.similarity_search(query, k=4)
    resume_context = "\n\n".join(doc.page_content for doc in docs)

    messages = [
        {
            "role": "system",
            "content": True
        },
        {
            "role": "user",
            "content": "Write a cover letter."
        }
    ]

    response = llm.invoke(messages)
    return response.context
