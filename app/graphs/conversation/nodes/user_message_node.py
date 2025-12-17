from app.graphs.conversation.state import ConversationState, Message

def user_message_node(state: ConversationState) -> dict:
    """
    Node to process user message and append to history.
    """
    user_msg_content = state.get("user_message")
    if not user_msg_content:
        return {}
    
    current_messages = state.get("messages", [])
    
    # Avoid duplicating if the last message is identical (simple de-dupe)
    # or just append. Since we control the flow, we append.
    
    new_message: Message = {"role": "user", "content": user_msg_content}
    
    # We return the UPDATED field. 
    # In standard StateGraph with TypedDict (no reducer), this replaces the field.
    # So we must return the full new list.
    return {
        "messages": current_messages + [new_message]
    }

