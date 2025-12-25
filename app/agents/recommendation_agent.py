from app.models.schemas import AgentState
from app.chains.recommendation_chain import build_recommendation_chain
from app.services.rag_service import rag_service
from app.prompts.rag_prompts import format_docs
from app.utils.text_processing import format_requirements
from langchain_core.messages import AIMessage


async def recommendation_node(state: AgentState) -> dict:
    """
    Agent Node: Provides product recommendations based on gathered requirements.
    """
    requirements = state.get("requirements", {})

    # 1. Construct search query from requirements (Already extracted in English/Unified format)
    search_query = format_requirements(requirements)
    if not requirements:
        # Fallback to translated query
        search_query = state.get("translated_query", "")

    # 2. Retrieve documents (English)
    retriever = rag_service.get_retriever()
    if not retriever:
        return {"answer": "System not ready."}

    docs = await retriever.ainvoke(search_query)
    context = format_docs(docs)
    # 3. Call Recommendation Chain (English)
    chain = build_recommendation_chain()

    response_text = await chain.ainvoke(
        {"requirements": search_query, "context": context}
    )

    current_path = state.get("path") or []
    new_path = current_path + ["recommendation_node"]

    return {
        "messages": [AIMessage(content=response_text)],
        "answer": response_text,
        "path": new_path,
    }
