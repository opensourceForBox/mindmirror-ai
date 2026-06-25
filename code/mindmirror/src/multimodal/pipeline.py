"""多模态实时处理管道

职责：
1. 接收视频帧（来自 WebRTC 或本地摄像头）
2. 帧采样（按 target_fps 降采样）
3. 预处理（亮度/对比度调整）
4. 调用情绪分析
5. 结果缓冲和平滑
"""

import asyncio
import time
from typing import Optional, AsyncGenerator
from dataclasses import dataclass, field
from collections import deque

import numpy as np

from src.emotion.analyzer import EmotionAnalyzer
from src.utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------

@dataclass
class FrameResult:
    """帧处理结果"""
    frame_id: int
    timestamp: float
    emotion_result: dict
    processing_time_ms: float
    face_detected: bool


@dataclass
class PipelineConfig:
    """管道配置"""
    target_fps: float = 2.0             # 情绪检测帧率（不需要每帧都分析）
    max_buffer_size: int = 10           # 帧缓冲区大小
    min_face_size: int = 80             # 最小人脸尺寸（像素）
    enable_preprocessing: bool = True   # 启用预处理
    max_consecutive_no_face: int = 30   # 连续无人脸帧数上限


# ---------------------------------------------------------------------------
# 管道主体
# ---------------------------------------------------------------------------

class VideoProcessingPipeline:
    """视频流实时处理管道"""

    def __init__(self, config: PipelineConfig = None):
        self.config = config or PipelineConfig()
        self.analyzer: Optional[EmotionAnalyzer] = None

        # 帧计数与时间控制
        self._frame_count: int = 0
        self._last_analyze_time: float = 0.0

        # 结果缓冲（最近 N 个结果）
        self._result_buffer: deque[FrameResult] = deque(maxlen=self.config.max_buffer_size)

        # 连续无人脸计数
        self._consecutive_no_face: int = 0

        # 运行状态
        self._running: bool = False

        logger.info(
            "VideoProcessingPipeline 初始化 | target_fps=%.1f, max_buffer=%d",
            self.config.target_fps, self.config.max_buffer_size,
        )

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------

    async def start(self):
        """启动处理管道，初始化情绪分析器"""
        if self._running:
            logger.warning("管道已在运行中")
            return
        self.analyzer = EmotionAnalyzer()
        self._running = True
        self._frame_count = 0
        self._last_analyze_time = 0.0
        self._consecutive_no_face = 0
        self._result_buffer.clear()
        logger.info("视频处理管道已启动")

    async def stop(self):
        """停止管道"""
        self._running = False
        logger.info("视频处理管道已停止 | 共处理 %d 帧", self._frame_count)

    # ------------------------------------------------------------------
    # 核心处理
    # ------------------------------------------------------------------

    async def process_frame(self, frame: np.ndarray) -> Optional[FrameResult]:
        """处理单帧

        基于 target_fps 决定是否分析此帧；若未到采样时间则返回 None。
        """
        if not self._running:
            logger.warning("管道未运行，忽略帧")
            return None

        self._frame_count += 1

        # 帧率控制
        if not self._should_analyze():
            return None

        start_time = time.perf_counter()

        # 预处理
        processed_frame = frame
        if self.config.enable_preprocessing:
            processed_frame = self._preprocess_frame(frame)

        # 调用情绪分析
        try:
            emotion_result = await self.analyzer.analyze_video_stream(processed_frame)
            emotion_dict = {
                "dominant_emotion": getattr(emotion_result, "dominant_emotion", "neutral"),
                "emotions": getattr(emotion_result, "emotions", {}),
                "confidence": getattr(emotion_result, "confidence", 0.0),
            }
            face_detected = getattr(emotion_result, "face_detected", True)
        except Exception as exc:
            logger.error("情绪分析失败: %s", exc, exc_info=True)
            emotion_dict = {"dominant_emotion": "unknown", "emotions": {}, "confidence": 0.0}
            face_detected = False

        # 无人脸追踪
        if face_detected:
            self._consecutive_no_face = 0
        else:
            self._consecutive_no_face += 1
            if self._consecutive_no_face >= self.config.max_consecutive_no_face:
                logger.warning(
                    "连续 %d 帧未检测到人脸，建议检查摄像头",
                    self._consecutive_no_face,
                )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        result = FrameResult(
            frame_id=self._frame_count,
            timestamp=time.time(),
            emotion_result=emotion_dict,
            processing_time_ms=round(elapsed_ms, 2),
            face_detected=face_detected,
        )
        self._result_buffer.append(result)
        logger.debug(
            "帧 #%d | %s (%.1fms) face=%s",
            result.frame_id,
            emotion_dict.get("dominant_emotion"),
            elapsed_ms,
            face_detected,
        )
        return result

    async def process_stream(self, frame_generator) -> AsyncGenerator[FrameResult, None]:
        """处理视频流（异步生成器）

        Args:
            frame_generator: 异步迭代器，每次产生一个 np.ndarray 帧

        Yields:
            FrameResult
        """
        async for frame in frame_generator:
            if not self._running:
                logger.info("管道已停止，结束流处理")
                break
            result = await self.process_frame(frame)
            if result is not None:
                yield result

    # ------------------------------------------------------------------
    # 结果平滑
    # ------------------------------------------------------------------

    def get_smoothed_emotion(self, window_size: int = 5) -> dict:
        """获取平滑后的情绪（滑动窗口加权平均）

        对最近 window_size 个结果中的置信度取平均，选出置信度最高的情绪。
        """
        recent = list(self._result_buffer)[-window_size:]
        if not recent:
            return {"dominant_emotion": "neutral", "confidence": 0.0, "emotions": {}}

        # 聚合所有情绪得分
        aggregated: dict[str, list[float]] = {}
        for r in recent:
            emotions = r.emotion_result.get("emotions", {})
            for emo, score in emotions.items():
                aggregated.setdefault(emo, []).append(float(score))

        if not aggregated:
            # 没有细粒度情绪数据，取最近一次 dominant
            last = recent[-1]
            return {
                "dominant_emotion": last.emotion_result.get("dominant_emotion", "neutral"),
                "confidence": last.emotion_result.get("confidence", 0.0),
                "emotions": {},
            }

        avg_emotions = {emo: sum(scores) / len(scores) for emo, scores in aggregated.items()}
        dominant = max(avg_emotions, key=avg_emotions.get)
        return {
            "dominant_emotion": dominant,
            "confidence": round(avg_emotions[dominant], 4),
            "emotions": {k: round(v, 4) for k, v in avg_emotions.items()},
        }

    # ------------------------------------------------------------------
    # 内部工具方法
    # ------------------------------------------------------------------

    def _should_analyze(self) -> bool:
        """基于帧率策略判断是否分析当前帧"""
        now = time.perf_counter()
        interval = 1.0 / self.config.target_fps
        if now - self._last_analyze_time >= interval:
            self._last_analyze_time = now
            return True
        return False

    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """帧预处理 — 自适应亮度/对比度（CLAHE）

        不依赖 OpenCV 也能运行（退化到直接返回原帧）。
        """
        try:
            import cv2
            # 转灰度做亮度检测
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mean_brightness = gray.mean()

            # 仅在亮度偏低或偏高时做 CLAHE
            if mean_brightness < 60 or mean_brightness > 200:
                lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
                l_channel, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                l_channel = clahe.apply(l_channel)
                lab = cv2.merge([l_channel, a, b])
                frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
                logger.debug("CLAHE 预处理已应用 (mean_brightness=%.1f)", mean_brightness)
        except ImportError:
            logger.warning("OpenCV 不可用，跳过预处理")
        except Exception as exc:
            logger.error("预处理异常: %s", exc)
        return frame

    # ------------------------------------------------------------------
    # 状态查询
    # ------------------------------------------------------------------

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def frame_count(self) -> int:
        return self._frame_count

    @property
    def latest_result(self) -> Optional[FrameResult]:
        return self._result_buffer[-1] if self._result_buffer else None
