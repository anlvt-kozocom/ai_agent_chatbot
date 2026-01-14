# AI Product Agent - Phone Sales Assistant

An intelligent AI Sales Assistant built with **LangGraph** and **RAG** to revolutionize how users search, compare, and buy mobile phones.

## Problem Statement
Buying a mobile phone is often overwhelming due to the fragmentation of information. Users have to visit multiple websites to check prices, compare specs, and read reviews. There is no single place to get personalized querying or real competitive analysis in a conversational manner.

## Solution
This project provides a "Smart Salesperson" persona that aids users through:
*   **Natural Language Layout**: Understands complex queries like "best Samsung phone under 20 million VND".
*   **Multi-Strategy Retrieval**: Combines semantic search (vector) with precise filtering (SQL) for accurate results.
*   **Intelligent Routing**: Directs users to finding products, comparing details, or getting technical info seamlessly.

## Tech Stack
- **Languages**: Python 3.10+, TypeScript, HTML/CSS.
- **Frameworks**: 
    - **Backend**: FastAPI, Uvicorn, LangGraph, LangChain.
    - **Frontend**: React (Vite).
- **AI**: 
    - **LLMs**: OpenAI gpt-4o-mini
    - **Vector Store**: FAISS.
    - **Embeddings**: text-embedding-3-large

## Quick Start

### 1. Clone Repo
```bash
git clone https://github.com/anlvt-kozocom/ai_agent_chatbot.git
cd ai_agent_chatbot
```

### 2. Install Dependencies

**Backend:**
```bash
cp .env.example .env
conda create -n ai_agent python=3.10 -y
conda activate ai_agent
pip install -r requirements.txt
```

**Frontend:**
```bash
cd sigma-chatbox/react-landing-page-sigma-chatbox
npm install

cp .env.example .env
```

### 3. Run Application

**Start Backend API:**
```bash
# In the root directory
# Make sure to set your .env file first!
uvicorn app.main:app --reload --host 127.0.0.1 --port 8006
```

**Start Frontend:**
```bash
# In sigma-chatbox/react-landing-page-sigma-chatbox
npm run dev
```

## Architecture
The system relies on a **LangGraph StateGraph** to manage conversational flow.

| Node | Description |
| :--- | :--- |
| `context_resolution` | Resolves coreferences (e.g., "how much is it?"). |
| `router_node` | Classifies user intent (Consultation, Comparison, Specs, etc.). |
| `price_filtering` | SQL-based tool for precise budget filtering. |
| `recall_node` | Hybrid retrieval (Vector + Keyword) for product documents. |
| `precision_node` | Reranks and deduplicates retrieved products. |
| `recommendation_node` | Generates the final advice/response. |
| `comparison_node` | Creates comparison tables for specific models. |
| `sales_synthesis` | Polishes the final output in a sales persona. |

## API Documentation
The backend exposes the following key endpoints:

*   **GET** `/`
    *   Status check.
*   **GET** `/health`
    *   Health check for the service.
*   **POST** `/chat`
    *   Main interaction endpoint.
    *   **Body**: `{"message": "string", "language": "en" | "vi" | "ja", "thread_id": "string"}`
*   **POST** `/chat/stream`
    *   SSE endpoint for real-time streaming responses.