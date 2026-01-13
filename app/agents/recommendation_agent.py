from app.models.schemas import AgentState
from langchain_core.runnables import RunnableConfig
from app.chains.recommendation_chain import build_recommendation_chain
from app.services.rag_service import rag_service
from app.prompts.rag_prompts import format_docs
from app.utils.text_processing import format_requirements, clean_number
from app.tools.price_tool import price_tool
import re
from langchain_core.messages import AIMessage


async def recommendation_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Agent Node: Provides product recommendations based on gathered requirements.
    """
    print("--- Entering Recommendation Node ---")
    requirements = state.get("requirements", {})

    # AUTO-DETECT brand from current query if missing in requirements
    brand = requirements.get("brand")
    if not brand:
        messages = state.get("messages", [])
        current_query = messages[-1].content if messages else ""
        query_lower = current_query.lower()

        # Brand keyword detection
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

        for brand_name, keywords in brand_keywords.items():
            if any(kw in query_lower for kw in keywords):
                brand = brand_name
                requirements["brand"] = brand
                print(
                    f"DEBUG recommendation_node: Auto-detected brand '{brand}' from query"
                )
                break

    # FAILSAFE: If still no brand after auto-detection
    if not brand:
        print(
            "WARNING: recommendation_node - no brand found even after auto-detection!"
        )
        language = state.get("language", "vi")
        if language == "vi":
            fallback_msg = "Xin lỗi, bạn muốn tìm điện thoại hãng nào ạ?"
        else:
            fallback_msg = "Could you please specify which brand you're interested in?"

        current_path = state.get("path") or []
        new_path = current_path + ["recommendation_node"]
        return {
            "answer": fallback_msg,
            "path": new_path,
        }

    # 1. Construct search query from requirements (Already extracted in English/Unified format)
    search_query = format_requirements(requirements)
    if not requirements:
        # Fallback to translated query
        search_query = state.get("translated_query", "")

    # 2. Use Precision Docs from State (Already retrieved based on these requirements)
    docs = state.get("precision_docs", [])
    context = format_docs(docs)

    # 2. Use Precision Docs from State (Already retrieved based on these requirements)
    docs = state.get("precision_docs", [])
    context = format_docs(docs)

    # 3. Call Recommendation Chain (English)
    chain = build_recommendation_chain()

    # Get language
    language = state.get("language", "en")

    response_text = await chain.ainvoke(
        {"requirements": search_query, "context": context, "language": language},
        config=config,
    )

    # --- POST PROCESS: Price Correction ---
    # Replace extracted prices with official ones if model names are found
    response_text = _post_process_prices(
        response_text, price_tool.get_all_products(), language
    )

    current_path = state.get("path") or []
    new_path = current_path + ["recommendation_node"]

    return {
        # "messages": [AIMessage(content=response_text)],
        "answer": response_text,
        "path": new_path,
    }


def _post_process_prices(text: str, price_data: list, language: str) -> str:
    """
    Scans the text for product model names and ensures their prices match the official data.
    """
    # 1. Identify which products are mentioned
    # Sort models by length desc to match longest names first (e.g. 'iPhone 15 Pro Max' before 'iPhone 15')
    # This optimization prevents partial matches from claiming the text first (though we are scanning the whole text)

    # We will build a list of (index, model_item) to know where they appear
    # But simpler: Iterate through all known models. If model name in text, try to fix price.

    # Filter only relevant items to speed up? No, 1600 is fine.
    # We need to sort price_data by model_name length descending to avoid aggressive short matching
    sorted_data = sorted(
        price_data, key=lambda x: len(x.get("model_name", "")), reverse=True
    )

    # Determine target currency keys
    price_key = "price_vnd"  # Default
    currency_suffix = "VND"
    if language == "en":
        price_key = "price_usd"
        currency_suffix = "USD"
    elif language == "ja":
        price_key = "price_yen"
        currency_suffix = "YEN"

    for item in sorted_data:
        model_name = item.get("model_name")
        if not model_name:
            continue

        # Check if model is mentioned (case-insensitive)
        # We use re.escape to handle special chars in model names
        if model_name.lower() in text.lower():
            # Get official price string
            official_price_str = item.get(price_key, "0")

            # Format official price nicely
            # If it looks like an int, format with commas
            try:
                official_price_val = float(official_price_str)
                if currency_suffix == "USD":
                    official_price_formatted = f"${official_price_val:,.2f}"
                else:
                    # VND/YEN usually no decimals
                    official_price_formatted = (
                        f"{int(official_price_val):,} {currency_suffix}"
                    )
            except:
                official_price_formatted = f"{official_price_str} {currency_suffix}"

            # Now, look for a price pattern NEAR the model name.
            # This is hard to do perfectly globally.
            # Strategy: Find the model name span, then look ahead for a price-like pattern.

            # Regex details:
            # Group 1: Model Name (preserved from text)
            # Group 2: Gap (non-greedy)
            # Group 3: Price string (to be replaced)

            # Expanded aliases to cover common variations like 'd', 'dong', 'đ', etc.
            # 'tr', 'củ' for Millions, 'k' for thousands
            currency_pattern = (
                r"(?:VND|USD|YEN|\$|₫|đ|k|Million|Triệu|USD|d|dong|đồng|tr|củ)"
            )

            pattern = re.compile(
                f"({re.escape(model_name)})(.{{0,100}}?)([\d,.]+\s*{currency_pattern})",
                re.IGNORECASE | re.DOTALL,
            )

            # Check if we have a match before substitution to decide on injection
            if pattern.search(text):
                # Replace logic: Keep model name (Group 1) and gap (Group 2), replace price (Group 3)
                text = pattern.sub(
                    lambda m: f"{m.group(1)}{m.group(2)}{official_price_formatted}",
                    text,
                )
            else:
                # If model is found but NO price pattern nearby, we should inject the price.
                # Avoid double injection if the price is already there but missed by regex (risk).
                # But user said "Always ensure".
                # Strategy: Append to the first occurrence of the model name.
                # "iPhone 15" -> "iPhone 15 (Official Price: ~20M VND)"

                # Use sub with count=1 to only affect the first one to avoid spamming
                text = re.sub(
                    re.escape(model_name),
                    lambda m: f"{m.group(0)} (Official Price: {official_price_formatted})",
                    text,
                    count=1,
                    flags=re.IGNORECASE,
                )

    return text
