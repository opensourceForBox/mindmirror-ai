"""MindMirror AI - FastAPI 应用入口"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import chat, emotion, health, video

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MindMirror AI",
    description="AI-powered mental health companion for youth",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(emotion.router)
app.include_router(video.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mindmirror-ai"}
