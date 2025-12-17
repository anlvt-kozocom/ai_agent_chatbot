from app.agents.assistant_agent import AssistantAgent
from app.graphs.conversation.state import ConversationState, Message

def assistant_node(agent: AssistantAgent):
    """
    Factory to create an assistant node with the given agent.
    """
    async def _node(state: ConversationState) -> dict:
        messages = state.get("messages", [])
        context = state.get("context", "")
        
        # Generate response
        response = await agent.agenerate_response(messages, context=context)
        
        new_message: Message = {"role": "assistant", "content": response}
        
        # Update state
        # We clear 'context' here so that RAG chunks are not persisted in the history permanently.
        # We only want to save the chat content (messages) and the summary.
        return {
            "assistant_message": response,
            "messages": messages + [new_message],
            "context": "" 
        }
        
    return _node
