from app.models.schemas import AgentState
from app.utils.config import MAX_HISTORY_WINDOW
from langchain_core.runnables import RunnableConfig
from app.chains.requirement_chain import build_requirement_chain
from app.utils.text_processing import format_requirements
from langchain_core.messages import AIMessage


async def requirement_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Agent Node: Asks for brand when missing.
    User's response will be processed in the NEXT turn.
    """
    print("--- Entering Requirement Node ---")
    messages = state.get("messages", [])
    requirements = state.get("requirements", {})

    formatted_requirements = format_requirements(requirements)

    # Initialize the chain
    chain = build_requirement_chain()

    language = state.get("language", "en")

    # Invoke chain
    response_text = await chain.ainvoke(
        {
            "current_requirements": formatted_requirements,
            "history": messages[-MAX_HISTORY_WINDOW:],
            "language": language,
        },
        config=config,
    )

    current_path = state.get("path") or []
    new_path = current_path + ["requirement_node"]

    # Return only the brand question - user will answer in next turn
    return {
        "answer": response_text,
        "path": new_path,
    }
