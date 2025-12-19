import json
import re

def clean_price(price: str, convert_to: str = 'VND') -> str:
    # convert price string like 1 ₹ = 291,54 VND, 1 USD to 26336 VND, 1 EUR to 30836 VND
    if not price:
        return "Unknown price"

    rates_list = {
        'VND': {
            'EUR': 30836,
            '€': 30836,
            'USD': 26336,
            '$': 26336,
            'INR': 291.54,
            '₹': 291.54
        },
        'USD': {
            'EUR': 1.18,
            '€': 1.18,
            'USD': 1,
            '$': 1,
            'INR': 0.011,
            '₹': 0.011
        },
        'YEN': {
            'EUR': 145.23,
            '€': 145.23,
            'USD': 130.32,
            '$': 130.32,
            'INR': 1.52,
            '₹': 1.52
        }
    }

    rates = rates_list.get(convert_to, {})
    
    # Remove commas (thousands separators)
    clean_s = price.replace(',', '')

    for symbol, rate in rates.items():
        escaped_symbol = re.escape(symbol)
        # Pattern: Symbol followed by number OR Number followed by Symbol
        # We handle optional whitespace
        pattern = fr"(?:{escaped_symbol})\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:{escaped_symbol})"

        match = re.search(pattern, clean_s, re.IGNORECASE)
        if match:
            # group 1 is number if symbol matched first
            # group 2 is number if symbol matched second
            val_str = match.group(1) or match.group(2)
            if val_str:
                val = float(val_str)
                converted = int(val * rate)
                if convert_to == 'VND':
                    return f"{converted} VND"
                elif convert_to == 'USD':
                    return f"${converted}"
                elif convert_to == 'YEN':
                    return f"¥{converted}"
                else:
                    return "Unknown price"

    return "Unknown price"


def clean_number(text):
    """Helper to extract number from string (e.g., '5000 mAh' -> 5000)"""
    if not text: return 0
    matches = re.findall(r'(\d+)', text.replace(',', '').replace('.', ''))
    return int(matches[0]) if matches else 0


def analyze_device(device):
    """
    Analyzes device specs to generate description, usage, and price range in English.
    Returns a tuple: (description, usage, price_range)
    """
    specs = device.get('specifications', {})
    model = device.get('model_name', 'Product')
    
    # 1. Extract Data
    # Battery
    bat_info = specs.get('Battery', {}).get('Type', '')
    bat_cap = clean_number(bat_info)
    
    # Display
    display_info = specs.get('Display', {}).get('Type', '') + " " + specs.get('Display', {}).get('Resolution', '')
    is_high_refresh = '120Hz' in display_info or '144Hz' in display_info
    is_oled = 'OLED' in display_info or 'AMOLED' in display_info
    
    # Camera
    cam_info = str(specs.get('Main Camera', {}))
    is_high_res_cam = '50 MP' in cam_info or '64 MP' in cam_info or '108 MP' in cam_info or '200 MP' in cam_info
    
    # RAM
    mem_info = specs.get('Memory', {}).get('Internal', '')
    ram_search = re.search(r'(\d+)GB RAM', mem_info)
    ram = int(ram_search.group(1)) if ram_search else 4 # Default 4GB
    
    # Price for segmentation
    price_str = device.get('price_vnd', '0')
    price_val = clean_number(price_str)

    # 2. Build Features & Usage
    features = []
    usages = []
    
    # Battery Logic
    if bat_cap >= 6000:
        features.append("massive battery life")
        usages.append("Long-term Travel")
    elif bat_cap >= 5000:
        features.append("all-day battery")
        
    # Display/Performance Logic
    if is_high_refresh and ram >= 8:
        features.append("smooth gaming performance")
        usages.append("Gaming")
    elif is_high_refresh:
        features.append("smooth 120Hz display")
    elif is_oled:
        features.append("vivid OLED display")
        usages.append("Media Consumption")
        
    # Camera Logic
    if is_high_res_cam:
        features.append("high-resolution camera")
        usages.append("Photography")
        
    # Multitasking
    if ram >= 12:
        usages.append("Heavy Multitasking")
    elif ram >= 8:
        usages.append("Multitasking")

    # 3. Determine Segment & Price Range
    segment = "smartphone"
    price_range = ""
    
    # Approximate conversion: 25k VND = 1 USD
    if price_val > 20000000: # > ~$800
        segment = "flagship"
        price_range = "High-End (>$800)"
        if "Gaming" not in usages and "Photography" not in usages:
            usages.append("Premium Experience")
    elif price_val > 10000000: # > ~$400
        segment = "premium"
        price_range = "Mid-High ($400-$800)"
    elif price_val > 4000000: # > ~$160
        segment = "mid-range"
        price_range = "Budget-Mid ($160-$400)"
        if not usages:
            usages.append("Daily Drivers")
    else:
        segment = "budget-friendly"
        price_range = "Low Cost (<$160)"
        if not usages:
            usages.append("Basic Communication")

    # Final Usage String
    usage_str = ", ".join(usages) if usages else "General Use"

    # 4. Construct Description
    if features:
        desc = f"{model} is a {segment} device featuring {', '.join(features)}."
    else:
        desc = f"{model} is a {segment} device with a modern design, suitable for everyday needs."
        
    desc += f" It comes equipped with {ram}GB RAM and a {bat_cap}mAh battery."
    
    return desc, usage_str, price_range


if __name__ == "__main__":
    try:
        print("Processing data...")
        with open('data/raw/phone.json', "r", encoding="utf-8") as f:
            data = json.load(f)

        new_data = []
        for item in data:
            brand_name = item.get("brand_name", "")
            if brand_name.lower() not in ['apple', 'samsung', 'sony']:
                continue
            
            devices = item.get("devices", [])
            valid_devices = []
            
            for device in devices:
                specs = device.get("specifications", {})
                misc = specs.get("Misc", {})
                price = misc.get("Price", "")
                
                if not specs:
                    print(f"No specifications for {device.get('model_name')}")
                    continue

                price_vnd = clean_price(price)
                if "Unknown" in price_vnd: 
                    print(f"Removed device (no price): {device.get('model_name')}")
                    continue
                    
                device["price_vnd"] = price_vnd
                device["price_usd"] = clean_price(price, 'USD')
                device["price_yen"] = clean_price(price, 'YEN')
                
                # Analyze device for description, usage, and price range
                desc, usage, price_range = analyze_device(device)
                
                device["description"] = desc
                device["usage"] = usage
                device["price_range"] = price_range
                
                valid_devices.append(device)
            
            if valid_devices:
                item["devices"] = valid_devices
                new_data.append(item)

        with open('data/clean/phone.json', "w", encoding="utf-8") as f:
            json.dump(new_data, f, ensure_ascii=False, indent=4)
        
        print("✅ Processing complete! File saved at: data/clean/phone.json")

    except Exception as e:
        print(f"An error occurred: {e}")
