"""
Script to re-index the vector store with the updated clean data.
This should be run after syncing prices in clean data files.
"""

import asyncio
from app.services.rag_service import rag_service


def main():
    print("=" * 70)
    print("🔄 RE-INDEXING VECTOR STORE WITH UPDATED PRICES")
    print("=" * 70)
    print("\n⚠️  This will rebuild the vector store from scratch.")
    print("   The updated clean data files will be used.\n")

    print("🚀 Starting re-index...")
    print("   (This may take a few minutes depending on data size)\n")

    # Re-build the vector store with reload_data=True
    rag_service.initialize(reload_data=True)

    print("\n" + "=" * 70)
    print("✅ RE-INDEX COMPLETE!")
    print("=" * 70)
    print(
        "\n💡 The vector store now contains the correct prices from product_prices.json"
    )
    print(
        "🧪 You can now test queries like 'samsung 17 triệu có những điện thoại nào?'"
    )


if __name__ == "__main__":
    main()
