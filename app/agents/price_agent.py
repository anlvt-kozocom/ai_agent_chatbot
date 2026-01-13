from app.models.schemas import AgentState
from app.tools.price_tool import price_tool
from app.utils.text_processing import clean_number
import re
import json
from app.services.llm import get_llm


async def price_filtering_node(state: AgentState) -> dict:
    """
    Agent Node: Performs pre-retrieval price filtering.
    Calculates a list of candidate product IDs based on user's budget/price requirements.
    """
    print("--- Entering Price Filtering Node ---")
    requirements = state.get("requirements", {})

    # 1. Check if price/budget is specified
    budget_raw = requirements.get("budget") or requirements.get("price")
    brand_filter = requirements.get("brand")
    price_sort = requirements.get("price_sort")

    # 1a. Handle Price Sort (Cheapest/Most Expensive)
    if price_sort:
        target_product = None
        if price_sort.lower() == "asc":
            target_product = price_tool.get_cheapest(brand_filter)
        elif price_sort.lower() == "desc":
            target_product = price_tool.get_most_expensive(brand_filter)

        if target_product:
            # We found a specific product, so we set candidate_ids to just this one
            return {
                "candidate_ids": [str(target_product.get("id"))],
                "path": (state.get("path") or []) + ["price_filtering_node"],
            }
        else:
            # If not found, maybe fall back to normal search or return None
            return {
                "candidate_ids": [],
                "path": (state.get("path") or []) + ["price_filtering_node"],
            }

    if not budget_raw:
        # Check extraction in case requirements didn't catch it yet
        try:
            llm = get_llm(temperature=0)
            messages = state.get("messages", [])
            current_query = messages[-1].content if messages else ""

            prompt = f"""Extract target price/currency or price range from the query. Return JSON.
            Rules:
            - For single price: {{"price": number, "currency": "str"}}
            - For price range: {{"min_price": number, "max_price": number, "currency": "str"}}
            - If "under/below/dưới/thấp hơn", set "min_price": 0 and "max_price": extracted_value.
            - If "over/above/trên/cao hơn", set "min_price": extracted_value and "max_price": 100000000 (VND) or 5000 (USD).
            - For sorting: If "cheapest/rẻ nhất", include "sort": "asc". If "most expensive/đắt nhất", include "sort": "desc".
            - normalize "triệu", "tr", "m" to zeros (e.g. "20 triệu" -> 20000000, currency "VND").
            - normalize "k" to thousands (e.g. "500k" -> 500000).
            - "$500" -> 500, currency "USD".
            Query: {current_query}"""

            res = await llm.ainvoke(prompt)
            content = res.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.replace("```", "").strip()

            if content and "{" in content:
                data = json.loads(content)
                if data.get("price") or (
                    data.get("min_price") and data.get("max_price")
                ):
                    # Successfully extracted price from query
                    budget_raw = data

                # Check for sort in fallback extraction
                if data.get("sort"):
                    price_sort = data.get("sort")
                    # Should recurse or handle here?
                    # Let's handle it immediately
                    if price_sort.lower() == "asc":
                        target_product = price_tool.get_cheapest(brand_filter)
                    elif price_sort.lower() == "desc":
                        target_product = price_tool.get_most_expensive(brand_filter)

                    if target_product:
                        return {
                            "candidate_ids": [str(target_product.get("id"))],
                            "path": (state.get("path") or [])
                            + ["price_filtering_node"],
                        }

        except Exception as e:
            print(f"DEBUG: Pre-extraction failed: {e}")

    if not budget_raw:
        return {
            "candidate_ids": None,
            "path": (state.get("path") or []) + ["price_filtering_node"],
        }

    # 2. Get Product IDs matching the price
    candidate_ids = []
    try:
        currency = "VND"  # Default
        language = state.get("language", "vi")

        # Handle dict budget (from LLM) or string budget (from requirements)
        if isinstance(budget_raw, dict):
            # Range
            if "min_price" in budget_raw and "max_price" in budget_raw:
                results = price_tool.get_products_by_price_range(
                    float(budget_raw["min_price"]),
                    float(budget_raw["max_price"]),
                    budget_raw.get("currency", "VND"),
                    brand=brand_filter,
                )
                candidate_ids = [str(r.get("id")) for r in results if r.get("id")]
            # Single price
            elif budget_raw.get("price"):
                results = price_tool.search_by_price(
                    float(budget_raw["price"]),
                    budget_raw.get("currency", "VND"),
                    brand=brand_filter,
                )
                candidate_ids = [str(r.get("id")) for r in results if r.get("id")]
        else:
            # String parsing with range detection (e.g. "under 10000000")
            budget_str = str(budget_raw).lower()
            target_val = clean_number(budget_str)

            if any(k in budget_str for k in ["under", "below", "dưới", "thấp hơn"]):
                results = price_tool.get_products_by_price_range(
                    0, target_val, currency, brand=brand_filter
                )
            elif any(k in budget_str for k in ["over", "above", "trên", "cao hơn"]):
                results = price_tool.get_products_by_price_range(
                    target_val, 100000000, currency, brand=brand_filter
                )
            else:
                results = price_tool.search_by_price(
                    target_val, currency, brand=brand_filter
                )

            candidate_ids = [str(r.get("id")) for r in results if r.get("id")]

    except Exception as e:
        print(f"Error in price filtering tool: {e}")

    return {
        "candidate_ids": candidate_ids if candidate_ids else None,
        "path": (state.get("path") or []) + ["price_filtering_node"],
    }
