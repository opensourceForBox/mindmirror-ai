"""WebRTC 视频流接入模块

通过 WebSocket 接收前端发送的视频帧（base64 编码的 JPEG），
调用 VideoProcessingPipeline 进行分析并返回情绪结果。
"""

import base64
import binascii
from typing import Optional

import numpy as np
from fastapi import WebSocket

from src.multimodal.pipeline import VideoProcessingPipeline
from src.multimodal.safety import VideoSafetyManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 尝试导入 OpenCV，允许在不安装 OpenCV 的环境下加载模块
try:
    import cv2
    _HAS_CV2 = True
except ImportError:
    _HAS_CV2 = False
    logger.warning("OpenCV 未安装，帧解码功能将受限")


class WebRTCHandler:
    """WebRTC 视频流处理器

    通过 WebSocket 接收前端发送的视频帧（base64 编码的图片）。
    每个 session_id 对应一条 WebSocket 连接和一个处理管道。
    """

    def __init__(
        self,
        pipeline: VideoProcessingPipeline,
        safety_manager: VideoSafetyManager,
    ):
        self.pipeline = pipeline
        self.safety = safety_manager
        self.active_connections: dict[str, WebSocket] = {}   # session_id -> WebSocket
        self._session_user_map: dict[str, str] = {}          # session_id -> user_id
        logger.info("WebRTCHandler 初始化完成")

    # ------------------------------------------------------------------
    # 连接管理
    # ------------------------------------------------------------------

    async def connect(self, websocket: WebSocket, session_id: str, user_id: str):
        """建立 WebSocket 连接

        1. 验证会话有效性
        2. 接受连接
        3. 确保管道已启动
        """
        # 会话验证
        if not self.safety.check_session_validity(session_id):
            await websocket.close(code=4001, reason="会话无效或已过期")
            logger.warning("拒绝连接 | session_id=%s 原因=会话无效", session_id)
            return

        await websocket.accept()
        self.active_connections[session_id] = websocket
        self._session_user_map[session_id] = user_id

        # 确保管道运行中
        if not self.pipeline.is_running:
            await self.pipeline.start()

        logger.info(
            "WebSocket 连接已建立 | session_id=%s user_id=%s",
            session_id, user_id,
        )

    async def disconnect(self, session_id: str):
        """断开连接并清理资源"""
        self.active_connections.pop(session_id, None)
        user_id = self._session_user_map.pop(session_id, None)
        self.safety.close_session(session_id)
        logger.info(
            "WebSocket 连接已断开 | session_id=%s user_id=%s",
            session_id, user_id,
        )

    # ------------------------------------------------------------------
    # 帧处理
    # ------------------------------------------------------------------

    async def handle_frame(self, session_id: str, frame_data: str) -> dict:
        """处理接收到的帧数据

        Args:
            session_id: 会话 ID
            frame_data: base64 编码的 JPEG 图片

        Returns:
            情绪分析结果字典，处理失败返回带 error 字段的字典
        """
        # 会话有效性检查
        if not self.safety.check_session_validity(session_id):
            return {"error": "会话无效或已超时", "code": "SESSION_INVALID"}

        # 解码帧
        frame = self._decode_frame(frame_data)
        if frame is None:
            return {"error": "帧解码失败，请检查图片格式", "code": "DECODE_ERROR"}

        # 权限二次检查
        user_id = self._session_user_map.get(session_id)
        if user_id:
            allowed, reason = self.safety.check_video_permission(user_id)
            if not allowed:
                return {"error": reason, "code": "PERMISSION_DENIED"}

        # 管道处理
        try:
            result = await self.pipeline.process_frame(frame)
        except Exception as exc:
            logger.error("帧处理异常 | session_id=%s err=%s", session_id, exc, exc_info=True)
            return {"error": "帧处理异常", "code": "PROCESS_ERROR"}

        if result is None:
            # 帧被跳过（帧率控制）
            return {
                "type": "skip",
                "message": "帧被跳过（帧率控制）",
                "smoothed_emotion": self.pipeline.get_smoothed_emotion(),
            }

        # 返回结果（仅情绪标签，绝不传输原始帧）
        return {
            "type": "emotion",
            "frame_id": result.frame_id,
            "timestamp": result.timestamp,
            "emotion": result.emotion_result,
            "face_detected": result.face_detected,
            "processing_time_ms": result.processing_time_ms,
            "smoothed_emotion": self.pipeline.get_smoothed_emotion(),
        }

    # ------------------------------------------------------------------
    # 帧解码
    # ------------------------------------------------------------------

    def _decode_frame(self, frame_data: str) -> Optional[np.ndarray]:
        """Base64 → numpy array (BGR)

        支持纯 base64 或 data URI (data:image/jpeg;base64,...)
        """
        try:
            # 处理 data URI
            if "," in frame_data and frame_data.startswith("data:"):
                frame_data = frame_data.split(",", 1)[1]

            raw_bytes = base64.b64decode(frame_data)

            if _HAS_CV2:
                np_arr = np.frombuffer(raw_bytes, dtype=np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if frame is None:
                    logger.warning("cv2.imdecode 返回 None")
                    return None
                return frame
            else:
                # 无 OpenCV 退路：返回原始字节构成的 1D 数组（上层需自行处理）
                logger.warning("无 OpenCV，返回原始字节数组")
                return np.frombuffer(raw_bytes, dtype=np.uint8)

        except binascii.Error as exc:
            logger.error("Base64 解码失败: %s", exc)
            return None
        except Exception as exc:
            logger.error("帧解码异常: %s", exc, exc_info=True)
            return None

    # ------------------------------------------------------------------
    # 状态查询
    # ------------------------------------------------------------------

    @property
    def active_session_count(self) -> int:
        return len(self.active_connections)
