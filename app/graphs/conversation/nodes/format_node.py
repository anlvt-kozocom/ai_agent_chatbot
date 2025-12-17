from app.graphs.conversation.state import ConversationState

def format_node(state: ConversationState) -> dict:
    """
    Node to format the assistant's response into Markdown.
    
    This node takes the raw 'assistant_message' and applies 
    standard markdown formatting or wrapping.
    """
    raw_response = state.get("assistant_message", "")

    
    # Return partial state update
    return {
        "assistant_message": raw_response
    }

