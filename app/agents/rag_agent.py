from app.models.schemas import AgentState
from app.chains.rag_chain import get_rag_chain
from app.services.rag_service import rag_service
from langchain_core.messages import AIMessage


async def rag_node(state: AgentState) -> dict:
    """
    RAG Node: Retrieves context and generates answer using internal data.
    """
    messages = state.get("messages", [])
    if not messages:
        return {"answer": "Error: No messages found."}

    last_message = messages[-1]
    query = last_message.content

    retriever = rag_service.get_retriever()
    if not retriever:
        return {
            "messages": [
                AIMessage(content="System Error: Retrieval service not available.")
            ],
            "answer": "System Error: Retrieval service not available.",
        }

    chain = get_rag_chain(retriever)

    response = await chain.ainvoke(query)

    response_content = (
        response.content if hasattr(response, "content") else str(response)
    )

    return {
        "messages": [AIMessage(content=response_content)],
        "answer": response_content,
    }
