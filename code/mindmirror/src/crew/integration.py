"""CrewAI 与 LangGraph 集成模块

将 CrewAI 多智能体分析能力无缝集成到 LangGraph 对话流程中，
作为可选的增强节点提供深度心理分析。

集成策略：
- 对话轮次 > 3 时启动完整多智能体分析
- 检测到情绪波动时触发深度情绪分析
- 危机场景立即触发危机检测
"""
import json
from typing import Any, Dict, Optional

from src.crew.crew import MindMirrorCrew
from src.utils.config import ZHIPU_API_KEY
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 触发完整分析的对话轮次阈值
_FULL_ANALYSIS_TURN_THRESHOLD = 3

# 情绪波动阈值 — 相邻两轮情绪差异超过此值触发深度分析
_EMOTION_VOLATILITY_THRESHOLD = 0.3


class CrewIntegration:
    """将 CrewAI 多智能体分析集成到 LangGraph 对话流程中

    在 LangGraph 的节点中作为可选增强层调用，
    根据对话上下文智能决定是否需要启动多智能体分析。

    Attributes:
        crew: MindMirrorCrew 实例
        available: CrewAI 是否可用（API Key 已配置）
    """

    def __init__(self):
        """初始化集成模块"""
        self.available = bool(ZHIPU_API_KEY)
        self.crew: Optional[MindMirrorCrew] = None

        if self.available:
            try:
                self.crew = MindMirrorCrew()
                logger.info("CrewIntegration 初始化成功，CrewAI 可用")
            except Exception as e:
                logger.error("CrewIntegration 初始化失败: %s", e)
                self.available = False
        else:
            logger.info("CrewIntegration 处于降级模式（API Key 未配置）")

    async def enhance_response(self, state: dict) -> dict:
        """增强对话响应 — 在 LangGraph 流程中作为可选节点调用

        触发条件：
        - 对话轮次 > 3 时启动完整分析
        - 检测到情绪波动时触发深度分析
        - 其他情况使用快速检查

        Args:
            state: LangGraph 对话状态字典，包含：
                - user_message: 用户当前消息
                - emotion_result: 情绪分析结果
                - emotion_history: 情绪历史
                - messages: 对话历史
                - turn_count: 对话轮次
                - risk_level: 风险等级

        Returns:
            增强后的状态更新字典，包含 crew_analysis 字段
        """
        if not self.available or self.crew is None:
            logger.debug("CrewAI 不可用，跳过增强分析")
            return {"crew_analysis": None}

        user_message = state.get("user_message", "")
        emotion_data = state.get("emotion_result") or {}
        history = state.get("messages") or []
        turn_count = state.get("turn_count", 0)
        risk_level = state.get("risk_level", "low")

        # 根据情境选择分析模式
        analysis_mode = self._determine_analysis_mode(
            turn_count, risk_level, state.get("emotion_history") or []
        )

        logger.info("CrewAI 分析模式: %s (turn=%d, risk=%s)", analysis_mode, turn_count, risk_level)

        try:
            if analysis_mode == "full":
                result = await self.crew.run_full_analysis(
                    user_message=user_message,
                    emotion_data=emotion_data,
                    history=history,
                )
            elif analysis_mode == "quick":
                result = await self.crew.run_quick_check(
                    user_message=user_message,
                    emotion_data=emotion_data,
                )
            else:
                # skip 模式 — 不执行 CrewAI 分析
                return {"crew_analysis": None}

            return {"crew_analysis": result}

        except Exception as e:
            logger.error("CrewAI 增强分析失败: %s", e, exc_info=True)
            return {"crew_analysis": None}

    async def get_intervention_plan(self, session_summary: dict) -> dict:
        """获取干预计划 — 基于会话总结生成个性化干预方案

        Args:
            session_summary: 会话总结信息，包含：
                - dominant_emotions: 本次会话的主要情绪列表
                - topics_discussed: 讨论的主题
                - overall_mood: 整体心情评估
                - user_message: 最近的用户消息

        Returns:
            干预计划字典
        """
        if not self.available or self.crew is None:
            logger.debug("CrewAI 不可用，返回默认干预计划")
            return self._default_intervention_plan()

        user_message = session_summary.get("user_message", "用户需要心理支持")
        emotion_data = {
            "dominant_emotion": session_summary.get("overall_mood", "neutral"),
            "score": 0.5,
        }

        try:
            result = await self.crew.run_full_analysis(
                user_message=user_message,
                emotion_data=emotion_data,
                history=[],
            )
            return result.get("intervention", self._default_intervention_plan())
        except Exception as e:
            logger.error("生成干预计划失败: %s", e, exc_info=True)
            return self._default_intervention_plan()

    def _determine_analysis_mode(
        self, turn_count: int, risk_level: str, emotion_history: list
    ) -> str:
        """根据上下文决定分析模式

        Args:
            turn_count: 当前对话轮次
            risk_level: 风险等级
            emotion_history: 情绪历史列表

        Returns:
            分析模式: "full" / "quick" / "skip"
        """
        # 高风险场景 — 始终执行快速检查
        if risk_level in ("high", "crisis"):
            return "quick"

        # 对话轮次超过阈值 — 执行完整分析
        if turn_count >= _FULL_ANALYSIS_TURN_THRESHOLD:
            return "full"

        # 检测情绪波动
        if self._detect_emotion_volatility(emotion_history):
            return "full"

        # 前几轮对话只做快速检查
        if turn_count >= 1:
            return "quick"

        return "skip"

    @staticmethod
    def _detect_emotion_volatility(emotion_history: list) -> bool:
        """检测情绪波动是否超过阈值

        比较最近几轮的情绪分数变化，如果波动过大则返回 True。

        Args:
            emotion_history: 情绪历史记录列表

        Returns:
            是否存在显著情绪波动
        """
        if len(emotion_history) < 2:
            return False

        recent = emotion_history[-3:]  # 最近 3 条
        scores = [entry.get("score", 0.5) for entry in recent if isinstance(entry, dict)]

        if len(scores) < 2:
            return False

        # 计算相邻分数的最大差值
        max_diff = max(abs(scores[i] - scores[i - 1]) for i in range(1, len(scores)))
        return max_diff > _EMOTION_VOLATILITY_THRESHOLD

    @staticmethod
    def _default_intervention_plan() -> dict:
        """默认干预计划（降级方案）"""
        return {
            "primary_intervention": {
                "type": "mindfulness",
                "name": "正念呼吸练习",
                "description": "进行 5 分钟的专注呼吸练习，帮助平复情绪",
                "estimated_duration": "5分钟",
            },
            "exercises": [
                {
                    "name": "腹式呼吸",
                    "category": "breathing",
                    "instructions": [
                        "找一个舒适的坐姿",
                        "将一只手放在腹部",
                        "缓慢吸气 4 秒，感受腹部隆起",
                        "屏息 2 秒",
                        "缓慢呼气 6 秒，感受腹部回落",
                        "重复 5-8 次",
                    ],
                    "difficulty": "easy",
                    "priority": "high",
                },
                {
                    "name": "情绪记录",
                    "category": "journaling",
                    "instructions": [
                        "写下此刻的感受（不评判）",
                        "记录触发这种感受的事件",
                        "描述身体上的感受",
                        "给情绪强度打分（1-10）",
                    ],
                    "difficulty": "easy",
                    "priority": "medium",
                },
            ],
            "follow_up_questions": [
                "你愿意和我聊聊最近让你感到困扰的事情吗？",
                "你平时有什么方式让自己放松下来？",
            ],
            "safety_plan": None,
        }


def crew_analysis_node(state: dict) -> dict:
    """LangGraph 节点函数 — CrewAI 多智能体分析

    可直接添加到 LangGraph 状态图中作为节点使用。

    Args:
        state: LangGraph 对话状态

    Returns:
        状态更新字典
    """
    import asyncio

    integration = CrewIntegration()

    # 在同步的 LangGraph 节点中运行异步方法
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果已有事件循环在运行，创建新线程执行
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = pool.submit(asyncio.run, integration.enhance_response(state)).result()
        else:
            result = asyncio.run(integration.enhance_response(state))
        return result
    except Exception as e:
        logger.error("CrewAI 节点执行失败: %s", e, exc_info=True)
        return {"crew_analysis": None}
