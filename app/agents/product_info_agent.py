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
    print("--- Entering Product Info Node ---")
    messages = state.get("messages", [])
    if not messages:
        return {"answer": "No question found."}

    # Use standalone query for Retrieval (handles "it", "that", etc.)
    query = state.get("standalone_query") or messages[-1].content
    language = state.get("language", "en")  # Default to english if not set

    # Slice history to window to avoid token overflow
    # history = messages[-(MAX_HISTORY_WINDOW + 1) : -1] # DEPRECATED

    # Get Strategy from State (Set by Retrieval Strategy Node)
    retrieval_strategy = state.get("retrieval_strategy", {})
    strategy_type = retrieval_strategy.get("strategy", "VECTOR_SEARCH")

    print(
        f"DEBUG: Product Info Node using pre-retrieved docs via strategy: {strategy_type}"
    )

    # USE PRECISION DOCS FROM STATE
    docs = state.get("precision_docs", [])

    print(f"DEBUG: Product Info Node received {len(docs)} precision_docs")

    # Format context
    context = format_docs(docs) if docs else "No additional product information found."

    # Generate Compressed Conversation Context
    from app.services.memory_service import compress_context

    conversation_context = compress_context(state)

    # 2. Call Chain
    chain = build_product_info_chain()

    response_text = await chain.ainvoke(
        {
            "question": query,
            "context": context,
            "conversation_context": conversation_context,
            "language": language,
        },
        config=config,
    )

    current_path = state.get("path") or []
    new_path = current_path + ["product_info_node"]

    return {
        "answer": response_text,
        "path": new_path,
    }
