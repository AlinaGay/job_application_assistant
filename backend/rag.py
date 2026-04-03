# rag.py

import os
import requests

from bs4 import BeautifulSoup
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import FAISS
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent

from config import EMBEDDING_MODEL, LLM_MODEL, CHUNK_SIZE, CHUNK_OVERLAP
from prompts import cover_letter_prompt


embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
llm = ChatOllama(model=LLM_MODEL)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
)

resume_store = None
about_me_store = None


def _load_and_split(file_path: str):
    """Load a PDF or TXT file and split into chunks."""
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path)
    docs = loader.load()
    return splitter.split_documents(docs)


def process_resume(file_path: str) -> int:
    """Index resume into FAISS vector store for similarity search."""
    global resume_store

    chunks = _load_and_split(file_path)
    resume_store = FAISS.from_documents(chunks, embeddings)

    return len(chunks)


def process_about_me(file_path: str) -> int:
    """Index about_me document into FAISS vector store for similarity search."""
    global about_me_store

    chunks = _load_and_split(file_path)
    about_me_store = FAISS.from_documents(chunks, embeddings)

    return len(chunks)


@tool
def retrieve_resume(query: str) -> str:
    """Search for relevant experience and skills from the candidate's resume."""
    if not resume_store:
        return "Resume not uploaded."
    docs = resume_store.similarity_search(query, k=4)
    return "\n\n".join(doc.page_content for doc in docs)


@tool
def retrieve_about_me(query: str) -> str:
    """Search for candidate's motivation, personal stories and values."""
    if not about_me_store:
        return "About_me not uploaded."
    docs = about_me_store.similarity_search(query, k=4)
    return "\n\n".join(doc.page_content for doc in docs)


tools = [retrieve_resume, retrieve_about_me]
agent = create_react_agent(llm, tools)


def generate_cover_letter(company_text: str, job_text: str) -> str:
    """Generate a cover letter using the ReAct agent.

    The agent autonomously retrieves relevant data from resume
    and about_me vector stores, then crafts a letter based on
    company info and job description.
    """
    if not resume_store:
        return "Please upload your resume first."
    if not about_me_store:
        return "Please upload About_me file first."

    system_text = cover_letter_prompt(company_text=company_text, job_text=job_text)

    result = agent.invoke({
        "messages": [
            {
                "role": "system",
                "content": system_text
            },
            {
                "role": "user",
                "content": "Write a cover letter."
            }
        ]
    })

    return result["messages"][-1].content
