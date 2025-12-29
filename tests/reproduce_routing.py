import sys
import os

sys.path.append(os.getcwd())
from app.agents.router_agent import heuristic_route


def test_price_routing_reproduction():
    test_cases = [
        ("Price of iPhone 15", "product_info"),
        ("Giá của iPhone 15", "product_info"),
        ("iPhone 15 giá bao nhiêu", "product_info"),
        ("Recommend a phone with good price", "recommendation"),
        ("Điện thoại giá rẻ", "recommendation"),
    ]

    for query, expected in test_cases:
        result = heuristic_route(query)
        print(f"'{query}' -> {result} (Expected: {expected})")
        # heuristic_route might return None if it wants to defer to LLM,
        # but here we expect strictly defined behavior if we want to valid heuristic.
        # Currently it probably returns 'recommendation' for the first cases.


if __name__ == "__main__":
    test_price_routing_reproduction()
