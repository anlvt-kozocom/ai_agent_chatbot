import os
import re
import json
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


I18N_LABELS = {
    "en": {
        "product": "Product",
        "description": "Description",
        "usage": "Recommended Usage",
        "market_segment": "Market Segment",
        "price": "Price",
        "tech_specs": "Technical Specifications",
        "image": "Image",
    },
    "vi": {
        "product": "Sản phẩm",
        "description": "Mô tả",
        "usage": "Sử dụng đề xuất",
        "market_segment": "Phân khúc thị trường",
        "price": "Giá",
        "tech_specs": "Thông số kỹ thuật",
        "image": "Hình ảnh",
    },
    "ja": {
        "product": "製品",
        "description": "説明",
        "usage": "推奨される使用法",
        "market_segment": "市場セグメント",
        "price": "価格",
        "tech_specs": "技術仕様",
        "image": "画像",
    },
}


def clean_number(text: Any) -> int:
    """Extract numeric value from text (e.g., '5000 mAh' -> 5000, '10,000,000' -> 10000000)."""
    if not text:
        return 0
    if isinstance(text, (int, float)):
        return int(text)
    # Remove commas and dots (separators) to safely find integer sequence
    clean_text = str(text).replace(",", "").replace(".", "")
    matches = re.findall(r"(\d+)", clean_text)
    return int(matches[0]) if matches else 0


def format_device_to_text(brand: str, device: Dict[str, Any], lang: str = "en") -> str:
    """Convert a device JSON object into a text representation for RAG."""
    labels = I18N_LABELS.get(lang, I18N_LABELS["en"])

    model = device.get("model_name", "Unknown Model")
    specs = device.get("specifications", {})

    # Start with high-level summary including new fields
    text_parts = [f"{labels['product']}: {brand} {model}"]

    if "description" in device:
        text_parts.append(f"{labels['description']}: {device['description']}")

    if "usage" in device:
        text_parts.append(f"{labels['usage']}: {device['usage']}")

    if "price_range" in device:
        text_parts.append(f"{labels['market_segment']}: {device['price_range']}")

    if "price" in device:
        text_parts.append(f"{labels['price']}: {device['price']}")

    # Detailed Specifications
    if specs:
        text_parts.append(f"\n{labels['tech_specs']}:")
        for category, details in specs.items():
            if isinstance(details, dict):
                detail_str = ", ".join(f"{k}: {v}" for k, v in details.items())
                text_parts.append(f"- {category}: {detail_str}")
            else:
                text_parts.append(f"- {category}: {details}")

    # Add Image URL if available (useful for frontend even if not for search)
    if "imageUrl" in device:
        text_parts.append(f"{labels['image']}: {device['imageUrl']}")

    return "\n".join(text_parts)


def load_text_files(directory: str) -> List[Document]:
    """
    Load .txt and .json files from a directory.
    - .txt: Checks for '### END OF PRODUCT ###' delimiter.
    - .json: Parses structured product data.
    """
    documents = []
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        return []

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        # Handle JSON files
        if filename.endswith(".json"):
            try:
                # Detect language from filename (e.g., phone_vi.json -> vi)
                lang = "en"
                if "_vi.json" in filename:
                    lang = "vi"
                elif "_ja.json" in filename:
                    lang = "ja"
                elif "_en.json" in filename:
                    lang = "en"

                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Expecting a list of brands with devices
                if isinstance(data, list):
                    for brand_entry in data:
                        brand_name = brand_entry.get("brand_name", "")
                        devices = brand_entry.get("devices", [])

                        for device in devices:
                            content = format_device_to_text(
                                brand_name, device, lang=lang
                            )

                            # Extract fields for metadata
                            specs = device.get("specifications", {})

                            # 1. Price
                            price_str = device.get("price", "")
                            price_val = clean_number(price_str)

                            # 2. Specs (Battery, Memory)
                            # Note: Correct path is device -> specifications -> Battery/Memory
                            bat_info = specs.get("Battery", {}).get("Type", "")
                            mem_info = specs.get("Memory", {}).get("Internal", "")

                            bat_cap = clean_number(bat_info)

                            # 3. RAM (Extract from Memory string like '8GB RAM')
                            ram_match = re.search(
                                r"(\d+)GB RAM", mem_info, re.IGNORECASE
                            )
                            ram_val = int(ram_match.group(1)) if ram_match else 0

                            # Enhanced Metadata for filtering
                            metadata = {
                                "brand": brand_name,
                                "model": device.get("model_name"),
                                "language": lang,
                                # Price info
                                "price_raw": price_str,
                                "price_int": price_val,  # Use for range filter (e.g. price_int < 10000000)
                                "price_range": device.get("price_range", "Unknown"),
                                # Usage/Features
                                "usage": device.get("usage", "General"),
                                # Technical Specs (Numeric for filtering)
                                "ram_gb": ram_val,
                                "battery_mah": bat_cap,
                                # Raw info
                                "memory_info": mem_info,
                                "battery_info": bat_info,
                            }

                            documents.append(
                                Document(page_content=content, metadata=metadata)
                            )
            except Exception as e:
                print(f"Error reading JSON file {filename}: {e}")

    return documents


def split_documents(
    documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200
) -> List[Document]:
    """Split documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,
    )
    return text_splitter.split_documents(documents)


def format_requirements(requirements: Dict[str, Any]) -> str:
    """Format requirements dictionary into a readable string."""
    if not requirements:
        return "No specific requirements."

    lines = []
    for key, value in requirements.items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)
