from app.models.schemas import AgentState
from app.chains.router_chain import get_router_chain, get_general_chat_chain
from app.chains.extraction_chain import build_extraction_chain
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from app.utils.config import MAX_HISTORY_WINDOW
import re


async def router_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Router Node: Classifies intent and extracts requirements.
    Uses 'translated_query' if available (English), otherwise raw content.
    """
    messages = state.get("messages", [])
    if not messages:
        return {"route": "general"}

    # Use standalone query for classification logic (best for context)
    # This comes from the context_resolution_node
    query = state.get("standalone_query")
    if not query:
        # Fallback to translated if available, or raw
        query = state.get("translated_query") or messages[-1].content

    # 0. Heuristic Routing (Keyword-based optimization)
    # Check for strong keywords to avoid LLM call for obvious cases
    heuristic_decision = heuristic_route(query)
    if heuristic_decision:
        print(f"DEBUG: Heuristic routing triggered -> {heuristic_decision}")
        route = heuristic_decision
    else:
        # 1. Classify with LLM if heuristic fails
        chain = get_router_chain()
        route = await chain.ainvoke({"question": query}, config=config)

    route = route.strip().lower()

    # Map raw route to known categories
    # User Request: 'requirement' is now treated as 'recommendation' to provide suggestions first
    valid_routes = ["product_info", "recommendation", "comparison", "general"]
    final_route = "general"

    if "requirement" in route:
        final_route = "recommendation"
    else:
        for r in valid_routes:
            if r in route:
                final_route = r
                break

    # 2. Extract Requirements if needed (using English query)
    # Use copy to ensure we accumulate requirements correctly across turns
    current_requirements = (
        state.get("requirements", {}).copy() if state.get("requirements") else {}
    )

    if final_route == "recommendation":
        extract_chain = build_extraction_chain()
        try:
            extracted = await extract_chain.ainvoke({"text": query}, config=config)
            # Merge logic: Overwrite keys that are not None/Empty
            # This ensures that if the user adds a new requirement (e.g., "good camera"),
            # it is added to the existing ones (e.g., "price 10m").
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
        "path": new_path,
    }


def heuristic_route(query: str) -> str | None:
    """
    Simple keyword-based routing to save LLM calls.
    Returns route name or None.
    """
    query_lower = query.lower()

    # Comparison Keywords - Check FIRST as it is specific
    comp_keywords = [
        # English
        "compare",
        "comparison",
        "vs",
        "versus",
        "difference",
        "choose",
        "better",
        "or",
        # Vietnamese
        "so sánh",
        "khác nhau",
        "nên mua nào",
        "nào tốt hơn",
        "so kèo",
        "giống nhau",
        "phân biệt",
        "đối chiếu",
        "hay là",
        "hay",
        "so với",
        "nên chọn",
        # Japanese
        "比較",
        "違い",
        "どっち",
        "どちら",
        "選ぶ",
        "くらべて",
        "対決",
    ]
    if any(k in query_lower for k in comp_keywords):
        return "comparison"

    # Recommendation / Requirement Keywords
    # Split into 'strong' (definitely recommendation) and 'ambiguous' (could be info)
    strong_rec_keywords = [
        # English
        "buy",
        "purchase",
        "recommend",
        "suggest",
        "looking for",
        "need",
        "find",
        "budget",
        "cheap",
        "expensive",
        "best",
        "good",
        # Vietnamese
        "mua",
        "tìm",
        "tư vấn",
        "rẻ",
        "đắt",
        "gợi ý",
        "cần",
        "ngon",
        # Japanese
        "買いたい",
        "購入",
        "おすすめ",
        "探して",
        "安い",
        "ほしい",
    ]

    ambiguous_keywords = [
        # English
        "price",
        "cost",
        "how much",
        # Vietnamese
        "giá",
        "bao nhiêu",
        "tiền",
        # Japanese
        "値段",
        "価格",
        "いくら",
    ]

    # Check for Strong Recommendation Keywords
    if any(k in query_lower for k in strong_rec_keywords):
        return "recommendation"

    # Product Info Keywords
    info_keywords = [
        # English
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
        # Vietnamese
        "cấu hình",
        "thông số",
        "pin",
        "bộ nhớ",
        "màn hình",
        "camera",
        "chip",
        "nặng",
        "kích thước",
        "là gì",
        "chi tiết",
        # Japanese
        "スペック",
        "仕様",
        "バッテリー",
        "メモリ",
        "ストレージ",
        "画面",
        "カメラ",
        "プロセッサ",
        "重さ",
        "サイズ",
        "とは",
        "詳細",
    ]

    if any(k in query_lower for k in info_keywords):
        return "product_info"

    # Ambiguous Case: If "price" is mentioned but NO strong recommendation words, treat as Info
    # e.g. "Price of iPhone 15" -> Info
    # e.g. "Cheap phone price" -> Recommendation (caught by 'cheap' above)
    if any(k in query_lower for k in ambiguous_keywords):
        return "product_info"

    return None


async def general_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    General Node: Handles general conversation.
    """
    messages = state.get("messages", [])

    # Use standalone query
    query = state.get("standalone_query")
    if not query:
        query = state.get("translated_query") or messages[-1].content

    # Get windowed history (exclude the last message which is the current query)
    # The current query is in 'messages[-1]' (if from user) or we just use 'messages[:-1]'.
    # Note: 'messages' in state usually includes the current latest message if it came from the graph input.
    # In LangGraph, 'messages' grows.
    from app.utils.history_utils import get_windowed_history

    history_str = get_windowed_history(
        messages[:-1], k=MAX_HISTORY_WINDOW
    )  # Exclude current message

    chain = get_general_chat_chain()
    response = await chain.ainvoke(
        {"question": query, "history": history_str}, config=config
    )

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
        "path": new_path,
    }
