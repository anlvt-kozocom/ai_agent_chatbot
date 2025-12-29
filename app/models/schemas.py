from typing import TypedDict, List, Annotated, Literal, Dict, Any
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


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
