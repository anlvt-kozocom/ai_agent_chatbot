"""
Test extraction chain with simple brand input
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.chains.extraction_chain import build_extraction_chain


async def test_extraction():
    chain = build_extraction_chain()

    # Test cases
    test_cases = [
        "Apple",
        "Samsung",
        "apple",
        "samsung",
        "Tôi chọn Apple",
        "Tôi muốn mua Apple",
        "iPhone",
    ]

    print("\n" + "=" * 80)
    print("Testing Extraction Chain with Brand Names")
    print("=" * 80 + "\n")

    for query in test_cases:
        try:
            result = await chain.ainvoke({"text": query})
            print(f"Query: '{query}'")
            print(f"Result: {result}")
            print(f"Brand extracted: {result.get('brand')}")
            print("-" * 40)
        except Exception as e:
            print(f"Query: '{query}'")
            print(f"ERROR: {e}")
            print("-" * 40)


if __name__ == "__main__":
    asyncio.run(test_extraction())
