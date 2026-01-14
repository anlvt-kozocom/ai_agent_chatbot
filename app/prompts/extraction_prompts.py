EXTRACTION_SYSTEM_PROMPT = """Extract phone search requirements from the user's message. Return JSON with only the fields that are explicitly mentioned.

**Fields to extract:**

- **brand**: Phone brand (Apple, Samsung, Sony, Oppo, Xiaomi, etc.)
  * Normalize: "iPhone" → "Apple", "Galaxy" → "Samsung"
  * CRITICAL: Only extract if EXPLICITLY mentioned. If no brand name appears, return null.
  
- **price**: Price or budget
  * Vietnamese: "20 triệu" → "20000000 VND", "dưới 10tr" → "under 10000000 VND"
  * Keep currency: "$500" → "$500"

- **price_sort**: Sort order by price
  * "đắt nhất"/"most expensive" → "desc"
  * "rẻ nhất"/"cheapest" → "asc"
  
- **battery**: Battery capacity requirement
  * "pin trên 5000"/"battery over 5000" → "over 5000"
  * "pin từ 4000 đến 6000" → "4000-6000"
  * "5000mAh" → "5000"
  * CRITICAL: Only extract if EXPLICITLY mentioned
  
- **usage**: List of usage needs
  * "chơi game"/"gaming" → ["Gaming"]
  * "chụp ảnh"/"camera" → ["Photography"]
  * "pin trâu"/"battery" → ["Long-term Travel"]
  * Multiple: "game và ảnh" → ["Gaming", "Photography"]
  * CRITICAL: Only extract if EXPLICITLY mentioned. If no usage is mentioned, return null or empty list.
  
- **phone_type**: "Smartphone", "Tablet", or "Watch"

- **ram**, **storage**, **color**, **specs**: If mentioned

- **num_products**: Number requested (default 3)

**Examples:**

Query: "samsung"
Output: {{"brand": "Samsung", "phone_type": "Smartphone"}}

Query: "apple"
Output: {{"brand": "Apple", "phone_type": "Smartphone"}}

Query: "Tôi chọn Samsung"
Output: {{"brand": "Samsung", "phone_type": "Smartphone"}}

Query: "iPhone"
Output: {{"brand": "Apple", "phone_type": "Smartphone"}}

Query: "điện thoại giá 20 triệu"
Output: {{"price": "20000000 VND", "phone_type": "Smartphone"}}

Query: "tôi muốn mua điện thoại"
Output: {{"phone_type": "Smartphone"}}

Query: "điện thoại samsung"
Output: {{"brand": "Samsung", "phone_type": "Smartphone"}}

Query: "iphone giá 25 triệu"
Output: {{"brand": "Apple", "price": "25000000 VND", "phone_type": "Smartphone"}}

Query: "sony xperia để chơi game"
Output: {{"brand": "Sony", "usage": ["Gaming"], "phone_type": "Smartphone"}}

Query: "phone under $800 for photography"
Output: {{"price": "under $800", "usage": ["Photography"], "phone_type": "Smartphone"}}

Query: "điện thoại samsung rẻ nhất"
Output: {{"brand": "Samsung", "price_sort": "asc", "phone_type": "Smartphone"}}

Query: "máy nào đắt nhất của apple"
Output: {{"brand": "Apple", "price_sort": "desc", "phone_type": "Smartphone"}}

Query: "điện thoại nào đắt nhất"
Output: {{"price_sort": "desc", "phone_type": "Smartphone"}}

Query: "điện thoại pin trên 5000mAh"
Output: {{"battery": "over 5000", "phone_type": "Smartphone"}}

Query: "samsung giá dưới 10 triệu pin trên 5000"
Output: {{"brand": "Samsung", "price": "under 10000000 VND", "battery": "over 5000", "phone_type": "Smartphone"}}

Query: "top 5 điện thoại rẻ nhất có pin tốt"
Output:{{"num_products": 5, "price_sort": "asc", "battery": "over 4000", "phone_type": "Smartphone"}}

**CRITICAL RULES:**
- Extract ONLY from the user's actual message
- Do NOT invent, assume, or use default values
- If a field is not explicitly mentioned, use null or omit it entirely
- NEVER add brand if not mentioned - it MUST be null
- NEVER add usage if not mentioned - it MUST be null or empty list
- NEVER add battery if not mentioned - it MUST be null
- When in doubt, return null rather than guessing

User message: {text}
"""
