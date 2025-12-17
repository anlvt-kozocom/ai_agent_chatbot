import httpx
import xml.etree.ElementTree as ET
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

VCB_URL = "https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx"

async def get_vcb_exchange_rates() -> str:
    """
    Fetches exchange rates from Vietcombank and returns a formatted string
    for the LLM prompt.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(VCB_URL, timeout=10.0)
            response.raise_for_status()
            
        xml_content = response.text
        root = ET.fromstring(xml_content)
        
        rates = []
        # Add VND base
        rates.append("1 USD = ... (fetched below)")
        
        rates_map: Dict[str, str] = {}
        
        for exrate in root.findall("Exrate"):
            code = exrate.get("CurrencyCode")
            # Prefer Transfer rate, fallback to Sell or Buy
            rate_str = exrate.get("Transfer")
            if rate_str == "-":
                rate_str = exrate.get("Sell")
            if rate_str == "-":
                rate_str = exrate.get("Buy")
                
            if code and rate_str and rate_str != "-":
                # VCB format is like "25,000.00" or "25,000"
                # We keep it as string for the LLM to understand
                rates_map[code] = rate_str
                
        # Format for LLM
        # Priority currencies
        priority_codes = ["USD", "EUR", "JPY", "KRW", "INR", "CNY", "SGD", "THB"]
        
        formatted_lines = ["Current Exchange Rates (Source: Vietcombank):"]
        
        for code in priority_codes:
            if code in rates_map:
                formatted_lines.append(f"1 {code} = {rates_map[code]} VND")
                
        # Add others if needed, but usually these cover most phone prices
        
        return "\n".join(formatted_lines)
        
    except Exception as e:
        logger.error(f"Failed to fetch VCB rates: {e}")
        # Fallback to hardcoded safe defaults if API fails
        return "Rate: 1 USD = 25,400 VND (Fallback)"

