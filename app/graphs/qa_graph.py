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

    requirements = state.get("requirements", {}) or {}

    if route == "PRODUCT_INFO":
        return "product_info_node"

    if route == "COMPARISON":
        return "comparison_node"

    if route == "GENERAL":
        return "general_node"

    # RECOMMENDATION route (previously handled requirement too)
    if route == "RECOMMENDATION":
        # STRICT REQUIREMENT: Must have brand
        if not requirements.get("brand"):
            return "requirement_node"

        return "recommendation_node"

    return "general_node"


def check_recommendation_status(state: AgentState) -> str:
    """
    Conditional edge after recommendation_node.
    Checks if requirements are sufficient to finish, or if we need to ask questions.
    """
    requirements = state.get("requirements", {})

    # Check for MANDATORY brand
    if not requirements.get("brand"):
        return "requirement_node"

    # Heuristic: At least one main criteria
    has_criteria = any(
        [
            requirements.get("price"),
            requirements.get("usage"),
            requirements.get("brand"),
            requirements.get("specs"),
            requirements.get("color"),
            requirements.get("storage"),
            requirements.get("ram"),
            requirements.get("battery"),
            requirements.get("screen"),
            requirements.get("camera"),
            requirements.get("processor"),
            requirements.get("gpu"),
        ]
    )

    if has_criteria:
        # Enough info -> Finish (Synthesize)
        return "sales_synthesis_node"
    else:
        # Not enough info -> Ask questions
        return "requirement_node"


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
    workflow.add_node("recall_node", recall_node)
    workflow.add_node("precision_node", precision_node)
    workflow.add_node("product_info_node", product_info_node)
    workflow.add_node("requirement_node", requirement_node)
    workflow.add_node("recommendation_node", recommendation_node)
    workflow.add_node("comparison_node", comparison_node)
    workflow.add_node("general_node", general_node)
    workflow.add_node("sales_synthesis_node", sales_synthesis_node)  # Final synthesis

    # Define edges
    # Start -> Context Resolution -> Router
    workflow.add_edge(START, "context_resolution_node")
    workflow.add_edge("context_resolution_node", "router_node")

    # Router -> Retrieval Strategy (MANDATORY intermediate step)
    workflow.add_edge("router_node", "retrieval_strategy_node")

    # Retrieval Strategy -> Recall -> Precision
    workflow.add_edge("retrieval_strategy_node", "recall_node")
    workflow.add_edge("recall_node", "precision_node")

    # Conditional edge from Precision Node (uses Route to determine next step)
    workflow.add_conditional_edges(
        "precision_node",
        route_decision,
        {
            "product_info_node": "product_info_node",
            "recommendation_node": "recommendation_node",
            "comparison_node": "comparison_node",
            "requirement_node": "requirement_node",
            "general_node": "general_node",
        },
    )

    # Processing nodes -> Sales Synthesis -> End
    workflow.add_edge("product_info_node", "sales_synthesis_node")
    workflow.add_edge("comparison_node", "sales_synthesis_node")
    workflow.add_edge("requirement_node", "sales_synthesis_node")

    # Conditional edge from Recommendation
    workflow.add_conditional_edges(
        "recommendation_node",
        check_recommendation_status,
        {
            "sales_synthesis_node": "sales_synthesis_node",
            "requirement_node": "requirement_node",
        },
    )

    workflow.add_edge("general_node", "sales_synthesis_node")

    # Final step
    workflow.add_edge("sales_synthesis_node", END)

    return workflow.compile(checkpointer=checkpointer)
