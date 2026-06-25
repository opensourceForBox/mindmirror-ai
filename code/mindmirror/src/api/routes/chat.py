"""对话 API 路由

处理用户对话请求，与 LangGraph 对话引擎交互。
提供消息发送、历史查询、情绪趋势三个端点。
"""
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.agent.manager import get_conversation_manager
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


# ── 请求 / 响应模型 ───────────────────────────────────────────────


class ChatRequest(BaseModel):
    """对话请求"""
    session_id: str
    message: str
    emotion_data: Optional[dict] = None  # 可选的外部情绪数据


class ChatResponse(BaseModel):
    """对话响应"""
    response: str
    emotion: Optional[dict] = None
    risk_level: str = "low"
    suggested_exercises: list[str] = []
    needs_human_intervention: bool = False


# ── 路由 ──────────────────────────────────────────────────────────


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """发送消息并获取 AI 回复

    完整的对话流程：情绪感知 → 危机检查 → 知识检索 → 回复生成。
    如果检测到危机信号，会自动触发危机干预流程。

    Args:
        request: ChatRequest 包含 session_id、message 和可选的 emotion_data

    Returns:
        ChatResponse 包含 AI 回复、情绪状态、风险等级等
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="消息内容不能为空")

    logger.info("收到对话请求: session=%s, msg_len=%d", request.session_id, len(request.message))

    manager = get_conversation_manager()
    result = await manager.chat(
        session_id=request.session_id,
        user_message=request.message,
        emotion_data=request.emotion_data,
    )

    # 如果有危机信号，记录告警
    if result.get("needs_human_intervention"):
        logger.warning(
            "危机干预触发: session=%s, risk=%s",
            request.session_id,
            result.get("risk_level"),
        )

    return ChatResponse(
        response=result.get("response", ""),
        emotion=result.get("emotion"),
        risk_level=result.get("risk_level", "low"),
        suggested_exercises=result.get("suggested_exercises", []),
        needs_human_intervention=result.get("needs_human_intervention", False),
    )


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """获取对话历史

    Args:
        session_id: 会话 ID

    Returns:
        对话消息列表
    """
    manager = get_conversation_manager()
    history = await manager.get_history(session_id)
    return {"session_id": session_id, "messages": history}


@router.get("/emotion-trend/{session_id}")
async def get_emotion_trend(session_id: str):
    """获取情绪变化趋势

    Args:
        session_id: 会话 ID

    Returns:
        情绪趋势数据
    """
    manager = get_conversation_manager()
    trend = await manager.get_emotion_trend(session_id)
    # 确保返回前端期望的格式
    data_points = trend if isinstance(trend, list) else []
    # 计算趋势方向
    if len(data_points) >= 2:
        recent = data_points[-3:] if len(data_points) >= 3 else data_points
        avg_recent = sum(p.get('valence', 0) for p in recent) / len(recent)
        if avg_recent > 0.2:
            direction = 'improving'
        elif avg_recent < -0.2:
            direction = 'declining'
        else:
            direction = 'stable'
    else:
        direction = 'stable'
    avg_valence = sum(p.get('valence', 0) for p in data_points) / max(len(data_points), 1)
    return {
        "session_id": session_id,
        "data_points": data_points,
        "average_valence": avg_valence,
        "trend": direction,
    }
