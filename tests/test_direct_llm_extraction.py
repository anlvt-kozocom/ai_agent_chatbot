"""
Direct test of LLM with extraction prompt
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.llm import get_llm
from app.prompts.extraction_prompts import EXTRACTION_SYSTEM_PROMPT


async def test_direct_llm():
    llm = get_llm(temperature=0)

    test_queries = [
        "Apple",
        "Samsung",
        "Xiaomi",
        "Tôi chọn Apple",
        "iPhone",
    ]

    print("\n" + "=" * 80)
    print("Testing Direct LLM Call with Extraction Prompt")
    print("=" * 80 + "\n")

    for query in test_queries:
        prompt = EXTRACTION_SYSTEM_PROMPT.replace("{text}", query)

        try:
            response = await llm.ainvoke(prompt)
            content = response.content

            print(f"Query: '{query}'")
            print(f"Raw LLM Response:\n{content}")

            # Try to parse JSON
            try:
                # Clean up the response
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.replace("```", "").strip()

                data = json.loads(content)
                print(f"Parsed JSON: {data}")
                print(f"Brand: {data.get('brand')}")
            except:
                print("Could not parse as JSON")

            print("-" * 80)
            print()
        except Exception as e:
            print(f"Query: '{query}'")
            print(f"ERROR: {e}")
            print("-" * 80)
            print()


if __name__ == "__main__":
    asyncio.run(test_direct_llm())
