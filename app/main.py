import os
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from fastapi.responses import StreamingResponse
import json

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


@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Endpoint to stream the response from the QA Agent Graph.
    Uses Server-Sent Events (SSE) to send token chunks.
    """
    try:
        # Config for the graph execution to point to a specific thread
        config = {"configurable": {"thread_id": request.thread_id}}

        # Prepare input state
        input_state = {"messages": [HumanMessage(content=request.message)]}

        async def event_generator():
            # Default language is English until detected otherwise
            original_language = "en"

            # Nodes that generate the core answer (before translation)
            core_answer_nodes = {
                "general_node",
                "product_info_node",
                "recommendation_node",
            }

            try:
                # Astream events from the graph
                async for event in graph.astream_events(
                    input_state, config=config, version="v1"
                ):
                    kind = event["event"]
                    node = event.get("metadata", {}).get("langgraph_node", "")

                    # 1. Detect Language from language_input_node output
                    if kind == "on_chain_end" and node == "language_input_node":
                        output = event["data"].get("output", {})
                        if output and "original_language" in output:
                            original_language = output["original_language"]

                    # 2. Filter Stream Events
                    if kind == "on_chat_model_stream":
                        # Check if we should stream this node
                        should_stream = False

                        # Always stream the final translation layer
                        if node == "language_output_node":
                            should_stream = True

                        # Stream core nodes ONLY if language is English (no translation needed)
                        # If language is NOT English, we hide these because they are "intermediate" (wrong language)
                        elif node in core_answer_nodes:
                            if original_language.lower() in [
                                "en",
                                "english",
                                "en-us",
                                "en-gb",
                            ]:
                                should_stream = True

                        if should_stream:
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
