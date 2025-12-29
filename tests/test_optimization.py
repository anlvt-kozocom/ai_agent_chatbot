import sys
import os

# Add app to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.router_agent import heuristic_route
from app.utils.config import MAX_HISTORY_WINDOW


def test_heuristic_routing():
    print("Testing Heuristic Routing...")

    test_cases = [
        # English
        ("I want to buy a phone", "recommendation"),
        ("Need a cheap mobile", "recommendation"),
        ("Recommend me a laptop", "recommendation"),
        ("What is the battery of iPhone 15", "product_info"),
        ("Tell me about Samsung S24 specs", "product_info"),
        # Vietnamese
        ("Tôi muốn mua điện thoại", "recommendation"),
        ("Tư vấn giúp tôi iphone", "recommendation"),
        ("Giá con này bao nhiêu", "recommendation"),
        ("Pin iphone 15 dùng được bao lâu", "product_info"),
        ("Thông số samsung s24", "product_info"),
        # Japanese
        ("iPhoneを買いたい", "recommendation"),
        ("安いスマホをおすすめして", "recommendation"),
        ("iPhone 15のバッテリーは？", "product_info"),
        ("Galaxyのスペックを教えて", "product_info"),
        # None/Fallback
        ("Hello", None),
        ("How are you?", None),
        ("Is apple better than samsung?", None),
    ]

    passed = 0
    for query, expected in test_cases:
        result = heuristic_route(query)
        if result == expected:
            print(f"[PASS] '{query}' -> {result}")
            passed += 1
        else:
            print(f"[FAIL] '{query}' -> Expected {expected}, Got {result}")

    print(f"Passed {passed}/{len(test_cases)}")


def test_config():
    print(f"\nTesting Config...")
    print(f"MAX_HISTORY_WINDOW = {MAX_HISTORY_WINDOW}")
    assert isinstance(MAX_HISTORY_WINDOW, int)
    assert MAX_HISTORY_WINDOW > 0


if __name__ == "__main__":
    test_config()
    test_heuristic_routing()
