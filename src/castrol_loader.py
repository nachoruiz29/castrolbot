import os
import faiss # type: ignore
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv
import pickle
# Cargar variables de entorno
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Rutas de carpetas
INPUT_DIR = "embeddings"
OUTPUT_DIR = "chunks"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Inicializar embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

def process_txt_file(filepath: str):
    filename = os.path.basename(filepath).replace(".txt", "")
    print(f"📄 Procesando: {filename}")

    # Leer texto
    with open(filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Chunking
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(raw_text)
    docs = [Document(page_content=chunk) for chunk in chunks]

    # Embeddings
    vectors = [embeddings.embed_query(doc.page_content) for doc in docs]
    dimension = len(vectors[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(vectors).astype("float32")) # type: ignore

    # Guardar archivos
    index_path = os.path.join(OUTPUT_DIR, f"{filename}.index")
    docs_path = os.path.join(OUTPUT_DIR, f"{filename}.pkl")

    faiss.write_index(index, index_path) # type: ignore
    with open(docs_path, "wb") as f:
        pickle.dump(docs, f)

    print(f"✅ Guardado: {index_path}, {docs_path}")

def run():
    for fname in os.listdir(INPUT_DIR):
        if fname.endswith(".txt"):
            full_path = os.path.join(INPUT_DIR, fname)
            process_txt_file(full_path)

if __name__ == "__main__":
    run()
