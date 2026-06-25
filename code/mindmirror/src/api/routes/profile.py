"""心理档案 API 路由

提供用户长期心理档案的查询、更新、对话历史检索和档案摘要功能。
"""
import json
import logging
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.conversation import Conversation
from src.models.database import get_db
from src.models.profile import PsychProfile
from src.models.user import User
from src.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profile", tags=["心理档案"])


# ─── 辅助函数 ──────────────────────────────────────────────────────────────────


def _safe_json_loads(raw: str | None, default: Any) -> Any:
    """安全解析 JSON 字符串，失败时返回默认值"""
    if not raw:
        return default
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        logger.warning("JSON 解析失败，使用默认值: %s", raw[:100])
        return default


def _profile_to_dict(profile: PsychProfile) -> dict:
    """将 PsychProfile ORM 对象转为可序列化的字典"""
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "personality_traits": _safe_json_loads(profile.personality_traits, {}),
        "issue_history": _safe_json_loads(profile.issue_history, []),
        "progress_notes": _safe_json_loads(profile.progress_notes, []),
        "interests": _safe_json_loads(profile.interests, []),
        "coping_styles": _safe_json_loads(profile.coping_styles, {}),
        "created_at": profile.created_at.isoformat() if profile.created_at else None,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
    }


async def _get_or_create_profile(
    db: AsyncSession, user_id: int
) -> PsychProfile:
    """获取或创建用户心理档案"""
    result = await db.execute(
        select(PsychProfile).where(PsychProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = PsychProfile(user_id=user_id)
        db.add(profile)
        await db.flush()
        logger.info("为用户 %d 创建了新的心理档案", user_id)
    return profile


# ─── 请求 / 响应模型 ────────────────────────────────────────────────────────────


class ProfileUpdateRequest(BaseModel):
    """档案更新请求 — 所有字段可选，仅更新提供的字段"""

    personality_traits: Optional[dict] = Field(
        None, description='性格特征, 如 {"introversion": 0.7, "sensitivity": 0.8}'
    )
    issue_history: Optional[list[dict]] = Field(
        None, description='问题历史, 如 [{"issue": "学业压力", "first_seen": "2024-01", "status": "ongoing"}]'
    )
    progress_notes: Optional[list[str]] = Field(
        None, description="进展记录列表"
    )
    interests: Optional[list[str]] = Field(None, description="兴趣爱好列表")
    coping_styles: Optional[dict] = Field(
        None, description='常用应对方式, 如 {"preferred": "倾诉", "avoidance": 0.3}'
    )


class ConversationSummary(BaseModel):
    """对话历史摘要（列表项）"""

    id: int
    session_id: str
    topic: Optional[str] = None
    emotion_summary: Optional[dict] = None
    message_count: int = 0
    duration_minutes: Optional[int] = None
    created_at: str

    model_config = {"from_attributes": True}


class ProfileSummaryResponse(BaseModel):
    """档案摘要响应"""

    user_id: int
    username: str
    personality_summary: str
    active_issues: list[str]
    interests: list[str]
    coping_styles: dict
    total_conversations: int
    last_updated: Optional[str] = None


# ─── 路由 ──────────────────────────────────────────────────────────────────────


@router.get("/")
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的心理档案

    如果用户还没有档案，会自动创建一个空档案。
    """
    profile = await _get_or_create_profile(db, current_user.id)
    return _profile_to_dict(profile)


@router.put("/")
async def update_profile(
    body: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新当前用户的心理档案

    所有字段都是可选的，仅更新提供的字段。
    progress_notes 字段为追加模式（不覆盖已有记录）。
    """
    profile = await _get_or_create_profile(db, current_user.id)

    if body.personality_traits is not None:
        # 合并而非覆盖已有性格特征
        existing = _safe_json_loads(profile.personality_traits, {})
        existing.update(body.personality_traits)
        profile.personality_traits = json.dumps(existing, ensure_ascii=False)

    if body.issue_history is not None:
        # 合并问题历史，避免重复
        existing = _safe_json_loads(profile.issue_history, [])
        existing_issues = {item.get("issue") for item in existing if isinstance(item, dict)}
        for new_item in body.issue_history:
            if isinstance(new_item, dict) and new_item.get("issue") not in existing_issues:
                existing.append(new_item)
        profile.issue_history = json.dumps(existing, ensure_ascii=False)

    if body.progress_notes is not None:
        # progress_notes 为追加模式
        existing = _safe_json_loads(profile.progress_notes, [])
        existing.extend(body.progress_notes)
        profile.progress_notes = json.dumps(existing, ensure_ascii=False)

    if body.interests is not None:
        # 合并兴趣，去重
        existing = _safe_json_loads(profile.interests, [])
        existing_set = set(existing)
        for interest in body.interests:
            if interest not in existing_set:
                existing.append(interest)
        profile.interests = json.dumps(existing, ensure_ascii=False)

    if body.coping_styles is not None:
        # 合并应对方式
        existing = _safe_json_loads(profile.coping_styles, {})
        existing.update(body.coping_styles)
        profile.coping_styles = json.dumps(existing, ensure_ascii=False)

    await db.flush()
    await db.refresh(profile)
    logger.info("用户 %d 更新了心理档案", current_user.id)

    return _profile_to_dict(profile)


@router.get("/conversations")
async def get_conversations(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的对话历史列表（分页）"""
    offset = (page - 1) * page_size

    # 查询总数
    count_result = await db.execute(
        select(Conversation).where(Conversation.user_id == current_user.id)
    )
    total = len(count_result.scalars().all())

    # 查询当前页
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(desc(Conversation.created_at))
        .offset(offset)
        .limit(page_size)
    )
    conversations = result.scalars().all()

    items = []
    for conv in conversations:
        messages = _safe_json_loads(conv.messages, [])
        items.append(
            {
                "id": conv.id,
                "session_id": conv.session_id,
                "topic": conv.topic,
                "emotion_summary": _safe_json_loads(conv.emotion_summary, None),
                "message_count": len(messages) if isinstance(messages, list) else 0,
                "duration_minutes": conv.duration_minutes,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
            }
        )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
    }


@router.get("/summary")
async def get_profile_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取档案摘要（用于前端展示）

    返回格式化的档案摘要，包括性格描述、活跃问题、兴趣爱好等。
    """
    profile = await _get_or_create_profile(db, current_user.id)

    # 解析档案数据
    personality = _safe_json_loads(profile.personality_traits, {})
    issues = _safe_json_loads(profile.issue_history, [])
    interests = _safe_json_loads(profile.interests, [])
    coping = _safe_json_loads(profile.coping_styles, {})

    # 生成性格描述
    personality_parts = []
    trait_labels = {
        "introversion": "内向",
        "extroversion": "外向",
        "sensitivity": "敏感度",
        "openness": "开放性",
        "conscientiousness": "尽责性",
        "agreeableness": "宜人性",
        "neuroticism": "神经质",
    }
    for trait, value in personality.items():
        if isinstance(value, (int, float)):
            label = trait_labels.get(trait, trait)
            level = "高" if value > 0.6 else ("中" if value > 0.3 else "低")
            personality_parts.append(f"{label}{level}({value:.1f})")

    # 提取活跃问题
    active_issues = [
        item.get("issue", "未知")
        for item in issues
        if isinstance(item, dict) and item.get("status") == "ongoing"
    ]

    # 统计对话数
    count_result = await db.execute(
        select(Conversation).where(Conversation.user_id == current_user.id)
    )
    total_conversations = len(count_result.scalars().all())

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "personality_summary": "、".join(personality_parts) if personality_parts else "尚无足够数据",
        "active_issues": active_issues,
        "interests": interests,
        "coping_styles": coping,
        "total_conversations": total_conversations,
        "last_updated": profile.updated_at.isoformat() if profile.updated_at else None,
    }
