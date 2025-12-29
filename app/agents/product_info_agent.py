from app.models.schemas import AgentState
from app.utils.config import MAX_HISTORY_WINDOW
from langchain_core.runnables import RunnableConfig
from app.chains.product_info_chain import build_product_info_chain
from app.services.rag_service import rag_service
from app.prompts.rag_prompts import format_docs
from langchain_core.messages import AIMessage


async def product_info_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Agent Node: Provides detailed product information (RAG).
    Uses query and language from state.
    """
    messages = state.get("messages", [])
    if not messages:
        return {"answer": "No question found."}

    # Use standalone query for Retrieval (handles "it", "that", etc.)
    query = state.get("standalone_query") or messages[-1].content
    language = state.get("language", "en")  # Default to english if not set

    # Slice history to window to avoid token overflow
    # Take last MAX_HISTORY_WINDOW messages excluding the current query (which is at -1)
    history = messages[-(MAX_HISTORY_WINDOW + 1) : -1]

    # 1. Retrieve (Filtered by Language)
    # Pass language to get_retriever for filtering
    retriever = rag_service.get_retriever(language=language)

    if not retriever:
        return {"answer": "Search system not ready."}

    docs = await retriever.ainvoke(query)
    context = format_docs(docs)

    # 2. Call Chain
    # The chain prompt should ideally adapt to language or the model should handle it.
    # Current prompt is in English but model is multilingual (GPT/Gemini).
    # Ideally we should also instruct the model to answer in the specific language.
    # For now, we assume the model follows the language of the context/query or we can add instructions.

    chain = build_product_info_chain()

    # We might want to pass target language to the prompt if needed,
    # but let's stick to existing chain interface for now.
    response_text = await chain.ainvoke(
        {
            "question": query,
            "context": context,
            "history": history,
            "history": history,
            "language": language,
        },
        config=config,
    )

    current_path = state.get("path") or []
    new_path = current_path + ["product_info_node"]

    return {
        # "messages": [AIMessage(content=response_text)],  <-- REMOVED to avoid history pollution
        "answer": response_text,
        "path": new_path,
    }
