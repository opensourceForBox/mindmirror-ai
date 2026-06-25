"""CrewAI 任务定义

为心理健康多智能体团队定义各 Agent 的专属任务：
- 心理评估任务：综合评估用户心理状态
- 情绪深度分析任务：识别情绪模式和变化趋势
- 知识检索任务：检索专业心理学知识
- 危机检测任务：危机信号实时监控
- 干预建议任务：CBT 干预策略推荐
"""
import json

from crewai import Task


def create_assessment_task(agent, user_message: str, emotion_data: dict, history: list) -> Task:
    """创建心理评估任务

    Args:
        agent: 心理评估专家 Agent
        user_message: 用户当前消息
        emotion_data: 情绪分析数据 {"dominant_emotion": str, "score": float, "emotions": dict}
        history: 对话历史列表

    Returns:
        CrewAI Task 实例
    """
    history_text = "无"
    if history:
        recent = history[-5:]
        history_text = "\n".join(
            f"  - [{msg.get('role', '未知')}] {msg.get('content', '')[:200]}"
            for msg in recent
        )

    emotion_text = json.dumps(emotion_data or {}, ensure_ascii=False, indent=2)

    return Task(
        description=f"""
请基于以下信息对用户的心理状态进行全面评估：

## 用户消息
{user_message}

## 情绪数据
{emotion_text}

## 近期对话历史
{history_text}

## 评估要求
请从以下维度进行评估，并以 JSON 格式输出：
1. **overall_score** (整数 1-10)：用户当前的整体心理健康状态评分，10 为最佳
2. **dominant_emotion** (字符串)：当前最显著的情绪特征
3. **emotion_intensity** (浮点数 0-1)：情绪强度
4. **potential_issues** (字符串数组)：可能存在的心理问题倾向，如 ["焦虑倾向", "社交回避"]
5. **risk_factors** (字符串数组)：需要关注的风险因素
6. **protective_factors** (字符串数组)：用户展现出的积极保护因素
7. **recommendation** (字符串)：针对当前状态的简要建议（50字以内）
""",
        expected_output=(
            '结构化 JSON 评估报告，格式：'
            '{"overall_score": int, "dominant_emotion": str, "emotion_intensity": float, '
            '"potential_issues": [str], "risk_factors": [str], '
            '"protective_factors": [str], "recommendation": str}'
        ),
        agent=agent,
    )


def create_emotion_analysis_task(agent, user_message: str, emotion_data: dict) -> Task:
    """创建情绪深度分析任务

    Args:
        agent: 情绪分析专家 Agent
        user_message: 用户当前消息
        emotion_data: 情绪分析数据

    Returns:
        CrewAI Task 实例
    """
    emotion_text = json.dumps(emotion_data or {}, ensure_ascii=False, indent=2)

    return Task(
        description=f"""
请对用户的当前情绪状态进行深度分析：

## 用户消息
{user_message}

## 初步情绪数据
{emotion_text}

## 分析要求
请从以下维度进行深度情绪分析，并以 JSON 格式输出：
1. **primary_emotion** (字符串)：主要情绪（如 sadness, anxiety, anger, joy, neutral）
2. **secondary_emotions** (字符串数组)：次要/伴随情绪列表
3. **hidden_emotions** (字符串数组)：可能被用户隐藏的深层情绪
4. **emotional_triggers** (字符串数组)：可能的情绪触发因素
5. **emotion_trend** (字符串)：情绪变化趋势描述（如"从焦虑转向无助"）
6. **empathy_suggestion** (字符串)：基于情绪状态，对话者应如何回应（30字以内）
7. **intensity_score** (浮点数 0-1)：整体情绪强度评分
""",
        expected_output=(
            '结构化 JSON 情绪分析报告，格式：'
            '{"primary_emotion": str, "secondary_emotions": [str], "hidden_emotions": [str], '
            '"emotional_triggers": [str], "emotion_trend": str, '
            '"empathy_suggestion": str, "intensity_score": float}'
        ),
        agent=agent,
    )


def create_knowledge_retrieval_task(agent, query: str, emotion_context: str) -> Task:
    """创建知识检索任务

    Args:
        agent: 心理学知识顾问 Agent
        query: 检索查询关键词
        emotion_context: 情绪上下文描述

    Returns:
        CrewAI Task 实例
    """
    return Task(
        description=f"""
请根据以下情境从心理学知识库中检索最相关的专业内容：

## 检索查询
{query}

## 情绪上下文
{emotion_context}

## 检索要求
请提供以下结构化信息（JSON 格式）：
1. **relevant_theories** (对象数组)：相关的心理学理论，每个包含：
   - "name": 理论名称
   - "description": 简要描述（50字以内）
   - "relevance": 与当前情境的关联说明
2. **cbt_techniques** (对象数组)：适用的 CBT 技术，每个包含：
   - "name": 技术名称
   - "steps": 执行步骤（字符串数组）
   - "difficulty": 难度级别（easy/medium/hard）
3. **psychoeducation** (字符串)：可供用户学习的心理教育内容（100字以内）
4. **coping_strategies** (字符串数组)：即时可用的应对策略列表（至少3个）
""",
        expected_output=(
            '结构化 JSON 知识检索报告，格式：'
            '{"relevant_theories": [{"name": str, "description": str, "relevance": str}], '
            '"cbt_techniques": [{"name": str, "steps": [str], "difficulty": str}], '
            '"psychoeducation": str, "coping_strategies": [str]}'
        ),
        agent=agent,
    )


def create_crisis_detection_task(agent, user_message: str, emotion_data: dict) -> Task:
    """创建危机检测任务

    Args:
        agent: 危机干预专家 Agent
        user_message: 用户当前消息
        emotion_data: 情绪分析数据

    Returns:
        CrewAI Task 实例
    """
    emotion_text = json.dumps(emotion_data or {}, ensure_ascii=False, indent=2)

    return Task(
        description=f"""
请对以下用户消息进行危机风险评估：

## 用户消息
{user_message}

## 情绪数据
{emotion_text}

## 评估要求
请以高度警觉的态度分析，宁可误报也不能漏报。输出 JSON 格式的危机评估结果：
1. **risk_level** (字符串)：风险等级，取值为 "low" / "medium" / "high" / "crisis"
2. **crisis_signals** (字符串数组)：检测到的危机信号关键词或表述
3. **self_harm_risk** (布尔值)：是否存在自我伤害风险
4. **suicide_risk** (布尔值)：是否存在自杀风险
5. **urgency** (字符串)：紧急程度，取值为 "routine" / "urgent" / "immediate"
6. **recommended_actions** (字符串数组)：建议采取的行动列表
7. **hotline_needed** (布尔值)：是否需要推送心理援助热线
8. **assessment_note** (字符串)：评估说明（50字以内）

注意：如果出现任何自杀/自伤相关表述，risk_level 必须设为 "high" 或 "crisis"。
""",
        expected_output=(
            '结构化 JSON 危机评估报告，格式：'
            '{"risk_level": str, "crisis_signals": [str], "self_harm_risk": bool, '
            '"suicide_risk": bool, "urgency": str, "recommended_actions": [str], '
            '"hotline_needed": bool, "assessment_note": str}'
        ),
        agent=agent,
    )


def create_intervention_task(agent, assessment: str, emotion: str) -> Task:
    """创建干预建议任务

    Args:
        agent: CBT 干预顾问 Agent
        assessment: 心理评估结果（JSON 字符串）
        emotion: 情绪分析结果（JSON 字符串）

    Returns:
        CrewAI Task 实例
    """
    return Task(
        description=f"""
基于心理评估和情绪分析结果，请制定个性化的 CBT 干预方案：

## 心理评估结果
{assessment}

## 情绪分析结果
{emotion}

## 干预方案要求
请制定结构化的干预方案（JSON 格式）：
1. **primary_intervention** (对象)：主要干预策略
   - "type": 干预类型（如 "cognitive_restructuring", "behavioral_activation", "relaxation"）
   - "name": 干预名称
   - "description": 详细描述（80字以内）
   - "estimated_duration": 预估时长（如 "10分钟"）
2. **exercises** (对象数组)：推荐的具体练习列表（至少2个），每个包含：
   - "name": 练习名称
   - "category": 类别（如 "breathing", "journaling", "cognitive", "behavioral"）
   - "instructions": 执行说明（字符串数组）
   - "difficulty": 难度级别（easy/medium/hard）
   - "priority": 优先级（high/medium/low）
3. **follow_up_questions** (字符串数组)：后续对话中可以深入了解的问题（至少2个）
4. **safety_plan** (对象，可选)：如果有风险时的安全计划
   - "hotlines": 援助热线列表
   - "trusted_contacts": 建议联系的信任人群
   - "coping_cards": 应急应对卡片内容
""",
        expected_output=(
            '结构化 JSON 干预方案，格式：'
            '{"primary_intervention": {"type": str, "name": str, "description": str, '
            '"estimated_duration": str}, "exercises": [{"name": str, "category": str, '
            '"instructions": [str], "difficulty": str, "priority": str}], '
            '"follow_up_questions": [str], "safety_plan": {"hotlines": [str], '
            '"trusted_contacts": [str], "coping_cards": [str]} | null}'
        ),
        agent=agent,
    )
