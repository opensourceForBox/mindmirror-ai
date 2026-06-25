"""音频情绪识别模块 — 基于 OpenSMILE + XGBoost

提供 WAV 文件和 numpy 音频流的情绪分析，OpenSMILE 不可用时降级到规则分析。
"""

import logging
import tempfile
import wave
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 延迟导入
# ---------------------------------------------------------------------------
_OPENSMILE_AVAILABLE: Optional[bool] = None
_SMILE: Optional[object] = None


def _get_opensmile():
    """延迟加载 OpenSMILE（eGeMAPS 特征集，88 维）"""
    global _OPENSMILE_AVAILABLE, _SMILE
    if _OPENSMILE_AVAILABLE is None:
        try:
            import opensmile

            _SMILE = opensmile.Smile(
                feature_set=opensmile.FeatureSet.eGeMAPSv02,
                feature_level=opensmile.FeatureLevel.Functionals,
            )
            _OPENSMILE_AVAILABLE = True
            logger.info("OpenSMILE eGeMAPS 加载成功")
        except Exception as exc:
            _OPENSMILE_AVAILABLE = False
            logger.warning("OpenSMILE 不可用 (%s)，将使用规则分析", exc)
    return _SMILE if _OPENSMILE_AVAILABLE else None


_XGB_AVAILABLE: Optional[bool] = None


def _check_xgboost():
    global _XGB_AVAILABLE
    if _XGB_AVAILABLE is None:
        try:
            import xgboost  # noqa: F401

            _XGB_AVAILABLE = True
        except ImportError:
            _XGB_AVAILABLE = False
    return _XGB_AVAILABLE


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------

@dataclass
class AudioEmotionResult:
    """音频情绪识别结果"""

    dominant_emotion: str  # 主要情绪（英文键）
    emotion_scores: Dict[str, float] = field(default_factory=dict)  # 各情绪概率
    confidence: float = 0.0  # 置信度 0-1
    valence: float = 0.0  # 效价 -1~1
    arousal: float = 0.0  # 唤醒度 0-1
    speech_rate: Optional[float] = None  # 语速（估计，音节/秒）
    pitch_mean: Optional[float] = None  # 平均音调 Hz
    energy: Optional[float] = None  # RMS 能量

    @property
    def dominant_emotion_cn(self) -> str:
        return AudioEmotionAnalyzer.EMOTION_MAP_CN.get(self.dominant_emotion, "未知")


# ---------------------------------------------------------------------------
# 分析器
# ---------------------------------------------------------------------------

class AudioEmotionAnalyzer:
    """音频情绪分析器

    使用 OpenSMILE 提取 eGeMAPS 特征 + XGBoost 分类，
    无模型时退化为基于特征统计的规则分析。
    """

    EMOTIONS: List[str] = [
        "neutral", "happy", "sad", "angry",
        "fearful", "surprised", "disgusted",
        "anxious", "depressed",
    ]

    EMOTION_MAP_CN: Dict[str, str] = {
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

    # 效价 / 唤醒度映射
    _VALENCE_MAP: Dict[str, float] = {
        "happy": 0.8, "surprised": 0.3, "neutral": 0.0,
        "sad": -0.7, "fearful": -0.6, "angry": -0.8,
        "disgusted": -0.9, "anxious": -0.4, "depressed": -0.8,
    }
    _AROUSAL_MAP: Dict[str, float] = {
        "angry": 0.9, "fearful": 0.8, "anxious": 0.7,
        "surprised": 0.7, "happy": 0.6, "disgusted": 0.5,
        "sad": 0.3, "depressed": 0.2, "neutral": 0.1,
    }

    def __init__(self, model_path: Optional[Path] = None):
        """初始化音频分析器

        Args:
            model_path: XGBoost 模型路径（可选，无模型时使用规则方法）
        """
        self._model = None
        if model_path and Path(model_path).exists() and _check_xgboost():
            try:
                import xgboost as xgb

                self._model = xgb.Booster()
                self._model.load_model(str(model_path))
                logger.info("XGBoost 模型已加载: %s", model_path)
            except Exception as exc:
                logger.warning("XGBoost 模型加载失败 (%s)，使用规则分析", exc)
        else:
            if model_path:
                logger.warning("模型路径无效或 XGBoost 未安装，使用规则分析")

    # ------------------------------------------------------------------
    # 公开方法
    # ------------------------------------------------------------------

    def analyze_file(self, audio_path: str) -> AudioEmotionResult:
        """分析音频文件

        Args:
            audio_path: WAV 文件路径

        Returns:
            AudioEmotionResult
        """
        try:
            features = self.extract_features(audio_path)
            if features is None:
                logger.warning("特征提取失败，返回默认结果: %s", audio_path)
                return self._default_result()
            return self._classify(features)
        except Exception as exc:
            logger.error("音频文件分析失败 (%s): %s", audio_path, exc, exc_info=True)
            return self._default_result()

    def analyze_stream(self, audio_data: np.ndarray, sample_rate: int = 16000) -> AudioEmotionResult:
        """分析音频流数据（numpy array）

        Args:
            audio_data: 单声道 float/int PCM 数据
            sample_rate: 采样率（默认 16 kHz）

        Returns:
            AudioEmotionResult
        """
        try:
            # 写临时 WAV 文件供 OpenSMILE 读取
            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp_path = tmp.name
                self._array_to_wav(audio_data, sample_rate, tmp_path)
                return self.analyze_file(tmp_path)
            finally:
                if tmp_path:
                    try:
                        Path(tmp_path).unlink()
                    except OSError:
                        pass
        except Exception as exc:
            logger.error("音频流分析失败: %s", exc, exc_info=True)
            return self._default_result()

    def extract_features(self, audio_path: str) -> Optional[np.ndarray]:
        """提取 eGeMAPS 特征向量

        Args:
            audio_path: WAV 文件路径

        Returns:
            88 维特征向量，OpenSMILE 不可用时返回基于 librosa/简单统计的备选特征
        """
        smile = _get_opensmile()
        if smile is not None:
            try:
                import pandas as pd  # OpenSMILE 返回 DataFrame

                df = smile.process_file(audio_path)
                if df is not None and not df.empty:
                    features = df.iloc[0].values.astype(np.float64)
                    logger.debug("eGeMAPS 特征维度: %d", len(features))
                    return features
            except Exception as exc:
                logger.warning("OpenSMILE 特征提取失败: %s", exc)

        # 备选：基于 wave 模块提取简单统计特征
        return self._extract_simple_features(audio_path)

    # ------------------------------------------------------------------
    # 内部分类
    # ------------------------------------------------------------------

    def _classify(self, features: np.ndarray) -> AudioEmotionResult:
        """根据特征选择分类方式：XGBoost 模型 / 规则分析"""
        if self._model is not None:
            try:
                return self._model_classify(features)
            except Exception as exc:
                logger.warning("模型分类失败，降级到规则分析: %s", exc)
        return self._rule_based_analysis(features)

    def _model_classify(self, features: np.ndarray) -> AudioEmotionResult:
        """使用 XGBoost 模型进行分类"""
        import xgboost as xgb

        # 对齐特征维度（模型可能期望特定维度）
        dmatrix = xgb.DMatrix(features.reshape(1, -1))
        raw_preds = self._model.predict(dmatrix)

        # softmax 归一化
        exp_preds = np.exp(raw_preds[0] - np.max(raw_preds[0]))
        probs = exp_preds / exp_preds.sum()

        # 对齐 EMOTIONS 列表（截断或补零）
        n_emotions = len(self.EMOTIONS)
        if len(probs) >= n_emotions:
            probs = probs[:n_emotions]
        else:
            probs = np.pad(probs, (0, n_emotions - len(probs)))

        # 归一化
        total = probs.sum()
        if total > 0:
            probs = probs / total

        scores = {emo: round(float(p), 4) for emo, p in zip(self.EMOTIONS, probs)}
        dominant = max(scores, key=scores.get)  # type: ignore[arg-type]
        valence, arousal = self._calculate_valence_arousal(scores)

        return AudioEmotionResult(
            dominant_emotion=dominant,
            emotion_scores=scores,
            confidence=round(scores[dominant], 4),
            valence=round(valence, 4),
            arousal=round(arousal, 4),
        )

    def _rule_based_analysis(self, features: np.ndarray) -> AudioEmotionResult:
        """基于规则的情绪分析（无模型时的备选方案）

        使用 eGeMAPS / 简单特征的统计特性进行规则判断：
        - 高音调 + 高能量 → 愤怒/兴奋
        - 低音调 + 低能量 → 悲伤/抑郁
        - 高语速 → 焦虑
        - 正常范围 → 平静

        features 向量说明（eGeMAPS 88维 / 简单备选特征）：
        - eGeMAPS：前几个维度包含 F0、能量、频谱等统计量
        - 简单特征：[pitch_mean, energy_rms, zcr_mean, duration, spectral_centroid]
        """
        # 提取关键统计量（兼容两种特征格式）
        if len(features) >= 88:
            # eGeMAPS：索引参考 opensmile 文档
            # F0 相关特征通常在前 10 维内
            pitch_proxy = float(np.mean(np.abs(features[:10])))
            energy_proxy = float(np.mean(np.abs(features[10:30])))
            rate_proxy = float(np.mean(np.abs(features[30:50])))
        elif len(features) >= 5:
            pitch_proxy = float(features[0])
            energy_proxy = float(features[1])
            rate_proxy = float(features[4])  # spectral centroid 近似语速
        else:
            pitch_proxy = float(np.mean(np.abs(features)))
            energy_proxy = float(np.std(features))
            rate_proxy = 0.0

        # 归一化（简单 min-max 到 [0,1] 区间，使用经验阈值）
        pitch_norm = min(pitch_proxy / 300.0, 1.0) if pitch_proxy > 0 else 0.0
        energy_norm = min(energy_proxy / 1.0, 1.0) if energy_proxy > 0 else 0.0

        # 规则判断
        scores: Dict[str, float] = {e: 0.0 for e in self.EMOTIONS}

        if pitch_norm > 0.7 and energy_norm > 0.7:
            # 高音调 + 高能量 → 愤怒/惊讶
            scores["angry"] = 0.45
            scores["surprised"] = 0.30
            scores["happy"] = 0.15
            scores["fearful"] = 0.10
        elif pitch_norm < 0.3 and energy_norm < 0.3:
            # 低音调 + 低能量 → 悲伤/抑郁
            scores["sad"] = 0.40
            scores["depressed"] = 0.35
            scores["neutral"] = 0.20
            scores["fearful"] = 0.05
        elif rate_proxy > 0.6:
            # 高语速 → 焦虑/兴奋
            scores["anxious"] = 0.45
            scores["happy"] = 0.25
            scores["fearful"] = 0.20
            scores["surprised"] = 0.10
        elif pitch_norm > 0.5 and energy_norm > 0.4:
            # 中等偏高 → 快乐/惊讶
            scores["happy"] = 0.50
            scores["surprised"] = 0.25
            scores["neutral"] = 0.15
            scores["angry"] = 0.10
        else:
            # 正常范围 → 平静
            scores["neutral"] = 0.65
            scores["happy"] = 0.15
            scores["sad"] = 0.10
            scores["anxious"] = 0.10

        # 归一化
        total = sum(scores.values())
        if total > 0:
            scores = {k: round(v / total, 4) for k, v in scores.items()}

        dominant = max(scores, key=scores.get)  # type: ignore[arg-type]
        valence, arousal = self._calculate_valence_arousal(scores)

        return AudioEmotionResult(
            dominant_emotion=dominant,
            emotion_scores=scores,
            confidence=round(scores[dominant], 4),
            valence=round(valence, 4),
            arousal=round(arousal, 4),
            pitch_mean=round(pitch_proxy, 2),
            energy=round(energy_proxy, 4),
        )

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    def _extract_simple_features(self, audio_path: str) -> Optional[np.ndarray]:
        """简单特征提取（OpenSMILE 不可用时的备选）

        返回 5 维特征：[pitch_mean, energy_rms, zcr_mean, duration_s, spectral_centroid]
        """
        try:
            with wave.open(audio_path, "rb") as wf:
                n_frames = wf.getnframes()
                sample_rate = wf.getframerate()
                raw = wf.readframes(n_frames)
                audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
                audio = audio / 32768.0  # 归一化到 [-1, 1]
        except Exception as exc:
            logger.warning("wave 模块读取失败: %s", exc)
            return None

        duration = len(audio) / sample_rate if sample_rate > 0 else 0.0
        energy_rms = float(np.sqrt(np.mean(audio ** 2)))
        zcr = float(np.mean(np.diff(np.sign(audio)) != 0))

        # 简单 pitch 估计（自相关峰值）
        pitch = self._estimate_pitch(audio, sample_rate)

        # 频谱质心
        fft = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), 1.0 / sample_rate)
        total_fft = fft.sum()
        spectral_centroid = float((freqs * fft).sum() / total_fft) if total_fft > 0 else 0.0

        features = np.array([pitch, energy_rms, zcr, duration, spectral_centroid], dtype=np.float64)
        logger.debug("简单特征: %s", features)
        return features

    @staticmethod
    def _estimate_pitch(audio: np.ndarray, sample_rate: int, f0_min: float = 75.0, f0_max: float = 500.0) -> float:
        """自相关法简单 pitch 估计"""
        try:
            min_lag = int(sample_rate / f0_max)
            max_lag = int(sample_rate / f0_min)
            if max_lag >= len(audio):
                max_lag = len(audio) - 1
            if min_lag >= max_lag:
                return 0.0

            corr = np.correlate(audio[:max_lag * 2], audio[:max_lag * 2], mode="full")
            corr = corr[len(corr) // 2:]
            segment = corr[min_lag:max_lag]
            if segment.size == 0:
                return 0.0
            peak = np.argmax(segment) + min_lag
            return float(sample_rate / peak) if peak > 0 else 0.0
        except Exception:
            return 0.0

    @staticmethod
    def _array_to_wav(audio_data: np.ndarray, sample_rate: int, path: str) -> None:
        """将 numpy 数组写为 WAV 文件"""
        # 确保是 int16
        if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
            audio_int = np.clip(audio_data * 32768, -32768, 32767).astype(np.int16)
        elif audio_data.dtype != np.int16:
            audio_int = audio_data.astype(np.int16)
        else:
            audio_int = audio_data

        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_int.tobytes())

    def _calculate_valence_arousal(self, scores: Dict[str, float]) -> Tuple[float, float]:
        """加权计算效价和唤醒度"""
        valence = sum(s * self._VALENCE_MAP.get(e, 0.0) for e, s in scores.items())
        arousal = sum(s * self._AROUSAL_MAP.get(e, 0.0) for e, s in scores.items())
        return max(-1.0, min(1.0, valence)), max(0.0, min(1.0, arousal))

    def _default_result(self) -> AudioEmotionResult:
        """返回默认结果"""
        scores = {e: 0.0 for e in self.EMOTIONS}
        scores["neutral"] = 1.0
        return AudioEmotionResult(
            dominant_emotion="neutral",
            emotion_scores=scores,
            confidence=0.0,
            valence=0.0,
            arousal=0.1,
        )
