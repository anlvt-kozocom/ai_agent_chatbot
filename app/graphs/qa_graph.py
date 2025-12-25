from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.models.schemas import AgentState
from app.agents.product_info_agent import product_info_node
from app.agents.requirement_agent import requirement_node
from app.agents.recommendation_agent import recommendation_node
from app.agents.router_agent import router_node, general_node
from app.agents.language_agent import (
    language_input_node,
    language_output_node,
)  # Import new nodes


def route_decision(state: AgentState) -> str:
    """
    Conditional edge function to determine the next node based on the route and state.
    """
    route = state.get("route", "general")
    requirements = state.get("requirements", {}) or {}

    if route == "product_info":
        return "product_info_node"

    if route == "general":
        return "general_node"

    # Both Recommendation and Requirement routes now go to recommendation_node first
    # BUT only if we have the BRAND.
    if route in ["recommendation", "requirement"]:
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

    # Heuristic: At least one main criteria (price, usage, brand)
    # Since brand is now mandatory, we technically always have criteria if we pass the first check.
    # But we keep this for robustness.
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
        # Enough info -> Finish
        return "language_output_node"
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
    workflow.add_node("language_input_node", language_input_node)  # Pre-processing
    workflow.add_node("router_node", router_node)
    workflow.add_node("product_info_node", product_info_node)
    workflow.add_node("requirement_node", requirement_node)
    workflow.add_node("recommendation_node", recommendation_node)
    workflow.add_node("general_node", general_node)
    workflow.add_node("language_output_node", language_output_node)  # Post-processing

    # Define edges
    # Start -> Detect Language -> Router
    workflow.add_edge(START, "language_input_node")
    workflow.add_edge("language_input_node", "router_node")

    # Conditional edge from Router
    workflow.add_conditional_edges(
        "router_node",
        route_decision,
        {
            "product_info_node": "product_info_node",
            "recommendation_node": "recommendation_node",
            "requirement_node": "requirement_node",
            "general_node": "general_node",
        },
    )

    # Processing nodes -> Language Output -> End
    workflow.add_edge("product_info_node", "language_output_node")
    workflow.add_edge("requirement_node", "language_output_node")

    # Conditional edge from Recommendation
    workflow.add_conditional_edges(
        "recommendation_node",
        check_recommendation_status,
        {
            "language_output_node": "language_output_node",
            "requirement_node": "requirement_node",
        },
    )

    workflow.add_edge("general_node", "language_output_node")

    workflow.add_edge("language_output_node", END)

    return workflow.compile(checkpointer=checkpointer)
