"""对话图节点定义

定义 LangGraph 状态图中的各个处理节点，包括：
- 情绪感知节点
- 危机检查节点
- 知识检索节点
- 回复生成节点
- 危机干预节点
- 练习建议节点
"""
import asyncio
import json
import re
from pathlib import Path
from typing import Literal, Optional

from sqlalchemy import select

from src.agent.llm import MindMirrorLLM, get_llm
from src.models.database import async_session_factory
from src.models.profile import PsychProfile
from src.services.notification import NotificationService
from src.utils.config import PROJECT_ROOT
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ======================================================================
# 全局单例（延迟初始化）
# ======================================================================
_llm: MindMirrorLLM | None = None
_system_prompt: str | None = None

# 文本情绪分析 — 关键词 / 情感词典（轻量级，不依赖外部模型）
_EMOTION_KEYWORDS: dict[str, list[str]] = {
    "sadness": ["难过", "伤心", "悲伤", "哭", "失落", "低落", "沮丧", "绝望", "无助",
                "孤独", "寂寞", "痛苦", "心碎", "崩溃", "委屈", "郁闷", "压抑", "忧伤"],
    "anxiety": ["焦虑", "紧张", "害怕", "恐惧", "担心", "不安", "慌", "怕", "压力",
                "失眠", "忐忑", "心慌", "惊恐", "担忧", "烦躁", "坐立不安"],
    "anger": ["生气", "愤怒", "气死", "烦", "讨厌", "恼火", "暴躁", "发火", "恨",
              "不公", "欺负", "受不了", "无语", "崩溃"],
    "joy": ["开心", "高兴", "快乐", "幸福", "满足", "感恩", "兴奋", "期待", "温暖",
            "治愈", "放松", "舒服", "自信", "有动力", "棒", "好"],
    "neutral": ["还行", "一般", "还好", "没什么", "普通", "正常"],
}

# 危机关键词 — 用于危机检查节点
CRISIS_KEYWORDS: list[str] = [
    "自杀", "自残", "不想活", "跳楼", "割腕", "结束生命", "去死", "死了算了",
    "活着没意思", "不想活了", "轻生", "寻死", "了结", "吞药", "上吊", "烧炭",
    "自我伤害", "伤害自己", "不想醒来", "消失", "世界没有我会更好",
    "活不下去", "没有意义", "累了不想活", "解脱", "最后", "遗书", "遗言",
    "告别", "再见了", "对不起大家", "是我的错我不该活着",
]

# 危机干预回复模板
CRISIS_RESPONSE_TEMPLATE = """我能感受到你现在正经历着非常艰难的时刻，你的感受对我来说非常重要。

**请记住，你不是一个人在面对这些。**

我虽然是 AI，但我真心希望你能获得专业的帮助。请你现在就拨打以下热线，会有专业的心理咨询师帮助你：

🔴 **全国心理援助热线**：400-161-9995（24小时）
🔴 **北京心理危机研究与干预中心**：010-82951332
🔴 **生命热线**：400-821-1215
🔴 **紧急求助**：120 或 110

如果你身边有信任的人——家人、朋友、老师——请告诉他们你现在的感受。

**你的生命是珍贵的，这些痛苦的感受是可以被帮助和改善的。** 请给自己一个机会，让专业的人来帮助你度过这个艰难的时刻。

我会一直在这里陪着你。💙"""


# 全局通知服务单例（延迟初始化）
_notification_service: Optional[NotificationService] = None


def _get_notification_service() -> NotificationService:
    """获取全局 NotificationService 单例"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service


def _get_llm() -> MindMirrorLLM:
    """获取全局 LLM 实例（延迟初始化）"""
    global _llm
    if _llm is None:
        _llm = get_llm()
    return _llm


def _get_system_prompt() -> str:
    """加载 System Prompt（延迟加载 + 缓存）"""
    global _system_prompt
    if _system_prompt is not None:
        return _system_prompt

    prompt_path = PROJECT_ROOT / "configs" / "prompts" / "therapist.md"
    try:
        _system_prompt = prompt_path.read_text(encoding="utf-8")
        logger.info("已加载 System Prompt: %s (%d 字符)", prompt_path, len(_system_prompt))
    except FileNotFoundError:
        logger.warning("System Prompt 文件不存在: %s，使用默认提示", prompt_path)
        _system_prompt = (
            "你是 MindMirror，一位温暖、专业的 AI 心理健康伙伴。"
            "请以温暖、同理心、非评判性的态度与用户交流。"
        )
    return _system_prompt


def _analyze_text_emotion(text: str) -> dict:
    """基于关键词的文本情绪分析（轻量级）

    Args:
        text: 用户消息文本

    Returns:
        {"dominant_emotion": str, "score": float, "emotions": dict}
    """
    scores: dict[str, float] = {emotion: 0.0 for emotion in _EMOTION_KEYWORDS}

    for emotion, keywords in _EMOTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                scores[emotion] += 1.0

    total = sum(scores.values())
    if total == 0:
        return {
            "dominant_emotion": "neutral",
            "score": 0.5,
            "emotions": {"neutral": 1.0},
        }

    # 归一化
    normalized = {k: v / total for k, v in scores.items()}
    dominant = max(normalized, key=normalized.get)

    return {
        "dominant_emotion": dominant,
        "score": normalized[dominant],
        "emotions": normalized,
    }


# ======================================================================
# 节点函数
# ======================================================================


async def emotion_perception_node(state: dict) -> dict:
    """情绪感知节点

    - 从 state 获取用户消息
    - 调用文本情绪分析（基于关键词和情感词典）
    - 如果有外部情绪数据（视频/音频），合并使用
    - 更新 emotion_result 和 emotion_history
    """
    user_message = state.get("user_message", "")
    logger.info("情绪感知节点: 分析用户消息 (长度=%d)", len(user_message))

    # 文本情绪分析
    text_result = _analyze_text_emotion(user_message)

    # 合并外部情绪数据（如来自视频/音频分析）
    external_emotion = state.get("emotion_result")
    if external_emotion and isinstance(external_emotion, dict):
        # 如果外部数据有 dominant_emotion，优先使用
        merged = {**text_result, **{
            k: v for k, v in external_emotion.items() if v is not None
        }}
        logger.info("合并外部情绪数据: dominant=%s", merged.get("dominant_emotion"))
    else:
        merged = text_result

    # 更新情绪历史（保留最近 10 条）
    history = list(state.get("emotion_history") or [])
    history.append({
        "turn": state.get("turn_count", 0),
        "emotion": merged["dominant_emotion"],
        "score": merged["score"],
    })
    if len(history) > 10:
        history = history[-10:]

    logger.info("情绪分析结果: %s (%.2f)", merged["dominant_emotion"], merged["score"])

    return {
        "emotion_result": merged,
        "emotion_history": history,
    }


async def crisis_check_node(state: dict) -> dict:
    """危机检查节点

    - 分析用户消息中的危机关键词
    - 结合情绪分析结果判断风险等级
    - 设置 risk_level 和 crisis_signals
    """
    user_message = state.get("user_message", "")
    emotion_result = state.get("emotion_result") or {}
    logger.info("危机检查节点: 评估风险等级")

    # 检测危机关键词
    found_signals: list[str] = []
    for keyword in CRISIS_KEYWORDS:
        if keyword in user_message:
            found_signals.append(keyword)

    # 结合情绪分析判断风险等级
    dominant_emotion = emotion_result.get("dominant_emotion", "neutral")
    emotion_score = emotion_result.get("score", 0)

    if found_signals:
        # 有明确危机关键词
        if len(found_signals) >= 3:
            risk_level = "crisis"
        elif len(found_signals) >= 2:
            risk_level = "high"
        else:
            risk_level = "medium"
        logger.warning("检测到危机信号: %s, 风险等级: %s", found_signals, risk_level)
    elif dominant_emotion == "sadness" and emotion_score > 0.7:
        # 高度悲伤但无明确危机信号
        risk_level = "medium"
        found_signals.append("高悲伤情绪")
        logger.warning("高悲伤情绪检测, 风险等级: medium")
    elif dominant_emotion in ("anxiety", "anger") and emotion_score > 0.8:
        risk_level = "medium"
        found_signals.append(f"高{dominant_emotion}情绪")
        logger.warning("高强度负面情绪检测, 风险等级: medium")
    else:
        risk_level = "low"

    return {
        "risk_level": risk_level,
        "crisis_signals": found_signals,
    }


def crisis_router(state: dict) -> Literal["crisis_intervention", "knowledge_retrieval"]:
    """危机路由 — 决定走危机干预还是正常对话

    Args:
        state: 当前对话状态

    Returns:
        下一个节点名称
    """
    risk_level = state.get("risk_level", "low")

    if risk_level in ("high", "crisis"):
        logger.warning("危机路由: 风险等级 %s → 进入危机干预", risk_level)
        return "crisis_intervention"

    logger.info("危机路由: 风险等级 %s → 进入正常对话流程", risk_level)
    return "knowledge_retrieval"


async def knowledge_retrieval_node(state: dict) -> dict:
    """知识检索节点

    - 基于用户消息和情绪状态构建检索 query
    - 调用 KnowledgeManager.query()
    - 选择最相关的知识片段
    """
    user_message = state.get("user_message", "")
    emotion_result = state.get("emotion_result") or {}
    dominant = emotion_result.get("dominant_emotion", "neutral")
    logger.info("知识检索节点: 检索相关知识")

    # 构建检索 query — 结合用户消息和情绪
    query_parts = [user_message]
    if dominant != "neutral":
        query_parts.append(f"{dominant}情绪 心理疏导")

    query = " ".join(query_parts)

    # 尝试从知识库检索
    try:
        from src.knowledge.manager import KnowledgeManager

        km = KnowledgeManager()
        await km.initialize()
        documents = await km.query(question=query, top_k=3)
        snippets = [doc.page_content for doc in documents if doc.page_content]
        logger.info("知识检索: 获取到 %d 个知识片段", len(snippets))
    except Exception as e:
        logger.warning("知识检索失败（降级处理）: %s", e)
        snippets = []

    return {
        "retrieved_knowledge": snippets,
    }


async def _get_profile_context(user_id: Optional[int]) -> Optional[str]:
    """从数据库查询用户心理档案并构建上下文字符串

    Args:
        user_id: 用户 ID，为 None 时返回 None

    Returns:
        格式化的档案上下文字符串，或 None（无档案或查询失败）
    """
    if not user_id:
        return None

    try:
        async with async_session_factory() as session:
            result = await session.execute(
                select(PsychProfile).where(PsychProfile.user_id == user_id)
            )
            profile = result.scalar_one_or_none()
            if profile is None:
                return None

            # 解析各 JSON 字段
            def _safe_loads(raw, default):
                if not raw:
                    return default
                try:
                    return json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    return default

            personality = _safe_loads(profile.personality_traits, {})
            issues = _safe_loads(profile.issue_history, [])
            interests = _safe_loads(profile.interests, [])
            coping = _safe_loads(profile.coping_styles, {})

            # 构建上下文片段
            parts = []

            # 性格特征
            if personality:
                trait_labels = {
                    "introversion": "内向",
                    "extroversion": "外向",
                    "sensitivity": "敏感度",
                    "openness": "开放性",
                    "neuroticism": "情绪波动性",
                }
                trait_descs = []
                for trait, value in personality.items():
                    if isinstance(value, (int, float)) and 0 <= value <= 1:
                        label = trait_labels.get(trait, trait)
                        level = "高" if value > 0.6 else ("中" if value > 0.3 else "低")
                        trait_descs.append(f"{label}{level}")
                if trait_descs:
                    parts.append(f"性格特征: {'、'.join(trait_descs)}")

            # 活跃问题
            active_issues = [
                item.get("issue", "")
                for item in issues
                if isinstance(item, dict) and item.get("status") == "ongoing"
            ]
            if active_issues:
                parts.append(f"正在经历的问题: {'、'.join(active_issues)}")

            # 兴趣爱好
            if interests:
                parts.append(f"兴趣爱好: {'、'.join(interests[:5])}")

            # 应对方式
            if coping and isinstance(coping, dict):
                preferred = coping.get("preferred")
                if preferred:
                    parts.append(f"偏好应对方式: {preferred}")

            if not parts:
                return None

            return "[用户心理档案]\n" + "\n".join(parts)

    except Exception as e:
        logger.warning("查询用户心理档案失败 (user_id=%s): %s", user_id, e)
        return None


async def response_generation_node(state: dict) -> dict:
    """回复生成节点

    - 组装 System Prompt（从 therapist.md 加载）
    - 将情绪状态、知识片段、对话历史作为上下文
    - 如果 state 中有 user_id，查询用户心理档案并注入上下文
    - 每 5 轮对话后自动触发档案更新
    - 调用 LLM 生成回复
    """
    user_message = state.get("user_message", "")
    emotion_result = state.get("emotion_result")
    knowledge = state.get("retrieved_knowledge") or []
    history = state.get("messages") or []
    user_id = state.get("user_id")
    logger.info("回复生成节点: 生成 AI 回复 (user_id=%s)", user_id)

    # 加载 System Prompt
    system_prompt = _get_system_prompt()

    # 查询用户心理档案并注入上下文
    if user_id:
        profile_context = await _get_profile_context(user_id)
        if profile_context:
            system_prompt = system_prompt + "\n\n" + profile_context
            logger.info("已注入用户 %d 的心理档案上下文", user_id)

    # 构建情绪上下文
    emotion_context = None
    if emotion_result:
        emotion_context = {
            "dominant_emotion": emotion_result.get("dominant_emotion", "neutral"),
            "score": emotion_result.get("score", 0),
        }
        # 添加情绪历史摘要
        emotion_history = state.get("emotion_history") or []
        if len(emotion_history) >= 3:
            recent = emotion_history[-3:]
            trend = " → ".join(e.get("emotion", "?") for e in recent)
            emotion_context["history_summary"] = f"近期情绪变化: {trend}"

    # 调用 LLM 生成回复
    llm = _get_llm()
    response = await llm.chat_with_context(
        user_message=user_message,
        emotion_context=emotion_context,
        knowledge_context=knowledge,
        history=history,
        system_prompt=system_prompt,
    )

    # 更新对话历史
    messages = list(history)
    messages.append({"role": "user", "content": user_message})
    messages.append({"role": "assistant", "content": response})

    # 限制历史长度（保留最近 20 条消息）
    if len(messages) > 20:
        messages = messages[-20:]

    turn_count = state.get("turn_count", 0) + 1

    # 每 5 轮对话后自动更新心理档案
    if user_id and turn_count % 5 == 0:
        try:
            from src.services.profile_service import update_profile_from_conversation

            logger.info("触发档案自动更新 (user_id=%d, turn=%d)", user_id, turn_count)
            await update_profile_from_conversation(
                user_id=user_id,
                messages=messages,
                emotion_data=emotion_result,
            )
        except Exception as e:
            logger.warning("档案自动更新失败: %s", e)

    logger.info("回复生成完成 (turn=%d, 回复长度=%d)", turn_count, len(response))

    return {
        "response": response,
        "messages": messages,
        "turn_count": turn_count,
    }


async def crisis_intervention_node(state: dict) -> dict:
    """危机干预节点

    - 生成危机干预回复（包含热线信息）
    - 设置 needs_human_intervention = True
    - 使用特定的危机话术模板
    """
    user_message = state.get("user_message", "")
    crisis_signals = state.get("crisis_signals") or []
    risk_level = state.get("risk_level", "high")
    history = state.get("messages") or []
    logger.warning("危机干预节点: 风险等级=%s, 信号=%s", risk_level, crisis_signals)

    if risk_level == "crisis":
        # 严重危机 — 直接使用模板
        response = CRISIS_RESPONSE_TEMPLATE
    else:
        # 中等风险 — 让 LLM 生成更个性化的关怀回复，附加热线信息
        system_prompt = _get_system_prompt()
        crisis_addendum = (
            "\n\n[重要提示] 系统检测到用户可能处于心理危机状态。"
            "请在回复中：1) 表达深切的关心和同理心；"
            "2) 强烈建议拨打心理援助热线 400-161-9995；"
            "3) 鼓励用户与身边信任的人交流。"
        )

        llm = _get_llm()
        response = await llm.chat_with_context(
            user_message=user_message,
            emotion_context=state.get("emotion_result"),
            knowledge_context=[],
            history=history,
            system_prompt=system_prompt + crisis_addendum,
        )

        # 确保回复中包含热线信息
        if "400-161-9995" not in response:
            response += (
                "\n\n---\n🔴 如果你感到无法承受，请随时拨打"
                "**全国心理援助热线：400-161-9995**（24小时），"
                "会有专业的心理咨询师帮助你。"
            )

    # 异步通知家长（仅 high/crisis，不阻塞主对话流程）
    user_id = state.get("user_id")
    if user_id and risk_level in ("high", "crisis"):
        notification_service = _get_notification_service()
        alert_type = "crisis" if risk_level == "crisis" else "high_risk"
        severity = "critical" if risk_level == "crisis" else "high"
        severity_cn = "紧急" if risk_level == "crisis" else "高风险"
        alert_message = (
            f"检测到{severity_cn}心理风险信号："
            f"{', '.join(crisis_signals) if crisis_signals else '情绪波动剧烈'}。"
            "建议尽快关注孩子状态。"
        )
        try:
            asyncio.create_task(
                notification_service.notify_parent(
                    child_user_id=user_id,
                    alert_type=alert_type,
                    message=alert_message,
                    severity=severity,
                )
            )
            logger.info("已异步触发家长通知 (user_id=%d, risk=%s)", user_id, risk_level)
        except Exception as e:
            logger.warning("触发家长通知失败 (user_id=%d): %s", user_id, e)

    # 更新对话历史
    messages = list(history)
    messages.append({"role": "user", "content": user_message})
    messages.append({"role": "assistant", "content": response})

    turn_count = state.get("turn_count", 0) + 1

    return {
        "response": response,
        "messages": messages,
        "turn_count": turn_count,
        "needs_human_intervention": True,
    }


async def exercise_suggestion_node(state: dict) -> dict:
    """练习建议节点

    - 基于情绪状态推荐 CBT 练习
    - 从知识库检索相关练习
    """
    emotion_result = state.get("emotion_result") or {}
    dominant = emotion_result.get("dominant_emotion", "neutral")
    logger.info("练习建议节点: dominant_emotion=%s", dominant)

    # 基于情绪类型的 CBT 练习推荐映射
    exercise_map: dict[str, list[str]] = {
        "sadness": [
            "行为激活：列出3件能让你感到一点点开心的小事",
            "感恩日记：写下今天值得感恩的3件事",
            "正念呼吸：进行5分钟的专注呼吸练习",
        ],
        "anxiety": [
            "腹式呼吸：4-7-8 呼吸法（吸气4秒、屏息7秒、呼气8秒）",
            "渐进式肌肉放松：从脚趾到头顶逐步紧张-放松每组肌肉",
            "担忧时间：设定每天15分钟的专属担忧时间",
        ],
        "anger": [
            "情绪记录：写下触发愤怒的事件、想法和感受",
            "认知重评：尝试从对方的角度思考这件事",
            "冷却技巧：深呼吸并倒数从10到1",
        ],
        "joy": [
            "积极体验强化：细细品味此刻的好感觉，记录在日记中",
            "善意行动：为他人做一件小小的善事",
        ],
        "neutral": [
            "情绪觉察：花几分钟感受当下的身体和情绪状态",
            "价值探索：思考对你来说最重要的是什么",
        ],
    }

    suggested = exercise_map.get(dominant, exercise_map["neutral"])

    return {
        "suggested_exercises": suggested,
    }
