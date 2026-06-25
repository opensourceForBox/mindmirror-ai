"""心理档案服务

基于对话内容自动更新用户心理档案。
每 5 轮对话后调用 LLM 总结新发现的信息（性格特点、问题、进展），
增量合并到已有档案中（不覆盖已有信息）。
"""
import json
import logging
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.agent.llm import MindMirrorLLM, get_llm
from src.models.database import async_session_factory
from src.models.profile import PsychProfile
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 每 N 轮对话后触发自动更新
UPDATE_INTERVAL = 5

# LLM 总结提示词
_SUMMARY_SYSTEM_PROMPT = """你是一位专业的心理分析师。你的任务是从对话记录中提取用户的心理特征信息，并以严格的 JSON 格式输出。

请分析对话内容，提取以下信息（如果对话中没有体现某个方面，对应字段使用 null）：

{
  "personality_traits": {
    "introversion": 0.0-1.0 的数值,  // 内向程度, null 表示未检测到
    "sensitivity": 0.0-1.0 的数值,  // 敏感度
    "openness": 0.0-1.0 的数值,     // 开放性
    "neuroticism": 0.0-1.0 的数值   // 神经质倾向
  },
  "issues": [
    {
      "issue": "问题名称",
      "first_seen": "YYYY-MM",
      "status": "ongoing"  // 或 "resolved"
    }
  ],
  "progress": "本次对话中观察到的进展摘要（一句话）",
  "interests": ["兴趣1", "兴趣2"],
  "coping_styles": {
    "preferred": "偏好的应对方式",
    "avoidance": 0.0-1.0  // 回避倾向
  }
}

注意：
1. 只输出 JSON，不要包含任何其他文字
2. 数值请基于对话内容合理估计
3. 如果没有足够信息判断某个字段，使用 null
4. issues 中不要包含已有的问题，只提取新发现的"""


def _safe_json_loads(raw: str | None, default: Any) -> Any:
    """安全解析 JSON 字符串"""
    if not raw:
        return default
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return default


def _parse_llm_json(response: str) -> dict | None:
    """从 LLM 响应中提取 JSON

    LLM 可能在 JSON 前后添加 markdown 标记或其他文字，
    尝试提取第一个 { ... } 块。
    """
    # 尝试直接解析
    try:
        return json.loads(response)
    except (json.JSONDecodeError, TypeError):
        pass

    # 尝试提取 ```json ... ``` 块
    if "```json" in response:
        start = response.index("```json") + 7
        end = response.index("```", start)
        try:
            return json.loads(response[start:end].strip())
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

    # 尝试提取第一个 { 到最后一个 }
    first_brace = response.find("{")
    last_brace = response.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        try:
            return json.loads(response[first_brace : last_brace + 1])
        except (json.JSONDecodeError, TypeError):
            pass

    logger.warning("无法从 LLM 响应中提取 JSON: %s", response[:200])
    return None


def _merge_personality(
    existing: dict, new_traits: dict | None
) -> dict:
    """合并性格特征 — 新值覆盖旧值（仅当新值非 None）"""
    if not new_traits:
        return existing
    merged = dict(existing)
    for key, value in new_traits.items():
        if value is not None:
            merged[key] = value
    return merged


def _merge_issues(
    existing: list, new_issues: list | None
) -> list:
    """合并问题历史 — 去重，已有问题不重复添加"""
    if not new_issues:
        return existing
    existing_issues = {
        item.get("issue") for item in existing if isinstance(item, dict)
    }
    merged = list(existing)
    for item in new_issues:
        if isinstance(item, dict) and item.get("issue") not in existing_issues:
            merged.append(item)
    return merged


def _merge_interests(
    existing: list, new_interests: list | None
) -> list:
    """合并兴趣 — 去重"""
    if not new_interests:
        return existing
    merged = list(existing)
    for interest in new_interests:
        if interest and interest not in merged:
            merged.append(interest)
    return merged


def _merge_coping_styles(
    existing: dict, new_styles: dict | None
) -> dict:
    """合并应对方式 — 新值覆盖旧值"""
    if not new_styles:
        return existing
    merged = dict(existing)
    merged.update(new_styles)
    return merged


async def update_profile_from_conversation(
    user_id: int,
    messages: list[dict],
    emotion_data: Optional[dict] = None,
    db: Optional[AsyncSession] = None,
) -> Optional[PsychProfile]:
    """从对话内容自动更新用户心理档案

    使用 LLM 分析对话内容，提取心理特征信息，
    增量合并到已有档案中（不覆盖已有信息）。

    Args:
        user_id: 用户 ID
        messages: 对话消息列表 [{"role": "user/assistant", "content": "..."}]
        emotion_data: 本次对话的情绪摘要数据
        db: 可选的数据库会话，不提供则新建一个

    Returns:
        更新后的 PsychProfile，或 None 表示更新失败
    """
    if not messages or len(messages) < 2:
        logger.info("对话消息过少，跳过档案更新 (user_id=%d)", user_id)
        return None

    # 构建对话文本
    conversation_text = "\n".join(
        f"{'用户' if msg.get('role') == 'user' else 'AI'}: {msg.get('content', '')}"
        for msg in messages
    )

    # 构建情绪上下文
    emotion_context = ""
    if emotion_data:
        emotion_context = f"\n\n[情绪数据] {json.dumps(emotion_data, ensure_ascii=False)}"

    # 调用 LLM 分析
    llm = get_llm()
    if not llm.client:
        logger.warning("LLM 客户端未配置，跳过档案更新")
        return None

    try:
        response = await llm.chat(
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"请分析以下对话记录，提取用户的心理特征信息。\n\n"
                        f"--- 对话记录 ---\n{conversation_text}{emotion_context}\n--- 对话记录结束 ---"
                    ),
                }
            ],
            system_prompt=_SUMMARY_SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=1000,
        )
    except Exception as e:
        logger.error("LLM 分析对话失败: %s", e)
        return None

    # 解析 LLM 响应
    extracted = _parse_llm_json(response)
    if not extracted:
        logger.warning("LLM 响应解析失败，跳过档案更新")
        return None

    logger.info("LLM 提取的档案信息: %s", json.dumps(extracted, ensure_ascii=False)[:200])

    # 使用传入的 db 或新建会话
    if db is not None:
        return await _do_update(db, user_id, extracted)

    async with async_session_factory() as session:
        try:
            result = await _do_update(session, user_id, extracted)
            await session.commit()
            return result
        except Exception:
            await session.rollback()
            raise


async def _do_update(
    db: AsyncSession, user_id: int, extracted: dict
) -> PsychProfile:
    """执行实际的档案更新操作"""
    # 获取或创建档案
    result = await db.execute(
        select(PsychProfile).where(PsychProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = PsychProfile(user_id=user_id)
        db.add(profile)
        await db.flush()

    # 合并性格特征
    new_traits = extracted.get("personality_traits")
    if new_traits and isinstance(new_traits, dict):
        existing_traits = _safe_json_loads(profile.personality_traits, {})
        merged_traits = _merge_personality(existing_traits, new_traits)
        profile.personality_traits = json.dumps(merged_traits, ensure_ascii=False)

    # 合并问题历史
    new_issues = extracted.get("issues")
    if new_issues and isinstance(new_issues, list):
        existing_issues = _safe_json_loads(profile.issue_history, [])
        merged_issues = _merge_issues(existing_issues, new_issues)
        profile.issue_history = json.dumps(merged_issues, ensure_ascii=False)

    # 追加进展记录
    progress = extracted.get("progress")
    if progress and isinstance(progress, str) and progress.strip():
        existing_notes = _safe_json_loads(profile.progress_notes, [])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        existing_notes.append({"time": timestamp, "note": progress.strip()})
        profile.progress_notes = json.dumps(existing_notes, ensure_ascii=False)

    # 合并兴趣
    new_interests = extracted.get("interests")
    if new_interests and isinstance(new_interests, list):
        existing_interests = _safe_json_loads(profile.interests, [])
        merged_interests = _merge_interests(existing_interests, new_interests)
        profile.interests = json.dumps(merged_interests, ensure_ascii=False)

    # 合并应对方式
    new_coping = extracted.get("coping_styles")
    if new_coping and isinstance(new_coping, dict):
        existing_coping = _safe_json_loads(profile.coping_styles, {})
        merged_coping = _merge_coping_styles(existing_coping, new_coping)
        profile.coping_styles = json.dumps(merged_coping, ensure_ascii=False)

    await db.flush()
    await db.refresh(profile)
    logger.info("用户 %d 的心理档案已更新", user_id)
    return profile


def should_update_profile(turn_count: int) -> bool:
    """判断是否应该触发档案更新

    每 UPDATE_INTERVAL 轮对话触发一次。
    """
    return turn_count > 0 and turn_count % UPDATE_INTERVAL == 0
