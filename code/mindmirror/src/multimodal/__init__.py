"""多模态处理模块

对外导出：
- VideoProcessingPipeline / PipelineConfig / FrameResult
- WebRTCHandler
- VideoSafetyManager / UserSafetyProfile / ConsentStatus
"""

from src.multimodal.pipeline import (
    FrameResult,
    PipelineConfig,
    VideoProcessingPipeline,
)
from src.multimodal.safety import (
    ConsentStatus,
    UserSafetyProfile,
    VideoSafetyManager,
)
from src.multimodal.webrtc import WebRTCHandler

__all__ = [
    "FrameResult",
    "PipelineConfig",
    "VideoProcessingPipeline",
    "WebRTCHandler",
    "ConsentStatus",
    "UserSafetyProfile",
    "VideoSafetyManager",
]
