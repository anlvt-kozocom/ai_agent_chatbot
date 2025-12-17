from typing import TypedDict, List, Annotated, Literal, Dict, Any
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    State schema for the Q&A Agent.
    """
    messages: Annotated[List[BaseMessage], add_messages]
    answer: str | None
    route: Literal["product_info", "requirement", "recommendation", "general"] | None
    requirements: Dict[str, Any] | None
    next_step: str | None
    
    # New fields for language support
    original_language: str | None # e.g., "vi", "en"
    translated_query: str | None # Query in English
    path: List[str] | None # Trace of visited nodes
