from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.models.schemas import AgentState
from app.agents.product_info_agent import product_info_node
from app.agents.requirement_agent import requirement_node
from app.agents.recommendation_agent import recommendation_node
from app.agents.comparison_agent import comparison_node
from app.agents.router_agent import router_node, general_node
from app.agents.sales_agent import sales_synthesis_node
from app.agents.context_resolution_agent import context_resolution_node
from app.agents.retrieval_strategy_agent import retrieval_strategy_node
from app.agents.price_agent import price_filtering_node
from app.agents.recall_agent import recall_node
from app.agents.precision_agent import precision_node


def route_decision(state: AgentState) -> str:
    """
    Conditional edge function to determine the next node based on the route and state.
    """
    route = state.get("route", "GENERAL")
    # Normalize just in case, though it should be uppercase from router
    if route:
        route = route.upper()

    if route == "PRODUCT_INFO":
        return "product_info_node"

    if route == "COMPARISON":
        return "comparison_node"

    if route == "GENERAL":
        return "general_node"

    if route == "RECOMMENDATION":
        return "recommendation_node"

    return "general_node"


def check_brand_requirement(state: AgentState) -> str:
    """
    Conditional edge function to check if brand is specified for RECOMMENDATION.

    IMPORTANT: Only applies brand requirement to RECOMMENDATION route.
    Other routes (COMPARISON, PRODUCT_INFO, GENERAL) proceed normally WITHOUT brand check.

    Priority logic:
    1. If NOT RECOMMENDATION route -> use normal routing (no brand check)
    2. If RECOMMENDATION && brand detected in query -> recommendation_node
    3. If RECOMMENDATION && no brand -> requirement_node
    """
    route = state.get("route", "GENERAL")
    if route:
        route = route.upper()

    # PRIORITY 1: For non-RECOMMENDATION routes, use normal routing
    # COMPARISON, PRODUCT_INFO, and GENERAL don't need brand requirement
    if route != "RECOMMENDATION":
        return route_decision(state)

    # PRIORITY 2: For RECOMMENDATION route, check if brand is present
    # Get current query to check for brand keywords
    messages = state.get("messages", [])
    current_query = messages[-1].content if messages else ""
    query_lower = current_query.lower()

    # Brand keyword detection
    brand_keywords = {
        "Apple": ["iphone", "apple", "táo khuyết"],
        "Samsung": ["samsung", "galaxy"],
        "Sony": ["sony", "xperia"],
        "Oppo": ["oppo"],
        "Xiaomi": ["xiaomi", "redmi", "poco"],
        "Vivo": ["vivo"],
        "Realme": ["realme"],
        "OnePlus": ["oneplus"],
        "Google": ["pixel", "google phone"],
        "Huawei": ["huawei"],
    }

    # Check if brand mentioned in current query
    brand_detected = False
    detected_brand_name = None
    for brand, keywords in brand_keywords.items():
        if any(kw in query_lower for kw in keywords):
            brand_detected = True
            detected_brand_name = brand

            break

    # PRIORITY 3: If brand detected in RECOMMENDATION query, proceed
    if brand_detected:
        return "recommendation_node"

    # PRIORITY 4: If RECOMMENDATION but no brand, ask for it

    return "requirement_node"


def route_after_retrieval(state: AgentState) -> str:
    """
    Conditional edge to skip Price Filtering for certain routes.
    """
    route = state.get("route", "GENERAL")
    if route:
        route = route.upper()

    if route == "GENERAL":
        return "general_node"

    if route == "PRODUCT_INFO":
        return "recall_node"

    # Default logic (RECOMMENDATION, COMPARISON, etc.) uses Price Filtering
    return "price_filtering_node"


def build_graph():
    """
    Constructs the LangGraph for the QA Agent with Multilingual Support.
    """
    checkpointer = MemorySaver()
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("context_resolution_node", context_resolution_node)
    workflow.add_node("router_node", router_node)
    workflow.add_node("retrieval_strategy_node", retrieval_strategy_node)
    workflow.add_node("price_filtering_node", price_filtering_node)
    workflow.add_node("recall_node", recall_node)
    workflow.add_node("precision_node", precision_node)
    workflow.add_node("product_info_node", product_info_node)
    workflow.add_node("recommendation_node", recommendation_node)
    workflow.add_node("comparison_node", comparison_node)
    workflow.add_node("general_node", general_node)
    workflow.add_node(
        "requirement_node", requirement_node
    )  # Brand requirement gathering
    workflow.add_node("sales_synthesis_node", sales_synthesis_node)  # Final synthesis

    # Define edges
    # Start -> Context Resolution -> Router
    workflow.add_edge(START, "context_resolution_node")
    workflow.add_edge("context_resolution_node", "router_node")

    # Router -> Retrieval Strategy (MANDATORY intermediate step)
    workflow.add_edge("router_node", "retrieval_strategy_node")

    # Retrieval Strategy -> Conditional Branching
    # PRODUCT_INFO and GENERAL skip price filtering logic
    workflow.add_conditional_edges(
        "retrieval_strategy_node",
        route_after_retrieval,
        {
            "price_filtering_node": "price_filtering_node",
            "recall_node": "recall_node",
            "general_node": "general_node",
        },
    )

    # Price Filtering -> Recall -> Precision
    workflow.add_edge("price_filtering_node", "recall_node")
    workflow.add_edge("recall_node", "precision_node")

    # Conditional edge from Precision Node (checks brand requirement for RECOMMENDATION only)
    workflow.add_conditional_edges(
        "precision_node",
        check_brand_requirement,
        {
            "product_info_node": "product_info_node",
            "recommendation_node": "recommendation_node",
            "comparison_node": "comparison_node",
            "general_node": "general_node",
            "requirement_node": "requirement_node",
        },
    )

    # Processing nodes -> Sales Synthesis -> End
    workflow.add_edge("product_info_node", "sales_synthesis_node")
    workflow.add_edge("comparison_node", "sales_synthesis_node")
    workflow.add_edge("recommendation_node", "sales_synthesis_node")
    # NOTE: requirement_node goes directly to END to allow re-evaluation on next turn
    workflow.add_edge("requirement_node", END)

    workflow.add_edge("general_node", "sales_synthesis_node")

    # Final step
    workflow.add_edge("sales_synthesis_node", END)

    return workflow.compile(checkpointer=checkpointer)
