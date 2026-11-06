"""FastAPI application factory for Emotions for AI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from emotions_ai.runtime.facade import EmotionAI


class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: str = "default"
    temperature: float = 0.7


class ChatResponse(BaseModel):
    text: str
    emotional_summary: dict[str, Any]
    guidance: dict[str, Any]
    cognitive_summary: str = ""


def create_app(emotion_ai: EmotionAI | None = None) -> FastAPI:
    ai = emotion_ai or EmotionAI()

    app = FastAPI(title="Emotions for AI", version="0.1.0")
    app.state.ai = ai

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.post("/chat", response_model=ChatResponse)
    async def chat(req: ChatRequest):
        result = await app.state.ai.chat(
            user_id=req.user_id,
            message=req.message,
            session_id=req.session_id,
            temperature=req.temperature,
        )
        return ChatResponse(
            text=result.text,
            emotional_summary=result.emotional_summary,
            guidance=result.guidance,
            cognitive_summary=result.cognitive_summary,
        )

    @app.get("/state/{user_id}")
    async def state(user_id: str, session_id: str = "default"):
        col = app.state.ai.get_state(user_id, session_id)
        return col.model_dump(mode="json")

    @app.get("/state/{user_id}/history")
    async def history(user_id: str, session_id: str = "default"):
        return app.state.ai.state_history(user_id, session_id)

    @app.delete("/memory/{user_id}")
    async def delete_memory(user_id: str):
        n = app.state.ai.delete_user_memory(user_id)
        return {"deleted": n}

    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard():
        p = Path(__file__).parent / "static" / "dashboard.html"
        return HTMLResponse(p.read_text(encoding="utf-8"))

    @app.post("/simulate")
    async def simulate(
        user_id: str,
        session_id: str = "default",
        duration_seconds: float = 3600.0,
        step_seconds: float = 300.0,
    ):
        return await app.state.ai.simulate_time(
            user_id=user_id,
            session_id=session_id,
            duration_seconds=duration_seconds,
            step_seconds=step_seconds,
        )

    @app.get("/state/{user_id}/timeline")
    async def timeline(user_id: str, session_id: str = "default", duration_seconds: float = 3600.0, step_seconds: float = 300.0):
        return await app.state.ai.simulate_time(
            user_id=user_id,
            session_id=session_id,
            duration_seconds=duration_seconds,
            step_seconds=step_seconds,
        )

    @app.websocket("/ws")
    async def websocket_endpoint(ws: WebSocket):
        await ws.accept()
        try:
            while True:
                data = await ws.receive_json()
                result = await app.state.ai.chat(
                    user_id=data.get("user_id", "anon"),
                    message=data.get("message", ""),
                    session_id=data.get("session_id", "default"),
                )
                await ws.send_json(result.to_dict())
        except WebSocketDisconnect:
            pass

    return app