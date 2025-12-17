from typing import List
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.retrievers import BaseRetriever

class QueryExpansionRetriever(BaseRetriever):
    """
    Wraps a base retriever and expands the user query with brand mappings.
    Example: "Z Fold6" -> "Samsung Galaxy Z Fold6"
    """
    base_retriever: BaseRetriever
    
    brand_mapping: dict = {
        "z fold": "Samsung Galaxy Z Fold",
        "z flip": "Samsung Galaxy Z Flip",
        "fold": "Samsung Galaxy Z Fold",
        "flip": "Samsung Galaxy Z Flip",
        "iphone": "Apple iPhone",
        "xperia": "Sony Xperia",
        "galaxy": "Samsung Galaxy",
        "redmi": "Xiaomi Redmi",
        "rog phone": "Asus ROG Phone",
        "zenfone": "Asus Zenfone"
    }

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        expanded_query = query
        query_lower = query.lower()
        
        # Simple string replacement for expansion
        # We prefer longer matches first (e.g. "z fold" before "fold")
        # but the dict order isn't guaranteed in older python, though usually fine in 3.7+
        # Let's sort keys by length descending to be safe
        sorted_keys = sorted(self.brand_mapping.keys(), key=len, reverse=True)
        
        for key in sorted_keys:
            if key in query_lower:
                # If the alias is present, but the full name isn't fully there, replace/append
                full_name = self.brand_mapping[key]
                if full_name.lower() not in query_lower:
                    # We can append the full name to the query to boost retrieval
                    expanded_query += f" {full_name}"
                    # Or replace: expanded_query = expanded_query.replace(key, full_name)
                    # Appending is safer to keep original user intent nuances.
                    break # Stop after first major match to avoid over-expansion? 
                          # Or continue? Let's stop to keep it simple for now.

        print(f"Original Query: {query} | Expanded Query: {expanded_query}")
        return self.base_retriever.invoke(expanded_query)

