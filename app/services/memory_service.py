import json
from typing import List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from app.models.schemas import AgentState, WorkingMemory, SummaryMemory
from app.services.llm import get_llm

# Constants
MAX_RECENT_TURNS = 5
INTENT_CONFIDENCE_THRESHOLD = 0.8


def get_empty_working_memory() -> WorkingMemory:
    return {
        "intent": None,
        "intent_confidence": 0.0,
        "intent_frozen": False,
        "budget_range": None,
        "preferred_brands": None,
        "product_category": None,
        "usage_context": None,
        "specific_products": None,
        "current_route": None,
    }


def get_empty_summary_memory() -> SummaryMemory:
    return {
        "summary_text": "",
        "key_decisions": [],
        "topics_covered": [],
    }


async def update_working_memory(
    state: AgentState, new_info: Dict[str, Any] = None
) -> WorkingMemory:
    """
    Updates the Working Memory based on the latest interaction.
    If 'new_info' is provided (e.g. from Router extraction), it merges it.
    Otherwise, it might run a lightweight extraction if needed (though usually Router does this).
    """
    current_wm = state.get("working_memory") or get_empty_working_memory()

    # If intent is frozen, we only update constraints, not the intent itself
    # unless a "RESET" signal is detected (which would be handled by Router logic mostly)

    if new_info:
        # Merge logic
        if new_info.get("intent") and not current_wm["intent_frozen"]:
            current_wm["intent"] = new_info["intent"]
            current_wm["intent_confidence"] = new_info.get("confidence", 0.0)

            # Auto-freeze if confidence is high
            if current_wm["intent_confidence"] >= INTENT_CONFIDENCE_THRESHOLD:
                current_wm["intent_frozen"] = True

        # Update constraints (Merge lists/dicts)
        if new_info.get("updates"):
            updates = new_info["updates"]
            if updates.get("budget_range"):
                current_wm["budget_range"] = updates["budget_range"]
            if updates.get("preferred_brands"):
                # Simple list append for now, or replace? Let's replace for clarity
                current_wm["preferred_brands"] = updates["preferred_brands"]
            if updates.get("usage_context"):
                # Replace for now
                current_wm["usage_context"] = updates["usage_context"]

    return current_wm


async def summarize_conversation(state: AgentState) -> SummaryMemory:
    """
    Compresses the conversation history into a structured summary.
    This should be called periodically (e.g. every 5 turns).
    """
    messages = state.get("messages", [])
    if len(messages) < 3:
        return state.get("summary_memory") or get_empty_summary_memory()

    llm = get_llm(temperature=0)

    # Simple summarization prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a conversation summarizer. 
        Compress the chat history into a structured JSON summary.
        
        Extract:
        - key_decisions: (e.g. "User rejected X", "User chose Y")
        - topics_covered: (e.g. "Battery life", "Gaming performance")
        - summary_text: A brief 2-sentence narrative of the status.
        
        Keep it concise.
        """,
            ),
            ("user", "{history}"),
        ]
    )

    # Format history string
    history_str = "\n".join([f"{m.type}: {m.content}" for m in messages])

    try:
        chain = prompt | llm.with_structured_output(SummaryMemory)
        summary = await chain.ainvoke({"history": history_str})
        return summary
    except Exception as e:
        print(f"Summarization failed: {e}")
        return state.get("summary_memory") or get_empty_summary_memory()


def compress_context(state: AgentState) -> str:
    """
    Constructs the minimal context string for LLM prompts.
    Includes:
    1. Working Memory (JSON)
    2. Summary Memory (Text)
    3. Last N turns (Raw Text)
    """
    wm = state.get("working_memory") or get_empty_working_memory()
    sm = state.get("summary_memory") or get_empty_summary_memory()
    messages = state.get("messages", [])

    # 1. Format Working Memory
    # Filter out None values to save tokens
    wm_clean = {k: v for k, v in wm.items() if v is not None}
    wm_str = f"CURRENT STATE: {json.dumps(wm_clean, indent=None)}"

    # 2. Format Summary
    sm_str = ""
    if sm["summary_text"]:
        sm_str = f"PREVIOUS CONTEXT: {sm['summary_text']}\nDECISIONS: {', '.join(sm['key_decisions'])}"

    # 3. Recent Turns
    recent_msgs = messages[-MAX_RECENT_TURNS:]
    history_str = "\n".join([f"{m.type.upper()}: {m.content}" for m in recent_msgs])

    final_context = f"""
{sm_str}

{wm_str}

RECENT CHAT:
{history_str}
"""
    return final_context.strip()
