from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


def get_windowed_history(messages: List[BaseMessage], k: int = 10) -> str:
    """
    Returns the last k messages formatted string for prompt context.

    Args:
        messages: List of conversation messages
        k: Number of messages to keep (default 10)

    Returns:
        Formatted history string
    """
    if not messages:
        return ""

    # Take last k messages
    windowed_messages = messages[-k:]

    history_lines = []
    for msg in windowed_messages:
        prefix = "User" if isinstance(msg, HumanMessage) else "Assistant"
        # Avoid including system messages if any, or check specific types
        if isinstance(msg, (HumanMessage, AIMessage)):
            history_lines.append(f"{prefix}: {msg.content}")

    return "\n".join(history_lines)
