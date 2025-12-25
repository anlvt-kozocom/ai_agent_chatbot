from app.models.schemas import AgentState
from app.chains.qa_chain import build_qa_chain
from langchain_core.messages import AIMessage, HumanMessage


async def qa_agent_node(state: AgentState) -> dict:
    """
    Agent Node: Responsible for processing the state and calling the QA chain.
    Agents layer: Reasoning and decision logic.
    """
    messages = state.get("messages", [])
    if not messages:
        return {"answer": "Không có câu hỏi nào được tìm thấy."}

    # Get the last message (assumed to be from user for this simple flow)
    last_message = messages[-1]

    # Logic to separate current question from history
    # LangGraph adds the new message to state before entering the node.
    # So 'messages' includes the current question at the end.

    current_question = last_message.content

    # History is everything EXCEPT the last message
    history = messages[:-1]

    # Initialize the chain
    qa_chain = build_qa_chain()

    # Invoke chain with history
    response_text = await qa_chain.ainvoke(
        {"question": current_question, "history": history}
    )

    # Update state
    # We return the NEW message to be added to the state history
    return {"messages": [AIMessage(content=response_text)], "answer": response_text}
