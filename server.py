import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

# Load env vars explicitly at startup
load_dotenv()

from app.api.v1.chat import router as chat_router
from app.services.chat_service import get_global_retriever


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events:
    - Startup: Initialize RAG retriever (load data, create vector store)
    - Shutdown: Cleanup if necessary
    """
    logger.info("Starting up application...")
    
    # Trigger RAG initialization
    try:
        get_global_retriever()
    except Exception as e:
        logger.error(f"Error during RAG initialization: {e}")
    
    yield
    
    logger.info("Shutting down application...")


def create_app() -> FastAPI:
    """
    Application factory for the AI Agent backend.
    """
    app = FastAPI(title="AI Agent Backend", version="1.0.0", lifespan=lifespan)

    # Routers should only handle HTTP, no business logic
    app.include_router(chat_router, prefix="/api/v1")

    return app


app = create_app()


