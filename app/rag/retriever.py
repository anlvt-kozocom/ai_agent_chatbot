from typing import List, Any
from langchain_core.documents import Document

class HybridEnsembleRetriever:
    """
    A hybrid retriever that combines multiple retrievers (e.g., Vector + BM25)
    using Reciprocal Rank Fusion (RRF).
    """
    def __init__(self, retrievers: List[Any], weights: List[float], k: int = 4, rrf_k: int = 60):
        self.retrievers = retrievers
        self.weights = weights
        self.k = k
        self.rrf_k = rrf_k

    def get_relevant_documents(self, query: str) -> List[Document]:
        scores = {}

        for retriever, weight in zip(self.retrievers, self.weights):
            # Check if retriever is async or sync, invoke appropriately
            # Here we assume sync .invoke() or .get_relevant_documents() is available
            # langchain standard is invoke()
            try:
                docs = retriever.invoke(query)
            except AttributeError:
                docs = retriever.get_relevant_documents(query)
                
            for rank, doc in enumerate(docs):
                key = doc.page_content
                # RRF score calculation
                scores[key] = scores.get(key, 0) + weight / (self.rrf_k + rank + 1)

        # Sort by score desc
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top k documents
        # Note: We reconstruct Document objects. Metadata might be lost if not handled.
        # For this specific implementation based on llm_gemini.py, it only kept page_content.
        return [Document(page_content=c) for c, _ in ranked[: self.k]]

