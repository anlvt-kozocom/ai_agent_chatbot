"""
Advanced SQL Agent for Text-to-SQL conversion.

This module provides LLM-powered SQL query generation for complex product searches
with multiple conditions (price, battery, brand, top N, sorting, etc.).
"""

from typing import Dict, List, Optional, Any
from app.models.schemas import AgentState
from app.services.llm import get_llm
import sqlite3
import os
import json
import re


# Database configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "data", "product_prices.db")


# SQL Schema for LLM
DATABASE_SCHEMA = """
Table: products
Columns:
  - id (INTEGER, PRIMARY KEY): Unique product identifier
  - branch (TEXT): Brand name (e.g., 'Apple', 'Samsung', 'Sony')
  - model_name (TEXT): Product model name
  - price_vnd (INTEGER): Price in Vietnamese Dong
  - price_usd (INTEGER): Price in US Dollars
  - price_yen (INTEGER): Price in Japanese Yen
  - battery_capacity (INTEGER): Battery capacity in mAh (milliampere-hour)
  - quantity (INTEGER): Stock quantity

Notes:
  - To filter by brand, use: WHERE branch LIKE '%BrandName%' (case-insensitive contains match)
  - To filter by price range in VND, use: WHERE price_vnd BETWEEN min_value AND max_value
  - To filter by battery capacity, use: WHERE battery_capacity >= min_value
  - To get top N products, use: ORDER BY column_name ASC/DESC LIMIT N
  - For cheapest/most expensive, use: ORDER BY price_vnd ASC/DESC LIMIT 1
"""


TEXT_TO_SQL_PROMPT_TEMPLATE = """You are an expert SQL query generator for a mobile phone database.

Your task is to convert natural language queries into SAFE and VALID SQL SELECT queries.

DATABASE SCHEMA:
{schema}

RULES:
1. ONLY generate SELECT queries. Never use INSERT, UPDATE, DELETE, DROP, or any DDL/DML.
2. Always use parameterized placeholders (?) for values to prevent SQL injection.
3. Return a JSON object with two fields:
   - "sql": The SQL query string with ? placeholders
   - "params": List of parameter values to bind to placeholders
4. Use LIKE with wildcards for fuzzy brand matching: WHERE branch LIKE ?
5. For "top N" queries, use ORDER BY with LIMIT.
6. For price "under/below", use: WHERE price_vnd < ?
7. For price "over/above", use: WHERE price_vnd > ?
8. For battery requirements, use: WHERE battery_capacity >= ?
9. Combine multiple conditions with AND.
10. Default currency is VND unless specified otherwise.

EXAMPLES:

Query: "phones under 10 million VND"
Output:
{{
  "sql": "SELECT * FROM products WHERE price_vnd < ? ORDER BY price_vnd ASC",
  "params": [10000000]
}}

Query: "Samsung phones with battery over 5000mAh"
Output:
{{
  "sql": "SELECT * FROM products WHERE branch LIKE ? AND battery_capacity >= ? ORDER BY price_vnd ASC",
  "params": ["%Samsung%", 5000]
}}

Query: "top 5 cheapest phones with battery over 5000mAh"
Output:
{{
  "sql": "SELECT * FROM products WHERE battery_capacity >= ? ORDER BY price_vnd ASC LIMIT ?",
  "params": [5000, 5]
}}

Query: "Get top 5 phones under 10m with battery over 5000mAh"
Output:
{{
  "sql": "SELECT * FROM products WHERE price_vnd < ? AND battery_capacity >= ? ORDER BY price_vnd ASC LIMIT ?",
  "params": [10000000, 5000, 5]
}}

Query: "điện thoại samsung giá dưới 10 triệu pin trên 5000mAh"
Output:
{{
  "sql": "SELECT * FROM products WHERE branch LIKE ? AND price_vnd < ? AND battery_capacity >= ? ORDER BY price_vnd ASC",
  "params": ["%Samsung%", 10000000, 5000]
}}

USER QUERY: {query}

Generate the SQL query as JSON:
"""


class SQLValidator:
    """Validates generated SQL queries for safety."""

    # Whitelist of allowed SQL keywords
    ALLOWED_KEYWORDS = {
        "SELECT",
        "FROM",
        "WHERE",
        "AND",
        "OR",
        "ORDER",
        "BY",
        "LIMIT",
        "ASC",
        "DESC",
        "LIKE",
        "BETWEEN",
        "IN",
        "NOT",
    }

    # Blacklist of dangerous keywords
    FORBIDDEN_KEYWORDS = {
        "DROP",
        "DELETE",
        "UPDATE",
        "INSERT",
        "ALTER",
        "CREATE",
        "TRUNCATE",
        "REPLACE",
        "EXEC",
        "EXECUTE",
        "--",
        ";",
    }

    # Allowed columns
    ALLOWED_COLUMNS = {
        "id",
        "branch",
        "model_name",
        "price_vnd",
        "price_usd",
        "price_yen",
        "battery_capacity",
        "quantity",
    }

    @classmethod
    def validate(cls, sql: str) -> bool:
        """
        Validate SQL query for safety.

        Args:
            sql: SQL query string

        Returns:
            bool: True if valid, False otherwise
        """
        sql_upper = sql.upper()

        # Check for forbidden keywords
        for keyword in cls.FORBIDDEN_KEYWORDS:
            if keyword in sql_upper:
                print(f"⚠️  SQL Validation Failed: Forbidden keyword '{keyword}' found")
                return False

        # Must start with SELECT
        if not sql_upper.strip().startswith("SELECT"):
            print("⚠️  SQL Validation Failed: Query must start with SELECT")
            return False

        # Must query from 'products' table only
        if "FROM PRODUCTS" not in sql_upper:
            print("⚠️  SQL Validation Failed: Query must be from 'products' table")
            return False

        return True


async def sql_filtering_node(state: AgentState) -> Dict[str, Any]:
    """
    SQL Agent Node: Performs complex filtering using LLM-powered Text-to-SQL.

    This node handles complex queries with multiple conditions:
    - Price range filtering
    - Battery capacity filtering
    - Brand filtering
    - Top N queries with sorting

    Args:
        state: Current agent state

    Returns:
        dict: Updated state with candidate_ids from SQL query results
    """
    print("--- Entering SQL Filtering Node ---")

    messages = state.get("messages", [])
    current_query = messages[-1].content if messages else ""

    requirements = state.get("requirements", {})
    language = state.get("language", "vi")

    # Log the query
    print(f"Query: {current_query}")
    print(f"Requirements: {requirements}")

    try:
        # Generate SQL using LLM
        llm = get_llm(temperature=0)  # Use deterministic generation

        prompt = TEXT_TO_SQL_PROMPT_TEMPLATE.format(
            schema=DATABASE_SCHEMA, query=current_query
        )

        response = await llm.ainvoke(prompt)
        content = response.content.strip()

        # Parse JSON response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.replace("```", "").strip()

        sql_data = json.loads(content)
        sql_query = sql_data.get("sql", "")
        params = sql_data.get("params", [])

        print(f"Generated SQL: {sql_query}")
        print(f"Parameters: {params}")

        # Validate SQL query
        if not SQLValidator.validate(sql_query):
            print("❌ SQL validation failed, falling back to empty results")
            return {
                "candidate_ids": None,
                "path": (state.get("path") or []) + ["sql_filtering_node"],
            }

        # Execute SQL query
        if not os.path.exists(DB_PATH):
            print(f"Error: Database not found at {DB_PATH}")
            return {
                "candidate_ids": None,
                "path": (state.get("path") or []) + ["sql_filtering_node"],
            }

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(sql_query, params)
        rows = cursor.fetchall()

        # Extract product IDs
        candidate_ids = [str(row["id"]) for row in rows]

        print(f"✅ Found {len(candidate_ids)} products matching criteria")
        print(
            f"Product IDs: {candidate_ids[:10]}{'...' if len(candidate_ids) > 10 else ''}"
        )

        conn.close()

        return {
            "candidate_ids": candidate_ids if candidate_ids else None,
            "path": (state.get("path") or []) + ["sql_filtering_node"],
        }

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse LLM response as JSON: {e}")
        print(f"Raw response: {content}")
        return {
            "candidate_ids": None,
            "path": (state.get("path") or []) + ["sql_filtering_node"],
        }

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return {
            "candidate_ids": None,
            "path": (state.get("path") or []) + ["sql_filtering_node"],
        }

    except Exception as e:
        print(f"❌ Unexpected error in SQL filtering: {e}")
        return {
            "candidate_ids": None,
            "path": (state.get("path") or []) + ["sql_filtering_node"],
        }
