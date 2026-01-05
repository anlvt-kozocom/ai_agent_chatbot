from langchain_core.runnables import RunnableConfig
from app.models.schemas import AgentState
from app.services.rag_service import rag_service
from app.utils.text_processing import format_requirements


async def recall_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Recall Stage Node:
    - Broadly retrieves documents based on the strategy.
    - Maximizes recall (high top_k).
    - Stores raw docs in state.
    """
    retrieval_strategy = state.get("retrieval_strategy")
    if not retrieval_strategy:
        # Should have been set by retrieval_strategy_node
        retrieval_strategy = {"strategy": "VECTOR_SEARCH"}

    strategy_type = retrieval_strategy.get("strategy", "VECTOR_SEARCH")
    language = state.get("language", "en")

    # Determine the query
    # If requirements exist (Recommendation flow), construct query from them
    requirements = state.get("requirements", {})
    if requirements:
        query = format_requirements(requirements)
    else:
        # Use standalone query or fallback to last message
        query = state.get("standalone_query")
        if not query and state.get("messages"):
            query = state.get("messages")[-1].content

    if not query:
        print("Warning: No query found for Recall.")
        return {"recall_docs": []}

    print(f"DEBUG: Recall Stage -> Strategy: {strategy_type}, Query: {query[:50]}...")

    # Execute Recall
    # We use a higher top_k for recall to allow Precision stage to refine
    recall_top_k = 20  # Hardcoded 'wide' net, or derived from strategy * multiplier

    docs = await rag_service.recall(
        strategy=strategy_type, query=query, top_k=recall_top_k, language=language
    )

    print(f"DEBUG: Recall Stage -> Retrieved {len(docs)} documents.")

    return {"recall_docs": docs, "path": (state.get("path") or []) + ["recall_node"]}
