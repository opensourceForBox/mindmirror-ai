"""CrewAI Crew 编排 — 多智能体协作流程

协调 5 个专业化 Agent 的执行顺序，支持两种运行模式：
- 完整分析模式：危机检测 → 情绪分析 + 心理评估 → 知识检索 → 干预建议
- 快速检查模式：仅危机检测 + 情绪分析（实时场景）
"""
import asyncio
import json
from typing import Any, Dict, List, Optional

from crewai import Crew, Process

from src.crew.agents import create_psychology_agents
from src.crew.tasks import (
    create_assessment_task,
    create_crisis_detection_task,
    create_emotion_analysis_task,
    create_intervention_task,
    create_knowledge_retrieval_task,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _parse_json_output(raw_output: str) -> dict:
    """尝试从 Crew 输出中解析 JSON

    CrewAI 的 task 输出是字符串，可能包含 JSON 块。
    尝试多种策略提取有效 JSON。

    Args:
        raw_output: Crew 任务的原始输出字符串

    Returns:
        解析后的字典，解析失败时返回 {"raw": raw_output}
    """
    if not raw_output:
        return {"raw": ""}

    text = raw_output.strip()

    # 策略1：直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 策略2：提取 ```json ... ``` 代码块
    if "```json" in text:
        start = text.index("```json") + 7
        end = text.index("```", start)
        try:
            return json.loads(text[start:end].strip())
        except (json.JSONDecodeError, ValueError):
            pass

    # 策略3：提取 ``` ... ``` 代码块
    if "```" in text:
        start = text.index("```") + 3
        end = text.index("```", start)
        try:
            return json.loads(text[start:end].strip())
        except (json.JSONDecodeError, ValueError):
            pass

    # 策略4：查找第一个 { 到最后一个 }
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        try:
            return json.loads(text[first_brace : last_brace + 1])
        except json.JSONDecodeError:
            pass

    logger.warning("无法从 Crew 输出解析 JSON，返回原始文本")
    return {"raw": raw_output}


class MindMirrorCrew:
    """MindMirror 心理健康多智能体团队

    编排 5 个专业化 Agent 的协作流程，对外提供异步接口。
    CrewAI 内部是同步执行，使用 asyncio.to_thread 包装为异步。

    Attributes:
        agents: 已创建的 Agent 字典
    """

    def __init__(self):
        """初始化多智能体团队"""
        self.agents = create_psychology_agents()
        logger.info("MindMirrorCrew 初始化完成")

    async def run_full_analysis(
        self,
        user_message: str,
        emotion_data: Optional[dict] = None,
        history: Optional[list] = None,
    ) -> Dict[str, Any]:
        """执行完整的多智能体分析

        流程：
        1. 危机检测（优先级最高，并行启动）
        2. 情绪分析 + 心理评估（并行）
        3. 知识检索（基于评估结果）
        4. 干预建议（基于所有分析结果）

        Args:
            user_message: 用户当前消息
            emotion_data: 外部情绪分析数据
            history: 对话历史

        Returns:
            包含所有分析结果的字典
        """
        logger.info("开始完整多智能体分析 (消息长度=%d)", len(user_message))

        emotion_data = emotion_data or {}
        history = history or []

        # 阶段1：危机检测（独立并行）
        crisis_result = await self._run_crisis_detection(user_message, emotion_data)

        # 如果检测到危机，立即返回，不做后续分析
        if crisis_result.get("risk_level") in ("high", "crisis"):
            logger.warning("检测到高风险危机信号，跳过后续分析")
            return {
                "crisis_result": crisis_result,
                "emotion_analysis": {},
                "assessment": {},
                "knowledge": {},
                "intervention": {},
                "summary": f"危机警报：风险等级 {crisis_result.get('risk_level')}",
            }

        # 阶段2：情绪分析 + 心理评估（并行执行）
        emotion_analysis, assessment = await asyncio.gather(
            self._run_emotion_analysis(user_message, emotion_data),
            self._run_assessment(user_message, emotion_data, history),
        )

        # 阶段3：知识检索（基于评估结果构建查询）
        emotion_context = self._build_emotion_context(emotion_analysis)
        query = f"{user_message} {emotion_analysis.get('primary_emotion', '')}"
        knowledge = await self._run_knowledge_retrieval(query, emotion_context)

        # 阶段4：干预建议（基于所有分析结果）
        assessment_str = json.dumps(assessment, ensure_ascii=False)
        emotion_str = json.dumps(emotion_analysis, ensure_ascii=False)
        intervention = await self._run_intervention(assessment_str, emotion_str)

        # 生成总结
        summary = self._generate_summary(
            crisis_result, emotion_analysis, assessment, knowledge, intervention
        )

        logger.info("完整多智能体分析完成")

        return {
            "crisis_result": crisis_result,
            "emotion_analysis": emotion_analysis,
            "assessment": assessment,
            "knowledge": knowledge,
            "intervention": intervention,
            "summary": summary,
        }

    async def run_quick_check(
        self,
        user_message: str,
        emotion_data: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """快速检查（仅危机检测 + 情绪分析，用于实时场景）

        Args:
            user_message: 用户当前消息
            emotion_data: 外部情绪分析数据

        Returns:
            包含危机检测和情绪分析结果的字典
        """
        logger.info("开始快速检查 (消息长度=%d)", len(user_message))

        emotion_data = emotion_data or {}

        # 并行执行危机检测和情绪分析
        crisis_result, emotion_analysis = await asyncio.gather(
            self._run_crisis_detection(user_message, emotion_data),
            self._run_emotion_analysis(user_message, emotion_data),
        )

        return {
            "crisis_result": crisis_result,
            "emotion_analysis": emotion_analysis,
            "summary": self._generate_quick_summary(crisis_result, emotion_analysis),
        }

    def _create_crew(
        self,
        agents: list,
        tasks: list,
        process: Process = Process.sequential,
    ) -> Crew:
        """创建 Crew 实例

        Args:
            agents: Agent 列表
            tasks: Task 列表
            process: 执行流程类型（sequential / hierarchical）

        Returns:
            Crew 实例
        """
        return Crew(
            agents=agents,
            tasks=tasks,
            process=process,
            verbose=True,
        )

    # ── 内部任务执行方法 ──────────────────────────────────────────

    async def _run_crisis_detection(
        self, user_message: str, emotion_data: dict
    ) -> dict:
        """执行危机检测任务"""
        try:
            agent = self.agents["crisis"]
            task = create_crisis_detection_task(agent, user_message, emotion_data)
            crew = self._create_crew([agent], [task])
            result = await asyncio.to_thread(crew.kickoff)
            parsed = _parse_json_output(str(result))
            logger.info("危机检测完成: risk_level=%s", parsed.get("risk_level", "unknown"))
            return parsed
        except Exception as e:
            logger.error("危机检测任务失败: %s", e, exc_info=True)
            return {"risk_level": "low", "error": str(e), "crisis_signals": []}

    async def _run_emotion_analysis(
        self, user_message: str, emotion_data: dict
    ) -> dict:
        """执行情绪分析任务"""
        try:
            agent = self.agents["emotion"]
            task = create_emotion_analysis_task(agent, user_message, emotion_data)
            crew = self._create_crew([agent], [task])
            result = await asyncio.to_thread(crew.kickoff)
            parsed = _parse_json_output(str(result))
            logger.info("情绪分析完成: primary=%s", parsed.get("primary_emotion", "unknown"))
            return parsed
        except Exception as e:
            logger.error("情绪分析任务失败: %s", e, exc_info=True)
            return {"primary_emotion": "neutral", "error": str(e)}

    async def _run_assessment(
        self, user_message: str, emotion_data: dict, history: list
    ) -> dict:
        """执行心理评估任务"""
        try:
            agent = self.agents["assessment"]
            task = create_assessment_task(agent, user_message, emotion_data, history)
            crew = self._create_crew([agent], [task])
            result = await asyncio.to_thread(crew.kickoff)
            parsed = _parse_json_output(str(result))
            logger.info("心理评估完成: score=%s", parsed.get("overall_score", "N/A"))
            return parsed
        except Exception as e:
            logger.error("心理评估任务失败: %s", e, exc_info=True)
            return {"overall_score": 5, "error": str(e)}

    async def _run_knowledge_retrieval(self, query: str, emotion_context: str) -> dict:
        """执行知识检索任务"""
        try:
            agent = self.agents["knowledge"]
            task = create_knowledge_retrieval_task(agent, query, emotion_context)
            crew = self._create_crew([agent], [task])
            result = await asyncio.to_thread(crew.kickoff)
            parsed = _parse_json_output(str(result))
            logger.info("知识检索完成")
            return parsed
        except Exception as e:
            logger.error("知识检索任务失败: %s", e, exc_info=True)
            return {"coping_strategies": [], "error": str(e)}

    async def _run_intervention(self, assessment: str, emotion: str) -> dict:
        """执行干预建议任务"""
        try:
            agent = self.agents["intervention"]
            task = create_intervention_task(agent, assessment, emotion)
            crew = self._create_crew([agent], [task])
            result = await asyncio.to_thread(crew.kickoff)
            parsed = _parse_json_output(str(result))
            logger.info("干预建议完成")
            return parsed
        except Exception as e:
            logger.error("干预建议任务失败: %s", e, exc_info=True)
            return {"exercises": [], "error": str(e)}

    # ── 辅助方法 ────────────────────────────────────────────────

    @staticmethod
    def _build_emotion_context(emotion_analysis: dict) -> str:
        """从情绪分析结果构建上下文描述"""
        primary = emotion_analysis.get("primary_emotion", "neutral")
        intensity = emotion_analysis.get("intensity_score", 0.5)
        trend = emotion_analysis.get("emotion_trend", "")
        triggers = emotion_analysis.get("emotional_triggers", [])
        return (
            f"主要情绪: {primary}，强度: {intensity}，"
            f"趋势: {trend}，触发因素: {', '.join(triggers) if triggers else '未知'}"
        )

    @staticmethod
    def _generate_summary(
        crisis: dict, emotion: dict, assessment: dict,
        knowledge: dict, intervention: dict,
    ) -> str:
        """生成完整分析的综合摘要"""
        parts = []

        # 评估分数
        score = assessment.get("overall_score")
        if score is not None:
            parts.append(f"心理健康评分: {score}/10")

        # 主要情绪
        primary_emotion = emotion.get("primary_emotion", "未知")
        parts.append(f"主要情绪: {primary_emotion}")

        # 风险等级
        risk = crisis.get("risk_level", "low")
        if risk != "low":
            parts.append(f"风险等级: {risk}")

        # 干预建议
        exercises = intervention.get("exercises", [])
        if exercises:
            names = [ex.get("name", "") for ex in exercises[:2]]
            parts.append(f"推荐练习: {', '.join(names)}")

        return " | ".join(parts) if parts else "分析完成"

    @staticmethod
    def _generate_quick_summary(crisis: dict, emotion: dict) -> str:
        """生成快速检查的简要摘要"""
        risk = crisis.get("risk_level", "low")
        primary = emotion.get("primary_emotion", "neutral")
        return f"快速检查 — 情绪: {primary}, 风险: {risk}"
