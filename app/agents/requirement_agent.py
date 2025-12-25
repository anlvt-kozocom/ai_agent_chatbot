from app.models.schemas import AgentState
from app.chains.requirement_chain import build_requirement_chain
from app.utils.text_processing import format_requirements
from langchain_core.messages import AIMessage


async def requirement_node(state: AgentState) -> dict:
    """
    Agent Node: Asks questions to gather more requirements.
    Uses English prompts.
    """
    messages = state.get("messages", [])
    requirements = state.get("requirements", {})

    formatted_requirements = format_requirements(requirements)

    # Initialize the chain
    chain = build_requirement_chain()

    # Invoke chain
    response_text = await chain.ainvoke(
        {"current_requirements": formatted_requirements, "history": messages}
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
        "messages": [AIMessage(content=response_text)],
        "answer": final_answer,
        "path": new_path,
    }
