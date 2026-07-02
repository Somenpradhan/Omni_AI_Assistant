import os
import sys
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Ensure app directory is registered in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.v1.endpoints import chat, upload, memory, sessions, health

app = FastAPI(
    title="Enterprise Multi-Agent AI Assistant API",
    description="FastAPI Backend for LangGraph Orchestrated Multi-Agent AI Assistant",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Expose endpoints at root for backward compatibility with frontend queries
app.include_router(chat.router, tags=["chat"])
app.include_router(upload.router, tags=["upload"])
app.include_router(memory.router, tags=["memory"])
app.include_router(sessions.router, tags=["sessions"])
app.include_router(health.router, tags=["health"])

@app.get("/", response_class=HTMLResponse)
def read_root():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse("<h2>Aether Enterprise API is Online. index.html is missing.</h2>")

@app.get("/chat-ui", response_class=HTMLResponse)
def serve_chat_ui():
    ui_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "chat_ui.html")
    if os.path.exists(ui_file):
        return FileResponse(ui_file)
    return HTMLResponse("<h2>chat_ui.html is missing in frontend directory.</h2>")

if __name__ == "__main__":
    import uvicorn
    # Append app directory for uvicorn imports
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
