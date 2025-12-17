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
    response_text = await chain.ainvoke({
        "current_requirements": formatted_requirements,
        "history": messages
    })
    
    current_path = state.get("path") or []
    new_path = current_path + ["requirement_node"]

    return {
        "messages": [AIMessage(content=response_text)],
        "answer": response_text,
        "path": new_path
    }
