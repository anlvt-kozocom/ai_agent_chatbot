import os
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from app.graphs.qa_graph import build_graph
from app.services.rag_service import rag_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize RAG service
    # Check env var for reloading data
    reload_data = os.getenv("RELOAD_RAG_DATA", "False").lower() == "true"
    try:
        rag_service.initialize(reload_data=reload_data)
    except Exception as e:
        print(f"Failed to initialize RAG service: {e}")
    yield
    # Shutdown logic if needed


app = FastAPI(lifespan=lifespan)

# Global graph instance with checkpointer
graph = build_graph()


# Request model for the API
class ChatRequest(BaseModel):
    message: str
    thread_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Session ID for conversation history",
    )


@app.get("/")
def read_root():
    return {"message": "LangGraph QA Agent API is running"}


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint to interact with the QA Agent Graph (RAG enabled).
    Now supports persistence via thread_id.
    """
    try:
        # Config for the graph execution to point to a specific thread
        config = {"configurable": {"thread_id": request.thread_id}}

        # Prepare input state
        input_state = {"messages": [HumanMessage(content=request.message)]}

        # Invoke the graph with config
        result = await graph.ainvoke(input_state, config=config)

        path = result.get("path", [])

        # Extract the answer
        return {
            "thread_id": request.thread_id,
            "question": request.message,
            "answer": result.get("answer"),
            "path": path,
            "history_count": len(result.get("messages", [])),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
