from app.models.schemas import AgentState
from app.chains.router_chain import get_router_chain, get_general_chat_chain
from app.chains.extraction_chain import build_extraction_chain
from langchain_core.messages import AIMessage

async def router_node(state: AgentState) -> dict:
    """
    Router Node: Classifies intent and extracts requirements.
    Uses 'translated_query' if available (English), otherwise raw content.
    """
    messages = state.get("messages", [])
    if not messages:
        return {"route": "general"}
    
    # Use translated query for classification logic (better for English-trained models)
    # But keep extracting form original if needed? 
    # Actually, prompts are now in English, so using translated query is BEST.
    query = state.get("translated_query")
    if not query:
        query = messages[-1].content
    
    # 1. Classify
    chain = get_router_chain()
    route = await chain.ainvoke({"question": query})
    route = route.strip().lower()
    
    # Map raw route to known categories
    # User Request: 'requirement' is now treated as 'recommendation' to provide suggestions first
    valid_routes = ["product_info", "recommendation", "general"]
    final_route = "general"
    
    if "requirement" in route:
        final_route = "recommendation"
    else:
        for r in valid_routes:
            if r in route:
                final_route = r
                break
            
    # 2. Extract Requirements if needed (using English query)
    current_requirements = state.get("requirements") or {}
    
    if final_route == "recommendation":
        extract_chain = build_extraction_chain()
        try:
            extracted = await extract_chain.ainvoke({"text": query})
            # Merge logic: Overwrite keys that are not None/Empty
            for k, v in extracted.items():
                if v:
                    current_requirements[k] = v
        except Exception as e:
            print(f"Extraction failed: {e}")
            
    # Return updated state
    current_path = state.get("path") or []
    new_path = current_path + ["router_node"]

    return {
        "route": final_route,
        "requirements": current_requirements,
        "path": new_path
    }

async def general_node(state: AgentState) -> dict:
    """
    General Node: Handles general conversation.
    """
    messages = state.get("messages", [])
    
    # Use translated query
    query = state.get("translated_query")
    if not query:
        query = messages[-1].content
    
    chain = get_general_chat_chain()
    response = await chain.ainvoke({"question": query})
    
    current_path = state.get("path") or []
    new_path = current_path + ["general_node"]

    return {
        # DO NOT append message here yet, wait for translation output node?
        # Actually, standard flow expects answer here. 
        # We will let language_output_node handle the FINAL message to user.
        # But we need to store the ENGLISH answer first.
        # So we update 'answer' but maybe not 'messages' if we want to hide English?
        # LangGraph usually accumulates messages. 
        # Let's return the English message here, and Language Output will ADD the translated one.
        # Or Language Output replaces it.
        # For simplicity: Add English message here. Language Node adds Translated message.
        "messages": [AIMessage(content=response)], 
        "answer": response,
        "path": new_path
    }
