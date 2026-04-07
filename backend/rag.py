# rag.py
"""RAG service for document indexing and cover letter generation.

Provides a RAGService class that manages FAISS vector stores
for resume and about_me documents, and uses a LangGraph ReAct agent
to generate personalized cover letters.
"""

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import FAISS
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent

from config import EMBEDDING_MODEL, LLM_MODEL, CHUNK_SIZE, CHUNK_OVERLAP
from prompts import cover_letter_prompt


class RAGServise:
    """Manages document indexing and cover letter generation.

    Stores resume and about_me documents in separate FAISS vector stores.
    Uses a ReAct agent with tools to retrieve relevant context
    and generate cover letters.
    """
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.llm = ChatOllama(model=LLM_MODEL)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )
        self.resume_store = None
        self.about_me_store = None
        self.agent = self._create_agent()

    def _load_and_split(self, file_path: str):
        """Load a PDF or TXT file and split into chunks."""
        if file_path.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path)
        docs = loader.load()
        return self.splitter.split_documents(docs)

    def _index_document(self, file_path: str) -> tuple[FAISS, int]:
        """Index a document into a new FAISS vector store."""
        chunks = self._load_and_split(file_path)
        store = FAISS.from_documents(chunks, self.embeddings)
        return store, len(chunks)

    def process_resume(self, file_path: str) -> int:
        """Index resume into FAISS vector store for similarity search."""
        self.resume_store, count = self._index_document(file_path)
        return count

    def process_about_me(self, file_path: str) -> int:
        """Index about_me into FAISS vector store for similarity search."""
        self.about_me_store, count = self._index_document(file_path)
        return count

    def _retrieve(self, store, query: str, label: str) -> str:
        """Search a vector store for relevant documents."""
        if not store:
            return f"{label} not uploaded."
        docs = store.similarity_search(query, k=4)
        return "\n\n".join(doc.page_content for doc in docs)

    def _create_agent(self):
        """Create the ReAct agent with retrieval tools."""

        @tool
        def retrieve_resume(query: str) -> str:
            """Search for relevant experience and skills from the resume."""
            return self._retrieve(self.resume_store, query, "Resume")

        @tool
        def retrieve_about_me(query: str) -> str:
            """Search for candidate's personal motivation."""
            return self._retrieve(self.about_me_store, query, "About Me")

        return create_react_agent(
            self.llm, [retrieve_resume, retrieve_about_me])

    def generate_cover_letter(self, company_text: str, job_text: str) -> str:
        """Generate a cover letter using the ReAct agent.

        The agent autonomously retrieves relevant data from resume
        and about_me vector stores, then crafts a letter based on
        company info and job description.
        """
        if not self.resume_store:
            return "Please upload your resume first."
        if not self.about_me_store:
            return "Please upload About_me file first."

        system_text = cover_letter_prompt(
            company_text=company_text, job_text=job_text)

        result = self.agent.invoke({
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


rag_service = RAGServise()
