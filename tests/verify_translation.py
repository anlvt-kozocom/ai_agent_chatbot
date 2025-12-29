import asyncio
import sys
import os

# Add the project root to the path so we can import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from app.chains.translation_chain import build_reverse_translation_chain


async def test_reverse_translation():
    print("Building reverse translation chain...")
    try:
        chain = build_reverse_translation_chain()
    except Exception as e:
        print(f"Error building chain: {e}")
        return

    # Scenario: Casual/Slang input that needs to be professionalized
    text = "Hey buddy, check this out, it's dirt cheap and totally barely used."
    target_lang = "vi"

    print(f"Input Text: {text}")
    print(f"Target Language: {target_lang}")

    try:
        result = await chain.ainvoke({"text": text, "target_language": target_lang})
        print("-" * 20)
        print(f"Translated Output:\n{result}")
        print("-" * 20)
    except Exception as e:
        print(f"Error invoking chain: {e}")


if __name__ == "__main__":
    asyncio.run(test_reverse_translation())
