import os
import uuid
from typing import Literal
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from fastapi.responses import StreamingResponse
import json

from app.graphs.qa_graph import build_graph
from app.services.rag_service import rag_service
from app.utils.callbacks import TokenUsageHandler
from app.services.usage_store import get_thread_usage


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
    language: Literal["en", "vi", "ja"] = "en"
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
        # Prepare callback handler
        handler = TokenUsageHandler(request.thread_id)

        # Config for the graph execution to point to a specific thread
        config = {
            "configurable": {"thread_id": request.thread_id},
            "callbacks": [handler],
        }

        # Prepare input state
        input_state = {
            "messages": [HumanMessage(content=request.message)],
            "language": request.language,
        }

        # Invoke the graph with config
        result = await graph.ainvoke(input_state, config=config)

        path = result.get("path", [])

        # Extract the answer
        return {
            "thread_id": request.thread_id,
            "question": request.message,
            "language": request.language,
            "answer": result.get("answer"),
            "path": path,
            "history_count": len(result.get("messages", [])),
            "token_usage": get_thread_usage(request.thread_id),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Endpoint to stream the response from the QA Agent Graph.
    Uses Server-Sent Events (SSE) to send token chunks.
    """
    try:
        # We can't easily return token usage in the stream end with this setup unless we send a specific event
        # But for now, we just attach the callback
        handler = TokenUsageHandler(request.thread_id)
        config = {
            "configurable": {"thread_id": request.thread_id},
            "callbacks": [handler],
        }

        async def event_generator():
            try:
                # Prepare input state
                input_state = {
                    "messages": [HumanMessage(content=request.message)],
                    "language": request.language,
                }

                # Astream events from the graph
                async for event in graph.astream_events(
                    input_state, config=config, version="v1"
                ):
                    kind = event["event"]
                    node = event.get("metadata", {}).get("langgraph_node", "")

                    # Filter Stream Events
                    if kind == "on_chat_model_stream":
                        # We stream most nodes now as they should output in the requested language directly
                        # or at least provide useful intermediate info.
                        # To keep it simple, we stream everything from core nodes.

                        core_nodes = {
                            "general_node",
                            "product_info_node",
                            "recommendation_node",
                            "requirement_node",
                            "sales_synthesis_node",
                        }

                        if node in core_nodes:
                            content = event["data"]["chunk"].content
                            if content:
                                payload = {
                                    "event": kind,
                                    "node": node,
                                    "content": content,
                                }
                                yield f"data: {json.dumps(payload)}\n\n"

                yield "data: [DONE]\n\n"
            except Exception as e:
                print(f"Error in event_generator: {e}")
                import traceback

                traceback.print_exc()
                # Optionally yield an error event so client knows
                error_payload = {"event": "error", "error": str(e)}
                yield f"data: {json.dumps(error_payload)}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
