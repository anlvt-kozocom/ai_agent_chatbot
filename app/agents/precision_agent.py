from langchain_core.runnables import RunnableConfig
from app.models.schemas import AgentState
from app.services.rag_service import rag_service


async def precision_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Precision Stage Node:
    - Refines candidates from Recall Stage.
    - Applies Reranking, Filtering, Deduplication.
    - Stores final precision docs in state.
    """
    print("--- Entering Precision Node ---")
    recall_docs = state.get("recall_docs", [])
    retrieval_strategy = state.get("retrieval_strategy", {})

    # Determine query for Reranking context
    query = state.get("standalone_query")
    if not query and state.get("messages"):
        query = state.get("messages")[-1].content

    # Check if requirements exist (Recommendation flow)
    requirements = state.get("requirements", {})
    if requirements:
        # Combine requirements for context if available
        pass

    precision_docs = await rag_service.precision(
        docs=recall_docs, strategy_config=retrieval_strategy, query=query
    )

    return {
        "precision_docs": precision_docs,
        "path": (state.get("path") or []) + ["precision_node"],
    }
