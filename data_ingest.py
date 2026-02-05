import os
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Эту функцию вызывает кнопка в приложении
def ingest_data(file_path):
    if not os.path.exists(file_path):
        return

    print(f"--- Индексация файла: {os.path.basename(file_path)} ---")
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    for doc in documents:
        doc.metadata["source"] = os.path.basename(file_path)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000, 
        chunk_overlap=400,
        separators=["\nСтатья ", "\nГлава ", "\n\n", "\n", " "]
    )
    chunks = text_splitter.split_documents(documents)
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    # Добавляем в существующую базу без удаления старого
    db_dir = "c:/Users/Николай/.gemini/antigravity/44fz/data/chroma_db"
    db = Chroma(persist_directory=db_dir, embedding_function=embeddings)
    db.add_documents(chunks)
    print(f"--- Файл добавлен в базу. ---")

# Эту функцию вызывает ручной запуск в терминале
def ingest_all_data(data_dir, db_dir):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    # ПЕРЕСОЗДАНИЕ базы для чистоты (только при ручном запуске)
    if os.path.exists(db_dir):
        shutil.rmtree(db_dir)
    os.makedirs(db_dir, exist_ok=True)
    
    db = Chroma(persist_directory=db_dir, embedding_function=embeddings)
    
    for file in os.listdir(data_dir):
        if file.endswith(".pdf"):
            full_path = os.path.join(data_dir, file)
            ingest_data(full_path)

if __name__ == "__main__":
    BASE_DIR = "c:/Users/Николай/.gemini/antigravity/44fz"
    ingest_all_data(os.path.join(BASE_DIR, "data"), os.path.join(BASE_DIR, "data/chroma_db"))
