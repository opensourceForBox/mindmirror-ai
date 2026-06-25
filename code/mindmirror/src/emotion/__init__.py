"""情绪识别模块

MindMirror AI 多模态情绪识别系统：
- 视频情绪识别（DeepFace + MediaPipe）
- 音频情绪识别（OpenSMILE + XGBoost）
- 多模态融合引擎
- 统一分析接口

用法::

    from src.emotion import EmotionAnalyzer, FusedEmotionResult

    analyzer = EmotionAnalyzer()
    result: FusedEmotionResult = await analyzer.analyze(video_frame=frame, audio_data=pcm)
"""

from .analyzer import EmotionAnalyzer
from .audio import AudioEmotionAnalyzer, AudioEmotionResult
from .fusion import EmotionFusion, FusedEmotionResult, UNIFIED_EMOTIONS, UNIFIED_EMOTION_CN
from .video import VideoEmotionAnalyzer, VideoEmotionResult

__all__ = [
    # 统一入口
    "EmotionAnalyzer",
    # 视频
    "VideoEmotionAnalyzer",
    "VideoEmotionResult",
    # 音频
    "AudioEmotionAnalyzer",
    "AudioEmotionResult",
    # 融合
    "EmotionFusion",
    "FusedEmotionResult",
    "UNIFIED_EMOTIONS",
    "UNIFIED_EMOTION_CN",
]
