from app.models.schemas import AgentState
from app.chains.comparison_chain import build_comparison_chain
from app.services.rag_service import rag_service
from app.prompts.rag_prompts import format_docs
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig


async def comparison_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Agent Node: Compares product information (RAG).
    Uses query and language from state.
    """
    print("--- Entering Comparison Node ---")
    messages = state.get("messages", [])
    if not messages:
        return {"answer": "No question found."}

    # Use standalone query for Retrieval
    query = state.get("standalone_query") or messages[-1].content
    language = state.get("language", "en")

    # 1. Use Precision Docs from State
    docs = state.get("precision_docs", [])
    context = format_docs(docs)

    # 2. Call Chain
    chain = build_comparison_chain()

    response_text = await chain.ainvoke(
        {
            "question": query,
            "context": context,
            "language": language,
        },
        config=config,
    )

    current_path = state.get("path") or []
    new_path = current_path + ["comparison_node"]

    return {
        # "messages": [AIMessage(content=response_text)], <-- REMOVED
        "answer": response_text,
        "path": new_path,
    }
