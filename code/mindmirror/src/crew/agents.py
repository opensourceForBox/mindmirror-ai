"""CrewAI 多智能体定义

定义心理健康领域的 5 个专业化 Agent：
- 心理评估 Agent：综合评估用户心理状态
- 情绪分析 Agent：深度分析情绪模式
- 知识检索 Agent：检索专业心理学知识
- 危机检测 Agent：实时危机信号监控
- 干预建议 Agent：CBT 干预策略推荐
"""
from typing import Optional

from src.utils.config import (
    LLM_PROVIDER,
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL,
    ZHIPU_API_KEY, ZHIPU_BASE_URL, ZHIPU_MODEL
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _get_crew_llm():
    """获取 CrewAI 使用的 LLM 实例"""
    from langchain_openai import ChatOpenAI

    if LLM_PROVIDER == "deepseek":
        api_key = DEEPSEEK_API_KEY
        base_url = DEEPSEEK_BASE_URL
        model = DEEPSEEK_MODEL
    else:
        api_key = ZHIPU_API_KEY
        base_url = f"{ZHIPU_BASE_URL}"
        model = ZHIPU_MODEL

    if not api_key:
        logger.warning(f"LLM API Key 未配置 (provider={LLM_PROVIDER})，CrewAI Agent 将不可用")
        return None

    try:
        llm = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=0.7,
        )
        logger.info(f"CrewAI LLM 初始化成功: provider={LLM_PROVIDER}, model={model}")
        return llm
    except Exception as e:
        logger.error(f"CrewAI LLM 初始化失败: {e}")
        return None


def create_psychology_agents(llm=None) -> dict:
    """创建心理健康多智能体团队

    Args:
        llm: 可选的 LLM 实例，默认自动创建基于 GLM-4 的实例

    Returns:
        包含 5 个 Agent 的字典，key 为 Agent 角色名称
    """
    from crewai import Agent

    if llm is None:
        llm = _get_crew_llm()

    # 当 LLM 不可用时的降级处理：仍然创建 Agent 但不绑定 llm
    agent_kwargs = {}
    if llm is not None:
        agent_kwargs["llm"] = llm

    # 1. 心理评估 Agent
    assessment_agent = Agent(
        role="心理评估专家",
        goal="综合评估用户的心理健康状态，识别潜在的心理问题",
        backstory=(
            "你是一位经验丰富的临床心理评估专家，擅长通过对话内容、"
            "情绪变化和行为模式综合评估个体的心理健康状况。你严谨、客观，"
            "善于发现细微的心理信号。"
        ),
        verbose=True,
        allow_delegation=True,
        **agent_kwargs,
    )

    # 2. 情绪分析 Agent
    emotion_agent = Agent(
        role="情绪分析专家",
        goal="深入分析用户的情绪状态，识别情绪模式和变化趋势",
        backstory=(
            "你是情绪心理学领域的专家，能够从文字、语调、面部表情等"
            "多维度解读人的情绪状态。你善于识别被隐藏的情绪和情绪转变的临界点。"
        ),
        verbose=True,
        **agent_kwargs,
    )

    # 3. 知识检索 Agent
    knowledge_agent = Agent(
        role="心理学知识顾问",
        goal="从专业心理学知识库中检索最相关的理论和技术，为对话提供专业支撑",
        backstory=(
            "你精通各个心理学分支，包括认知行为疗法、社会心理学、"
            "发展心理学和行为心理学。你善于将复杂的心理学理论转化为通俗易懂的建议。"
        ),
        verbose=True,
        **agent_kwargs,
    )

    # 4. 危机检测 Agent
    crisis_agent = Agent(
        role="危机干预专家",
        goal="实时监控危机信号，确保用户安全，必要时触发紧急干预",
        backstory=(
            "你是一位训练有素的危机干预专家，擅长识别自杀/自伤风险信号。"
            "你的首要任务是确保用户安全，宁可误报也不能漏报。"
        ),
        verbose=True,
        **agent_kwargs,
    )

    # 5. 干预建议 Agent
    intervention_agent = Agent(
        role="CBT干预顾问",
        goal="根据用户当前状态，推荐最适合的认知行为治疗练习和干预策略",
        backstory=(
            "你是认知行为疗法的实践专家，擅长根据个体情况定制"
            "个性化的CBT练习方案。你了解各种心理干预技术的适用场景。"
        ),
        verbose=True,
        **agent_kwargs,
    )

    agents = {
        "assessment": assessment_agent,
        "emotion": emotion_agent,
        "knowledge": knowledge_agent,
        "crisis": crisis_agent,
        "intervention": intervention_agent,
    }

    logger.info("已创建 %d 个心理专业 Agent (LLM 可用: %s)", len(agents), llm is not None)
    return agents
