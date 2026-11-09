from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.assistant_manager import AssistantManager

BASE_DIR = Path(__file__).resolve().parent.parent
app = FastAPI(title="Open Jarvis", version="0.1.0")
manager = AssistantManager()
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


class ChatRequest(BaseModel):
    assistant_id: str = Field(min_length=1, max_length=50)
    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    assistant_id: str
    reply: str
    plugin_used: str | None = None


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "name": "Open Jarvis"}


@app.get("/api/assistants")
def assistants() -> list[dict[str, str]]:
    return manager.list_assistants()


@app.get("/api/plugins")
def plugins() -> list[dict[str, str]]:
    return manager.list_plugins()


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        reply, plugin_used = manager.respond(request.assistant_id, request.message.strip())
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Assistant not found") from error
    return ChatResponse(
        assistant_id=request.assistant_id,
        reply=reply,
        plugin_used=plugin_used,
    )
