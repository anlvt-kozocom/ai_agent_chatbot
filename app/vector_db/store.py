import os
import asyncio
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import VectorStore

def initialize_vector_store(all_chunks, model_name: str = 'models/text-embedding-004') -> VectorStore:
    """
    Creates and returns a FAISS vector store from documents.
    """
    # Fix for asyncio loop issue in some environments if needed, 
    # but generally libraries should handle their own loops.
    # Kept from original code if relevant for specific envs.
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        pass # No running loop, safe to create new if needed elsewhere

    api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyBbxQ2lVTJEVaW5rXwn3SH5C4WXINoNQMo")
    
    
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set")

    embeddings = GoogleGenerativeAIEmbeddings(
        model=model_name,
        google_api_key=api_key,
        task_type="retrieval_document"
    )
    
    # Create Vector Store
    # Check if vector store exists locally
    if os.path.exists("faiss_index"):
        vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    else:
        # Create Vector Store
        # Note: User requested to remove batching logic
        vector_store = FAISS.from_documents(all_chunks, embeddings)
        # Save vector store locally
        vector_store.save_local("faiss_index")
            
    return vector_store

