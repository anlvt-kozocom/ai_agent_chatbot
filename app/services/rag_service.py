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
from app.services.llm import get_llm

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

        # Initialize LLM for reranking using the central factory
        # This ensures we use the configured provider (OpenAI/Google) and model
        self.rerank_llm = get_llm(temperature=0)

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
        self,
        strategy: str,
        query: str,
        top_k: int = 20,
        language: Optional[str] = None,
        candidate_ids: Optional[List[str]] = None,
    ) -> List[Document]:
        """
        Recall Stage: Broadly retrieve potentially relevant documents.
        Maximized for recall, not precision.
        """
        if not self.vector_store:
            print("Vector store not initialized.")
            return []

        search_kwargs = {"k": top_k}

        # Build filter
        metadata_filter = {}
        if language:
            metadata_filter["language"] = language

        # If candidate_ids are provided, we must use them.
        # FAISS in LangChain usually takes a dict for exact match.
        # For a list of IDs, we might need to filter after retrieval if the DB is small,
        # or use a more sophisticated filter if the vectorstore supports it.
        # Here we retrieve slightly more and filter manually to ensure correctness across FAISS versions.

        if candidate_ids:
            # If we have a short list of candidates, we can increase top_k to ensure we find them
            # but ideally the vector store would support ID filtering.
            actual_top_k = min(
                top_k * 5 + len(candidate_ids), 100
            )  # Increased cap for safety
            search_kwargs["k"] = actual_top_k

        docs = []
        if strategy == "NO_RAG":
            return []

        # Execute search

        results = await self.vector_store.asimilarity_search(query, **search_kwargs)

        # Post-filter by language and candidate_ids
        filtered_docs = []
        for doc in results:
            # Language filter
            if language and doc.metadata.get("language") != language:
                continue

            # ID filter
            if candidate_ids:
                doc_id = str(doc.metadata.get("product_id"))
                if doc_id not in candidate_ids:
                    continue
                else:
                    pass

            filtered_docs.append(doc)
            if len(filtered_docs) >= top_k:
                break

        return filtered_docs

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

        # 1. Deduplicate by product identity (not content similarity)
        # Use product_id if available, otherwise brand+model combination
        # This ensures different products are NOT incorrectly deduplicated
        unique_docs = {}
        for doc in docs:
            # Priority 1: Use product_id if available (most reliable)
            product_id = doc.metadata.get("product_id")
            if product_id:
                key = f"id_{product_id}"
            else:
                # Priority 2: Use brand + model combination
                brand = doc.metadata.get("brand", "")
                model = doc.metadata.get("model", "")
                if brand and model:
                    key = f"{brand}_{model}"
                else:
                    # Fallback: Use content hash (for documents without metadata)
                    key = doc.page_content[:100]

            if key not in unique_docs:
                unique_docs[key] = {"doc": doc, "score": 0.0, "reason": ""}

        candidates = list(unique_docs.values())

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

            # Price Match (Numeric & Range)
            target_price_raw = filters.get("price")
            product_price = metadata.get("price_int", 0)

            if target_price_raw:
                try:
                    target_price_str = (
                        str(target_price_raw).lower().replace(".", "").replace(",", "")
                    )
                    import re

                    # Handle multipliers
                    multiplier = 1
                    if (
                        "trieu" in target_price_str
                        or "triệu" in target_price_str
                        or "tr" in target_price_str
                        or "m" in target_price_str
                    ):
                        # Check if "m" is not part of "ram" or "mah" (simple check: if it ends with m or space m)
                        # Safer to just look for "triệu" or "tr" mostly, "m" can be ambiguous.
                        # But let's support explicit 'm' for million if distinct.
                        if "triệu" in target_price_str or "tr" in target_price_str:
                            multiplier = 1000000
                        elif (
                            "m" in target_price_str
                            and "mah" not in target_price_str
                            and "ram" not in target_price_str
                        ):
                            multiplier = 1000000

                    # Extract number
                    num_match = re.search(r"(\d+)", target_price_str)
                    price_num = int(num_match.group(1)) * multiplier if num_match else 0

                    if (
                        "under" in target_price_str
                        or "<" in target_price_str
                        or "duoi" in target_price_str
                        or "dưới" in target_price_str
                    ):
                        if product_price > 0 and product_price <= price_num:
                            item["score"] += 5.0
                            item["reason"] += "[Price Under Limit] "
                    elif (
                        "over" in target_price_str
                        or ">" in target_price_str
                        or "tren" in target_price_str
                        or "trên" in target_price_str
                    ):
                        if product_price > 0 and product_price >= price_num:
                            item["score"] += 5.0
                            item["reason"] += "[Price Over Limit] "
                    else:
                        # Approximate match (within 20%)
                        if product_price > 0 and (
                            price_num * 0.8 <= product_price <= price_num * 1.2
                        ):
                            item["score"] += 5.0
                            item["reason"] += "[Price Match] "
                except Exception as e:
                    # Fallback to text match
                    # print(f"Price Parse Error: {e}")
                    if str(target_price_raw) in doc.page_content:
                        item["score"] += 3.0
                        item["reason"] += "[Price Text Match] "

            # RAM Match
            target_ram = filters.get("ram")
            if target_ram:
                # heuristic: extraction returns "8GB", metadata has numeric 8
                import re

                ram_match = re.search(r"(\d+)", str(target_ram))
                if ram_match:
                    target_ram_val = int(ram_match.group(1))
                    product_ram = metadata.get("ram_gb", 0)
                    if product_ram == target_ram_val:
                        item["score"] += 4.0
                        item["reason"] += "[RAM Match] "
                elif str(target_ram).lower() in doc.page_content.lower():
                    item["score"] += 3.0
                    item["reason"] += "[RAM Text Match] "

            # Storage Match
            target_storage = filters.get("storage")
            if target_storage:
                if str(target_storage).lower() in doc.page_content.lower():
                    item["score"] += 4.0
                    item["reason"] += "[Storage Match] "

            # Color Match
            target_color = filters.get("color")
            if target_color:
                # Loose text match for color
                if str(target_color).lower() in doc.page_content.lower():
                    item["score"] += 3.0
                    item["reason"] += "[Color Match] "

        # 3. LLM Reranking
        rerank = strategy_config.get("rerank", False)
        # Trigger if rerank=True, even for 0 candidates (handled above), but max 20 to save cost
        if rerank and 0 < len(candidates) <= 20:
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
