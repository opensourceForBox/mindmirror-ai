"""对话管理器 — 提供高层接口

封装 LangGraph 编译后的状态图，对外提供简洁的 async API，
供 FastAPI 路由层调用。
"""
from typing import Optional

from langgraph.checkpoint.memory import MemorySaver

from src.agent.graph import build_conversation_graph
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ConversationManager:
    """对话管理器

    管理 LangGraph 图的编译与运行，提供会话级的对话、
    历史查询和情绪趋势查询接口。

    Attributes:
        graph: 未编译的 StateGraph
        checkpointer: 内存检查点（MemorySaver）
        compiled_graph: 编译后的可执行图
    """

    def __init__(self):
        self.checkpointer = MemorySaver()
        self.graph = build_conversation_graph()
        self.compiled_graph = self.graph.compile(checkpointer=self.checkpointer)
        logger.info("ConversationManager 初始化完成")

    async def chat(
        self,
        session_id: str,
        user_message: str,
        emotion_data: Optional[dict] = None,
    ) -> dict:
        """处理一次对话

        构建初始状态 → 调用图执行 → 返回结果。

        Args:
            session_id: 会话 ID（用于 LangGraph 的 thread_id）
            user_message: 用户消息文本
            emotion_data: 可选的外部情绪数据（来自视频/音频分析）

        Returns:
            {
                "response": "AI 回复",
                "emotion": {...},
                "risk_level": "low",
                "suggested_exercises": [...],
                "needs_human_intervention": false,
            }
        """
        # 构建初始输入状态
        input_state = {
            "user_message": user_message,
            "emotion_result": emotion_data,      # 外部情绪数据（可选）
            "emotion_history": [],
            "messages": [],
            "retrieved_knowledge": [],
            "risk_level": "low",
            "crisis_signals": [],
            "session_id": session_id,
            "turn_count": 0,
            "needs_human_intervention": False,
            "response": "",
            "suggested_exercises": [],
        }

        # LangGraph config — thread_id 用于关联同一会话的多轮对话
        config = {"configurable": {"thread_id": session_id}}

        # 尝试从检查点恢复历史状态
        try:
            existing_state = await self.compiled_graph.aget_state(config)
            if existing_state and existing_state.values:
                # 合并历史对话和情绪记录
                prev = existing_state.values
                input_state["messages"] = prev.get("messages", [])
                input_state["emotion_history"] = prev.get("emotion_history", [])
                input_state["turn_count"] = prev.get("turn_count", 0)
                logger.info(
                    "恢复会话 %s: turn=%d, messages=%d",
                    session_id,
                    input_state["turn_count"],
                    len(input_state["messages"]),
                )
        except Exception as e:
            logger.debug("无历史检查点（新会话）: %s", e)

        # 执行状态图
        try:
            result = await self.compiled_graph.ainvoke(input_state, config)
        except Exception as e:
            logger.error("状态图执行失败: %s", e, exc_info=True)
            return {
                "response": "抱歉，对话过程中出现了一些问题。请稍后再试。",
                "emotion": {},
                "risk_level": "low",
                "suggested_exercises": [],
                "needs_human_intervention": False,
            }

        return {
            "response": result.get("response", ""),
            "emotion": result.get("emotion_result"),
            "risk_level": result.get("risk_level", "low"),
            "suggested_exercises": result.get("suggested_exercises", []),
            "needs_human_intervention": result.get("needs_human_intervention", False),
        }

    async def get_history(self, session_id: str) -> list[dict]:
        """获取对话历史

        Args:
            session_id: 会话 ID

        Returns:
            对话消息列表
        """
        config = {"configurable": {"thread_id": session_id}}
        try:
            state = await self.compiled_graph.aget_state(config)
            if state and state.values:
                return state.values.get("messages", [])
        except Exception as e:
            logger.warning("获取对话历史失败: %s", e)
        return []

    async def get_emotion_trend(self, session_id: str) -> list[dict]:
        """获取情绪变化趋势

        Args:
            session_id: 会话 ID

        Returns:
            情绪历史记录列表
        """
        config = {"configurable": {"thread_id": session_id}}
        try:
            state = await self.compiled_graph.aget_state(config)
            if state and state.values:
                return state.values.get("emotion_history", [])
        except Exception as e:
            logger.warning("获取情绪趋势失败: %s", e)
        return []


# ── 全局单例 ──────────────────────────────────────────────────────
_manager: Optional[ConversationManager] = None


def get_conversation_manager() -> ConversationManager:
    """获取全局 ConversationManager 单例"""
    global _manager
    if _manager is None:
        _manager = ConversationManager()
    return _manager
