from app.models.schemas import AgentState
from app.chains.translation_chain import build_translation_chain, build_reverse_translation_chain
from langchain_core.messages import AIMessage, HumanMessage

async def language_input_node(state: AgentState) -> dict:
    """
    Node: Detects language and translates input to English.
    """
    messages = state.get("messages", [])
    if not messages:
        return {}
        
    last_message = messages[-1]
    # Check if last message is from user (HumanMessage)
    if isinstance(last_message, AIMessage):
        # If it's AI message, we don't translate input
        return {}
        
    user_text = last_message.content
    
    chain = build_translation_chain()
    result = await chain.ainvoke({"text": user_text})
    
    # Update path
    current_path = state.get("path") or []
    new_path = current_path + ["language_input_node"]
    
    return {
        "original_language": result.get("original_language", "en"),
        "translated_query": result.get("translated_text", user_text),
        "path": new_path
    }

async def language_output_node(state: AgentState) -> dict:
    """
    Node: Translates the final answer back to the user's original language.
    """
    original_lang = state.get("original_language", "en")
    answer_text = state.get("answer")
    
    if not answer_text:
        return {}
        
    # If original language is English, no need to translate
    current_path = state.get("path") or []
    new_path = current_path + ["language_output_node"]

    if original_lang.lower() in ["en", "english", "en-us", "en-gb"]:
        return {"path": new_path} # Keep as is, just log path
        
    chain = build_reverse_translation_chain()
    translated_answer = await chain.ainvoke({
        "text": answer_text,
        "target_language": original_lang
    })
    
    # Update the last AI message with translated content
    # Note: This appends a new message or we could replace. 
    # LangGraph add_messages appends. For better UX, we might just update the answer field
    # and let the UI handle it, OR we replace the last message content.
    # Here, we will just update the answer in state and append the translated message.
    
    return {
        "messages": [AIMessage(content=translated_answer)],
        "answer": translated_answer,
        "path": new_path
    }


