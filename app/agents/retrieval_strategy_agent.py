from typing import Any, Dict
from langchain_core.runnables import RunnableConfig
from app.models.schemas import AgentState, RetrievalStrategy


def define_retrieval_strategy(state: AgentState) -> RetrievalStrategy:
    """
    Core logic to decide retrieval strategy based on route and query.
    This is pure logic, separable from the node handler.
    """
    route = state.get("route", "GENERAL")
    query = state.get("standalone_query") or ""
    query_lower = query.lower()
    requirements = state.get("requirements", {}) or {}

    # Defaults
    strategy = "NO_RAG"
    top_k = 4
    rerank = False
    filters: Dict[str, Any] = {}
    reason = "Default strategy"

    if route == "GENERAL":
        strategy = "NO_RAG"
        reason = "General conversation logic does not require RAG."

    elif route == "COMPARISON":
        strategy = "MULTI_PRODUCT"
        top_k = 10  # Increased for better multi-product coverage after dedup
        rerank = True
        reason = "Comparison requires fetching info for multiple products."

    elif route == "RECOMMENDATION":
        strategy = "HYBRID"

        # Count how many conditions are specified
        conditions_count = 0
        if requirements.get("brand"):
            conditions_count += 1
        if requirements.get("price") or requirements.get("budget"):
            conditions_count += 1
        if requirements.get("usage"):
            # Handle both string and list usage
            usage = requirements.get("usage")
            if isinstance(usage, list) and len(usage) > 0:
                conditions_count += len(
                    usage
                )  # Multiple usage needs count as multiple conditions
            elif isinstance(usage, str):
                conditions_count += 1

        # Adjust top_k based on complexity
        if conditions_count >= 3:
            # Multi-condition query: need more candidates for better filtering
            top_k = 15
        else:
            top_k = 10  # Broad initial search

        rerank = True
        # Convert requirements to filters if possible
        # This is a placeholder for mapping requirements -> metadata filters
        if requirements:
            filters = requirements
        reason = f"Recommendation needs filtering + semantic search. ({conditions_count} conditions detected)"

    elif route == "PRODUCT_INFO":
        # Distinguish between SQL_LOOKUP (specific fields) and VECTOR_SEARCH (general info)

        # Heuristic for SQL/Structured data
        sql_keywords = [
            "stock",
            "color",
            "ram",
            "storage",
            "màu",
            "dung lượng",
        ]

        if any(k in query_lower for k in sql_keywords):
            strategy = "SQL_LOOKUP"
            top_k = 1
            reason = "Query asks for specific structured attribute."
        else:
            strategy = "VECTOR_SEARCH"
            top_k = 4
            rerank = True  # Enable Precision Stage Reranking
            reason = "Query asks for general product information."

    return {
        "strategy": strategy,
        "top_k": top_k,
        "rerank": rerank,
        "filters": filters,
        "reason": reason,
    }


async def retrieval_strategy_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Node that determines the retrieval strategy.
    """
    print("--- Entering Retrieval Strategy Node ---")
    strategy_decision = define_retrieval_strategy(state)

    print(
        f"DEBUG: Retrieval Strategy -> {strategy_decision['strategy']} ({strategy_decision['reason']})"
    )

    current_path = state.get("path") or []
    new_path = current_path + ["retrieval_strategy_node"]

    return {"retrieval_strategy": strategy_decision, "path": new_path}
