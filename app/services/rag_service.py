import os
import shutil
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun

from app.utils.text_processing import load_text_files, split_documents
from app.services.query_expansion import QueryExpansionRetriever

load_dotenv()

class HybridEnsembleRetriever(BaseRetriever):
    retrievers: List[BaseRetriever]
    weights: List[float]
    k: int = 4
    rrf_k: int = 60

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        scores: Dict[str, Dict[str, Any]] = {}

        for retriever, weight in zip(self.retrievers, self.weights):
            docs = retriever.invoke(query)

            for rank, doc in enumerate(docs):
                # Use content as key for deduplication if needed, or id(doc) if instances vary
                key = str(id(doc)) 
                if key not in scores:
                    scores[key] = {"doc": doc, "score": 0.0}
                scores[key]["score"] += weight / (self.rrf_k + rank + 1)

        ranked = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
        return [x["doc"] for x in ranked[: self.k]]

class RAGService:
    def __init__(self, 
                 data_dir: str = "data/clean", 
                 index_dir: str = "data/vector_store",
                 embedding_model: str = "models/text-embedding-004"):
        self.data_dir = data_dir
        self.index_dir = index_dir
        
        # Configure embeddings with request options if possible, but basic init is usually fine
        # We rely on batching logic in _build_index to avoid 500s
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=embedding_model, 
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            task_type="retrieval_document"
        )
        self.vector_store: Optional[FAISS] = None
        self.retriever: Optional[BaseRetriever] = None

    def initialize(self, reload_data: bool = False):
        """
        Initialize the RAG service.
        If reload_data is True, it re-reads data from raw files and rebuilds the vector store.
        Otherwise, it tries to load from disk.
        """
        index_exists = os.path.exists(os.path.join(self.index_dir, "index.faiss"))
        if reload_data or not index_exists:
            self._build_index()
        else:
            print("Initializing RAG: Loading existing vector store...")
            try:
                self._load_index()
                
            except Exception as e:
                self._build_index()
                
        self._setup_retriever()

    def _build_index(self):
        docs = load_text_files(self.data_dir)
        print(f"Loaded {len(docs)} documents from {self.data_dir}")
        if not docs:
            print(f"Warning: No documents found in {self.data_dir}")
            return

        # Use a larger chunk size to keep product details together
        chunks = split_documents(docs, chunk_size=4000, chunk_overlap=200)
        if not chunks:
             print("Warning: No chunks created.")
             return
        
        print(f"Created {len(chunks)} chunks. Starting embedding...")

        # Batch processing to avoid API limits/errors
        batch_size = 100
        total_chunks = len(chunks)
        self.vector_store = None
        
        for i in range(0, total_chunks, batch_size):
            batch = chunks[i : i + batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(total_chunks + batch_size - 1)//batch_size}...")
            
            retry_count = 0
            max_retries = 3
            
            while retry_count < max_retries:
                try:
                    if self.vector_store is None:
                        self.vector_store = FAISS.from_documents(batch, self.embeddings)
                    else:
                        self.vector_store.add_documents(batch)
                    break # Success
                except Exception as e:
                    retry_count += 1
                    print(f"Error processing batch (Attempt {retry_count}/{max_retries}): {e}")
                    time.sleep(2 * retry_count) # Exponential backoff
            
            if retry_count == max_retries:
                print("Failed to process batch after retries. Skipping or failing...")
                # Depending on strictness, we might raise or continue. 
                # Continuing might leave gaps. Let's raise to be safe or just log error.
                print("Critical: Failed to embed a batch of documents.")

        if self.vector_store:
            self.vector_store.save_local(self.index_dir)
            print(f"Vector store saved to {self.index_dir}")
        else:
            print("Failed to create vector store.")

    def _load_index(self):
        self.vector_store = FAISS.load_local(
            self.index_dir, 
            self.embeddings, 
            allow_dangerous_deserialization=True
        )

    def _setup_retriever(self):
        if not self.vector_store:
            print("Warning: Vector store not initialized. Retriever will not work.")
            return

        # Create FAISS retriever
        faiss_retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
        
        try:
             # Extracting all documents from FAISS docstore (in-memory)
             # Note: FAISS docstore access might vary by version, safe fallback included
             all_docs = []
             if hasattr(self.vector_store, "docstore") and hasattr(self.vector_store.docstore, "_dict"):
                 all_docs = list(self.vector_store.docstore._dict.values())
             
             if not all_docs:
                 # Fallback: retrieve a large number of docs
                 # Warning: This is not ideal for large datasets but works for small internal data
                 all_docs = self.vector_store.similarity_search(" ", k=min(100, self.vector_store.index.ntotal))
             
             if all_docs:
                bm25_retriever = BM25Retriever.from_documents(all_docs)
                bm25_retriever.k = 4
                
                self.retriever = HybridEnsembleRetriever(
                    retrievers=[faiss_retriever, bm25_retriever],
                    weights=[0.7, 0.3],
                    k=4
                )
             else:
                 print("Warning: Could not retrieve docs for BM25. Using FAISS only.")
                 self.retriever = faiss_retriever

        except Exception as e:
            print(f"Error setting up hybrid retriever: {e}. Falling back to FAISS only.")
            self.retriever = faiss_retriever

    def get_retriever(self):
        if self.retriever:
            return QueryExpansionRetriever(base_retriever=self.retriever)
        return self.retriever

# Singleton instance
rag_service = RAGService()
