import os
import sys
import asyncio
from typing import Dict, Any

# Add app to path
sys.path.append(os.getcwd())

from app.agents.price_agent import price_filtering_node
from app.tools.price_tool import price_tool


async def verify_agent_integration():
    print("--- Verifying Agent Integration (Extreme Price Logic) ---")

    # Helper to simulate state
    def create_state(requirements: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "requirements": requirements,
            "messages": [],
            "path": [],
            "language": "en",
        }

    # Test Case 1: Cheapest Samsung (Brand + Sort ASC)
    print("\n1. Testing 'Cheapest Samsung' (brand='Samsung', price_sort='asc')")
    state1 = create_state({"brand": "Samsung", "price_sort": "asc"})
    result1 = await price_filtering_node(state1)

    if result1.get("candidate_ids"):
        product_id = result1["candidate_ids"][0]
        # Verify directly with DB to see what this ID corresponds to
        conn = price_tool._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = dict(cursor.fetchone())
        conn.close()
        print(
            f"Result: ID {product_id} -> {product['model_name']} ({product['price_vnd']} VND)"
        )
    else:
        print("Result: No candidates found.")

    # Test Case 2: Most Expensive Apple (Brand + Sort DESC)
    print("\n2. Testing 'Most Expensive Apple' (brand='Apple', price_sort='desc')")
    state2 = create_state({"brand": "Apple", "price_sort": "desc"})
    result2 = await price_filtering_node(state2)

    if result2.get("candidate_ids"):
        product_id = result2["candidate_ids"][0]
        conn = price_tool._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = dict(cursor.fetchone())
        conn.close()
        print(
            f"Result: ID {product_id} -> {product['model_name']} ({product['price_vnd']} VND)"
        )
    else:
        print("Result: No candidates found.")

    # Test Case 3: Most Expensive Overall (No Brand, Sort DESC)
    print("\n3. Testing 'Most Expensive Overall' (brand=None, price_sort='desc')")
    state3 = create_state({"price_sort": "desc"})
    result3 = await price_filtering_node(state3)

    if result3.get("candidate_ids"):
        product_id = result3["candidate_ids"][0]
        conn = price_tool._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = dict(cursor.fetchone())
        conn.close()
        print(
            f"Result: ID {product_id} -> {product['model_name']} ({product['price_vnd']} VND)"
        )
    else:
        print("Result: No candidates found.")


if __name__ == "__main__":
    asyncio.run(verify_agent_integration())
