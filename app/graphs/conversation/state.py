from typing import List, TypedDict, Optional


class Message(TypedDict):
    role: str
    content: str


class ConversationState(TypedDict):
    """
    Typed state for the conversation graph.

    All fields are explicit and non-dynamic as required.
    """

    conversation_id: str
    user_message: str
    assistant_message: str
    messages: List[Message]
    context: str  # Added context field for RAG
    summary: str # Added summary field
