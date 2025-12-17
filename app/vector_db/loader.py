import os
import logging
from typing import List

from langchain_community.document_loaders import (
    PyMuPDFLoader,
    Docx2txtLoader,
    TextLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

def load_data_from_folder(folder_path: str = "data") -> List[Document]:
    """
    Scans the folder and loads all .txt, .docx, .pdf .json files,
    then splits content into chunks.
    """
    if not os.path.exists(folder_path):
        logger.warning(f"Data folder '{folder_path}' does not exist.")
        return []

    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    all_chunks = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        logger.info(f"Loading file: {file_path}")
        
        docs = []
        try:
            if filename.endswith(".pdf"):
                loader = PyMuPDFLoader(file_path)
                docs = loader.load()
            elif filename.endswith(".docx"):
                loader = Docx2txtLoader(file_path)
                docs = loader.load()
            elif filename.endswith(".txt"):
                loader = TextLoader(file_path, encoding="utf-8")
                docs = loader.load()
            elif filename.endswith(".json"):
                loader = TextLoader(file_path)
                docs = loader.load()
            if docs:
                chunks = splitter.split_documents(docs)
                all_chunks.extend(chunks)
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            continue
            
    logger.info(f"Loaded and split {len(all_chunks)} chunks from '{folder_path}'.")
    return all_chunks

