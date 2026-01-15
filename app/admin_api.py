import os
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.services.rag_service import rag_service
from app.services.warranty_rag_service import warranty_rag_service


# Request/Response Models
class FileItem(BaseModel):
    name: str
    path: str
    type: str  # 'file' or 'directory'
    extension: Optional[str] = None


class FileContent(BaseModel):
    path: str
    content: str


class SyncResponse(BaseModel):
    status: str
    message: str
    details: Optional[Dict] = None


# Admin API App
app = FastAPI(title="Admin API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base directory
BASE_DIR = Path(__file__).parent.parent


def get_file_tree(directory: Path, base_path: Path) -> List[FileItem]:
    """Recursively get file tree structure"""
    items = []

    try:
        for item in sorted(directory.iterdir()):
            # Skip hidden files and __pycache__
            if item.name.startswith(".") or item.name == "__pycache__":
                continue

            relative_path = str(item.relative_to(base_path))

            if item.is_file():
                items.append(
                    FileItem(
                        name=item.name,
                        path=relative_path,
                        type="file",
                        extension=item.suffix,
                    )
                )
            elif item.is_dir():
                items.append(
                    FileItem(name=item.name, path=relative_path, type="directory")
                )
                # Recursively add subdirectory contents
                items.extend(get_file_tree(item, base_path))
    except PermissionError:
        pass

    return items


@app.get("/")
async def root():
    return {"message": "Admin API is running", "version": "1.0.0"}


@app.get("/api/files/prompts", response_model=List[FileItem])
async def list_prompts():
    """List all prompt files"""
    prompts_dir = BASE_DIR / "app" / "prompts"

    if not prompts_dir.exists():
        raise HTTPException(status_code=404, detail="Prompts directory not found")

    return get_file_tree(prompts_dir, BASE_DIR)


@app.get("/api/files/data", response_model=List[FileItem])
async def list_data_files():
    """List all data files"""
    data_dir = BASE_DIR / "data"

    if not data_dir.exists():
        raise HTTPException(status_code=404, detail="Data directory not found")

    items = []

    # Get files from main directories we care about
    for subdir in ["clean", "raw", "warranty"]:
        subdir_path = data_dir / subdir
        if subdir_path.exists():
            items.extend(get_file_tree(subdir_path, BASE_DIR))

    # Also include root data files
    for item in data_dir.iterdir():
        if item.is_file() and not item.name.startswith("."):
            relative_path = str(item.relative_to(BASE_DIR))
            items.append(
                FileItem(
                    name=item.name,
                    path=relative_path,
                    type="file",
                    extension=item.suffix,
                )
            )

    return items


@app.get("/api/file/content")
async def get_file_content(path: str):
    """Get content of a specific file"""
    file_path = BASE_DIR / path

    # Security check: ensure file is within BASE_DIR
    try:
        file_path = file_path.resolve()
        BASE_DIR.resolve()
        if not str(file_path).startswith(str(BASE_DIR.resolve())):
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid path")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Path is not a file")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return {
            "path": path,
            "content": content,
            "size": file_path.stat().st_size,
            "extension": file_path.suffix,
        }
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File is not a text file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


@app.put("/api/file/content")
async def update_file_content(file_data: FileContent = Body(...)):
    """Update content of a specific file"""
    file_path = BASE_DIR / file_data.path

    # Security check: ensure file is within BASE_DIR
    try:
        file_path = file_path.resolve()
        if not str(file_path).startswith(str(BASE_DIR.resolve())):
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid path")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Write new content
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_data.content)

        return {
            "status": "success",
            "message": f"File updated successfully: {file_data.path}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating file: {str(e)}")


@app.post("/api/sync/vector-store", response_model=SyncResponse)
async def sync_vector_store():
    """Rebuild product data vector store"""
    try:
        # Run sync in background to avoid timeout
        await asyncio.to_thread(rag_service.initialize, reload_data=True)

        return SyncResponse(
            status="success",
            message="Product vector store rebuilt successfully",
            details={
                "service": "rag_service",
                "data_dir": rag_service.data_dir,
                "index_dir": rag_service.index_dir,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error rebuilding vector store: {str(e)}"
        )


@app.post("/api/sync/warranty-vector-store", response_model=SyncResponse)
async def sync_warranty_vector_store():
    """Rebuild warranty data vector store"""
    try:
        # Run sync in background to avoid timeout
        await asyncio.to_thread(warranty_rag_service.initialize, reload_data=True)

        return SyncResponse(
            status="success",
            message="Warranty vector store rebuilt successfully",
            details={
                "service": "warranty_rag_service",
                "data_dir": warranty_rag_service.data_dir,
                "index_dir": warranty_rag_service.index_dir,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error rebuilding warranty vector store: {str(e)}"
        )


@app.get("/api/sync/status")
async def get_sync_status():
    """Get status of vector stores"""
    product_index_exists = os.path.exists(
        os.path.join(rag_service.index_dir, "index.faiss")
    )
    warranty_index_exists = os.path.exists(
        os.path.join(warranty_rag_service.index_dir, "index.faiss")
    )

    return {
        "product_vector_store": {
            "exists": product_index_exists,
            "path": rag_service.index_dir,
            "initialized": rag_service.vector_store is not None,
        },
        "warranty_vector_store": {
            "exists": warranty_index_exists,
            "path": warranty_rag_service.index_dir,
            "initialized": warranty_rag_service.vector_store is not None,
        },
    }


# Mount static files directory for serving frontend
admin_static_dir = BASE_DIR / "admin"
if admin_static_dir.exists():
    app.mount(
        "/", StaticFiles(directory=str(admin_static_dir), html=True), name="static"
    )
