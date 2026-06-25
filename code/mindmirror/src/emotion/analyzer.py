"""情绪分析统一接口

提供单模态 / 多模态情绪分析的统一入口，
封装视频、音频、融合三个子模块，对外暴露简洁的 async API。
"""

import logging
from pathlib import Path
from typing import Optional

import numpy as np

from .audio import AudioEmotionAnalyzer, AudioEmotionResult
from .fusion import EmotionFusion, FusedEmotionResult
from .video import VideoEmotionAnalyzer, VideoEmotionResult

logger = logging.getLogger(__name__)


class EmotionAnalyzer:
    """情绪分析器 — 统一入口

    内部持有三个子模块：
    - VideoEmotionAnalyzer  （DeepFace + MediaPipe）
    - AudioEmotionAnalyzer  （OpenSMILE + XGBoost）
    - EmotionFusion         （多模态融合引擎）

    所有公开方法均为 async，方便在 FastAPI / asyncio 环境中调用。
    CPU 密集型分析使用 asyncio.to_thread 在线程池中执行。
    """

    def __init__(self, audio_model_path: Optional[Path] = None):
        """初始化情绪分析器

        Args:
            audio_model_path: 可选 XGBoost 模型路径
        """
        self.video_analyzer = VideoEmotionAnalyzer()
        self.audio_analyzer = AudioEmotionAnalyzer(model_path=audio_model_path)
        self.fusion_engine = EmotionFusion()
        logger.info("EmotionAnalyzer 初始化完成")

    # ------------------------------------------------------------------
    # 统一多模态分析
    # ------------------------------------------------------------------

    async def analyze(
        self,
        video_frame: Optional[np.ndarray] = None,
        audio_data: Optional[np.ndarray] = None,
        sample_rate: int = 16000,
    ) -> FusedEmotionResult:
        """统一分析接口 — 同时或单独分析视频帧和音频数据

        Args:
            video_frame: BGR OpenCV 图像帧（可选）
            audio_data: 单声道 PCM numpy 数组（可选）
            sample_rate: 音频采样率（默认 16 kHz）

        Returns:
            FusedEmotionResult
        """
        import asyncio

        video_result: Optional[VideoEmotionResult] = None
        audio_result: Optional[AudioEmotionResult] = None

        # 并行执行两个模态的分析（在线程池中）
        tasks = []
        if video_frame is not None:
            tasks.append(asyncio.to_thread(self.video_analyzer.analyze_frame, video_frame))
        if audio_data is not None:
            tasks.append(
                asyncio.to_thread(self.audio_analyzer.analyze_stream, audio_data, sample_rate)
            )

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            idx = 0
            if video_frame is not None:
                r = results[idx]
                idx += 1
                if isinstance(r, Exception):
                    logger.error("视频分析异常: %s", r, exc_info=True)
                else:
                    video_result = r
            if audio_data is not None:
                r = results[idx]
                if isinstance(r, Exception):
                    logger.error("音频分析异常: %s", r, exc_info=True)
                else:
                    audio_result = r

        return self.fusion_engine.fuse(video_result, audio_result)

    # ------------------------------------------------------------------
    # 单模态快捷方法
    # ------------------------------------------------------------------

    async def analyze_video_stream(self, frame: np.ndarray) -> VideoEmotionResult:
        """仅分析视频帧

        Args:
            frame: BGR OpenCV 图像帧

        Returns:
            VideoEmotionResult
        """
        import asyncio

        return await asyncio.to_thread(self.video_analyzer.analyze_frame, frame)

    async def analyze_audio_stream(
        self, audio_data: np.ndarray, sample_rate: int = 16000
    ) -> AudioEmotionResult:
        """仅分析音频流

        Args:
            audio_data: 单声道 PCM numpy 数组
            sample_rate: 采样率

        Returns:
            AudioEmotionResult
        """
        import asyncio

        return await asyncio.to_thread(self.audio_analyzer.analyze_stream, audio_data, sample_rate)

    async def analyze_audio_file(self, audio_path: str) -> AudioEmotionResult:
        """分析音频文件

        Args:
            audio_path: WAV 文件路径

        Returns:
            AudioEmotionResult
        """
        import asyncio

        return await asyncio.to_thread(self.audio_analyzer.analyze_file, audio_path)
