from langchain_core.runnables import RunnableConfig
from app.models.schemas import AgentState
from app.services.rag_service import rag_service
from app.utils.text_processing import format_requirements
from langchain_core.documents import Document
from app.tools.price_tool import price_tool
from app.services.llm import get_llm
import json


async def recall_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Recall Stage Node:
    - Broadly retrieves documents based on the strategy.
    - Maximizes recall (high top_k).
    - Stores raw docs in state.
    """
    print("--- Entering Recall Node ---")
    retrieval_strategy = state.get("retrieval_strategy")
    if not retrieval_strategy:
        # Should have been set by retrieval_strategy_node
        retrieval_strategy = {"strategy": "VECTOR_SEARCH"}

    strategy_type = retrieval_strategy.get("strategy", "VECTOR_SEARCH")
    language = state.get("language", "en")
    route = state.get("route", "")

    # Determine the query
    # IMPORTANT: Only use format_requirements for RECOMMENDATION route
    # PRODUCT_INFO, COMPARISON, and GENERAL should use the original query
    requirements = state.get("requirements", {})
    if requirements and route == "RECOMMENDATION":
        # For RECOMMENDATION: construct query from requirements
        query = format_requirements(requirements)
    else:
        # For all other routes: use standalone query or fallback to last message
        query = state.get("standalone_query")
        if not query and state.get("messages"):
            query = state.get("messages")[-1].content

    if not query:
        print("Warning: No query found for Recall.")
        return {"recall_docs": []}

    # Execute Recall
    # We use a higher top_k for recall to allow Precision stage to refine
    recall_top_k = 20  # Hardcoded 'wide' net, or derived from strategy * multiplier

    # 1. Standard Retrieval (RAG)
    # Use candidate_ids from state (pre-filtered by price_filtering_node)
    candidate_ids = state.get("candidate_ids")

    # SAFETY: If we are in PRODUCT_INFO route, we skipped price_filtering_node.
    # We must IGNORE any stale candidate_ids from previous turns.
    if state.get("route") == "PRODUCT_INFO":
        candidate_ids = None

    # Special handling for MULTI_PRODUCT (Comparison) -> Extract specific products
    if strategy_type == "MULTI_PRODUCT" and not candidate_ids:
        # Use explicit query source for extraction (ignore format_requirements which might mask entities)
        extraction_query = state.get("standalone_query")
        if not extraction_query and state.get("messages"):
            extraction_query = state.get("messages")[-1].content

        try:
            llm = get_llm(temperature=0)
            prompt = f"""Extract product names mentioned in the query for comparison. Return JSON list of strings.
            Query: {extraction_query}
            Output format: {{"products": ["Product A", "Product B"]}}"""

            res = await llm.ainvoke(prompt)
            content = res.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.replace("```", "").strip()

            if content and "{" in content:
                data = json.loads(content)
                product_names = data.get("products", [])

                # Look up IDs for these names
                comparison_ids = []
                for name in product_names:
                    # Use fuzzy match from PriceTool
                    p_info = price_tool.get_price_by_name(name)
                    if p_info:
                        if p_info.get("id"):
                            comparison_ids.append(str(p_info["id"]))
                    else:
                        print(f"DEBUG: PriceTool Lookup '{name}' -> NOT FOUND")

                if comparison_ids:
                    candidate_ids = comparison_ids
                    # Switch to MULTI_PRODUCT search strategy (or just vector search with ID filter)
                    # We increase top_k to ensure we get enough docs for ALL products
                    recall_top_k = 10 * len(comparison_ids)

                    # CRITICAL: Update query to focus on these products, otherwise "brand: Apple" might miss them
                    query = " ".join(product_names)

        except Exception as e:
            print(f"DEBUG: Comparison product extraction failed: {e}")

    # 1.5 Optimize Query using SQL Metadata (User Request)
    # If we have specific candidate IDs, use their Brand/Model to query RAG.
    if candidate_ids:
        try:
            # Fetch details to get names
            products = price_tool.get_products_by_ids(candidate_ids)

            product_query_parts = []
            for p in products:
                # DB column is 'branch', but let's be safe
                brand = p.get("branch") or p.get("brand") or ""
                model = p.get("model_name") or ""
                full_name = f"{brand} {model}".strip()
                if full_name:
                    product_query_parts.append(full_name)

            # Only replace query if we have a reasonable number of specific products
            # If we have 50 products, a query with 50 names might be too noisy/long.
            if product_query_parts and len(product_query_parts) <= 10:
                query = " ".join(product_query_parts)
                print(f"DEBUG: Optimized RAG Query with SQL Metadata: {query}")

        except Exception as e:
            print(f"DEBUG: Query optimization failed: {e}")

    # 2. Execute Recall with Optimized Query
    # IMPORTANT: Pass candidate_ids to RAG for filtering by product_id metadata
    # This is critical for price filtering and multi-product searches
    # For PRODUCT_INFO, we keep candidate_ids=None to allow broad search.
    use_candidate_ids = None
    if candidate_ids and state.get("route") != "PRODUCT_INFO":
        use_candidate_ids = candidate_ids
        print(
            f"DEBUG: Using candidate_ids for RAG filtering ({len(use_candidate_ids)} products): {use_candidate_ids[:5]}..."
        )

    rag_docs = await rag_service.recall(
        strategy=strategy_type,
        query=query,
        top_k=recall_top_k,
        language=language,
        candidate_ids=use_candidate_ids,
    )

    # 2.5 FALLBACK: If RAG returns NO documents for PRODUCT_INFO, use PriceTool
    # This handles short queries like "iphone 15" that don't match well in vector search
    if len(rag_docs) == 0 and state.get("route") == "PRODUCT_INFO":
        print(
            f"DEBUG: RAG returned 0 docs for PRODUCT_INFO query '{query}'. Trying PriceTool fallback..."
        )
        # Try to get product info from PriceTool
        price_info = price_tool.get_price_by_name(query)
        if price_info:
            # Create a synthetic document with the product info
            brand = price_info.get("branch") or price_info.get("brand", "")
            model = price_info.get("model_name", "")
            price_vnd = price_info.get("price_vnd", "N/A")
            price_usd = price_info.get("price_usd", "N/A")
            price_yen = price_info.get("price_yen", "N/A")

            content = f"""Sản phẩm: {brand} {model}

[AUTHORITATIVE PRICE TOOL INFO]
VND: {price_vnd}
USD: {price_usd}
YEN: {price_yen}
"""
            doc = Document(
                page_content=content,
                metadata={
                    "brand": brand,
                    "model_name": model,
                    **price_info,
                    "source": "price_tool_fallback",
                },
            )
            rag_docs = [doc]
            print(f"DEBUG: Created fallback document for {brand} {model}")

    # 2. Universal Enrichment: Ensure ALL docs have the correct price from tool
    # Even if they weren't filtered by price, we want authoritative prices.
    all_docs = rag_docs

    # 4. Universal Enrichment: Ensure ALL docs have the correct price from tool
    final_docs = []
    for doc in all_docs:
        # Extract model name from metadata or content
        # Try multiple field names as the metadata structure varies
        model_name = (
            doc.metadata.get("model")
            or doc.metadata.get("model_name")
            or doc.metadata.get("name")
        )
        # Try to infer if missing (rare for RAG docs if structured correctly, but raw chunks might be messy)
        if not model_name:
            # Basic heuristic: Check if 'Product:' line exists
            import re

            m = re.search(r"(?:Product|Name|Sản phẩm): (.+)", doc.page_content)
            if m:
                model_name = m.group(1).strip()

        if model_name:
            price_info = price_tool.get_price_by_name(model_name)
            if price_info:
                print(
                    f"DEBUG: ✅ Enriching doc with price for '{model_name}': VND {price_info.get('price_vnd')}"
                )

                # CRITICAL FIX: Remove ALL old price mentions from content
                # This prevents LLM from seeing conflicting prices
                import re

                content = doc.page_content

                # Remove common price patterns (USD, EUR, GBP, etc.)
                # Pattern: $XXX.XX, €XXX, £XXX, About XXX EUR/USD, etc.
                price_patterns = [
                    r"\$\s*[\d,]+\.?\d*",  # $499.99, $500
                    r"€\s*[\d,]+\.?\d*",  # €499.99
                    r"£\s*[\d,]+\.?\d*",  # £499.99
                    r"About\s+\d+\s+(EUR|USD|GBP)",  # About 600 EUR
                    r"Price:\s*[\$€£][\d,\.]+[\s/\$€£\d,\.]*",  # Price: $500 / €450
                    r"Giá:\s*[\$€£][\d,\.]+[\s/\$€£\d,\.]*",  # Giá: $500
                ]

                for pattern in price_patterns:
                    content = re.sub(
                        pattern,
                        "[PRICE REMOVED - SEE AUTHORITATIVE INFO ABOVE]",
                        content,
                        flags=re.IGNORECASE,
                    )

                # CRITICAL: Prepend Authoritative Info at the TOP so LLM sees it FIRST
                # Use prominent formatting
                update_str = (
                    f"*** [AUTHORITATIVE PRICE TOOL INFO - USE THESE PRICES ONLY] ***\n"
                )
                update_str += f"VND: {price_info.get('price_vnd', 'N/A')}\n"
                update_str += f"USD: {price_info.get('price_usd', 'N/A')}\n"
                update_str += f"YEN: {price_info.get('price_yen', 'N/A')}\n"
                update_str += f"*** IGNORE ANY OTHER PRICES IN THIS DOCUMENT ***\n\n"

                # Prepend to cleaned content
                doc.page_content = update_str + content
                # Update metadata
                doc.metadata.update(price_info)
            else:
                print(f"DEBUG: ❌ No price found for model_name='{model_name}'")

        final_docs.append(doc)

    docs = final_docs

    return {"recall_docs": docs, "path": (state.get("path") or []) + ["recall_node"]}
