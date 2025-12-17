import os
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.graphs.conversation.state import ConversationState, Message
from app.services.exchange_rate import get_vcb_exchange_rates

async def currency_converter_node(state: ConversationState) -> dict:
    """
    Node to rewrite the last assistant message if it contains non-VND currencies.
    It strictly converts everything to VND using real-time rates.
    """
    messages = state.get("messages", [])
    if not messages:
        return {}
    
    last_message = messages[-1]
    # Verify it's an assistant message
    if last_message.get("role") != "assistant":
        return {}
    
    content = last_message.get("content", "")

    # Initialize a small/fast LLM for this specific cleaning task
    api_key = os.getenv("GOOGLE_API_KEY")
    model_name = os.getenv("MODEL_NAME", "gemini-2.5-flash-lite")
    
    if not api_key:
        return {} # Can't fix without LLM
        
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0, 
        google_api_key=api_key
    )

    # Fetch real-time rates
    rates_info = await get_vcb_exchange_rates()

    # Prompt specifically for cleaning currencies
    system_prompt = f"""
    You are a Currency Formatting Specialist.
    Your task is to rewrite the provided text to strictly adhere to these rules:
    1. Identify all prices in any currency (USD, EUR, Rupee, etc.).
    2. Convert them to VND (Vietnamese Dong) using the REAL-TIME rates below:
    
    {rates_info}
    
    (For currencies not listed, infer based on standard cross rates via USD).
    
    3. REPLACE the original price with the VND amount (e.g., "3.999.000 VND").
    4. DELETE any mention of the original currency or the calculation.
    5. KEEP the rest of the text structure, formatting, and content exactly the same.
    6. Output ONLY the rewritten text.
    """

    response = await llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=content)
    ])
    
    cleaned_content = str(response.content)

    # Update the last message in the list
    return {
        "assistant_message": cleaned_content,
        "messages": messages[:-1] + [{"role": "assistant", "content": cleaned_content}] 
    }
