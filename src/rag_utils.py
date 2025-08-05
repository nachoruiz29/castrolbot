# rag_utils.py
import os
import faiss
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

_embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
_index = None
_docs = []

def load_index():
    global _index, _docs
    catalog_path = "castrol_docs/castrol_argentina_catalogo.txt"
    if not os.path.exists(catalog_path):
        return

    with open(catalog_path, "r", encoding="utf-8") as f:
        text = f.read()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)
    _docs = [Document(page_content=chunk) for chunk in chunks]
    vectors = [_embeddings.embed_query(doc.page_content) for doc in _docs]
    _index = faiss.IndexFlatL2(len(vectors[0]))
    _index.add(vectors)

def get_relevant_context(query: str, k=2):
    if _index is None:
        load_index()
    if _index is None:
        return ""
    query_vector = _embeddings.embed_query(query)
    distances, indices = _index.search([query_vector], k)
    return "\n".join([_docs[i].page_content for i in indices[0]])