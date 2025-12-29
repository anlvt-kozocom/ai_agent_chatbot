import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.router_agent import heuristic_route


def test_comparison_routing():
    print("Testing Comparison Routing...")

    test_cases = [
        ("Compare iPhone 15 and Samsung S24", "comparison"),
        ("What is the difference between iPhone 14 and 15?", "comparison"),
        ("So sánh iPhone 15 vs S24", "comparison"),
        ("Nên mua iPhone hay Samsung", "comparison"),
        ("iPhone 15 vs S24 どっち？", "comparison"),
        ("I want to buy a phone", "recommendation"),
        ("iPhone 15 specs", "product_info"),
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


if __name__ == "__main__":
    test_comparison_routing()
