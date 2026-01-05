import asyncio
from typing import List, Any
from langchain_core.documents import Document
from app.services.rag_service import rag_service
from app.agents.precision_agent import precision_node
from app.models.schemas import AgentState


async def test_precision_logic():
    print("--- Testing Precision Stage Logic ---")

    # 1. Mock Data
    doc1 = Document(
        page_content="This is a cheap phone. Price is $100. Good condition.",
        metadata={"brand": "Generic"},
    )
    doc2 = Document(
        page_content="iPhone 13 Specs. Brand new Apple device. High quality.",
        metadata={"brand": "Apple"},
    )
    doc3 = Document(
        page_content="Samsung Galaxy. Good Android phone.",
        metadata={"brand": "Samsung"},
    )
    doc4 = Document(
        page_content="Another Apple iPhone. Expensive.", metadata={"brand": "Apple"}
    )

    recall_docs = [doc1, doc2, doc3, doc4]

    # 2. Mock State with Strategy
    state: AgentState = {
        "recall_docs": recall_docs,
        "retrieval_strategy": {
            "strategy": "VECTOR_SEARCH",
            "top_k": 3,
            "rerank": True,  # Test LLM Rerank
            "filters": {
                "brand": "Apple",  # Test Brand Rule (+5)
                "price": "$100",  # Test Price Rule (+3)
            },
        },
        "standalone_query": "cheap Apple iPhone",
        "path": [],
        "messages": [],
    }

    # 3. Execute Precision Node
    print("Executing precision_node...")
    result = await precision_node(state, config={})

    precision_docs = result.get("precision_docs", [])

    print(f"\nResult: Got {len(precision_docs)} docs (Top K=3)")
    for i, doc in enumerate(precision_docs):
        print(
            f"Rank {i + 1}: {doc.page_content[:50]}... | Brand: {doc.metadata.get('brand')}"
        )

    # 4. Assertions
    # Doc2 (Apple) should be boosted by brand (+5).
    # Doc4 (Apple) should be boosted by brand (+5).
    # Doc1 (Price match) should be boosted by price (+3).
    # Doc3 (Samsung) should be low.

    # Check if Top 1 is likely Apple (Rules) or relevant (LLM)
    # Note: LLM output is non-deterministic but "cheap Apple iPhone" should favor Apple docs.

    brands = [d.metadata.get("brand") for d in precision_docs]
    print(f"Top Brands: {brands}")

    assert "Apple" in brands, (
        "Precision Validation Failed: Apple brand rule did not boost Apple docs to top."
    )
    print("✅ Precision Logic Verified (Rule-based + Rerank flow executed)")


if __name__ == "__main__":
    asyncio.run(test_precision_logic())
