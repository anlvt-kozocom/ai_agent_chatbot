from app.models.schemas import AgentState
from app.chains.sales_chain import build_sales_chain
from app.chains.summarization_chain import build_summarization_chain
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig


async def sales_synthesis_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Agent Node: Synthesizes the final answer into a sales persona response.
    """
    answer = state.get("answer")
    language = state.get("language", "en")

    if not answer:
        # Fallback if no answer generated
        answer = "I'm sorry, I couldn't find the information you need."

    chain = build_sales_chain()

    # Generate sales response
    sales_response = await chain.ainvoke(
        {"answer": answer, "language": language}, config=config
    )

    # Summarize the response for history context (Context Optimization)
    summary_chain = build_summarization_chain()
    summary = await summary_chain.ainvoke({"text": sales_response}, config=config)

    # Update state
    # We return the FULL 'answer' so the API can return it to the user.
    # But we return 'messages' containing the SUMMARY so LangGraph adds the summary to history.
    return {
        "messages": [AIMessage(content=summary)],
        "answer": sales_response,  # API uses this
        "path": ["sales_synthesis_node"],
    }
