from app.models.schemas import AgentState
from app.chains.product_info_chain import build_product_info_chain
from app.services.rag_service import rag_service
from app.prompts.rag_prompts import format_docs
from langchain_core.messages import AIMessage

async def product_info_node(state: AgentState) -> dict:
    """
    Agent Node: Provides detailed product information (RAG).
    Uses translated query (English).
    """
    messages = state.get("messages", [])
    if not messages:
        return {"answer": "No question found."}
    
    query = state.get("translated_query")
    if not query:
        query = messages[-1].content

    history = messages[:-1] # This might contain mixed languages, but acceptable for now.
    
    # 1. Retrieve (English Query -> English Docs)
    retriever = rag_service.get_retriever()
    if not retriever:
         return {"answer": "Search system not ready."}

    docs = await retriever.ainvoke(query)
    context = format_docs(docs)
    
    # 2. Call Chain (English Prompt)
    chain = build_product_info_chain()
    
    response_text = await chain.ainvoke({
        "question": query,
        "context": context,
        "history": history
    })
    
    current_path = state.get("path") or []
    new_path = current_path + ["product_info_node"]

    return {
        "messages": [AIMessage(content=response_text)],
        "answer": response_text,
        "path": new_path
    }
