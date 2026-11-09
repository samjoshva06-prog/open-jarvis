from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.ai_provider import ProviderError
from app.assistant_manager import AssistantManager

BASE_DIR = Path(__file__).resolve().parent.parent
app = FastAPI(title="Open Jarvis", version="0.2.0")
manager = AssistantManager()
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    assistant_id: str = Field(min_length=1, max_length=50)
    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


class ChatResponse(BaseModel):
    assistant_id: str
    reply: str
    plugin_used: str | None = None


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/health")
def health() -> dict[str, str | bool]:
    return {"status": "ok", "name": "Open Jarvis", "ai_configured": manager.provider.is_configured}


@app.get("/api/assistants")
def assistants() -> list[dict[str, str]]:
    return manager.list_assistants()


@app.get("/api/plugins")
def plugins() -> list[dict[str, str]]:
    return manager.list_plugins()


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        reply, plugin_used = manager.respond(
            request.assistant_id,
            request.message.strip(),
            [item.model_dump() for item in request.history],
        )
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Assistant not found") from error
    except ProviderError as error:
        raise HTTPException(
            status_code=502,
            detail="The AI provider is unavailable. Check your provider settings and try again.",
        ) from error
    return ChatResponse(assistant_id=request.assistant_id, reply=reply, plugin_used=plugin_used)
