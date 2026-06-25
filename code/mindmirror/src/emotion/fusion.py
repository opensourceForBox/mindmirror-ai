"""多模态情绪融合模块

融合视频（面部表情）和音频（语音特征）的情绪识别结果，
输出统一的综合情绪判断，包含危机检测。
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .audio import AudioEmotionResult
from .video import VideoEmotionResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 统一情绪标签（视频 7 类 + 音频 9 类 → 统一 9 类）
# ---------------------------------------------------------------------------

# 视频标签 → 融合标签映射
_VIDEO_TO_UNIFIED: Dict[str, str] = {
    "angry": "angry",
    "disgust": "disgusted",
    "fear": "fearful",
    "happy": "happy",
    "sad": "sad",
    "surprise": "surprised",
    "neutral": "neutral",
}

# 音频标签已在 AudioEmotionAnalyzer.EMOTIONS 中，直接统一

UNIFIED_EMOTIONS: List[str] = [
    "neutral", "happy", "sad", "angry",
    "fearful", "surprised", "disgusted",
    "anxious", "depressed",
]

UNIFIED_EMOTION_CN: Dict[str, str] = {
    "neutral": "平静",
    "happy": "快乐",
    "sad": "悲伤",
    "angry": "愤怒",
    "fearful": "恐惧",
    "surprised": "惊讶",
    "disgusted": "厌恶",
    "anxious": "焦虑",
    "depressed": "抑郁",
}


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------

@dataclass
class FusedEmotionResult:
    """融合后的情绪结果"""

    dominant_emotion: str  # 主要情绪（英文键）
    emotion_scores: Dict[str, float] = field(default_factory=dict)  # 统一情绪分布
    confidence: float = 0.0  # 综合置信度 0-1
    valence: float = 0.0  # 效价 -1~1
    arousal: float = 0.0  # 唤醒度 0-1
    video_weight: float = 0.0  # 视频实际权重
    audio_weight: float = 0.0  # 音频实际权重
    risk_level: str = "low"  # 风险等级 low/medium/high/crisis
    crisis_signals: List[str] = field(default_factory=list)  # 危机信号列表
    source: str = "fused"  # 数据来源 video/audio/fused

    @property
    def dominant_emotion_cn(self) -> str:
        return UNIFIED_EMOTION_CN.get(self.dominant_emotion, "未知")


# ---------------------------------------------------------------------------
# 效价 / 唤醒度映射（统一标签）
# ---------------------------------------------------------------------------

_VALENCE_MAP: Dict[str, float] = {
    "happy": 0.8,
    "surprised": 0.3,
    "neutral": 0.0,
    "sad": -0.7,
    "fearful": -0.6,
    "angry": -0.8,
    "disgusted": -0.9,
    "anxious": -0.4,
    "depressed": -0.8,
}

_AROUSAL_MAP: Dict[str, float] = {
    "angry": 0.9,
    "fearful": 0.8,
    "anxious": 0.7,
    "surprised": 0.7,
    "happy": 0.6,
    "disgusted": 0.5,
    "sad": 0.3,
    "depressed": 0.2,
    "neutral": 0.1,
}


# ---------------------------------------------------------------------------
# 融合引擎
# ---------------------------------------------------------------------------

class EmotionFusion:
    """多模态情绪融合引擎

    融合策略：
    1. 晚融合：分别获取各模态的情绪分数，在分数层面合并
    2. 动态加权：基于各模态置信度和情绪类型调整权重
    3. 冲突处理：当两个模态的主要情绪不一致时的决策规则
    4. 危机检测：任一高置信度危机信号触发风险升级
    """

    # 默认权重（视频略高于音频）
    DEFAULT_VIDEO_WEIGHT: float = 0.6
    DEFAULT_AUDIO_WEIGHT: float = 0.4

    # 情绪优先级规则（特定情绪下调整模态权重）
    EMOTION_PRIORITY: Dict[str, Dict[str, float]] = {
        "anxious": {"video": 0.3, "audio": 0.7},   # 焦虑：音频优先（语音颤抖/语速）
        "depressed": {"video": 0.7, "audio": 0.3},  # 抑郁：视频优先（面部表情）
        "angry": {"video": 0.5, "audio": 0.5},      # 愤怒：平等权重
    }

    # 危机情绪阈值（分数超过此值触发危机信号）
    CRISIS_THRESHOLDS: Dict[str, float] = {
        "sad": 0.8,
        "fearful": 0.85,
        "depressed": 0.7,
    }

    # 危机描述
    _CRISIS_DESCRIPTIONS: Dict[str, str] = {
        "sad": "极高悲伤情绪，可能存在情绪困扰",
        "fearful": "强烈恐惧情绪，可能处于应激状态",
        "depressed": "持续抑郁信号，建议关注心理健康",
    }

    # 低置信度阈值（低于此值认为结果不可靠）
    LOW_CONFIDENCE_THRESHOLD: float = 0.25

    # 冲突置信度差异阈值（差距大于此值时信任高置信模态）
    CONFLICT_CONF_DIFF: float = 0.3

    def __init__(self):
        logger.info("EmotionFusion 引擎初始化")

    # ------------------------------------------------------------------
    # 核心融合方法
    # ------------------------------------------------------------------

    def fuse(
        self,
        video_result: Optional[VideoEmotionResult],
        audio_result: Optional[AudioEmotionResult],
    ) -> FusedEmotionResult:
        """融合视频和音频情绪结果

        支持三种场景：
        - 仅视频：直接使用视频结果
        - 仅音频：直接使用音频结果
        - 双模态：执行加权融合 + 冲突检测 + 危机评估

        Args:
            video_result: 视频情绪结果，可为 None
            audio_result: 音频情绪结果，可为 None

        Returns:
            FusedEmotionResult
        """
        has_video = video_result is not None and video_result.face_detected
        has_audio = audio_result is not None and audio_result.confidence > 0.0

        # 单模态场景
        if has_video and not has_audio:
            return self._from_video_only(video_result)  # type: ignore[arg-type]
        if has_audio and not has_video:
            return self._from_audio_only(audio_result)  # type: ignore[arg-type]

        # 两者均不可用
        if not has_video and not has_audio:
            logger.warning("视频和音频均无有效结果，返回默认")
            return self._default_result()

        # 双模态融合
        return self._fuse_both(video_result, audio_result)  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # 单模态转换
    # ------------------------------------------------------------------

    def _from_video_only(self, vr: VideoEmotionResult) -> FusedEmotionResult:
        """仅视频结果 → 融合结果"""
        unified_scores = self._map_video_scores(vr.emotion_scores)
        dominant = vr.dominant_emotion
        if dominant in _VIDEO_TO_UNIFIED:
            dominant = _VIDEO_TO_UNIFIED[dominant]

        risk_level, crisis_signals = self._detect_crisis(unified_scores, vr.valence)

        return FusedEmotionResult(
            dominant_emotion=dominant,
            emotion_scores=unified_scores,
            confidence=vr.confidence,
            valence=vr.valence,
            arousal=vr.arousal,
            video_weight=1.0,
            audio_weight=0.0,
            risk_level=risk_level,
            crisis_signals=crisis_signals,
            source="video",
        )

    def _from_audio_only(self, ar: AudioEmotionResult) -> FusedEmotionResult:
        """仅音频结果 → 融合结果"""
        scores = {e: ar.emotion_scores.get(e, 0.0) for e in UNIFIED_EMOTIONS}
        total = sum(scores.values())
        if total > 0:
            scores = {k: round(v / total, 4) for k, v in scores.items()}

        risk_level, crisis_signals = self._detect_crisis(scores, ar.valence)

        return FusedEmotionResult(
            dominant_emotion=ar.dominant_emotion,
            emotion_scores=scores,
            confidence=ar.confidence,
            valence=ar.valence,
            arousal=ar.arousal,
            video_weight=0.0,
            audio_weight=1.0,
            risk_level=risk_level,
            crisis_signals=crisis_signals,
            source="audio",
        )

    # ------------------------------------------------------------------
    # 双模态融合
    # ------------------------------------------------------------------

    def _fuse_both(self, vr: VideoEmotionResult, ar: AudioEmotionResult) -> FusedEmotionResult:
        """双模态加权融合"""
        # 1. 动态权重
        vw, aw = self._dynamic_weight(vr, ar)
        logger.debug("动态权重: video=%.2f, audio=%.2f", vw, aw)

        # 2. 统一情绪分数
        video_unified = self._map_video_scores(vr.emotion_scores)
        audio_unified = {e: ar.emotion_scores.get(e, 0.0) for e in UNIFIED_EMOTIONS}

        # 3. 加权合并
        fused_scores: Dict[str, float] = {}
        for emo in UNIFIED_EMOTIONS:
            fused_scores[emo] = round(vw * video_unified.get(emo, 0.0) + aw * audio_unified.get(emo, 0.0), 4)

        # 归一化
        total = sum(fused_scores.values())
        if total > 0:
            fused_scores = {k: round(v / total, 4) for k, v in fused_scores.items()}

        # 4. 冲突处理
        video_dominant = _VIDEO_TO_UNIFIED.get(vr.dominant_emotion, vr.dominant_emotion)
        audio_dominant = ar.dominant_emotion
        if video_dominant != audio_dominant:
            dominant = self._resolve_conflict(
                video_dominant, audio_dominant, vr.confidence, ar.confidence
            )
            logger.debug(
                "模态冲突: video=%s(%.2f) vs audio=%s(%.2f) → %s",
                video_dominant, vr.confidence,
                audio_dominant, ar.confidence,
                dominant,
            )
        else:
            dominant = video_dominant

        # 5. 综合置信度（加权平均）
        confidence = round(vw * vr.confidence + aw * ar.confidence, 4)

        # 6. 效价 / 唤醒度
        valence = round(vw * vr.valence + aw * ar.valence, 4)
        arousal = round(vw * vr.arousal + aw * ar.arousal, 4)
        valence = max(-1.0, min(1.0, valence))
        arousal = max(0.0, min(1.0, arousal))

        # 7. 危机检测
        risk_level, crisis_signals = self._detect_crisis(fused_scores, valence)

        return FusedEmotionResult(
            dominant_emotion=dominant,
            emotion_scores=fused_scores,
            confidence=confidence,
            valence=valence,
            arousal=arousal,
            video_weight=round(vw, 4),
            audio_weight=round(aw, 4),
            risk_level=risk_level,
            crisis_signals=crisis_signals,
            source="fused",
        )

    # ------------------------------------------------------------------
    # 权重计算
    # ------------------------------------------------------------------

    def _dynamic_weight(self, vr: VideoEmotionResult, ar: AudioEmotionResult) -> Tuple[float, float]:
        """基于置信度和情绪优先级动态计算权重

        步骤：
        1. 从置信度计算基础权重（置信度高的模态权重更大）
        2. 应用情绪优先级规则调整
        3. 归一化确保 vw + aw = 1
        """
        # 基础权重：按置信度比例分配
        v_conf = max(vr.confidence, 0.01)
        a_conf = max(ar.confidence, 0.01)

        # 低置信度惩罚
        if vr.confidence < self.LOW_CONFIDENCE_THRESHOLD:
            v_conf *= 0.5
        if ar.confidence < self.LOW_CONFIDENCE_THRESHOLD:
            a_conf *= 0.5

        total_conf = v_conf + a_conf
        vw = v_conf / total_conf * self.DEFAULT_VIDEO_WEIGHT
        aw = a_conf / total_conf * self.DEFAULT_AUDIO_WEIGHT

        # 情绪优先级调整（取视频主导情绪查询优先级表）
        video_emo_unified = _VIDEO_TO_UNIFIED.get(vr.dominant_emotion, vr.dominant_emotion)
        audio_emo = ar.dominant_emotion

        # 优先使用置信度较高的模态的情绪来查优先级
        ref_emotion = video_emo_unified if vr.confidence >= ar.confidence else audio_emo
        priority = self.EMOTION_PRIORITY.get(ref_emotion)
        if priority:
            vw = vw * priority["video"]
            aw = aw * priority["audio"]

        # 归一化
        total = vw + aw
        if total > 0:
            vw = vw / total
            aw = aw / total
        else:
            vw = self.DEFAULT_VIDEO_WEIGHT
            aw = self.DEFAULT_AUDIO_WEIGHT

        return vw, aw

    # ------------------------------------------------------------------
    # 冲突处理
    # ------------------------------------------------------------------

    def _resolve_conflict(
        self,
        video_emotion: str,
        audio_emotion: str,
        video_conf: float,
        audio_conf: float,
    ) -> str:
        """解决模态冲突

        规则：
        1. 置信度差距 > CONFLICT_CONF_DIFF → 信任高置信模态
        2. 任一模态检测到危机情绪（sad/fearful/depressed）→ 取危机情绪（保守原则）
        3. 置信度相近 → 取视频结果（面部表情在冲突时略优先）
        """
        crisis_emotions = {"sad", "fearful", "depressed"}

        # 规则 2：保守原则 — 危机情绪优先
        if video_emotion in crisis_emotions and audio_emotion not in crisis_emotions:
            return video_emotion
        if audio_emotion in crisis_emotions and video_emotion not in crisis_emotions:
            return audio_emotion

        # 规则 1：置信度差距大时信任高置信模态
        conf_diff = abs(video_conf - audio_conf)
        if conf_diff > self.CONFLICT_CONF_DIFF:
            return video_emotion if video_conf > audio_conf else audio_emotion

        # 规则 3：置信度相近 → 视频优先（面部表情在心理学研究中更稳定）
        return video_emotion

    # ------------------------------------------------------------------
    # 危机检测
    # ------------------------------------------------------------------

    def _detect_crisis(self, fused_scores: Dict[str, float], valence: float) -> Tuple[str, List[str]]:
        """检测危机信号

        风险等级：
        - low：无危机信号
        - medium：单一危机情绪超过阈值
        - high：多个危机情绪超过阈值，或极度负面效价
        - crisis：多个严重信号 + 效价极低

        Args:
            fused_scores: 统一情绪分数
            valence: 效价值

        Returns:
            (risk_level, crisis_signals)
        """
        crisis_signals: List[str] = []

        for emotion, threshold in self.CRISIS_THRESHOLDS.items():
            score = fused_scores.get(emotion, 0.0)
            if score >= threshold:
                desc = self._CRISIS_DESCRIPTIONS.get(emotion, f"{emotion} 情绪过高")
                crisis_signals.append(desc)
                logger.warning("危机信号: %s (score=%.2f, threshold=%.2f)", emotion, score, threshold)

        # 极度负面效价也触发
        if valence <= -0.7:
            crisis_signals.append("情绪效价极低，可能存在严重心理困扰")

        # 确定风险等级
        if not crisis_signals:
            risk_level = "low"
        elif len(crisis_signals) == 1 and valence > -0.5:
            risk_level = "medium"
        elif len(crisis_signals) >= 2 or valence <= -0.7:
            # 多信号 + 极低效价 → 可能危机
            if valence <= -0.8 and len(crisis_signals) >= 2:
                risk_level = "crisis"
            else:
                risk_level = "high"
        else:
            risk_level = "medium"

        return risk_level, crisis_signals

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    def _map_video_scores(self, video_scores: Dict[str, float]) -> Dict[str, float]:
        """将视频 7 类情绪分数映射到统一 9 类

        视频缺少 anxious/depressed，这两项设为 0（仅视频时无法判断）。
        """
        unified: Dict[str, float] = {}
        for v_key, u_key in _VIDEO_TO_UNIFIED.items():
            unified[u_key] = video_scores.get(v_key, 0.0)
        # 补充视频不具备的情绪
        for emo in UNIFIED_EMOTIONS:
            if emo not in unified:
                unified[emo] = 0.0
        return unified

    def _default_result(self) -> FusedEmotionResult:
        """默认结果"""
        scores = {e: 0.0 for e in UNIFIED_EMOTIONS}
        scores["neutral"] = 1.0
        return FusedEmotionResult(
            dominant_emotion="neutral",
            emotion_scores=scores,
            confidence=0.0,
            valence=0.0,
            arousal=0.1,
            video_weight=0.0,
            audio_weight=0.0,
            risk_level="low",
            crisis_signals=[],
            source="fused",
        )
