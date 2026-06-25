"""CORS 中间件配置

跨域资源共享配置，支持前端 Web 应用访问。
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI, origins: list[str] | None = None) -> None:
    """配置 CORS 中间件

    Args:
        app: FastAPI 应用实例
        origins: 允许的源列表，None 则允许所有
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
