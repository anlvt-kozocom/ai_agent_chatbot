"""
Script to sync prices from product_prices.json to clean data files.
This removes outdated prices from RAG data and adds correct prices from database.
"""

import json
import os
from typing import Dict, List


def load_price_data() -> Dict[str, Dict]:
    """Load prices from product_prices.json and create lookup by brand+model"""
    with open("data/product_prices.json", "r", encoding="utf-8") as f:
        prices = json.load(f)

    # Create lookup dict: "brand model" -> price_data
    price_lookup = {}
    for item in prices:
        brand = item["branch"]  # Note: field is called 'branch' in DB
        model = item["model_name"]
        key = f"{brand} {model}".lower().strip()
        price_lookup[key] = {
            "id": item["id"],
            "price_vnd": int(item["price_vnd"]),
            "price_usd": int(item["price_usd"]),
            "price_yen": int(item["price_yen"]),
        }

    print(f"✅ Loaded {len(price_lookup)} products from product_prices.json")
    return price_lookup


def fuzzy_match_price(brand: str, model: str, price_lookup: Dict) -> Dict:
    """Try to find price using fuzzy matching"""
    # Try exact match first
    key = f"{brand} {model}".lower().strip()
    if key in price_lookup:
        return price_lookup[key]

    # Try model name only (some models don't have brand prefix)
    for lookup_key, price_data in price_lookup.items():
        if model.lower() in lookup_key:
            return price_data

    return None


def clean_device(device: Dict, brand: str, price_lookup: Dict, stats: Dict) -> Dict:
    """Clean a single device: sync price, remove unnecessary fields"""
    model = device.get("model_name", "")

    # Find matching price
    price_data = fuzzy_match_price(brand, model, price_lookup)

    if price_data:
        # Update with correct prices
        device["price_vnd"] = price_data["price_vnd"]
        device["price_usd"] = price_data["price_usd"]
        device["price_yen"] = price_data["price_yen"]
        device["product_id"] = price_data["id"]
        stats["synced"] += 1
    else:
        # No price found - remove price fields to avoid confusion
        device.pop("price_vnd", None)
        device.pop("price_usd", None)
        device.pop("price_yen", None)
        device.pop("product_id", None)
        stats["no_price"] += 1
        print(f"  ⚠️  No price found for: {brand} {model}")

    # Remove old price field (if exists)
    device.pop("price", None)

    # Clean specifications - remove Price from Misc
    if "specifications" in device:
        specs = device["specifications"]

        # Remove price from Misc section
        if "Misc" in specs and isinstance(specs["Misc"], dict):
            specs["Misc"].pop("Price", None)

            # If Misc is now empty, remove it
            if not specs["Misc"]:
                specs.pop("Misc")

        # Remove unnecessary spec categories (optional - customize as needed)
        unnecessary_keys = ["Our Tests", "EU LABEL"]  # Add more if needed
        for key in unnecessary_keys:
            specs.pop(key, None)

    return device


def sync_clean_data_file(filepath: str, price_lookup: Dict) -> Dict:
    """Sync prices in a clean data file"""
    print(f"\n📄 Processing: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    stats = {"synced": 0, "no_price": 0, "total": 0}

    # Process each brand
    for brand_data in data:
        brand = brand_data.get("brand_name", "")
        devices = brand_data.get("devices", [])

        print(f"\n  {brand}: {len(devices)} devices")

        # Clean each device
        cleaned_devices = []
        for device in devices:
            stats["total"] += 1
            cleaned = clean_device(device, brand, price_lookup, stats)
            cleaned_devices.append(cleaned)

        brand_data["devices"] = cleaned_devices

    # Save cleaned data
    backup_path = filepath.replace(".json", "_backup.json")

    # Create backup
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n  💾 Backup saved: {backup_path}")

    # Save cleaned data
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✅ Cleaned data saved: {filepath}")

    return stats


def main():
    """Main function"""
    print("=" * 70)
    print("🔧 SYNC CLEAN DATA WITH PRODUCT PRICES")
    print("=" * 70)

    # Load price data
    price_lookup = load_price_data()

    # Process all clean data files
    clean_files = [
        "data/clean/phone_vi.json",
        "data/clean/phone_en.json",
        "data/clean/phone_ja.json",
    ]

    total_stats = {"synced": 0, "no_price": 0, "total": 0}

    for filepath in clean_files:
        if os.path.exists(filepath):
            stats = sync_clean_data_file(filepath, price_lookup)
            for key in total_stats:
                total_stats[key] += stats[key]
        else:
            print(f"⚠️  File not found: {filepath}")

    # Print summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"Total devices processed: {total_stats['total']}")
    print(f"✅ Successfully synced:   {total_stats['synced']}")
    print(f"⚠️  No price found:       {total_stats['no_price']}")
    print(
        f"✅ Coverage:              {total_stats['synced'] / total_stats['total'] * 100:.1f}%"
    )
    print("\n✨ Done! Clean data has been updated with correct prices.")
    print("💡 Next step: Re-index the vector store for changes to take effect.")


if __name__ == "__main__":
    main()
