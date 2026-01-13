"""
Test extraction chain and see raw output
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.chains.extraction_chain import build_extraction_chain
from langchain_core.output_parsers import JsonOutputParser


async def test_extraction_debug():
    chain = build_extraction_chain()

    query = "Apple"

    print(f"\n{'=' * 80}")
    print(f"Testing Query: '{query}'")
    print(f"{'=' * 80}\n")

    # Invoke the chain
    result = await chain.ainvoke({"text": query})

    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    print(f"Brand: {result.get('brand')}")

    # Also try manual parsing
    print(f"\n{'=' * 80}")
    print("Testing Manual LLM + Parse Flow")
    print(f"{'=' * 80}\n")

    from app.services.llm import get_llm
    from app.prompts.extraction_prompts import EXTRACTION_SYSTEM_PROMPT
    from langchain_core.prompts import ChatPromptTemplate

    llm = get_llm(temperature=0)
    prompt_template = ChatPromptTemplate.from_template(EXTRACTION_SYSTEM_PROMPT)

    # Get prompt
    prompt = await prompt_template.ainvoke({"text": query})
    print(f"Prompt: {prompt}")
    print()

    # Get LLM response
    llm_response = await llm.ainvoke(prompt)
    print(f"LLM Response:")
    print(llm_response.content)
    print()

    # Parse
    parser = JsonOutputParser()
    try:
        parsed = parser.parse(llm_response.content)
        print(f"Parsed: {parsed}")
        print(f"Brand: {parsed.get('brand')}")
    except Exception as e:
        print(f"Parse error: {e}")


if __name__ == "__main__":
    asyncio.run(test_extraction_debug())
