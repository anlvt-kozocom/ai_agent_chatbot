import os
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

import json
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def format_device_to_text(brand: str, device: Dict[str, Any]) -> str:
    """Convert a device JSON object into a text representation."""
    model = device.get("model_name", "Unknown Model")
    specs = device.get("specifications", {})
    
    text_parts = [f"Name: {brand} {model}"]
    
    # Flatten specifications for text search
    if specs:
        text_parts.append("Specifications:")
        for category, details in specs.items():
            if isinstance(details, dict):
                detail_str = ", ".join(f"{k}: {v}" for k, v in details.items())
                text_parts.append(f"- {category}: {detail_str}")
            else:
                text_parts.append(f"- {category}: {details}")
    if "price_vnd" in device:
        text_parts.append(f"Price in VND: {device['price_vnd']}")
    if "price_usd" in device:
        text_parts.append(f"Price in USD: {device['price_usd']}")
    if "price_yen" in device:
        text_parts.append(f"Price in YEN: {device['price_yen']}")
        
    # Add other top-level fields if needed
    if "imageUrl" in device:
        text_parts.append(f"Image: {device['imageUrl']}")
        
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
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                # Expecting a list of brands with devices
                if isinstance(data, list):
                    for brand_entry in data:
                        brand_name = brand_entry.get("brand_name", "")
                        devices = brand_entry.get("devices", [])
                        
                        
                        for device in devices:
                            content = format_device_to_text(brand_name, device)
                            price_vnd = device.get("price_vnd", "")
                            price_usd = device.get("price_usd", "")
                            price_yen = device.get("price_yen", "")
                            memory = device.get("Memory", {}).get("Internal", "")
                            battery = device.get("Battery", {}).get("Type", "")
                            metadata = {
                                "brand": brand_name,
                                "model": device.get("model_name"),
                                "price_vnd": price_vnd,
                                "price_usd": price_usd,
                                "price_yen": price_yen,
                                "memory": memory,
                                "battery": battery
                            }
                            documents.append(Document(page_content=content, metadata=metadata))
            except Exception as e:
                print(f"Error reading JSON file {filename}: {e}")

    return documents

def split_documents(documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
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
        return "Chưa có yêu cầu cụ thể."
    
    lines = []
    for key, value in requirements.items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)
