"""LangGraph 心理对话状态图

基于 LangGraph 实现的心理对话状态管理，负责协调各节点之间的状态流转。

流程：
    用户输入 → 情绪感知 → 危机检查 → [路由]
                                          ├─ (low/medium) → 知识检索 → 回复生成 → 练习建议 → END
                                          └─ (high/crisis) → 危机干预 → END
"""
from typing import Optional, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from src.agent.nodes import (
    crisis_check_node,
    crisis_intervention_node,
    crisis_router,
    emotion_perception_node,
    exercise_suggestion_node,
    knowledge_retrieval_node,
    response_generation_node,
)


class ConversationState(TypedDict):
    """对话状态"""

    # 用户输入
    user_message: str

    # 情绪状态
    emotion_result: Optional[dict]       # 从情绪分析器获得
    emotion_history: list[dict]          # 近期情绪历史

    # 对话历史
    messages: list[dict]                 # ChatMessage 格式 [{"role": "...", "content": "..."}]

    # 知识检索结果
    retrieved_knowledge: list[str]       # 检索到的知识片段

    # 危机评估
    risk_level: str                      # low / medium / high / crisis
    crisis_signals: list[str]           # 危机信号

    # 对话元数据
    session_id: str
    turn_count: int
    needs_human_intervention: bool       # 是否需要人工干预

    # 输出
    response: str                        # AI 回复
    suggested_exercises: list[str]       # 建议的 CBT 练习


def build_conversation_graph() -> StateGraph:
    """构建心理对话状态图

    注册所有节点，配置条件边（基于 risk_level 路由），
    使用 MemorySaver 作为检查点。

    Returns:
        编译后的 CompiledGraph
    """
    graph = StateGraph(ConversationState)

    # ── 注册节点 ──────────────────────────────────────────────
    graph.add_node("emotion_perception", emotion_perception_node)
    graph.add_node("crisis_check", crisis_check_node)
    graph.add_node("knowledge_retrieval", knowledge_retrieval_node)
    graph.add_node("response_generation", response_generation_node)
    graph.add_node("crisis_intervention", crisis_intervention_node)
    graph.add_node("exercise_suggestion", exercise_suggestion_node)

    # ── 设置入口 ──────────────────────────────────────────────
    graph.set_entry_point("emotion_perception")

    # ── 固定边：情绪感知 → 危机检查 ───────────────────────────
    graph.add_edge("emotion_perception", "crisis_check")

    # ── 条件边：危机检查 → 路由决策 ───────────────────────────
    graph.add_conditional_edges(
        "crisis_check",
        crisis_router,
        {
            "crisis_intervention": "crisis_intervention",
            "knowledge_retrieval": "knowledge_retrieval",
        },
    )

    # ── 正常对话路径 ──────────────────────────────────────────
    graph.add_edge("knowledge_retrieval", "response_generation")
    graph.add_edge("response_generation", "exercise_suggestion")
    graph.add_edge("exercise_suggestion", END)

    # ── 危机干预路径 → 结束 ──────────────────────────────────
    graph.add_edge("crisis_intervention", END)

    return graph
