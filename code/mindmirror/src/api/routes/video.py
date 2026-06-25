"""视频流 WebSocket API

协议：
- 客户端发送：{"type": "frame", "data": "base64_jpeg_data"}
- 服务端回复：{"type": "emotion", "data": {...emotion_result...}}
- 客户端发送：{"type": "stop"} 停止分析
"""

import json
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel

from src.multimodal.pipeline import PipelineConfig, VideoProcessingPipeline
from src.multimodal.safety import VideoSafetyManager
from src.multimodal.webrtc import WebRTCHandler
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/video", tags=["video"])

# ---------------------------------------------------------------------------
# 模块级单例（按需初始化）
# ---------------------------------------------------------------------------

_safety_manager: Optional[VideoSafetyManager] = None
_handler: Optional[WebRTCHandler] = None


def _get_safety_manager() -> VideoSafetyManager:
    global _safety_manager
    if _safety_manager is None:
        _safety_manager = VideoSafetyManager()
    return _safety_manager


def _get_handler() -> WebRTCHandler:
    global _handler
    if _handler is None:
        pipeline = VideoProcessingPipeline(PipelineConfig())
        _handler = WebRTCHandler(pipeline=pipeline, safety_manager=_get_safety_manager())
    return _handler


# ---------------------------------------------------------------------------
# Pydantic 请求模型
# ---------------------------------------------------------------------------

class VideoPermissionRequest(BaseModel):
    user_id: str
    age: int
    parental_consent: bool = False


class ConsentVerifyRequest(BaseModel):
    user_id: str
    consent_code: str


class ConsentGenerateRequest(BaseModel):
    user_id: str
    parent_email: str


# ---------------------------------------------------------------------------
# WebSocket 端点
# ---------------------------------------------------------------------------

@router.websocket("/stream/{session_id}")
async def video_stream(websocket: WebSocket, session_id: str):
    """视频流 WebSocket 端点

    客户端需在连接时通过 query 参数提供 user_id：
    /api/video/stream/{session_id}?user_id=xxx
    """
    user_id: Optional[str] = websocket.query_params.get("user_id")
    if not user_id:
        await websocket.close(code=4000, reason="缺少 user_id 参数")
        return

    handler = _get_handler()
    safety = _get_safety_manager()

    # 建立连接（内部会校验会话有效性）
    await handler.connect(websocket, session_id, user_id)
    if session_id not in handler.active_connections:
        # connect 拒绝了连接
        return

    logger.info("视频流开始 | session_id=%s user_id=%s", session_id, user_id)

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "无效的 JSON 格式", "code": "INVALID_JSON"})
                continue

            msg_type = message.get("type", "")

            if msg_type == "frame":
                frame_data = message.get("data", "")
                if not frame_data:
                    await websocket.send_json({"error": "缺少帧数据", "code": "MISSING_DATA"})
                    continue
                result = await handler.handle_frame(session_id, frame_data)
                await websocket.send_json(result)

            elif msg_type == "stop":
                await websocket.send_json({"type": "stopped", "message": "分析已停止"})
                logger.info("收到停止信号 | session_id=%s", session_id)
                break

            elif msg_type == "ping":
                # 心跳保活
                valid = safety.check_session_validity(session_id)
                await websocket.send_json({"type": "pong", "session_valid": valid})

            else:
                await websocket.send_json({
                    "error": f"未知消息类型: {msg_type}",
                    "code": "UNKNOWN_TYPE",
                })

    except WebSocketDisconnect:
        logger.info("WebSocket 断开 | session_id=%s", session_id)
    except Exception as exc:
        logger.error("WebSocket 异常 | session_id=%s err=%s", session_id, exc, exc_info=True)
        try:
            await websocket.send_json({"error": "服务器内部错误", "code": "INTERNAL_ERROR"})
        except Exception:
            pass
    finally:
        await handler.disconnect(session_id)


# ---------------------------------------------------------------------------
# REST 端点
# ---------------------------------------------------------------------------

@router.post("/permission")
async def request_video_permission(request: VideoPermissionRequest):
    """请求视频处理权限（注册用户并进行年龄/家长同意检查）"""
    safety = _get_safety_manager()
    profile = safety.register_user(
        user_id=request.user_id,
        age=request.age,
        parental_consent=request.parental_consent,
    )
    allowed, reason = safety.check_video_permission(request.user_id)
    return {
        "user_id": request.user_id,
        "allowed": allowed,
        "reason": reason,
        "is_minor": profile.is_minor,
        "consent_status": profile.parental_consent.value,
    }


@router.post("/consent/generate")
async def generate_consent(request: ConsentGenerateRequest):
    """为未成年用户生成家长同意验证码"""
    safety = _get_safety_manager()
    try:
        code = safety.generate_consent_request(request.user_id, request.parent_email)
        return {
            "user_id": request.user_id,
            "consent_code": code,
            "message": "验证码已生成，请发送给家长进行验证",
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/consent/verify")
async def verify_consent(request: ConsentVerifyRequest):
    """验证家长同意验证码"""
    safety = _get_safety_manager()
    success = safety.verify_parental_consent(request.user_id, request.consent_code)
    if success:
        return {"user_id": request.user_id, "verified": True, "message": "家长同意已验证"}
    raise HTTPException(status_code=400, detail="验证码无效或不匹配")


@router.post("/session")
async def create_video_session(user_id: str):
    """创建视频处理会话"""
    safety = _get_safety_manager()
    try:
        session_id = safety.create_session(user_id)
        return {"session_id": session_id, "user_id": user_id}
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))


@router.get("/policy")
async def get_data_policy():
    """获取数据处理政策"""
    safety = _get_safety_manager()
    return safety.get_data_policy()


@router.get("/logs/{user_id}")
async def get_access_logs(user_id: str, limit: int = 50):
    """获取用户数据访问审计日志"""
    safety = _get_safety_manager()
    return {"user_id": user_id, "logs": safety.get_access_logs(user_id, limit)}
