# rag.py

import os
import requests

from bs4 import BeautifulSoup
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import FAISS
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent

from prompts import cover_letter_prompt


embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

llm = ChatOllama(model="llama3.2")

vector_store = None


@tool
def retrieve_resume(query: str) -> str:
    """Search for relevant information from the candidate's resume."""
    if not vector_store:
        return "Resume was not uploaded."
    docs = vector_store.similarity_search(query, k=4)
    return "\n\n".join(doc.page_content for doc in docs)


@tool
def scrape_url(url: str) -> str:
    """Fetch and extract text content from a web page by URL."""
    try:
        headers = {"User-Agent": "CoverLetterApp/1.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        return text[:5000] if len(text) > 100 else "Failed to extract text."
    except Exception as error:
        return f"Loading error: {str(error)}"


tools = [retrieve_resume, scrape_url]
agent = create_react_agent(llm, tools)


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


def generate_cover_letter(company_text: str, about_me_text: str) -> str:
    if not vector_store:
        return "Please, upload information about you."

    system_text = cover_letter_prompt(
        company_text=company_text,
        about_me_text=about_me_text
    )

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
