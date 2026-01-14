import sqlite3
import json
import os
import re

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_FILE = os.path.join(DATA_DIR, "product_prices.db")
CLEAN_DIR = os.path.join(DATA_DIR, "clean")


def extract_battery_mah(battery_spec):
    """
    Extract battery capacity in mAh from battery specification string.

    Examples:
        "5000 mAh" -> 5000
        "Li-Ion 5000 mAh" -> 5000
        "Li-Po 5000 mAh, non-removable" -> 5000
        "3349 mAh" -> 3349

    Returns:
        int: Battery capacity in mAh, or None if not found
    """
    if not battery_spec:
        return None

    # Pattern to match numbers followed by "mAh" (case-insensitive)
    pattern = r"(\d+)\s*mAh"
    match = re.search(pattern, battery_spec, re.IGNORECASE)

    if match:
        return int(match.group(1))

    return None


def load_battery_data_from_json():
    """
    Load battery data from JSON files in data/clean directory.

    Returns:
        dict: Mapping of product_id to battery_capacity (in mAh)
    """
    battery_data = {}

    # Process all phone JSON files (en, vi, ja)
    json_files = ["phone_en.json", "phone_vi.json", "phone_ja.json"]

    for json_file in json_files:
        file_path = os.path.join(CLEAN_DIR, json_file)

        if not os.path.exists(file_path):
            print(f"Warning: {json_file} not found, skipping...")
            continue

        print(f"Processing {json_file}...")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Iterate through brands and devices
        for brand_data in data:
            devices = brand_data.get("devices", [])

            for device in devices:
                product_id = device.get("product_id")

                if not product_id:
                    continue

                # Skip if already processed (first file wins)
                if product_id in battery_data:
                    continue

                # Extract battery spec
                specs = device.get("specifications", {})
                battery_info = specs.get("Battery", {})
                battery_type = battery_info.get("Type", "")

                # Extract mAh value
                battery_mah = extract_battery_mah(battery_type)

                if battery_mah:
                    battery_data[product_id] = battery_mah
                    print(f"  Product ID {product_id}: {battery_mah} mAh")

    print(f"\nExtracted battery data for {len(battery_data)} products")
    return battery_data


def add_battery_column():
    """
    Add battery_capacity column to products table and populate with data.
    """
    print(f"Connecting to database: {DB_FILE}")

    if not os.path.exists(DB_FILE):
        print(f"Error: Database file not found at {DB_FILE}")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check if column already exists
    cursor.execute("PRAGMA table_info(products);")
    columns = [col[1] for col in cursor.fetchall()]

    if "battery_capacity" in columns:
        print("Column 'battery_capacity' already exists. Dropping and recreating...")
        # SQLite doesn't support DROP COLUMN directly, so we'll update the values
        cursor.execute("UPDATE products SET battery_capacity = NULL;")
    else:
        print("Adding 'battery_capacity' column to products table...")
        cursor.execute("ALTER TABLE products ADD COLUMN battery_capacity INTEGER;")

    conn.commit()

    # Load battery data from JSON files
    battery_data = load_battery_data_from_json()

    # Update database with battery data
    updated_count = 0
    not_found_count = 0

    print("\nUpdating database with battery capacity...")

    for product_id, battery_mah in battery_data.items():
        cursor.execute(
            "UPDATE products SET battery_capacity = ? WHERE id = ?",
            (battery_mah, product_id),
        )

        if cursor.rowcount > 0:
            updated_count += 1
        else:
            not_found_count += 1

    conn.commit()

    # Verify results
    cursor.execute("SELECT COUNT(*) FROM products WHERE battery_capacity IS NOT NULL;")
    total_with_battery = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products;")
    total_products = cursor.fetchone()[0]

    print(f"\n=== Migration Summary ===")
    print(f"Total products in database: {total_products}")
    print(f"Products updated with battery data: {updated_count}")
    print(f"Products with battery capacity: {total_with_battery}")
    print(f"Products not found in JSON: {not_found_count}")
    print(f"Products without battery data: {total_products - total_with_battery}")

    # Show sample data
    print("\n=== Sample Records ===")
    cursor.execute("""
        SELECT id, branch, model_name, battery_capacity 
        FROM products 
        WHERE battery_capacity IS NOT NULL 
        ORDER BY battery_capacity DESC 
        LIMIT 5;
    """)

    print("Top 5 products by battery capacity:")
    for row in cursor.fetchall():
        print(f"  ID {row[0]}: {row[1]} {row[2]} - {row[3]} mAh")

    conn.close()
    print("\n✅ Migration completed successfully!")


if __name__ == "__main__":
    add_battery_column()
