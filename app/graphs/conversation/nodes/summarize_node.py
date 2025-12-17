import os
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.graphs.conversation.state import ConversationState

def summarize_node(state: ConversationState) -> dict:
    """
    Node to summarize the current conversation history.
    This helps to compress context before storing or for long-running chats.
    """
    messages = state.get("messages", [])
    current_summary = state.get("summary", "")
    
    # Only summarize if we have enough messages (e.g., > 4)
    if len(messages) < 4:
        return {}
    
    # Initialize LLM for summarization
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {}
    model_name = os.getenv("MODEL_NAME")
                    
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0, 
        google_api_key=api_key
    )
    
    # Construct prompt
    prompt = f"""
    Current summary of conversation:
    {current_summary}

    New lines of conversation:
    {messages[-2:]} 

    Please verify and update the summary with the new information. Keep it concise.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    new_summary = str(response.content)
    
    # Update state: Save new summary and potentially trim messages (optional)
    return {
        "summary": new_summary
    }

