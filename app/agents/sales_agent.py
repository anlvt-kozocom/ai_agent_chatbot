from app.models.schemas import AgentState
from app.chains.sales_chain import build_sales_chain
from app.chains.summarization_chain import build_summarization_chain
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig


async def sales_synthesis_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Agent Node: Synthesizes the final answer into a sales persona response.
    """
    print("--- Entering Sales Synthesis Node ---")
    answer = state.get("answer")
    language = state.get("language", "en")

    if not answer:
        # Fallback if no answer generated
        answer = "I'm sorry, I couldn't find the information you need."

    # Detect if source is Comparison
    path = state.get("path") or []
    is_comparison = "comparison_node" in path

    chain = build_sales_chain(is_comparison=is_comparison)

    # Generate sales response
    sales_response = await chain.ainvoke(
        {"answer": answer, "language": language}, config=config
    )
    # Summarize the response for history context (Context Optimization)
    summary_config = config.copy() if config else {}
    if "tags" not in summary_config:
        summary_config["tags"] = []
    summary_config["tags"].append("skip_stream")

    summary_chain = build_summarization_chain()
    summary = await summary_chain.ainvoke(
        {"text": sales_response}, config=summary_config
    )

    # NEW: Update Global Summary Memory
    from app.services.memory_service import summarize_conversation

    # We update summary memory based on current state (which has history BEFORE this response)
    # This prepares the summary for the NEXT turn.
    updated_summary_memory = await summarize_conversation(state, config=summary_config)
    # Update state
    # We return the FULL 'answer' so the API can return it to the user.
    # But we return 'messages' containing the SUMMARY so LangGraph adds the summary to history.
    return {
        "summary_memory": updated_summary_memory,
        "messages": [AIMessage(content=summary)],
        "answer": sales_response,  # API uses this
        "path": (state.get("path") or []) + ["sales_synthesis_node"],
    }
