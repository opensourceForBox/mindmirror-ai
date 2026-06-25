"""MindMirror AI - FastAPI 应用入口"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import assessment, auth, chat, emotion, health, parent, profile, topics, video
from src.models.database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库"""
    await init_db()
    logger.info("数据库初始化完成")
    yield


app = FastAPI(
    title="MindMirror AI",
    description="AI-powered mental health companion for youth",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(emotion.router)
app.include_router(video.router)
app.include_router(profile.router)
app.include_router(topics.router)
app.include_router(assessment.router)
app.include_router(parent.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mindmirror-ai"}
