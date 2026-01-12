from app.models.schemas import AgentState
from app.utils.config import MAX_HISTORY_WINDOW
from langchain_core.runnables import RunnableConfig
from app.chains.requirement_chain import build_requirement_chain
from app.utils.text_processing import format_requirements
from langchain_core.messages import AIMessage


async def requirement_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Agent Node: Asks questions to gather more requirements.
    Uses English prompts.
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

    # Do NOT overwrite 'answer' from recommendation_node
    # Instead, we just append the question to the message history
    # The final output to user will be: Recommendation + Follow-up Question

    # We need to ensure the final answer combines both if they exist
    previous_answer = state.get("answer", "")
    final_answer = (
        f"{previous_answer}\n\n{response_text}" if previous_answer else response_text
    )

    return {
        # "messages": [AIMessage(content=response_text)], <-- REMOVED
        "answer": final_answer,
        "path": new_path,
    }
