import os
import time
from typing import List, Optional
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()


class HybridWarrantyRetriever(BaseRetriever):
    """Hybrid retriever combining FAISS and BM25 for warranty documents."""

    retrievers: List[BaseRetriever]
    weights: List[float]
    k: int = 4
    rrf_k: int = 60

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        scores = {}

        for retriever, weight in zip(self.retrievers, self.weights):
            docs = retriever.invoke(query)

            for rank, doc in enumerate(docs):
                key = str(id(doc))
                if key not in scores:
                    scores[key] = {"doc": doc, "score": 0.0}
                scores[key]["score"] += weight / (self.rrf_k + rank + 1)

        ranked = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
        return [x["doc"] for x in ranked[: self.k]]


class WarrantyRAGService:
    """
    Separate RAG service for warranty policy documents.
    Completely isolated from the phone product RAG system.
    """

    def __init__(
        self,
        data_dir: str = "data/warranty",
        index_dir: str = "data/warranty_vector_store",
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

    def initialize(self, reload_data: bool = False):
        """
        Initialize the warranty RAG service.
        If reload_data is True, rebuild the vector store from warranty documents.
        Otherwise, load from disk if available.
        """
        index_exists = os.path.exists(os.path.join(self.index_dir, "index.faiss"))
        if reload_data or not index_exists:
            print("Warranty RAG: Building warranty vector store from documents...")
            self._build_index()
        else:
            print("Warranty RAG: Loading existing warranty vector store...")
            try:
                self._load_index()
            except Exception as e:
                print(f"Warranty RAG: Failed to load index ({e}), rebuilding...")
                self._build_index()

        self._setup_retriever()

    def _load_warranty_documents(self) -> List[Document]:
        """Load warranty documents from the warranty directory."""
        documents = []

        if not os.path.exists(self.data_dir):
            print(f"Warning: Warranty data directory not found: {self.data_dir}")
            return documents

        # Load both Vietnamese and English warranty files
        for filename in os.listdir(self.data_dir):
            if not filename.endswith(".txt"):
                continue

            filepath = os.path.join(self.data_dir, filename)

            # Determine language from filename
            language = "vi" if "vi" in filename else "en"

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Create document with metadata
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": filename,
                        "language": language,
                        "doc_type": "warranty_policy",
                    },
                )
                documents.append(doc)
                print(f"Loaded warranty document: {filename} ({language})")

            except Exception as e:
                print(f"Error loading {filename}: {e}")

        return documents

    def _build_index(self):
        """Build the warranty vector store from warranty documents."""
        # Load warranty documents
        docs = self._load_warranty_documents()

        if not docs:
            print("Warning: No warranty documents found!")
            return

        print(f"Loaded {len(docs)} warranty documents")

        # Split documents into chunks for better retrieval
        # Use smaller chunks for warranty docs since they're policy text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", ". ", " ", ""]
        )

        chunks = []
        for doc in docs:
            doc_chunks = text_splitter.split_documents([doc])
            chunks.extend(doc_chunks)

        print(f"Created {len(chunks)} chunks from warranty documents")

        if not chunks:
            print("Warning: No chunks created from warranty documents!")
            return

        # Create vector store with embeddings
        try:
            print("Embedding warranty documents...")
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)

            # Save to disk
            os.makedirs(self.index_dir, exist_ok=True)
            self.vector_store.save_local(self.index_dir)
            print(f"Warranty vector store saved to {self.index_dir}")

        except Exception as e:
            print(f"Error building warranty vector store: {e}")
            raise

    def _load_index(self):
        """Load the warranty vector store from disk."""
        self.vector_store = FAISS.load_local(
            self.index_dir, self.embeddings, allow_dangerous_deserialization=True
        )
        print("Warranty vector store loaded successfully")

    def _setup_retriever(self):
        """Setup hybrid retriever for warranty documents."""
        if not self.vector_store:
            print(
                "Warning: Warranty vector store not initialized. Retriever will not work."
            )
            return

        # Create FAISS retriever
        faiss_retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})

        try:
            # Extract all documents for BM25
            all_docs = []
            if hasattr(self.vector_store, "docstore") and hasattr(
                self.vector_store.docstore, "_dict"
            ):
                all_docs = list(self.vector_store.docstore._dict.values())

            if not all_docs:
                # Fallback: retrieve a large number of docs
                all_docs = self.vector_store.similarity_search(
                    " ", k=min(100, self.vector_store.index.ntotal)
                )

            if all_docs:
                # Create BM25 retriever
                bm25_retriever = BM25Retriever.from_documents(all_docs)
                bm25_retriever.k = 4

                # Create hybrid retriever
                self.retriever = HybridWarrantyRetriever(
                    retrievers=[faiss_retriever, bm25_retriever],
                    weights=[0.7, 0.3],
                    k=4,
                )
                print("Warranty hybrid retriever setup complete")
            else:
                print("Warning: Could not retrieve docs for BM25. Using FAISS only.")
                self.retriever = faiss_retriever

        except Exception as e:
            print(
                f"Error setting up warranty hybrid retriever: {e}. Falling back to FAISS only."
            )
            self.retriever = faiss_retriever

    async def retrieve(
        self, query: str, language: Optional[str] = None, top_k: int = 4
    ) -> List[Document]:
        """
        Retrieve relevant warranty documents for the given query.

        Args:
            query: The user's warranty-related query
            language: Optional language filter ("vi" or "en")
            top_k: Number of documents to retrieve

        Returns:
            List of relevant warranty documents
        """
        if not self.vector_store:
            print("Warranty vector store not initialized.")
            return []

        try:
            # Use vector store for retrieval with language filter
            search_kwargs = {"k": top_k}

            # Add language filter if specified
            if language:
                search_kwargs["filter"] = {"language": language}

            # Retrieve documents
            docs = await self.vector_store.asimilarity_search(query, **search_kwargs)

            # Post-filter by language if filter didn't work
            if language:
                docs = [doc for doc in docs if doc.metadata.get("language") == language]

            return docs[:top_k]

        except Exception as e:
            print(f"Error retrieving warranty documents: {e}")
            return []


# Singleton instance for warranty RAG service
warranty_rag_service = WarrantyRAGService()
