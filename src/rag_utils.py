# src/rag_utils.py

import os
import faiss  # type: ignore
import pickle
import numpy as np
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

load_dotenv()

# --- Paths ---
CHUNKS_DIR = os.path.join(os.path.dirname(__file__), "..", "chunks")
INDEX_FILE = os.path.join(CHUNKS_DIR, "catalogo.index")
DOCS_FILE = os.path.join(CHUNKS_DIR, "catalogo.pkl")

# --- Embeddings + Memoria global ---
_embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
_index = None
_docs: list[Document] = []

def load_index():
    """Carga el índice FAISS y los documentos embebidos desde disco."""
    global _index, _docs

    if not os.path.exists(INDEX_FILE) or not os.path.exists(DOCS_FILE):
        raise RuntimeError("❌ No se encontraron los archivos de embeddings. Ejecutá castrol_loader.py primero.")

    with open(DOCS_FILE, "rb") as f:
        _docs = pickle.load(f)

    _index = faiss.read_index(INDEX_FILE)  # type: ignore

def get_relevant_context(query: str, k: int = 3) -> str:
    """
    Busca los k chunks más relevantes del catálogo Castrol
    que se relacionan con la consulta del usuario.
    """
    global _index, _docs

    if _index is None or not _docs:
        load_index()

    query_vector = _embeddings.embed_query(query)
    query_vector_np = np.array([query_vector]).astype("float32")

    distances, indices = _index.search(query_vector_np, k)
    results = [ _docs[i].page_content for i in indices[0] ]
    return "\n".join(results)