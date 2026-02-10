"""
Knowledge base ingestion script.
Loads markdown files and stores them in Chroma vector database.
"""
import os
import asyncio
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import get_settings

settings = get_settings()

# Knowledge base directory
KNOWLEDGE_DIR = Path(__file__).parent.parent.parent / "knowledge"


def load_documents():
    """Load all markdown files from knowledge directory."""
    loader = DirectoryLoader(
        str(KNOWLEDGE_DIR),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    return loader.load()


def split_documents(documents):
    """Split documents into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return splitter.split_documents(documents)


async def ingest_knowledge_base() -> int:
    """
    Ingest all markdown files from knowledge directory into Chroma.
    Returns the number of documents ingested.
    """
    # Ensure knowledge directory exists
    if not KNOWLEDGE_DIR.exists():
        KNOWLEDGE_DIR.mkdir(parents=True)
        return 0
    
    # Load and split documents
    documents = load_documents()
    if not documents:
        return 0
    
    chunks = split_documents(documents)
    
    # Create embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=settings.google_api_key
    )
    
    # Clear existing database and create new one
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=settings.chroma_persist_dir
    )
    
    return len(chunks)


if __name__ == "__main__":
    """Run ingestion manually."""
    import asyncio
    count = asyncio.run(ingest_knowledge_base())
    print(f"Ingested {count} document chunks")
