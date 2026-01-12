from app.models.schemas import AgentState
from langchain_core.runnables import RunnableConfig
from app.chains.context_resolution_chain import get_context_resolution_chain
from app.utils.config import MAX_HISTORY_WINDOW
from app.utils.history_utils import get_windowed_history


async def context_resolution_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Node to resolve the latest user query into a standalone query based on history.
    """
    print("--- Entering Context Resolution Node ---")
    messages = state.get("messages", [])
    if not messages:
        return {"standalone_query": ""}

    current_query = messages[-1].content

    # If no history, the query is already standalone
    if len(messages) <= 1:
        return {
            "standalone_query": current_query,
            "path": state.get("path", []) + ["context_resolution_node"],
        }

    # Get history excluding the current message
    history_messages = messages[:-1]
    history_str = get_windowed_history(history_messages, k=MAX_HISTORY_WINDOW)

    if not history_str:
        return {
            "standalone_query": current_query,
            "path": state.get("path", []) + ["context_resolution_node"],
        }

    # Call chain to resolve context
    chain = get_context_resolution_chain()
    standalone_query = await chain.ainvoke(
        {"question": current_query, "history": history_str}, config=config
    )

    print(
        f"DEBUG: Context Resolution - Original: '{current_query}' -> Standalone: '{standalone_query}'"
    )

    return {
        "standalone_query": standalone_query,
        "path": state.get("path", []) + ["context_resolution_node"],
    }
