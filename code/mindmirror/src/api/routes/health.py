"""健康检查接口

服务状态监控和就绪检测。
"""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def liveness():
    """存活探针"""
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness():
    """就绪探针，检查各依赖服务状态"""
    # TODO: 检查 Qdrant、Redis 等依赖服务
    return {"status": "ready", "services": {"qdrant": "unknown", "redis": "unknown"}}
