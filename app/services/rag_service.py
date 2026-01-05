import os
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
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
    def __init__(
        self,
        data_dir: str = "data/clean",
        index_dir: str = "data/vector_store",
    ):
        self.data_dir = data_dir
        self.index_dir = index_dir
        self.embedding_provider = os.getenv("EMBEDDING_PROVIDER", "google")
        # Configure embeddings based on provider
        if self.embedding_provider == "openai":
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY environment variable is not set")
            model_name = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
            self.embeddings = OpenAIEmbeddings(
                model=model_name, openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        else:
            embedding_model = os.getenv(
                "GOOGLE_EMBEDDING_MODEL", "models/text-embedding-004"
            )
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=embedding_model,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                task_type="retrieval_document",
            )
        self.vector_store: Optional[FAISS] = None
        self.retriever: Optional[BaseRetriever] = None

        # Initialize small LLM for reranking (cheap model)
        # Using 4o-mini or gemini-flash logic based on env
        if self.embedding_provider == "openai":
            self.rerank_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        else:
            self.rerank_llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash", temperature=0
            )

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
            print(
                f"Processing batch {i // batch_size + 1}/{(total_chunks + batch_size - 1) // batch_size}..."
            )

            retry_count = 0
            max_retries = 3

            while retry_count < max_retries:
                try:
                    if self.vector_store is None:
                        self.vector_store = FAISS.from_documents(batch, self.embeddings)
                    else:
                        self.vector_store.add_documents(batch)
                    break  # Success
                except Exception as e:
                    retry_count += 1
                    print(
                        f"Error processing batch (Attempt {retry_count}/{max_retries}): {e}"
                    )
                    time.sleep(2 * retry_count)  # Exponential backoff

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
            self.index_dir, self.embeddings, allow_dangerous_deserialization=True
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
            if hasattr(self.vector_store, "docstore") and hasattr(
                self.vector_store.docstore, "_dict"
            ):
                all_docs = list(self.vector_store.docstore._dict.values())

            if not all_docs:
                # Fallback: retrieve a large number of docs
                # Warning: This is not ideal for large datasets but works for small internal data
                all_docs = self.vector_store.similarity_search(
                    " ", k=min(100, self.vector_store.index.ntotal)
                )

            if all_docs:
                bm25_retriever = BM25Retriever.from_documents(all_docs)
                bm25_retriever.k = 4

                self.retriever = HybridEnsembleRetriever(
                    retrievers=[faiss_retriever, bm25_retriever],
                    weights=[0.7, 0.3],
                    k=4,
                )
            else:
                print("Warning: Could not retrieve docs for BM25. Using FAISS only.")
                self.retriever = faiss_retriever

        except Exception as e:
            print(
                f"Error setting up hybrid retriever: {e}. Falling back to FAISS only."
            )
            self.retriever = faiss_retriever

    async def recall(
        self, strategy: str, query: str, top_k: int = 20, language: Optional[str] = None
    ) -> List[Document]:
        """
        Recall Stage: Broadly retrieve potentially relevant documents.
        Maximized for recall, not precision.
        """
        if not self.vector_store:
            print("Vector store not initialized.")
            return []

        search_kwargs = {"k": top_k}
        if language:
            search_kwargs["filter"] = {"language": language}

        docs = []
        if strategy == "NO_RAG":
            return []

        elif strategy == "SQL_LOOKUP":
            # Simulate SQL by strict vector search + filtering (if we had specific metadata)
            # For recall, we still want to grab a few candidates
            docs = await self.vector_store.asimilarity_search(query, **search_kwargs)

        else:
            # VECTOR_SEARCH, HYBRID, MULTI_PRODUCT
            # For now, default to Vector Search as the base for Recall
            # (Hybrid logic from existing code could be adapted here if strictly needed)
            docs = await self.vector_store.asimilarity_search(query, **search_kwargs)

        return docs

    async def precision(
        self, docs: List[Document], strategy_config: Dict[str, Any], query: str = ""
    ) -> List[Document]:
        """
        Precision Stage: Refine candidates.
        - Deduplicate
        - Rule-Based Scoring (Metadata)
        - LLM Reranking (Cheap)
        """
        if not docs:
            return []

        # 1. Deduplicate (by content hash)
        unique_docs = {}
        for doc in docs:
            # Simple dedup key: first 100 chars
            key = doc.page_content[:100]
            if key not in unique_docs:
                unique_docs[key] = {"doc": doc, "score": 0.0, "reason": ""}

        candidates = list(unique_docs.values())
        print(f"DEBUG: Precision -> Deduplicated to {len(candidates)} candidates.")

        # 2. Rule-Based Scoring (Metadata)
        filters = strategy_config.get("filters", {})

        for item in candidates:
            doc = item["doc"]
            metadata = doc.metadata

            # Brand Match
            target_brand = filters.get("brand")
            if (
                target_brand
                and str(target_brand).lower() in str(metadata.get("brand", "")).lower()
            ):
                item["score"] += 5.0
                item["reason"] += "[Brand Match] "

            # Price Match (Heuristic)
            target_price = filters.get("price")
            if target_price:
                if str(target_price) in doc.page_content:
                    item["score"] += 3.0
                    item["reason"] += "[Price Mention] "

        # 3. LLM Reranking
        rerank = strategy_config.get("rerank", False)
        # Trigger if rerank=True, even for 0 candidates (handled above), but max 20 to save cost
        if rerank and 0 < len(candidates) <= 20:
            print("DEBUG: Precision -> Triggering LLM Reranking...")
            try:
                # Prepare batch context
                doc_texts = []
                for i, item in enumerate(candidates):
                    # Truncate content for speed/cost
                    content_snippet = item["doc"].page_content[:400].replace("\n", " ")
                    doc_texts.append(f"Doc {i}: {content_snippet}")

                context_str = "\n".join(doc_texts)

                prompt = f'''You are a relevance ranker. Rank the following documents based on their relevance to the query: "{query}".
Return ONLY the Document IDs (e.g., "Doc 0", "Doc 1") of the top 5 most relevant documents, in order of relevance.
If a document is irrelevant, do not include it.

Documents:
{context_str}'''

                response = await self.rerank_llm.ainvoke(prompt)
                response_text = response.content
                print(f"DEBUG: Rerank Output: {response_text[:100]}...")

                import re

                matches = re.findall(r"Doc (\d+)", response_text)

                rank_score_boost = 10.0
                for rank, doc_idx_str in enumerate(matches):
                    try:
                        idx = int(doc_idx_str)
                        if 0 <= idx < len(candidates):
                            boost = rank_score_boost - rank
                            if boost < 1:
                                boost = 1
                            candidates[idx]["score"] += boost
                            candidates[idx]["reason"] += f"[LLM Rank {rank + 1}] "
                    except ValueError:
                        continue

            except Exception as e:
                print(f"Warning: LLM Reranking failed: {e}")

        # 4. Selection
        candidates.sort(key=lambda x: x["score"], reverse=True)

        # Debug Log
        for i, c in enumerate(candidates[:3]):
            print(f"DEBUG: Top {i + 1}: Score={c['score']}, Reason={c['reason']}")

        final_top_k = strategy_config.get("top_k", 4)
        top_candidates = [x["doc"] for x in candidates[:final_top_k]]

        return top_candidates

    # Deprecated or Internal Wrapper
    def get_retriever(self, language: Optional[str] = None):
        # Kept for backward compatibility if any legacy code calls it,
        # but new flow should use recall()
        return self.vector_store.as_retriever() if self.vector_store else None


# Singleton instance
rag_service = RAGService()
