import os
import shutil
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL

from ingestion.file_handlers import load_file_to_docs

# -------------------------
# Build Index from Files
# -------------------------
def ingest_files(file_paths, persist_dir):
    """Load documents, split, embed, and save FAISS index."""
    all_docs = []

    for file_path in file_paths:
        try:
            docs = load_file_to_docs(file_path)
            all_docs.extend(docs)
        except Exception as e:
            print(f"[ERROR] Failed to process {file_path}: {e}")

    if not all_docs:
        raise ValueError("No documents could be ingested.")

    # Split text into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    split_docs = splitter.split_documents(all_docs)

    # Create embeddings
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    # Build FAISS index
    index = FAISS.from_documents(split_docs, embeddings)

    # Save FAISS index
    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)
    index.save_local(persist_dir)

    return index


# -------------------------
# Load Existing Index
# -------------------------
def load_index(persist_dir):
    """Load FAISS index if available."""
    if not os.path.exists(persist_dir):
        return None
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    try:
        index = FAISS.load_local(
            persist_dir,
            embeddings,
            allow_dangerous_deserialization=True 
        )
        return index
    except Exception as e:
        print(f"[ERROR] Failed to load FAISS index: {e}")
        return None
