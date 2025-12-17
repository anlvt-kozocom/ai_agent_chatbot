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


with open('data/raw/phone.json', "r", encoding="utf-8") as f:
    data = json.load(f)

new_data = []
for item in data:
    brand_name = item.get("brand_name", "")
    if brand_name.lower() not in ['nokia', 'apple', 'samsung', 'sony', 'xiaomi', 'huawei', 'realme', 'oppo', 'vivo', 'honor', 'asus']:
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
        valid_devices.append(device)
    
    if valid_devices:
        item["devices"] = valid_devices
        new_data.append(item)

with open('data/clean/phone.json', "w", encoding="utf-8") as f:
    json.dump(new_data, f, ensure_ascii=False, indent=4)
