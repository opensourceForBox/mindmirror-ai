"""情绪分析 API 路由

提供图片/音频情绪识别的 REST 端点。
- POST /api/emotion/analyze/image  — 上传图片进行面部情绪分析
- POST /api/emotion/analyze/audio  — 上传音频文件进行语音情绪分析
"""

import logging
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

from src.emotion.analyzer import EmotionAnalyzer
from src.emotion.video import VideoEmotionResult
from src.emotion.audio import AudioEmotionResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/emotion", tags=["emotion"])

# 模块级单例（延迟初始化）
_analyzer: Optional[EmotionAnalyzer] = None


def _get_analyzer() -> EmotionAnalyzer:
    """获取/懒初始化情绪分析器单例"""
    global _analyzer
    if _analyzer is None:
        _analyzer = EmotionAnalyzer()
        logger.info("EmotionAnalyzer 单例已创建")
    return _analyzer


# ---------------------------------------------------------------------------
# 响应模型
# ---------------------------------------------------------------------------

class EmotionResponse(BaseModel):
    """情绪分析响应"""

    dominant_emotion: str = Field(..., description="主要情绪（英文键）")
    dominant_emotion_cn: str = Field("", description="主要情绪（中文）")
    emotion_scores: dict = Field(default_factory=dict, description="各情绪概率分布")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="置信度 0-1")
    valence: float = Field(0.0, ge=-1.0, le=1.0, description="效价 -1~1")
    arousal: float = Field(0.0, ge=0.0, le=1.0, description="唤醒度 0-1")
    risk_level: str = Field("low", description="风险等级 low/medium/high/crisis")
    crisis_signals: list = Field(default_factory=list, description="危机信号列表")
    source: str = Field("unknown", description="数据来源 video/audio/fused")


class ErrorResponse(BaseModel):
    detail: str


# ---------------------------------------------------------------------------
# 图片分析
# ---------------------------------------------------------------------------

@router.post(
    "/analyze/image",
    response_model=EmotionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="分析上传图片的情绪",
    description="上传 JPG/PNG 图片，返回面部表情情绪分析结果",
)
async def analyze_image(file: UploadFile = File(...)):
    """分析上传图片的情绪"""
    # 验证文件类型
    allowed_types = {"image/jpeg", "image/png", "image/bmp", "image/webp"}
    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.content_type}")

    try:
        import cv2

        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="文件内容为空")

        # 解码图片
        arr = np.frombuffer(contents, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is None:
            raise HTTPException(status_code=400, detail="无法解码图片，请确认文件格式正确")

        analyzer = _get_analyzer()
        result: VideoEmotionResult = await analyzer.analyze_video_stream(frame)

        # 转换为融合结果的响应格式（图片只有视频模态）
        from src.emotion.fusion import _VIDEO_TO_UNIFIED, UNIFIED_EMOTIONS

        unified_scores = {}
        for v_key, u_key in _VIDEO_TO_UNIFIED.items():
            unified_scores[u_key] = result.emotion_scores.get(v_key, 0.0)
        for emo in UNIFIED_EMOTIONS:
            if emo not in unified_scores:
                unified_scores[emo] = 0.0

        dominant = _VIDEO_TO_UNIFIED.get(result.dominant_emotion, result.dominant_emotion)

        # 危机检测
        from src.emotion.fusion import EmotionFusion

        fusion = analyzer.fusion_engine
        risk_level, crisis_signals = fusion._detect_crisis(unified_scores, result.valence)

        return EmotionResponse(
            dominant_emotion=dominant,
            dominant_emotion_cn=result.dominant_emotion_cn,
            emotion_scores=unified_scores,
            confidence=result.confidence,
            valence=result.valence,
            arousal=result.arousal,
            risk_level=risk_level,
            crisis_signals=crisis_signals,
            source="video",
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("图片情绪分析失败: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"情绪分析失败: {str(exc)}")


# ---------------------------------------------------------------------------
# 音频分析
# ---------------------------------------------------------------------------

@router.post(
    "/analyze/audio",
    response_model=EmotionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="分析上传音频的情绪",
    description="上传 WAV 音频文件，返回语音情绪分析结果",
)
async def analyze_audio(file: UploadFile = File(...)):
    """分析上传音频文件的情绪"""
    allowed_types = {
        "audio/wav", "audio/x-wav", "audio/wave", "audio/mpeg", "audio/mp3",
        "audio/webm", "audio/ogg", "audio/mp4",
        "audio/webm;codecs=opus", "audio/ogg;codecs=opus",
    }
    allowed_ext = (".wav", ".mp3", ".webm", ".ogg", ".mp4", ".m4a")
    if file.content_type and file.content_type not in allowed_types and not (file.filename and file.filename.endswith(allowed_ext)):
        raise HTTPException(status_code=400, detail=f"不支持的音频类型: {file.content_type}")

    tmp_path = None
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="文件内容为空")

        # 写临时文件
        # 根据文件名推断后缀
        fname = file.filename or "recording.wav"
        if fname.endswith(".mp3"):
            suffix = ".mp3"
        elif fname.endswith(".webm"):
            suffix = ".webm"
        elif fname.endswith(".ogg"):
            suffix = ".ogg"
        elif fname.endswith(".mp4") or fname.endswith(".m4a"):
            suffix = ".mp4"
        else:
            suffix = ".wav"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        analyzer = _get_analyzer()
        result: AudioEmotionResult = await analyzer.analyze_audio_file(tmp_path)

        # 危机检测
        fusion = analyzer.fusion_engine
        from src.emotion.fusion import UNIFIED_EMOTIONS

        scores = {e: result.emotion_scores.get(e, 0.0) for e in UNIFIED_EMOTIONS}
        total = sum(scores.values())
        if total > 0:
            scores = {k: round(v / total, 4) for k, v in scores.items()}

        risk_level, crisis_signals = fusion._detect_crisis(scores, result.valence)

        return EmotionResponse(
            dominant_emotion=result.dominant_emotion,
            dominant_emotion_cn=result.dominant_emotion_cn,
            emotion_scores=scores,
            confidence=result.confidence,
            valence=result.valence,
            arousal=result.arousal,
            risk_level=risk_level,
            crisis_signals=crisis_signals,
            source="audio",
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("音频情绪分析失败: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"情绪分析失败: {str(exc)}")
    finally:
        if tmp_path:
            try:
                Path(tmp_path).unlink()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# 健康检查（模块级）
# ---------------------------------------------------------------------------

@router.get("/health", summary="情绪模块健康检查")
async def emotion_health():
    """情绪模块健康检查"""
    analyzer = _get_analyzer()
    from src.emotion.video import _get_deepface, _get_mediapipe_detector

    df = _get_deepface()
    mp = _get_mediapipe_detector()
    from src.emotion.audio import _get_opensmile

    smile = _get_opensmile()

    return {
        "status": "ok",
        "deepface_available": df is not None,
        "mediapipe_available": mp is not None,
        "opensmile_available": smile is not None,
        "xgboost_model_loaded": analyzer.audio_analyzer._model is not None,
    }
