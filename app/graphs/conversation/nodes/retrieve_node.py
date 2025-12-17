from typing import Any, Protocol
import logging

from app.graphs.conversation.state import ConversationState
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class RetrieverProtocol(Protocol):
    """
    Protocol for the retriever to ensure type safety.
    """
    def invoke(self, input: str) -> Any:
        ...

def retrieve_node(retriever: RetrieverProtocol):
    """
    Factory to create a retrieval node.
    """
    async def _node(state: ConversationState) -> dict:
        query = state.get("user_message", "")
        thread_id = state.get("conversation_id", "unknown")
        
        logger.info(f"[Thread: {thread_id}] Retrieving documents for query: {query}")
        
        # Call the retriever
        docs = retriever.invoke(query)

        # Format documents into a single context string
        context = "\n\n".join(d.page_content for d in docs)
        logger.info(f"[Thread: {thread_id}] Retrieved {len(docs)} docs. Context length: {len(context)}")

        # Update state with the retrieved context
        # This replaces the old context with the new one relevant to the CURRENT query.
        return {
            "context": context
        }

    return _node
