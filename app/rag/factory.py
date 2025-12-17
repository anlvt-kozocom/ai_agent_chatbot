from langchain_core.vectorstores import VectorStore

def get_retriever(vector_store: VectorStore, k_vector: int = 4, k_bm25: int = 8, k_final: int = 4):
    """
    Constructs the retriever. 
    Currently using only Vector Search (FAISS) to avoid rank_bm25 dependency.
    """
    # 1. Vector Search Retriever
    # Simply return the vector store as a retriever
    return vector_store.as_retriever(search_kwargs={"k": k_final})
