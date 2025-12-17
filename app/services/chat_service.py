from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional, Protocol, Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END

from app.agents.assistant_agent import AssistantAgent
from app.graphs.conversation.state import ConversationState
from app.graphs.conversation.nodes.user_message_node import user_message_node
from app.graphs.conversation.nodes.assistant_node import assistant_node
from app.graphs.conversation.nodes.format_node import format_node
from app.graphs.conversation.nodes.retrieve_node import retrieve_node
from app.graphs.conversation.nodes.summarize_node import summarize_node
from app.graphs.conversation.nodes.currency_converter_node import currency_converter_node

# Import RAG components
from app.vector_db.loader import load_data_from_folder
from app.vector_db.store import initialize_vector_store
from app.rag.factory import get_retriever


logger = logging.getLogger(__name__)


# --- Singleton for Retriever to avoid re-indexing on every request ---
_GLOBAL_RETRIEVER = None
_GLOBAL_MEMORY = None # Singleton MemorySaver

def get_global_retriever(refresh: bool = False):
    global _GLOBAL_RETRIEVER
    
    # Check environment variable to force refresh on startup
    force_refresh_env = os.getenv("RAG_FORCE_REFRESH", "false").lower() == "true"
    
    # If refresh is explicitly requested OR environment forces it (and we haven't initialized yet)
    should_refresh = refresh or (force_refresh_env and _GLOBAL_RETRIEVER is None)

    if _GLOBAL_RETRIEVER is None or should_refresh:
        logger.info("Initializing global retriever (refresh=%s, env_force=%s)...", should_refresh, force_refresh_env)
        try:
            # 1. Load data
            all_chunks = load_data_from_folder()
            if not all_chunks:
                logger.warning("No data found in 'data/' folder. RAG will return empty results.")
                # Pass empty list to vector store might fail depending on implementation
                # But let's proceed to see.
            
            # 2. Create Vector Store
            # using 'models/text-embedding-004' as per main.py
            if all_chunks:
                # If refreshing, we might want to force re-indexing (ignore existing local index)
                # But initialize_vector_store currently prefers loading from disk.
                # We need to modify initialize_vector_store to support force rebuild OR
                # we delete the local index folder before calling it.
                if should_refresh and os.path.exists("faiss_index"):
                    import shutil
                    logger.info("Removing existing faiss_index for refresh...")
                    shutil.rmtree("faiss_index")

                vector = initialize_vector_store(all_chunks, 'models/text-embedding-004')
                # 3. Create Retriever
                _GLOBAL_RETRIEVER = get_retriever(vector)
                logger.info("Global retriever initialized successfully.")
            else:
                 # Fallback for empty data
                logger.warning("Empty data chunks, skipping vector store initialization.")
                class DummyRetriever:
                    def invoke(self, query: str):
                        return []
                _GLOBAL_RETRIEVER = DummyRetriever()

        except Exception as e:
            logger.error(f"Failed to initialize retriever: {e}")
            # Fallback: Create a dummy retriever that returns empty list
            class DummyRetriever:
                def invoke(self, query: str):
                    return []
            _GLOBAL_RETRIEVER = DummyRetriever()

    return _GLOBAL_RETRIEVER

def get_global_memory():
    """
    Singleton for MemorySaver to ensure state persistence across requests
    during the application lifetime.
    """
    global _GLOBAL_MEMORY
    if _GLOBAL_MEMORY is None:
        _GLOBAL_MEMORY = MemorySaver()
    return _GLOBAL_MEMORY

class ChatService:
    """
    Orchestrates the conversation graph for chat interactions.
    This is the application service layer (no HTTP concerns here).
    """

    def __init__(self, agent: AssistantAgent, retriever, checkpointer: MemorySaver) -> None:
        self._agent = agent
        self._retriever = retriever
        self._checkpointer = checkpointer
        self._graph = self._build_graph()

    def reload_retriever(self):
        """
        Force reload the global retriever.
        """
        logger.info("Reloading RAG data...")
        self._retriever = get_global_retriever(refresh=True)
        # We need to rebuild the graph or at least update the node that uses the retriever.
        # But the graph is built with a closure over `self._retriever`.
        # Since `self._retriever` is a reference, if we update `self._retriever` here, does the closure see the new object?
        # No, the closure `retrieve_node(self._retriever)` binds the object at creation time.
        # We need to re-build the graph.
        self._graph = self._build_graph()
        logger.info("RAG data reloaded and graph rebuilt.")

    def _build_graph(self):
        """
        Build the LangGraph conversation flow.
        Only orchestration here, no business logic.
        """
        workflow = StateGraph(ConversationState)

        # 1. Start Node: Receive message (process user input)
        workflow.add_node("user_message", user_message_node)
        
        # 2. Retrieval Node: Fetch context
        workflow.add_node("retrieve", retrieve_node(self._retriever))
        
        # 3. Assistant Node: LLM generation
        workflow.add_node("assistant", assistant_node(self._agent))
        
        # 4. Format Node: Markdown Formatting
        workflow.add_node("formatter", format_node)

        # 5. Summarize Node: Compress history (optional)
        workflow.add_node("summarize", summarize_node)

        # 6. Currency Converter Node: Fix prices
        workflow.add_node("currency_converter", currency_converter_node)

        # Define Flow
        workflow.set_entry_point("user_message")
        
        # user_message -> retrieve -> assistant -> (condition) -> summarize -> END
        workflow.add_edge("user_message", "retrieve")
        workflow.add_edge("retrieve", "assistant")
        
        def route_currency(state: ConversationState):
            messages = state.get("messages", [])
            if not messages:
                return "summarize"
            
            last_msg = messages[-1].get("content", "")
            # Check for common foreign currency indicators or patterns
            # Note: This is a simple heuristic.
            foreign_indicators = ["USD", "Rupee", "EUR", "INR", "$", "€", "₹"]
            
            # If any foreign indicator is present AND "VND" is NOT the only currency mentioned (simplified)
            # Actually, just checking if foreign indicators exist is safer. 
            # Even if it says "10 USD (250,000 VND)", the user wants "250,000 VND" only.
            if any(indicator in last_msg for indicator in foreign_indicators):
                return "currency_converter"
            
            return "summarize"

        workflow.add_conditional_edges(
            "assistant",
            route_currency,
            {
                "currency_converter": "currency_converter",
                "summarize": "summarize"
            }
        )
        
        workflow.add_edge("currency_converter", "summarize")
        workflow.add_edge("summarize", END)

        app = workflow.compile(checkpointer=self._checkpointer)
    
        return app

    async def handle_chat(
        self,
        conversation_id: Optional[str],
        user_message: str,
    ) -> Dict[str, Any]:
        """
        Run the conversation graph for a single user message.
        """
        thread_id = conversation_id or "default"

        initial_state: Dict[str, Any] = {
            "conversation_id": thread_id,
            "user_message": user_message,
            "assistant_message": "",
        }

        logger.info("Running graph for thread_id=%s", thread_id)

        result = await self._graph.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": thread_id}},
        )

        logger.info("Graph completed for thread_id=%s", thread_id)

        return {
            "conversation_id": result["conversation_id"],
            "assistant_message": result["assistant_message"],
            "state": result,
        }


def get_chat_service() -> ChatService:
    """
    Dependency provider for FastAPI.
    """
    # In a real app you might use DI container / settings
    agent = AssistantAgent()
    retriever = get_global_retriever()
    checkpointer = get_global_memory()
    return ChatService(agent=agent, retriever=retriever, checkpointer=checkpointer)
