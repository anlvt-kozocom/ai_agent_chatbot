import sqlite3
import os
from typing import List, Dict, Optional


class PriceTool:
    def __init__(self, db_path: str = "data/product_prices.db"):
        # Helper to find the absolute path regardless of where it's called
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.db_path = os.path.join(base_dir, db_path)
        self._check_db()

    def _check_db(self):
        if not os.path.exists(self.db_path):
            print(f"Error: Database file {self.db_path} not found.")

    def _get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Access columns by name
            return conn
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None

    def get_all_products(self) -> List[Dict]:
        """
        Retrieve all products from the database.
        """
        conn = self._get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            query = "SELECT * FROM products"
            print(f"DEBUG SQL: {query}")
            cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error querying database: {e}")
            return []
        finally:
            conn.close()

    def search_by_price(self, target: float, currency: str, brand=None) -> List[Dict]:
        """
        Search for products around the target price using SQL.
        Logic:
        - VND: +/- 2,000,000
        - USD: +/- 50
        - YEN: +/- 10,000

        Args:
            target: Target price
            currency: Currency (VND, USD, YEN)
            brand: Optional brand filter (string or list of strings, case-insensitive)
        """
        currency = currency.strip().lower()

        # Define variations and determines column/range
        vnd_aliases = ["vnd", "d", "đ", "dong", "đồng", "vnđ", "vietnam dong"]
        usd_aliases = ["usd", "$", "dollar", "dola", "đô"]
        yen_aliases = ["yen", "yên", "jpy", "¥"]

        range_val = 0
        column = ""
        matched_currency = ""

        if any(alias == currency for alias in vnd_aliases) or any(
            x in currency for x in ["vnd", "dong", "đồng", "đ"]
        ):
            range_val = 2000000
            column = "price_vnd"
            matched_currency = "VND"
        elif any(alias == currency for alias in usd_aliases) or any(
            x in currency for x in ["usd", "dollar", "$", "đô"]
        ):
            range_val = 50
            column = "price_usd"
            matched_currency = "USD"
        elif any(alias == currency for alias in yen_aliases) or any(
            x in currency for x in ["yen", "jpy", "yên"]
        ):
            range_val = 10000
            column = "price_yen"
            matched_currency = "YEN"
        else:
            return []

        min_price = target - range_val
        max_price = target + range_val

        print(
            f"DEBUG: PriceTool searching SQL {target} {matched_currency} (Col: {column}, Range: {min_price}-{max_price})"
        )

        conn = self._get_connection()
        if not conn:
            return []

        query = f"SELECT * FROM products WHERE {column} BETWEEN ? AND ?"
        params = [min_price, max_price]

        # Handle brand filtering - support both single brand and multiple brands
        if brand:
            if isinstance(brand, list):
                # Multiple brands - use WHERE IN clause
                placeholders = ",".join(["?"] * len(brand))
                query += f" AND branch IN ({placeholders})"
                params.extend(brand)
            else:
                # Single brand - use LIKE for fuzzy matching
                query += " AND branch LIKE ?"
                params.append(f"%{brand}%")

        try:
            cursor = conn.cursor()
            print(f"DEBUG SQL: {query} | Params: {params}")
            cursor.execute(query, params)
            rows = cursor.fetchall()

            results = []
            for row in rows:
                item = dict(row)
                # Add match info
                price = item.get(column)
                item["_match_reason"] = (
                    f"Price {price} is within range of {target} ({matched_currency})"
                )
                if brand:
                    item["_match_reason"] += f", Brand: {brand}"
                results.append(item)

            return results
        except Exception as e:
            print(f"Error querying database: {e}")
            return []
        finally:
            conn.close()

    def get_products_by_price_range(
        self,
        min_price: float,
        max_price: float,
        currency: str,
        brand=None,
        usage: List[str] = None,
    ) -> List[Dict]:
        """
        Get products within a price range using SQL.

        Args:
            min_price: Minimum price
            max_price: Maximum price
            currency: Currency (VND, USD, YEN)
            brand: Optional brand filter (string or list of strings, case-insensitive)
            usage: Optional usage filter (not currently used)
        """
        currency = currency.strip().lower()

        # Determine currency column
        vnd_aliases = ["vnd", "d", "đ", "dong", "đồng", "vnđ", "vietnam dong"]
        usd_aliases = ["usd", "$", "dollar", "dola", "đô"]
        yen_aliases = ["yen", "yên", "jpy", "¥"]

        column = ""
        matched_currency = ""

        if any(alias == currency for alias in vnd_aliases) or any(
            x in currency for x in ["vnd", "dong", "đồng", "đ"]
        ):
            column = "price_vnd"
            matched_currency = "VND"
        elif any(alias == currency for alias in usd_aliases) or any(
            x in currency for x in ["usd", "dollar", "$", "đô"]
        ):
            column = "price_usd"
            matched_currency = "USD"
        elif any(alias == currency for alias in yen_aliases) or any(
            x in currency for x in ["yen", "jpy", "yên"]
        ):
            column = "price_yen"
            matched_currency = "YEN"
        else:
            return []

        print(
            f"DEBUG: PriceTool range search SQL {min_price}-{max_price} {matched_currency}, brand={brand}"
        )

        conn = self._get_connection()
        if not conn:
            return []

        query = f"SELECT * FROM products WHERE {column} >= ? AND {column} <= ?"
        params = [min_price, max_price]

        # Handle brand filtering - support both single brand and multiple brands
        if brand:
            if isinstance(brand, list):
                # Multiple brands - use WHERE IN clause
                placeholders = ",".join(["?"] * len(brand))
                query += f" AND branch IN ({placeholders})"
                params.extend(brand)
            else:
                # Single brand - use LIKE for fuzzy matching
                query += " AND branch LIKE ?"
                params.append(f"%{brand}%")

        try:
            cursor = conn.cursor()
            print(f"DEBUG SQL: {query} | Params: {params}")
            cursor.execute(query, params)
            rows = cursor.fetchall()

            results = []
            for row in rows:
                item = dict(row)
                price = item.get(column)
                item["_match_reason"] = (
                    f"Price {price} {matched_currency} in range {min_price}-{max_price}"
                )
                if brand:
                    item["_match_reason"] += f", Brand: {brand}"
                results.append(item)

            return results
        except Exception as e:
            print(f"Error querying database: {e}")
            return []
        finally:
            conn.close()

    def get_price_by_name(self, model_name: str) -> Optional[Dict]:
        """
        Look up exact price details by model name using SQL.
        Uses token-based LIKE queries to approximate fuzzy matching.
        """
        if not model_name:
            return None

        # Normalize and split tokens
        target = model_name.lower().strip()
        tokens = target.split()

        if not tokens:
            return None

        conn = self._get_connection()
        if not conn:
            return None

        # Logic: Find products where model_name contains ALL tokens or branch+model_name contains ALL tokens
        # We can construct a query like: WHERE model_name LIKE %t1% AND model_name LIKE %t2% ...
        # This handles order independence (e.g. "Samsung S24" matches "Samsung Galaxy S24")

        conditions = []
        params = []

        for token in tokens:
            # Check likely combined column (branch + model_name) implicitly by checking if tokens exist in model_name or branch
            # Actually, usually users search by model parts.
            # Simple approach: model_name LIKE %token% OR branch LIKE %token% ??
            # No, standard fuzzy usually implies AND logic for tokens.
            # "Samsung S24" -> "Samsung" in (Brand/Model) AND "S24" in (Brand/Model)

            # Let's try to match against the concatenated string usually used for searching?
            # Or just check model_name. Most names in DB are like "Galaxy S24". "Samsung" is branch.
            # So searching "Samsung S24" against model_name "Galaxy S24" might fail if we enforce ALL tokens in model_name.
            # It should be: (branch || ' ' || model_name) LIKE %token%

            conditions.append("(branch || ' ' || model_name) LIKE ?")
            params.append(f"%{token}%")

        where_clause = " AND ".join(conditions)
        query = f"SELECT * FROM products WHERE {where_clause}"

        try:
            cursor = conn.cursor()
            print(f"DEBUG SQL: {query} | Params: {params}")
            cursor.execute(query, params)
            rows = cursor.fetchall()

            if not rows:
                return None

            # Post-processing to find best match among results
            # Similar to original logic: prefer shortest name (most concise match) or exact match

            best_match = None

            # Convert to list of dicts
            candidates = [dict(row) for row in rows]

            for item in candidates:
                name = item.get("model_name", "").lower()
                full_name = f"{item.get('branch', '')} {name}".lower()

                # 1. Exact match
                if target == name or target == full_name:
                    return item

                # 2. Prefer shortest model name (heuristic for "closest" match when tokens are subset)
                if best_match is None or len(name) < len(
                    best_match.get("model_name", "")
                ):
                    best_match = item

            return best_match

        except Exception as e:
            print(f"Error querying database: {e}")
            return None
        finally:
            conn.close()

    def get_most_expensive(self, brand=None) -> Optional[Dict]:
        """
        Get the most expensive product (optionally for a specific brand or list of brands).

        Args:
            brand: Optional brand filter (string or list of strings)
        """
        return self._get_extreme_price_product(brand, "DESC")

    def get_cheapest(self, brand=None) -> Optional[Dict]:
        """
        Get the cheapest product (optionally for a specific brand or list of brands).

        Args:
            brand: Optional brand filter (string or list of strings)
        """
        return self._get_extreme_price_product(brand, "ASC")

    def _get_extreme_price_product(self, brand, order: str) -> Optional[Dict]:
        """
        Helper to get the most expensive or cheapest product.

        Args:
            brand: Optional brand filter (string or list of strings)
            order: Sort order (DESC for most expensive, ASC for cheapest)
        """
        conn = self._get_connection()
        if not conn:
            return None

        # Sort by price_vnd as the standard reference
        # Handle brand filtering - support both single brand and multiple brands
        if brand:
            if isinstance(brand, list):
                # Multiple brands - use WHERE IN clause
                placeholders = ",".join(["?"] * len(brand))
                query = f"SELECT * FROM products WHERE branch IN ({placeholders}) ORDER BY price_vnd {order} LIMIT 1"
                params = tuple(brand)
            else:
                # Single brand - use LIKE for fuzzy matching
                query = f"SELECT * FROM products WHERE branch LIKE ? ORDER BY price_vnd {order} LIMIT 1"
                params = (f"%{brand}%",)
        else:
            query = f"SELECT * FROM products ORDER BY price_vnd {order} LIMIT 1"
            params = ()

        try:
            cursor = conn.cursor()
            print(f"DEBUG SQL: {query} | Params: {params}")
            cursor.execute(query, params)
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None
        except Exception as e:
            print(f"Error querying database: {e}")
            return None
        finally:
            conn.close()

    def get_products_by_ids(self, ids: List[str]) -> List[Dict]:
        """
        Get info for a list of product IDs.
        """
        if not ids:
            return []

        conn = self._get_connection()
        if not conn:
            return []

        # Prepare placeholders
        placeholders = ",".join(["?"] * len(ids))
        query = f"SELECT * FROM products WHERE id IN ({placeholders})"

        try:
            cursor = conn.cursor()
            # print(f"DEBUG SQL: {query} | Params: {ids}")
            cursor.execute(query, ids)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error querying database: {e}")
            return []
        finally:
            conn.close()


price_tool = PriceTool()
