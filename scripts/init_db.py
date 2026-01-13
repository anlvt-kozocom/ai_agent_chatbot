import sqlite3
import json
import os
import random

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
JSON_FILE = os.path.join(DATA_DIR, "product_prices.json")
DB_FILE = os.path.join(DATA_DIR, "product_prices.db")


def init_db():
    print(f"Initializing database at {DB_FILE}...")

    # Connect to SQLite database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Drop table if exists
    cursor.execute("DROP TABLE IF EXISTS products")

    # Create table
    create_table_sql = """
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        branch TEXT,
        model_name TEXT,
        price_vnd INTEGER,
        price_usd INTEGER,
        price_yen INTEGER,
        quantity INTEGER
    );
    """
    cursor.execute(create_table_sql)
    print("Table 'products' created.")

    # Load data from JSON
    if not os.path.exists(JSON_FILE):
        print(f"Error: JSON file not found at {JSON_FILE}")
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded {len(data)} items from JSON.")

    # Insert data
    inserted_count = 0
    for item in data:
        try:
            # Extract and clean data
            p_id = item.get("id")
            branch = item.get("branch")
            model_name = item.get("model_name")

            # Helper to clean and convert price
            def parse_price(val):
                if isinstance(val, int):
                    return val
                if isinstance(val, str):
                    # Remove non-numeric characters except maybe minus sign (though prices shouldn't be negative)
                    return int("".join(filter(str.isdigit, val)))
                return 0

            price_vnd = parse_price(item.get("price_vnd", 0))
            price_usd = parse_price(item.get("price_usd", 0))
            price_yen = parse_price(item.get("price_yen", 0))
            quantity = random.randint(0, 20)

            cursor.execute(
                """
                INSERT INTO products (id, branch, model_name, price_vnd, price_usd, price_yen, quantity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (p_id, branch, model_name, price_vnd, price_usd, price_yen, quantity),
            )
            inserted_count += 1

        except Exception as e:
            print(f"Error inserting item {item}: {e}")

    # Commit changes
    conn.commit()
    conn.close()

    print(f"Successfully inserted {inserted_count} records.")


if __name__ == "__main__":
    init_db()
