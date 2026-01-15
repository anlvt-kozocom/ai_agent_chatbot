# AI Product Agent - System Architecture Analysis

**Document Date:** January 14, 2026  
**System:** LangGraph-based AI Product Recommendation Agent  
**Analysis Type:** Node Function and Data Flow Analysis

---

## Executive Summary

This document provides a comprehensive analysis of the AI Product Agent system architecture, detailing the function of each node in the LangGraph execution flow. The system employs a hybrid RAG (Retrieval-Augmented Generation) + SQL approach to deliver intelligent product recommendations and comparisons.

---

## System Architecture Overview

The system consists of 16 interconnected nodes organized into a directed acyclic graph (DAG) with conditional branching. The architecture supports:

- **Multi-turn conversations** with context awareness
- **Intent-based routing** for different query types
- **Hybrid data retrieval** combining SQL databases and vector stores
- **Specialized processing** for comparisons, recommendations, product information, and warranty policies

---

## Node Catalog and Functions

### 1. Entry Point

#### `__start__`
- **Type:** System Node
- **Function:** Entry point for the LangGraph execution
- **Input:** User message, thread_id, language preference
- **Output:** Initialized state object
- **Next Node:** `context_resolution_node`

---

### 2. Context Processing Layer

#### `context_resolution_node`
- **Type:** Processing Node
- **Function:** Resolves conversational context and anaphoric references
- **Key Capabilities:**
  - Resolves pronouns ("it", "that one") using conversation history
  - Normalizes user queries for downstream processing
  - Maintains conversation coherence across turns
- **Input:** Raw user query + conversation history
- **Output:** Contextualized, normalized query
- **Next Node:** `router_node`

---

### 3. Intent Classification Layer

#### `router_node`
- **Type:** Decision Node
- **Function:** Classifies user intent and determines processing pathway
- **Intent Categories:**
  - `comparison` - Compare multiple products
  - `product_info` - Get details about specific product
  - `general` - General questions about technology/market
  - `recommendation` - Product recommendations based on criteria
  - `warranty` - Warranty and return policy questions
- **Technology:** LLM-based intent classification
- **Input:** Normalized query
- **Output:** Classified intent + routing decision
- **Next Node:** `retrieval_strategy_node`

---

### 4. Retrieval Strategy Layer

#### `retrieval_strategy_node`
- **Type:** Strategy Node
- **Function:** Determines optimal data retrieval strategy
- **Decision Logic:**
  - **Price-based queries** → `price_filtering_node`
  - **Multi-condition queries** (battery, camera, RAM) → `sql_filtering_node`
  - **Direct flow** → `recall_node` (for simple lookups)
- **Input:** User intent + extracted conditions
- **Output:** Strategy selection
- **Next Nodes:** `price_filtering_node` OR `sql_filtering_node`

---

### 5. Data Filtering Layer

#### `price_filtering_node`
- **Type:** SQL Query Node
- **Function:** Filters products based on price criteria
- **Capabilities:**
  - Price range filtering (e.g., "under 10 million")
  - Find cheapest/most expensive products
  - Brand + price combination filtering
- **Data Source:** SQLite database
- **Input:** Price range, brand (optional), sort preference
- **Output:** List of product_ids matching criteria
- **Next Node:** `recall_node`

#### `sql_filtering_node`
- **Type:** Advanced SQL Node
- **Function:** Handles complex multi-condition queries
- **Capabilities:**
  - Text-to-SQL conversion using LLM
  - Multi-attribute filtering (battery > 5000mAh, camera specs, etc.)
  - Query validation and error handling
- **Data Source:** SQLite database with extended schema
- **Input:** Complex search criteria
- **Output:** Filtered product_ids
- **Next Node:** `recall_node`

---

### 6. Information Retrieval Layer

#### `recall_node`
- **Type:** RAG Node
- **Function:** Retrieves detailed product information from vector store
- **Capabilities:**
  - Semantic search using embeddings
  - Product ID-based retrieval
  - Language-specific document filtering
  - Relevance scoring and ranking
- **Data Source:** FAISS vector store
- **Input:** product_ids OR search query
- **Output:** Retrieved documents with product details
- **Next Node:** `precision_node`

---

### 7. Result Refinement Layer

#### `precision_node`
- **Type:** Reranking Node
- **Function:** Refines and deduplicates retrieved results
- **Capabilities:**
  - Document reranking for relevance
  - Deduplication by product_id
  - Top-k selection
  - Routing to specialized processing nodes
- **Input:** Retrieved documents
- **Output:** Refined, deduplicated documents
- **Next Nodes:** Routes to one of:
  - `comparison_node`
  - `general_node`
  - `product_info_node`
  - `recommendation_node`

---

### 8. Specialized Processing Layer

#### `comparison_node`
- **Type:** Formatting Node
- **Function:** Generates structured product comparisons
- **Capabilities:**
  - Extract specifications for multiple products
  - Create comparison tables (markdown format)
  - Highlight key differences
- **Input:** Multiple product documents
- **Output:** Formatted comparison table
- **Next Node:** `sales_synthesis_node`

#### `general_node`
- **Type:** QA Node
- **Function:** Answers general technology/market questions
- **Capabilities:**
  - RAG-based information retrieval
  - General knowledge synthesis
  - Technology trend explanations
- **Input:** General query + context documents
- **Output:** Informative answer
- **Next Node:** `sales_synthesis_node`

#### `product_info_node`
- **Type:** Information Node
- **Function:** Provides detailed information about specific products
- **Capabilities:**
  - Extract comprehensive product specifications
  - Present features, pricing, availability
  - Format for readability
- **Input:** Single product query + documents
- **Output:** Structured product information
- **Next Node:** `sales_synthesis_node`

#### `recommendation_node`
- **Type:** Recommendation Node
- **Function:** Suggests products matching user requirements
- **Capabilities:**
  - Requirement-based filtering
  - Price post-processing and validation
  - Top-N recommendation selection
  - Missing information detection
- **Input:** User requirements + filtered products
- **Output:** Ranked product recommendations
- **Special Flow:** Can route to `requirement_node` if information is missing
- **Next Node:** `sales_synthesis_node` OR `requirement_node`

#### `warranty_node`
- **Type:** Policy Information Node
- **Function:** Answers warranty and return policy questions
- **Capabilities:**
  - Retrieves warranty documents from dedicated RAG service
  - Answers policy-related questions (return periods, coverage, conditions)
  - Multilingual support (Vietnamese/English)
  - Context-aware responses based on warranty documents
- **Data Source:** Separate FAISS vector store for warranty documents
- **Input:** Warranty/policy question
- **Output:** Clear answer based on warranty policy documents
- **Special Flow:** Bypasses product retrieval pipeline, goes directly from router
- **Next Node:** `__end__` (direct termination, no sales synthesis needed)

---

### 9. Information Gathering Layer

#### `requirement_node`
- **Type:** Dialogue Management Node
- **Function:** Collects missing information through conversational turns
- **Capabilities:**
  - Identify missing required fields (e.g., brand)
  - Generate clarifying questions
  - Extract information from short user responses
  - Multi-turn conversation handling
- **Input:** Incomplete user requirements
- **Output:** Complete requirements OR clarifying question
- **Flow:** Creates a loop back to previous processing nodes once information is collected
- **Next Node:** Loops back to appropriate processing node OR `sales_synthesis_node`

---

### 10. Response Generation Layer

#### `sales_synthesis_node`
- **Type:** Response Generation Node
- **Function:** Synthesizes final user-facing response
- **Capabilities:**
  - Aggregates information from all processing nodes
  - Formats in sales-oriented, friendly language
  - Ensures professional and helpful tone
  - Multilingual response generation (Vietnamese/English)
- **Input:** Processed information from specialized nodes
- **Output:** Final formatted response
- **Next Node:** `__end__`

---

### 11. Exit Point

#### `__end__`
- **Type:** System Node
- **Function:** Terminates graph execution
- **Output:** Returns final response to user

---

## Data Flow Patterns

### Pattern 1: Simple Product Lookup
```
start → context_resolution → router → retrieval_strategy → recall → precision → product_info → sales_synthesis → end
```

### Pattern 2: Price-Based Recommendation
```
start → context_resolution → router → retrieval_strategy → price_filtering → recall → precision → recommendation → sales_synthesis → end
```

### Pattern 3: Complex Multi-Condition Search
```
start → context_resolution → router → retrieval_strategy → sql_filtering → recall → precision → recommendation → sales_synthesis → end
```

### Pattern 4: Product Comparison
```
start → context_resolution → router → retrieval_strategy → recall → precision → comparison → sales_synthesis → end
```

### Pattern 5: Multi-Turn Requirement Gathering
```
start → context_resolution → router → retrieval_strategy → recall → precision → recommendation → requirement → (loops back) → sales_synthesis → end
```

### Pattern 6: Warranty Policy Query
```
start → context_resolution → router → warranty_node → end
```
**Note:** Warranty queries bypass the entire product retrieval pipeline and go directly to the warranty node for policy information.

---

## Architectural Strengths

1. **Hybrid Approach:** Combines structured SQL filtering with unstructured RAG retrieval
2. **Intent-Aware Routing:** Efficiently routes queries to specialized processors
3. **Context Preservation:** Maintains conversation coherence across multiple turns
4. **Flexible Filtering:** Supports both simple price filters and complex multi-attribute queries
5. **Result Refinement:** Precision node ensures high-quality, deduplicated results
6. **Conversational Intelligence:** Requirement node enables natural dialogue for information gathering

---

## Technical Stack

- **Framework:** LangGraph (for graph orchestration)
- **Database:** SQLite (structured product data)
- **Vector Store:** FAISS (semantic search)
- **LLM:** Used for intent classification, text-to-SQL, and response generation
- **Embeddings:** For semantic document retrieval

---

## Graph Characteristics

- **Node Count:** 16 nodes
- **Maximum Depth:** 9 hops (start to end)
- **Branching Points:** 3 major branches (price_filtering vs sql_filtering, 4-way split at precision, warranty shortcut)
- **Loops:** 1 feedback loop (requirement_node can loop back)
- **Parallel Paths:** Multiple independent processing paths converge at sales_synthesis (except warranty which terminates directly)

---

## Recommendations for Optimization

1. **Caching:** Implement caching for frequently accessed product information
2. **Parallel Execution:** Consider parallelizing price_filtering and recall for certain queries
3. **Early Stopping:** Add confidence thresholds to avoid unnecessary processing
4. **Monitoring:** Add observability for node execution times and success rates
5. **A/B Testing:** Test different routing strategies for ambiguous queries

---

## Document Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-14 | Initial architecture analysis |
| 1.1 | 2026-01-15 | Added warranty_node documentation and updated node count |

---

**Prepared by:** AI Architecture Analysis  
**For:** AI Product Agent Development Team
