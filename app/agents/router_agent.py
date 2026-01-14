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
   - **User mentions ONLY a brand name (e.g. "Apple", "Samsung", "Oppo") -> RECOMMENDATION.**
   - **Multi-condition queries (price + brand, price + usage, brand + usage, etc.) -> RECOMMENDATION.**
   - Examples of RECOMMENDATION:
     * "Samsung phone around 20 million" (brand + price)
     * "Phone for gaming under $500" (usage + price)
     * "Samsung with good camera" (brand + usage)
     * "điện thoại samsung giá 20 triệu để chơi game" (brand + price + usage)

RULES:
- OUTPUT MUST BE A JSON OBJECT matching the schema.
- ABSOLUTELY NO RAG USAGE. Use only the user query and conversation context.
- IF AMBIGUOUS, choose the most specific category.
- "Requirements" like price, color, usage mostly map to RECOMMENDATION.
- Distinguish: "iPhone" (Brand) -> RECOMMENDATION, "iPhone 15" (Specific Model) -> PRODUCT_INFO.
- Multi-criteria queries always -> RECOMMENDATION.
"""


async def router_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Router Node: Classifies intent using strict Decision Engine pattern.
    Priority: Frozen Intent > LLM Decision.
    """
    from app.services.memory_service import update_working_memory

    print("--- Entering Router Node ---")
    messages = state.get("messages", [])
    if not messages:
        return {"route": "GENERAL"}

    # Use standalone query for classification logic
    query = state.get("standalone_query")
    if not query:
        # Fallback to last message content
        query = messages[-1].content if messages else ""

    # Query is already resolved by context_resolution_node
    # We will ALWAYS run the Routing Logic fresh for every turn.

    # 1. Routing via LLM
    final_decision = None
    if query:
        try:
            # Use temperature=0 for consistent classification
            llm = get_llm(temperature=0)
            structured_llm = llm.with_structured_output(RouteDecision)

            prompt = ChatPromptTemplate.from_messages(
                [("system", SYSTEM_ROUTER_TEMPLATE), ("user", "{question}")]
            )

            chain = prompt | structured_llm
            final_decision = await chain.ainvoke({"question": query}, config=config)
        except Exception as e:
            print(f"Router LLM Error: {e}")

    # Fallback if something went wrong
    if not final_decision or "route" not in final_decision:
        final_decision = {
            "route": "GENERAL",
            "confidence": 0.0,
            "reason": "Fallback: LLM routing failed",
        }

    final_route = final_decision["route"]
    current_requirements = (
        state.get("requirements", {}).copy() if state.get("requirements") else {}
    )
    # 1. Routing via LLM (Done above now)

    # ... (Logic moved up) ...

    # 2. Extract Requirements if needed (only for RECOMMENDATION or updated requirement)
    # We keep this side-effect to maintain state for recommendation_node

    # ALWAYS run keyword fallback for brand detection (regardless of route)
    # This ensures short responses like "samsung" are captured
    query_lower = query.lower()
    brand_keywords = {
        "Apple": ["iphone", "apple", "táo khuyết"],
        "Samsung": ["samsung", "galaxy"],
        "Sony": ["sony", "xperia"],
        "Oppo": ["oppo"],
        "Xiaomi": ["xiaomi", "redmi", "poco"],
        "Vivo": ["vivo"],
        "Realme": ["realme"],
        "OnePlus": ["oneplus"],
        "Google": ["pixel", "google phone"],
        "Huawei": ["huawei"],
    }

    # Check for brand keywords
    detected_brand = None
    for brand, keywords in brand_keywords.items():
        if any(kw in query_lower for kw in keywords):
            detected_brand = brand

            break

    # If brand detected, add to requirements immediately
    if detected_brand:
        current_requirements["brand"] = detected_brand

    # Now run full extraction only for RECOMMENDATION route
    if final_route == "RECOMMENDATION":
        extract_chain = build_extraction_chain()
        try:
            extracted = await extract_chain.ainvoke({"text": query}, config=config)

            # If LLM extracted a brand and we didn't have one from keywords, use LLM's
            if extracted.get("brand") and not detected_brand:
                current_requirements["brand"] = extracted["brand"]

            # USAGE KEYWORD FALLBACK: Override usage if LLM extraction seems wrong
            # Detect actual usage needs from query text
            usage_keywords = {
                "Photography": [
                    "chụp ảnh",
                    "camera",
                    "photo",
                    "nhiếp ảnh",
                    "quay phim",
                    "selfie",
                ],
                "Gaming": ["chơi game", "gaming", "game", "hiệu năng cao", "chơi"],
                "Long-term Travel": [
                    "pin trâu",
                    "pin khỏe",
                    "pin tốt",
                    "battery",
                    "dung lượng pin",
                    "pin lâu",
                ],
                "Media Consumption": [
                    "xem phim",
                    "giải trí",
                    "màn hình đẹp",
                    "watching movies",
                    "video",
                ],
                "Multitasking": [
                    "làm việc",
                    "đa nhiệm",
                    "work",
                    "multiple apps",
                    "productivity",
                ],
            }

            detected_usages = []
            for usage_type, keywords in usage_keywords.items():
                if any(kw in query_lower for kw in keywords):
                    detected_usages.append(usage_type)

            # Apply usage fallback
            if detected_usages:
                # If we detected specific usages, use them instead of LLM output
                if extracted.get("usage") != detected_usages:
                    extracted["usage"] = detected_usages
            else:
                # If NO usage keywords detected, remove the usage field entirely
                # (avoid defaulting to Gaming)
                if "usage" in extracted:
                    del extracted["usage"]

            # Merge other extracted fields (price, etc.)
            for k, v in extracted.items():
                if v and k != "brand":  # Skip brand as we handled it above
                    current_requirements[k] = v

        except Exception as e:
            print(f"Extraction failed: {e}")

    # NEW: Update Working Memory
    # Prepare info to merge
    memory_update = {
        "intent": final_route,
        "confidence": 1.0,  # Default high confidence if frozen, else could be from LLM
        "updates": {
            "budget_range": None,
            "preferred_brands": None,
            "usage_context": None,
        },
    }

    # If we had LLM decision with confidence, use it (if not frozen)
    # If we had LLM decision with confidence, use it
    if "final_decision" in locals() and final_decision:
        memory_update["confidence"] = final_decision.get("confidence", 0.0)

    # Sync requirements to memory updates (simple mapping)
    if "current_requirements" in locals():
        updates = {}
        if current_requirements.get("brand"):
            # Brand is usually a string, schema expects List[str]
            updates["preferred_brands"] = (
                [current_requirements["brand"]]
                if isinstance(current_requirements["brand"], str)
                else current_requirements["brand"]
            )

        if current_requirements.get("usage"):
            # Handle both string and list usage formats
            usage_value = current_requirements["usage"]
            if isinstance(usage_value, str):
                updates["usage_context"] = [usage_value]
            elif isinstance(usage_value, list):
                updates["usage_context"] = usage_value

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


async def general_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    General Node: Handles general conversation.
    """
    from app.chains.router_chain import get_general_chat_chain
    from app.utils.history_utils import get_windowed_history
    from app.utils.config import MAX_HISTORY_WINDOW
    from langchain_core.messages import AIMessage

    print("--- Entering General Node ---")
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
