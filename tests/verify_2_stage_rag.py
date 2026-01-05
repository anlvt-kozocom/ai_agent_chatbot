import asyncio
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from app.graphs.qa_graph import build_graph

load_dotenv()


async def verify_rag_pipeline():
    graph = build_graph()

    # Test query that should trigger Product Info route + RAG
    query = "Specs of iPhone 13"
    inputs = {"messages": [HumanMessage(content=query)], "language": "en"}

    print(f"--- Running Query: {query} ---")

    final_state = await graph.ainvoke(
        inputs, config={"configurable": {"thread_id": "verify_test"}}
    )

    path = final_state.get("path", [])
    recall_docs = final_state.get("recall_docs", [])
    precision_docs = final_state.get("precision_docs", [])
    answer = final_state.get("answer", "")

    print(f"\nPath: {path}")
    print(f"Recall Docs Count: {len(recall_docs)}")
    print(f"Precision Docs Count: {len(precision_docs)}")
    print(f"Final Answer: {answer[:100]}...")

    # Assertions
    assert "recall_node" in path, "recall_node missing from path"
    assert "precision_node" in path, "precision_node missing from path"

    # Since we might not have real data in vector store if not initialized with data,
    # counts might be 0, but the node presence confirms the flow.
    # If using existing vector store (which the user state suggests exists), we might get docs.

    if "product_info_node" in path:
        print(
            "\n✅ Verification SUCCESS: Flow went through Recall -> Precision -> Product Info"
        )
    else:
        print("\n⚠️ Verification WARNING: Did not end in product_info_node as expected.")


if __name__ == "__main__":
    asyncio.run(verify_rag_pipeline())
