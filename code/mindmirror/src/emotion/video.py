"""视频情绪识别模块 — 基于 DeepFace + MediaPipe

提供单帧/批量帧的面部表情情绪分析，支持多人脸处理、低光照容错。
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# DeepFace 延迟导入标志
_DEEPFACE_AVAILABLE: Optional[bool] = None
_DEEPFACE = None


def _get_deepface():
    """延迟加载 DeepFace，避免模块导入时阻塞"""
    global _DEEPFACE_AVAILABLE, _DEEPFACE
    if _DEEPFACE_AVAILABLE is None:
        try:
            from deepface import DeepFace as _df

            _DEEPFACE = _df
            _DEEPFACE_AVAILABLE = True
            logger.info("DeepFace 加载成功")
        except ImportError:
            _DEEPFACE_AVAILABLE = False
            logger.warning("DeepFace 未安装，视频情绪识别将使用降级模式")
    return _DEEPFACE if _DEEPFACE_AVAILABLE else None


# ---------------------------------------------------------------------------
# MediaPipe 人脸检测（用于快速定位人脸区域）
# ---------------------------------------------------------------------------
_MEDIAPIPE_AVAILABLE: Optional[bool] = None
_MP_FACE_DETECTION = None


def _get_mediapipe_detector():
    """延迟加载 MediaPipe 人脸检测器"""
    global _MEDIAPIPE_AVAILABLE, _MP_FACE_DETECTION
    if _MEDIAPIPE_AVAILABLE is None:
        try:
            import mediapipe as mp

            _MP_FACE_DETECTION = mp.solutions.face_detection.FaceDetection(
                model_selection=1, min_detection_confidence=0.5
            )
            _MEDIAPIPE_AVAILABLE = True
            logger.info("MediaPipe 人脸检测器加载成功")
        except Exception as exc:
            _MEDIAPIPE_AVAILABLE = False
            logger.warning("MediaPipe 加载失败 (%s)，将使用 OpenCV Haar 级联", exc)
    return _MP_FACE_DETECTION if _MEDIAPIPE_AVAILABLE else None


# OpenCV Haar 级联备用检测器
_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
_HAAR_CASCADE = cv2.CascadeClassifier(_CASCADE_PATH)


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------

@dataclass
class VideoEmotionResult:
    """视频情绪识别结果"""

    dominant_emotion: str  # 主要情绪（英文键）
    emotion_scores: Dict[str, float] = field(default_factory=dict)  # 各情绪概率
    confidence: float = 0.0  # 置信度 0-1
    valence: float = 0.0  # 效价 -1~1
    arousal: float = 0.0  # 唤醒度 0-1
    face_detected: bool = False  # 是否检测到人脸
    face_region: Optional[Tuple[int, int, int, int]] = None  # (x, y, w, h)

    @property
    def dominant_emotion_cn(self) -> str:
        """主要情绪的中文翻译"""
        return VideoEmotionAnalyzer.EMOTION_MAP.get(self.dominant_emotion, "未知")


# ---------------------------------------------------------------------------
# 分析器
# ---------------------------------------------------------------------------

class VideoEmotionAnalyzer:
    """视频情绪分析器

    使用 DeepFace 进行面部表情识别，MediaPipe / OpenCV Haar 进行人脸检测。
    """

    EMOTION_MAP: Dict[str, str] = {
        "angry": "愤怒",
        "disgust": "厌恶",
        "fear": "恐惧",
        "happy": "快乐",
        "sad": "悲伤",
        "surprise": "惊讶",
        "neutral": "平静",
    }

    # 效价（正=积极，负=消极）
    VALENCE_MAP: Dict[str, float] = {
        "happy": 0.8,
        "surprise": 0.3,
        "neutral": 0.0,
        "sad": -0.7,
        "fear": -0.6,
        "angry": -0.8,
        "disgust": -0.9,
    }

    # 唤醒度（高=激动，低=平静）
    AROUSAL_MAP: Dict[str, float] = {
        "angry": 0.9,
        "fear": 0.8,
        "surprise": 0.7,
        "happy": 0.6,
        "disgust": 0.5,
        "sad": 0.3,
        "neutral": 0.1,
    }

    # DeepFace 支持的模型（按精度/速度平衡选择）
    _PREFERRED_MODELS = ["Facenet512", "VGG-Face"]
    _DEFAULT_MODEL = "VGG-Face"

    def __init__(self, model_name: Optional[str] = None):
        """初始化视频情绪分析器

        Args:
            model_name: DeepFace 模型名称，默认自动选择
        """
        self._model_name = model_name or self._DEFAULT_MODEL
        logger.info("VideoEmotionAnalyzer 初始化，模型: %s", self._model_name)

    # ------------------------------------------------------------------
    # 公开方法
    # ------------------------------------------------------------------

    def analyze_frame(self, frame: np.ndarray) -> VideoEmotionResult:
        """分析单帧图像的情绪

        Args:
            frame: BGR 格式的 OpenCV 图像帧

        Returns:
            VideoEmotionResult，无人脸时返回 face_detected=False 的默认结果
        """
        if frame is None or frame.size == 0:
            logger.warning("收到空帧，返回默认结果")
            return self._default_result()

        # 预处理：低光照增强
        processed_frame = self._preprocess_frame(frame)

        # 1. 人脸检测 —— 优先 MediaPipe，失败则用 Haar
        face_region = self._detect_face(processed_frame)

        # 2. DeepFace 情绪识别
        df = _get_deepface()
        if df is None:
            # DeepFace 不可用，返回仅含人脸检测信息的结果
            return VideoEmotionResult(
                dominant_emotion="neutral",
                emotion_scores={e: 0.0 for e in self.EMOTION_MAP},
                confidence=0.0,
                face_detected=face_region is not None,
                face_region=face_region,
            )

        try:
            result = self._run_deepface(df, processed_frame, face_region)
            if result is not None:
                return result
        except Exception as exc:
            logger.error("DeepFace 分析失败: %s", exc, exc_info=True)

        # 兜底：返回默认结果
        fallback = self._default_result()
        fallback.face_detected = face_region is not None
        fallback.face_region = face_region
        return fallback

    def analyze_frame_batch(self, frames: List[np.ndarray]) -> List[VideoEmotionResult]:
        """批量分析多帧，返回每帧的结果列表

        Args:
            frames: BGR 图像帧列表

        Returns:
            与输入帧一一对应的 VideoEmotionResult 列表
        """
        results: List[VideoEmotionResult] = []
        for frame in frames:
            results.append(self.analyze_frame(frame))
        return results

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    def _run_deepface(
        self, df, frame: np.ndarray, face_region: Optional[Tuple[int, int, int, int]]
    ) -> Optional[VideoEmotionResult]:
        """执行 DeepFace 分析并封装结果

        尝试使用指定人脸区域裁剪后分析；若未指定则让 DeepFace 自动检测。
        """
        import tempfile, os

        # DeepFace.analyze 需要文件路径，使用临时文件
        tmp_path = None
        try:
            img_to_use = frame
            if face_region is not None:
                x, y, w, h = face_region
                # 加 padding 避免裁剪过紧
                fh, fw = frame.shape[:2]
                pad = int(0.2 * max(w, h))
                x1 = max(0, x - pad)
                y1 = max(0, y - pad)
                x2 = min(fw, x + w + pad)
                y2 = min(fh, y + h + pad)
                img_to_use = frame[y1:y2, x1:x2]

            # 写临时文件
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp_path = tmp.name
            cv2.imwrite(tmp_path, img_to_use)

            analysis = df.analyze(
                img_path=tmp_path,
                actions=["emotion"],
                models=[self._model_name],
                enforce_detection=False,
                silent=True,
            )

            # DeepFace 返回 list（多人脸）或 dict（单人脸）
            if isinstance(analysis, list):
                if not analysis:
                    return None
                # 取第一个人脸（最大人脸，由 DeepFace 内部排序）
                analysis = analysis[0]

            emotion_data = analysis.get("emotion", {})
            dominant = analysis.get("dominant_emotion", "neutral")

            # DeepFace 输出的 key 与 EMOTION_MAP 对齐
            scores: Dict[str, float] = {}
            for emo_key in self.EMOTION_MAP:
                # DeepFace 使用 'neutral' / 'sad' 等，基本一致
                raw_score = emotion_data.get(emo_key, 0.0)
                scores[emo_key] = round(float(raw_score) / 100.0, 4)

            # 归一化（确保总和为 1）
            total = sum(scores.values())
            if total > 0:
                scores = {k: round(v / total, 4) for k, v in scores.items()}

            dominant = dominant.lower() if isinstance(dominant, str) else "neutral"
            if dominant not in self.EMOTION_MAP:
                dominant = max(scores, key=scores.get)  # type: ignore[arg-type]

            confidence = scores.get(dominant, 0.0)
            valence, arousal = self._calculate_valence_arousal(scores)

            return VideoEmotionResult(
                dominant_emotion=dominant,
                emotion_scores=scores,
                confidence=round(confidence, 4),
                valence=round(valence, 4),
                arousal=round(arousal, 4),
                face_detected=True,
                face_region=face_region,
            )
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

    def _detect_face(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """检测帧中最大人脸，返回 (x, y, w, h)；未检测到返回 None"""
        # 尝试 MediaPipe
        mp_det = _get_mediapipe_detector()
        if mp_det is not None:
            try:
                import mediapipe as mp

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = mp_det.process(rgb)
                if results.detections:
                    # 选最大人脸
                    best = max(
                        results.detections,
                        key=lambda d: d.location_data.relative_bounding_box.width
                        * d.location_data.relative_bounding_box.height,
                    )
                    bb = best.location_data.relative_bounding_box
                    fh, fw = frame.shape[:2]
                    x = int(bb.xmin * fw)
                    y = int(bb.ymin * fh)
                    w = int(bb.width * fw)
                    h = int(bb.height * fh)
                    return (max(0, x), max(0, y), w, h)
            except Exception as exc:
                logger.debug("MediaPipe 检测异常: %s", exc)

        # 备用：OpenCV Haar 级联
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = _HAAR_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            if len(faces) == 0:
                return None
            # 取最大人脸
            largest = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = largest
            return (int(x), int(y), int(w), int(h))
        except Exception as exc:
            logger.debug("Haar 检测异常: %s", exc)
            return None

    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """低光照 / 模糊帧预处理

        - 低光照：CLAHE 自适应直方图均衡
        - 模糊：轻度锐化
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mean_brightness = gray.mean()

            if mean_brightness < 60:
                # CLAHE 增强亮度
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                enhanced_gray = clahe.apply(gray)
                # 转回 BGR
                enhanced = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)
                logger.debug("低光照增强已应用 (mean=%d)", mean_brightness)
                return enhanced

            # 轻度锐化（拉普拉斯核）
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            if blur_score < 50:
                kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
                sharpened = cv2.filter2D(frame, -1, kernel)
                logger.debug("模糊帧锐化已应用 (laplacian_var=%.1f)", blur_score)
                return sharpened
        except Exception as exc:
            logger.debug("预处理异常，使用原始帧: %s", exc)

        return frame

    def _calculate_valence_arousal(self, emotion_scores: Dict[str, float]) -> Tuple[float, float]:
        """根据情绪分数加权计算效价和唤醒度

        公式：valence = Σ(score_i * valence_i)，arousal = Σ(score_i * arousal_i)
        """
        valence = sum(
            score * self.VALENCE_MAP.get(emo, 0.0) for emo, score in emotion_scores.items()
        )
        arousal = sum(
            score * self.AROUSAL_MAP.get(emo, 0.0) for emo, score in emotion_scores.items()
        )
        # 钳位
        valence = max(-1.0, min(1.0, valence))
        arousal = max(0.0, min(1.0, arousal))
        return valence, arousal

    def _default_result(self) -> VideoEmotionResult:
        """返回无人脸 / 分析失败时的默认结果"""
        scores = {e: 0.0 for e in self.EMOTION_MAP}
        scores["neutral"] = 1.0
        return VideoEmotionResult(
            dominant_emotion="neutral",
            emotion_scores=scores,
            confidence=0.0,
            valence=0.0,
            arousal=0.1,
            face_detected=False,
        )
