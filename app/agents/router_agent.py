from typing import Literal, TypedDict, Optional, Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from app.models.schemas import AgentState
from app.services.llm import get_llm
from app.chains.extraction_chain import build_extraction_chain


# Defined Schema for Router policies
class RouteDecision(TypedDict):
    route: Literal["GENERAL", "PRODUCT_INFO", "COMPARISON", "RECOMMENDATION"]
    confidence: float
    reason: str


SYSTEM_ROUTER_TEMPLATE = """You are an expert intent classification engine for a mobile phone store AI assistant.
Your job is to analyze the user's input and route it to the correct handler.

ROUTING DESTINATIONS:
1. GENERAL:
   - Greetings, phatic communication (hello, hi, thank you).
   - General knowledge questions NOT about specific products.
   - Questions about the AI itself.

2. PRODUCT_INFO:
   - Questions about specific product specifications (RAM, battery, screen, camera, price of specific model).
   - "Tell me about iPhone 15", "How much is Galaxy S24?", "I want to buy iPhone 15" (Specific intent).
   - Detailed inquiries about a specific device.

3. COMPARISON:
   - Requests to compare two or more products.
   - "Compare iPhone 15 and 16", "Which is better, S24 or iPhone 15?", "Difference between X and Y".

4. RECOMMENDATION:
   - Requests for buying advice.
   - Queries with criteria (budget, usage, brand preference).
   - "Suggest a phone under 10 million", "I need a phone for gaming", "Best Samsung phone currently".
   - "Cheap phone", "Looking for new phone".

RULES:
- OUTPUT MUST BE A JSON OBJECT matching the schema.
- ABSOLUTELY NO RAG USAGE. Use only the user query and conversation context.
- IF AMBIGUOUS, choose the most specific category.
- "Requirements" like price, color, usage mostly map to RECOMMENDATION.
"""


async def router_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Router Node: Classifies intent using strict Decision Engine pattern.
    Priority: Heuristic Rules > LLM Decision.
    """
    from app.services.memory_service import update_working_memory

    messages = state.get("messages", [])
    if not messages:
        return {"route": "GENERAL"}

    # Use standalone query for classification logic
    query = state.get("standalone_query")
    if not query:
        # Fallback to last message content
        query = messages[-1].content if messages else ""

    # Check Working Memory for frozen intent
    working_memory = state.get("working_memory")
    if (
        working_memory
        and working_memory.get("intent_frozen")
        and working_memory.get("intent")
    ):
        print(f"DEBUG: Intent frozen -> {working_memory['intent']}")
        final_route = working_memory["intent"]
        # Ensure route is valid for next steps
        current_requirements = (
            state.get("requirements", {}).copy() if state.get("requirements") else {}
        )
    else:
        # 1. Heuristic Routing (Rule-based priority)
        heuristic_decision = heuristic_route(query)
        if heuristic_decision:
            print(
                f"DEBUG: Heuristic routing triggered -> {heuristic_decision['route']}"
            )
            final_decision = heuristic_decision
        else:
            # 2. LLM Decision (Fallback)
            try:
                llm = get_llm(temperature=0)
                structured_llm = llm.with_structured_output(RouteDecision)

                prompt = ChatPromptTemplate.from_messages(
                    [("system", SYSTEM_ROUTER_TEMPLATE), ("user", "{question}")]
                )

                chain = prompt | structured_llm
                final_decision: RouteDecision = await chain.ainvoke(
                    {"question": query}, config=config
                )

                # Fallback if structure fails (though with_structured_output should handle it)
                if not final_decision or "route" not in final_decision:
                    final_decision = {
                        "route": "GENERAL",
                        "confidence": 0.0,
                        "reason": "Fallback parsing error",
                    }

            except Exception as e:
                print(f"Router LLM Error: {e}")
                final_decision = {
                    "route": "GENERAL",
                    "confidence": 0.0,
                    "reason": f"Error: {str(e)}",
                }

        final_route = final_decision["route"]

        # 3. Extract Requirements if needed (only for RECOMMENDATION or updated requirement)
        # We keep this side-effect to maintain state for recommendation_node
        current_requirements = (
            state.get("requirements", {}).copy() if state.get("requirements") else {}
        )

        if final_route == "RECOMMENDATION":
            extract_chain = build_extraction_chain()
            try:
                extracted = await extract_chain.ainvoke({"text": query}, config=config)
                for k, v in extracted.items():
                    if v:
                        current_requirements[k] = v
            except Exception as e:
                print(f"Extraction failed: {e}")

    # NEW: Update Working Memory
    # Prepare info to merge
    memory_update = {
        "intent": final_route,
        "confidence": 1.0,  # Default high confidence if heuristic or frozen, else could be from LLM
        "updates": {
            "budget_range": None,
            "preferred_brands": None,
            "usage_context": None,
        },  # Placeholder for now, could be richer
    }

    # If we had LLM decision with confidence, use it (if not frozen)
    if (
        not (working_memory and working_memory.get("intent_frozen"))
        and "final_decision" in locals()
    ):
        memory_update["confidence"] = final_decision.get("confidence", 0.0)

    # Sync requirements to memory updates (simple mapping)
    if "current_requirements" in locals():
        # Map flat requirements to detailed memory structure if possible
        # For now, just persisting requirements in state is handled by the return,
        # but let's try to populate memory constraints if we have them.
        updates = {}
        if current_requirements.get("budget"):
            # Parsing budget string to int range is complex, skipping for this iteration or leaving as raw string if schema allows
            # Schema says budget_range is Dict[str, int], but extraction returns string maybe?
            # Let's trust extraction chain returns standard format or just skip for now to avoid validation error
            pass
        if current_requirements.get("brand"):
            # Brand is usually a string, schema expects List[str]
            updates["preferred_brands"] = (
                [current_requirements["brand"]]
                if isinstance(current_requirements["brand"], str)
                else current_requirements["brand"]
            )

        memory_update["updates"] = updates

    updated_wm = await update_working_memory(state, memory_update)

    # Return updated state
    current_path = state.get("path") or []
    new_path = current_path + ["router_node"]

    return {
        "route": final_route,
        "requirements": current_requirements,
        "path": new_path,
        "working_memory": updated_wm,
    }


def heuristic_route(query: str) -> Optional[RouteDecision]:
    """
    Simple keyword-based routing to save LLM calls.
    Returns RouteDecision or None.
    """
    if not query:
        return None

    query_lower = query.lower()

    # Comparison Keywords (High Priority)
    comp_keywords = [
        "compare",
        "comparison",
        "vs",
        "versus",
        "difference",
        "choose",
        "better",
        "or",
        "so sánh",
        "khác nhau",
        "nên mua nào",
        "nào tốt hơn",
        "so kèo",
        "giống nhau",
        "phân biệt",
        "đối chiếu",
        "hay là",
        "so với",
        "nên chọn",
        "比較",
        "違い",
        "どっち",
        "どちら",
        "選ぶ",
        "くらべて",
        "対決",
    ]
    if any(k in query_lower for k in comp_keywords):
        return {
            "route": "COMPARISON",
            "confidence": 1.0,
            "reason": "Keyword match: comparison",
        }

    # Recommendation Keywords
    strong_rec_keywords = [
        "recommend",
        "suggest",
        "looking for",
        "budget",
        "cheap",
        "expensive",
        "best",
        "good",
        "tư vấn",
        "gợi ý",
        "ngon",
        "thích",
        "おすすめ",
        "探して",
        "安い",
        "ほしい",
    ]
    if any(k in query_lower for k in strong_rec_keywords):
        return {
            "route": "RECOMMENDATION",
            "confidence": 1.0,
            "reason": "Keyword match: recommendation",
        }

    # Product Info Keywords
    # Note: Some overlap with 'best' (rec) or 'specs' (info), careful order
    info_keywords = [
        "spec",
        "specification",
        "ram",
        "battery",
        "storage",
        "screen",
        "display",
        "camera",
        "processor",
        "cpu",
        "weight",
        "size",
        "dimension",
        "what is",
        "tell me about",
        "info",
        "details",
        "how much",
        "price",
        "cost",
        "cấu hình",
        "thông số",
        "pin",
        "bộ nhớ",
        "màn hình",
        "chip",
        "nặng",
        "kích thước",
        "là gì",
        "chi tiết",
        "giá",
        "bao nhiêu",
        "tiền",
        "スペック",
        "仕様",
        "バッテリー",
        "メモリ",
        "ストレージ",
        "画面",
        "プロセッサ",
        "重さ",
        "サイズ",
        "とは",
        "詳細",
        "値段",
        "価格",
        "いくら",
    ]
    if any(k in query_lower for k in info_keywords):
        return {
            "route": "PRODUCT_INFO",
            "confidence": 1.0,
            "reason": "Keyword match: product_info",
        }

    return None


async def general_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    General Node: Handles general conversation.
    """
    from app.chains.router_chain import get_general_chat_chain
    from app.utils.history_utils import get_windowed_history
    from app.utils.config import MAX_HISTORY_WINDOW
    from langchain_core.messages import AIMessage

    messages = state.get("messages", [])
    query = state.get("standalone_query")
    if not query:
        query = messages[-1].content if messages else ""

    # history_str = get_windowed_history(messages[:-1], k=MAX_HISTORY_WINDOW)
    from app.services.memory_service import compress_context

    context_str = compress_context(state)

    chain = get_general_chat_chain()
    response = await chain.ainvoke(
        {"question": query, "context": context_str}, config=config
    )

    current_path = state.get("path") or []
    new_path = current_path + ["general_node"]

    return {
        "messages": [AIMessage(content=response)],
        "answer": response,
        "path": new_path,
    }
