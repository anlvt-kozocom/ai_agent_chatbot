from typing import TypedDict, List, Annotated, Literal, Dict, Any
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class RetrievalStrategy(TypedDict):
    """
    Structured object defining HOW retrieval should be performed.
    """

    strategy: Literal[
        "NO_RAG", "SQL_LOOKUP", "VECTOR_SEARCH", "HYBRID", "MULTI_PRODUCT"
    ]
    top_k: int
    rerank: bool
    filters: Dict[str, Any] | None
    reason: str


class WorkingMemory(TypedDict):
    """
    Structured state of the current conversation optimization.
    READ-WRITE: The agent updates this as it learns more about the user.
    """

    intent: (
        Literal[
            "GENERAL",
            "PRODUCT_INFO",
            "COMPARISON",
            "RECOMMENDATION",
            "REQUIREMENT_GATHERING",
        ]
        | None
    )
    intent_confidence: float
    # Frozen means we are confident in the intent and won't re-classify until user changes topic
    intent_frozen: bool

    # Extracted entities and constraints
    budget_range: Dict[str, int] | None  # e.g. {"min": 0, "max": 15000000}
    preferred_brands: List[str] | None
    product_category: str | None  # e.g. "smartphone", "laptop" (currently only phone)
    usage_context: List[str] | None  # e.g. ["gaming", "photography"]
    specific_products: List[str] | None  # e.g. ["iPhone 15", "Samsung S24"]

    # Routing
    current_route: str | None


class SummaryMemory(TypedDict):
    """
    Compressed summary of the conversation history.
    READ-ONLY (mostly): Updated periodically, not every turn if unchanged.
    """

    summary_text: str  # Concise text summary
    key_decisions: List[str]  # e.g. "User rejected iPhone 13 due to price"
    topics_covered: List[str]


class AgentState(TypedDict):
    """
    State schema for the Q&A Agent.
    """

    messages: Annotated[List[BaseMessage], add_messages]
    answer: str | None
    route: (
        Literal[
            "product_info", "requirement", "recommendation", "comparison", "general"
        ]
        | None
    )
    requirements: Dict[str, Any] | None
    next_step: str | None

    # New fields for language support
    language: str | None  # e.g., "vi", "en", "ja"
    original_language: str | None  # Deprecated but kept for compatibility if needed
    translated_query: str | None  # Deprecated
    standalone_query: str | None  # Resolved query with context from history
    path: List[str] | None  # Trace of visited nodes
    retrieval_strategy: RetrievalStrategy | None

    # Memory Layers
    working_memory: WorkingMemory | None
    summary_memory: SummaryMemory | None

    # RAG Pipeline State
    recall_docs: List[Any] | None  # Raw candidates from Recall Stage
    precision_docs: List[Any] | None  # Refined docs from Precision Stage
