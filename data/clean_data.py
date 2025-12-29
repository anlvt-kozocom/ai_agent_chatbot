import json
import re

TRANSLATIONS = {
    "en": {
        "massive_battery": "massive battery life",
        "long_term_travel": "Long-term Travel",
        "all_day_battery": "all-day battery",
        "smooth_gaming": "smooth gaming performance",
        "gaming": "Gaming",
        "smooth_120hz": "smooth 120Hz display",
        "vivid_oled": "vivid OLED display",
        "media_consumption": "Media Consumption",
        "high_res_cam": "high-resolution camera",
        "photography": "Photography",
        "heavy_multitasking": "Heavy Multitasking",
        "multitasking": "Multitasking",
        "flagship": "flagship",
        "premium": "premium",
        "mid_range": "mid-range",
        "budget_friendly": "budget-friendly",
        "price_high_end": "High-End (>$800)",
        "price_mid_high": "Mid-High ($400-$800)",
        "price_budget_mid": "Budget-Mid ($160-$400)",
        "price_low_cost": "Low Cost (<$160)",
        "daily_drivers": "Daily Drivers",
        "basic_communication": "Basic Communication",
        "general_use": "General Use",
        "desc_template_features": "{model} is a {segment} device featuring {features}.",
        "desc_template_basic": "{model} is a {segment} device with a modern design, suitable for everyday needs.",
        "desc_template_specs": " It comes equipped with {ram}GB RAM and a {bat_cap}mAh battery.",
    },
    "vi": {
        "massive_battery": "thời lượng pin khủng",
        "long_term_travel": "Du lịch dài ngày",
        "all_day_battery": "pin cả ngày",
        "smooth_gaming": "hiệu năng chơi game mượt mà",
        "gaming": "Chơi game",
        "smooth_120hz": "màn hình 120Hz mượt mà",
        "vivid_oled": "màn hình OLED sống động",
        "media_consumption": "Giải trí đa phương tiện",
        "high_res_cam": "camera độ phân giải cao",
        "photography": "Nhiếp ảnh",
        "heavy_multitasking": "Đa nhiệm nặng",
        "multitasking": "Đa nhiệm",
        "flagship": "flagship",
        "premium": "cao cấp",
        "mid_range": "tầm trung",
        "budget_friendly": "giá rẻ",
        "price_high_end": "Cao cấp (>$800)",
        "price_mid_high": "Cận cao cấp ($400-$800)",
        "price_budget_mid": "Tầm trung ($160-$400)",
        "price_low_cost": "Giá rẻ (<$160)",
        "daily_drivers": "Sử dụng hàng ngày",
        "basic_communication": "Liên lạc cơ bản",
        "general_use": "Sử dụng phổ thông",
        "desc_template_features": "{model} là điện thoại {segment} nổi bật với {features}.",
        "desc_template_basic": "{model} là điện thoại {segment} có thiết kế hiện đại, phù hợp cho nhu cầu hàng ngày.",
        "desc_template_specs": " Máy được trang bị RAM {ram}GB và pin {bat_cap}mAh.",
    },
    "ja": {
        "massive_battery": "圧倒的なバッテリー持ち",
        "long_term_travel": "長期旅行",
        "all_day_battery": "一日中持つバッテリー",
        "smooth_gaming": "快適なゲーム性能",
        "gaming": "ゲーミング",
        "smooth_120hz": "滑らかな120Hzディスプレイ",
        "vivid_oled": "鮮やかなOLEDディスプレイ",
        "media_consumption": "メディア鑑賞",
        "high_res_cam": "高解像度カメラ",
        "photography": "写真撮影",
        "heavy_multitasking": "ヘビーなマルチタスク",
        "multitasking": "マルチタスク",
        "flagship": "フラッグシップ",
        "premium": "プレミアム",
        "mid_range": "ミッドレンジ",
        "budget_friendly": "格安",
        "price_high_end": "ハイエンド (>$800)",
        "price_mid_high": "ミッドハイ ($400-$800)",
        "price_budget_mid": "ミッドレンジ ($160-$400)",
        "price_low_cost": "ローエンド (<$160)",
        "daily_drivers": "日常使用",
        "basic_communication": "基本的な通信",
        "general_use": "一般用途",
        "desc_template_features": "{model}は{features}を特徴とする{segment}スマホです。",
        "desc_template_basic": "{model}はモダンなデザインの{segment}スマホで、日常のニーズに適しています。",
        "desc_template_specs": " {ram}GBのRAMと{bat_cap}mAhのバッテリーを搭載しています。",
    },
}


def clean_price(price: str, convert_to: str = "VND") -> str:
    # convert price string like 1 ₹ = 291,54 VND, 1 USD to 26336 VND, 1 EUR to 30836 VND
    if not price:
        return "Unknown price"

    rates_list = {
        "VND": {
            "EUR": 30836,
            "€": 30836,
            "USD": 26336,
            "$": 26336,
            "INR": 291.54,
            "₹": 291.54,
        },
        "USD": {"EUR": 1.18, "€": 1.18, "USD": 1, "$": 1, "INR": 0.011, "₹": 0.011},
        "YEN": {
            "EUR": 145.23,
            "€": 145.23,
            "USD": 130.32,
            "$": 130.32,
            "INR": 1.52,
            "₹": 1.52,
        },
    }

    rates = rates_list.get(convert_to, {})

    # Remove commas (thousands separators)
    clean_s = price.replace(",", "")

    for symbol, rate in rates.items():
        escaped_symbol = re.escape(symbol)
        # Pattern: Symbol followed by number OR Number followed by Symbol
        # We handle optional whitespace
        pattern = rf"(?:{escaped_symbol})\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:{escaped_symbol})"

        match = re.search(pattern, clean_s, re.IGNORECASE)
        if match:
            # group 1 is number if symbol matched first
            # group 2 is number if symbol matched second
            val_str = match.group(1) or match.group(2)
            if val_str:
                val = float(val_str)
                converted = int(val * rate)
                if convert_to == "VND":
                    return f"{converted} VND"
                elif convert_to == "USD":
                    return f"${converted}"
                elif convert_to == "YEN":
                    return f"¥{converted}"
                else:
                    return "Unknown price"

    return "Unknown price"


def clean_number(text):
    """Helper to extract number from string (e.g., '5000 mAh' -> 5000)"""
    if not text:
        return 0
    matches = re.findall(r"(\d+)", text.replace(",", "").replace(".", ""))
    return int(matches[0]) if matches else 0


def analyze_device(device, lang="en"):
    """
    Analyzes device specs to generate description, usage, and price range in specified language.
    Returns a tuple: (description, usage, price_range)
    """
    t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])

    specs = device.get("specifications", {})
    model = device.get("model_name", "Product")

    # 1. Extract Data
    # Battery
    bat_info = specs.get("Battery", {}).get("Type", "")
    bat_cap = clean_number(bat_info)

    # Display
    display_info = (
        specs.get("Display", {}).get("Type", "")
        + " "
        + specs.get("Display", {}).get("Resolution", "")
    )
    is_high_refresh = "120Hz" in display_info or "144Hz" in display_info
    is_oled = "OLED" in display_info or "AMOLED" in display_info

    # Camera
    cam_info = str(specs.get("Main Camera", {}))
    is_high_res_cam = (
        "50 MP" in cam_info
        or "64 MP" in cam_info
        or "108 MP" in cam_info
        or "200 MP" in cam_info
    )

    # RAM
    mem_info = specs.get("Memory", {}).get("Internal", "")
    ram_search = re.search(r"(\d+)GB RAM", mem_info)
    ram = int(ram_search.group(1)) if ram_search else 4  # Default 4GB

    # Price for segmentation
    price_str = device.get("price_vnd", "0")
    price_val = clean_number(price_str)

    # 2. Build Features & Usage
    features = []
    usages = []

    # Battery Logic
    if bat_cap >= 6000:
        features.append(t["massive_battery"])
        usages.append(t["long_term_travel"])
    elif bat_cap >= 5000:
        features.append(t["all_day_battery"])

    # Display/Performance Logic
    if is_high_refresh and ram >= 8:
        features.append(t["smooth_gaming"])
        usages.append(t["gaming"])
    elif is_high_refresh:
        features.append(t["smooth_120hz"])
    elif is_oled:
        features.append(t["vivid_oled"])
        usages.append(t["media_consumption"])

    # Camera Logic
    if is_high_res_cam:
        features.append(t["high_res_cam"])
        usages.append(t["photography"])

    # Multitasking
    if ram >= 12:
        usages.append(t["heavy_multitasking"])
    elif ram >= 8:
        usages.append(t["multitasking"])

    # 3. Determine Segment & Price Range
    segment = "smartphone"
    price_range = ""

    # Approximate conversion: 25k VND = 1 USD
    if price_val > 20000000:  # > ~$800
        segment = t["flagship"]
        price_range = t["price_high_end"]
        if t["gaming"] not in usages and t["photography"] not in usages:
            # For premium experience, assuming it's implicit or just check lang
            # Adding a hardcoded fallback or adding to dict would be better.
            # For now let's just use generic logic
            pass
    elif price_val > 10000000:  # > ~$400
        segment = t["premium"]
        price_range = t["price_mid_high"]
    elif price_val > 4000000:  # > ~$160
        segment = t["mid_range"]
        price_range = t["price_budget_mid"]
        if not usages:
            usages.append(t["daily_drivers"])
    else:
        segment = t["budget_friendly"]
        price_range = t["price_low_cost"]
        if not usages:
            usages.append(t["basic_communication"])

    if not usages:
        usages.append(t["general_use"])

    # Final Usage String
    # Join with comma for EN/VI, maybe different for JA?
    # JA usually uses '、'
    separator = "、" if lang == "ja" else ", "
    usage_str = separator.join(usages)

    # 4. Construct Description
    if features:
        feat_separator = "、" if lang == "ja" else ", "
        features_str = feat_separator.join(features)
        desc = t["desc_template_features"].format(
            model=model, segment=segment, features=features_str
        )
    else:
        desc = t["desc_template_basic"].format(model=model, segment=segment)

    desc += t["desc_template_specs"].format(ram=ram, bat_cap=bat_cap)

    return desc, usage_str, price_range


if __name__ == "__main__":
    try:
        print("Processing data...")
        # Read raw data once
        with open("data/raw/phone.json", "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        languages = ["en", "vi", "ja"]

        for lang in languages:
            print(f"Generating data for language: {lang}")
            new_data = []

            for item in raw_data:
                # Deep copy item to avoid modifying original or shared references across languages loops
                # though we are building new list, dicts are mutable.
                # Actually we can just create a new dict for output item

                brand_name = item.get("brand_name", "")
                if brand_name.lower() not in ["apple", "samsung", "sony"]:
                    continue

                valid_devices = []
                devices = item.get("devices", [])

                for device in devices:
                    specs = device.get("specifications", {})
                    misc = specs.get("Misc", {})
                    price = misc.get("Price", "")

                    if not specs:
                        continue

                    # Clean price - kept consistent across files for now (VND base)
                    # or should we customize currency based on file?
                    # The request asked to separate into 3 files for 3 languages.
                    # Usually price formatting follows locale, but 'price_vnd' field implies VND.
                    # Let's keep the existing logic for price fields but update description/usage.

                    price_vnd = clean_price(price, "VND")
                    if "Unknown" in price_vnd:
                        continue

                    # Create a copy of device dict for this language
                    device_processed = device.copy()

                    device_processed["price_vnd"] = price_vnd
                    device_processed["price_usd"] = clean_price(price, "USD")
                    device_processed["price_yen"] = clean_price(price, "YEN")

                    # Analyze device for description, usage, and price range in specific language
                    desc, usage, price_range = analyze_device(
                        device_processed, lang=lang
                    )

                    device_processed["description"] = desc
                    device_processed["usage"] = usage
                    device_processed["price_range"] = price_range

                    valid_devices.append(device_processed)

                if valid_devices:
                    # Create new item dict
                    item_processed = item.copy()
                    item_processed["devices"] = valid_devices
                    new_data.append(item_processed)

            output_file = f"data/clean/phone_{lang}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(new_data, f, ensure_ascii=False, indent=4)

            print(f"✅ Saved: {output_file}")

        print("✅ All processing complete!")

    except Exception as e:
        print(f"An error occurred: {e}")
