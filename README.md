# AI Product Agent - Phone Sales Assistant

This project is a smart AI Sales Assistant built using **LangGraph** and **RAG (Retrieval-Augmented Generation)**. The core objective is to help users search, compare, and receive detailed information about mobile phone products in a natural and accurate way.

## 🚀 Key Features
- **Product Discovery**: Suggest phones based on needs (budget, brand, configuration).
- **Phone Comparison**: Detailed specification comparison between different models.
- **Price Lookup**: Integrated SQL to provide accurate, real-time prices (VND, USD, YEN).
- **Multilingual Support**: Optimized for Vietnamese.
- **Smart Conversational Flow**: Collects missing information (like brand) before providing recommendations.

## 🛠 Libraries and Technologies
- **Core Framework**: [LangGraph](https://github.com/langchain-ai/langgraph) (Agent orchestration).
- **LLM Orchestration**: [LangChain](https://github.com/langchain-ai/langchain).
- **Language Models**: OpenAI (GPT-4o) or Google Gemini (1.5 Flash/Pro).
- **Vector Database**: FAISS (for storing and querying product information).
- **Backend API**: FastAPI & Uvicorn.
- **Database**: SQLite (for precise price filtering).
- **Retrieval**: Hybrid Search (Vector Similarity + BM25) with LLM Reranking.

## 📁 Project Structure
```text
ai_product_agent/
├── app/
│   ├── agents/          # Logic for each Node in the Graph
│   ├── chains/          # Language processing chains (Prompts & LLMs)
│   ├── graphs/          # LangGraph flow configuration (qa_graph.py)
│   ├── services/        # Core services (RAG, Memory, LLM)
│   ├── tools/           # Helper tools (PriceTool connecting to SQL)
│   ├── models/          # Pydantic Schemas definitions
│   └── main.py          # FastAPI Entry point
├── data/                # Product data (JSON, SQL, Text)
├── sigma-chatbox/       # User Interface (React)
├── tests/               # Test scripts
└── requirements.txt     # Python dependency list
```

## 🧠 Graph Structure and Nodes
The system uses a StateGraph to coordinate the conversation:

| Node | Purpose |
| :--- | :--- |
| `context_resolution` | Resolves conversational context and references (e.g., "it", "this"). |
| `router_node` | Classifies user intent (Consultation, Comparison, Info lookup, or General QA). |
| `retrieval_strategy` | Decides the appropriate data retrieval strategy based on intent. |
| `price_filtering` | (SQL Tool) Filters product lists to match the user's budget exactly. |
| `recall_node` | Performs broad retrieval of relevant documents from the Vector Store. |
| `precision_node` | Removes duplicates and uses an LLM to rerank the best results. |
| `requirement_node` | Asks the user for missing critical information (like Brand). |
| `recommendation_node` | Generates consultation content based on filtered products. |
| `comparison_node` | Analyzes and generates comparison tables for requested products. |
| `product_info_node` | Provides detailed specifications for a specific product. |
| `sales_synthesis` | Synthesizes the final response in a friendly salesperson style. |

## 🔧 Tools Used
1. **PriceTool**: Directly queries the SQLite database for accurate prices with flexible tolerance for each currency.
2. **RAG Service**: A Hybrid Retriever system combining Vector Search (semantic) and BM25 (keyword).
3. **Memory Server**: Stores conversation history per `thread_id` to give the agent long-term memory within a session.

## ⚙️ Environment Setup

### 1. Create Conda Environment (Python 3.10)
```bash
conda create -n ai_agent python=3.10 -y
conda activate ai_agent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file from `.env.example` and fill in the necessary API keys (OPENAI_API_KEY or GOOGLE_API_KEY).

### 4. Run the Application
```bash
uvicorn app.main:app --reload
```
