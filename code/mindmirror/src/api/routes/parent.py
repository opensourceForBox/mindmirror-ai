"""家长端 API 路由

提供家长查看绑定孩子情绪摘要、告警、心理档案摘要和仪表盘的能力。
"""
import json
import logging
from datetime import date, datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.alert import Alert
from src.models.checkin import DailyCheckin
from src.models.conversation import Conversation
from src.models.database import get_db
from src.models.profile import PsychProfile
from src.models.user import User
from src.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/parent", tags=["家长端"])


# ─── 辅助函数 ──────────────────────────────────────────────────────────────────


def _safe_json_loads(raw: str | None, default: Any) -> Any:
    """安全解析 JSON 字符串，失败时返回默认值"""
    if not raw:
        return default
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return default


def _parse_emotion_summary(conv: Conversation) -> dict:
    """解析对话的情绪摘要"""
    summary = _safe_json_loads(conv.emotion_summary, {})
    if isinstance(summary, dict):
        return summary
    return {}


async def _verify_parent_child(
    parent: User, child_id: int, db: AsyncSession
) -> User:
    """验证调用者是家长且 child_id 是其绑定的孩子"""
    if parent.role != "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅家长可访问此接口",
        )

    result = await db.execute(select(User).where(User.id == child_id))
    child = result.scalar_one_or_none()
    if child is None or child.parent_id != parent.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该孩子或无权查看",
        )
    return child


async def _get_or_create_profile(db: AsyncSession, user_id: int) -> PsychProfile:
    """获取或创建用户心理档案"""
    result = await db.execute(
        select(PsychProfile).where(PsychProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = PsychProfile(user_id=user_id)
        db.add(profile)
        await db.flush()
        await db.refresh(profile)
    return profile


# ─── 响应模型 ──────────────────────────────────────────────────────────────────


class ChildInfo(BaseModel):
    """孩子基本信息"""

    id: int
    username: str
    email: str
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}


class EmotionSummaryResponse(BaseModel):
    """孩子近7天情绪摘要"""

    child_name: str
    avg_mood: Optional[float] = None
    mood_trend: str = "stable"
    dominant_emotions: list[str] = Field(default_factory=list)
    conversation_count: int = 0


class AlertItem(BaseModel):
    """告警列表项"""

    id: int
    alert_type: str
    severity: str
    message: str
    is_read: bool
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}


class ProfileSummarySanitized(BaseModel):
    """脱敏版心理档案摘要"""

    user_id: int
    username: str
    personality_summary: str
    active_issues: list[str]
    interests: list[str]
    coping_styles: dict
    total_conversations: int
    last_updated: Optional[str] = None


class ChildDashboardCard(BaseModel):
    """仪表盘中的孩子卡片"""

    child: ChildInfo
    unread_alerts: int
    latest_alert: Optional[AlertItem] = None
    emotion_summary: EmotionSummaryResponse


class DashboardResponse(BaseModel):
    """家长仪表盘综合数据"""

    parent_name: str
    children: list[ChildDashboardCard]


class MoodHistoryPoint(BaseModel):
    """单天心情分数"""

    date: str
    mood_score: int
    mood_note: Optional[str] = None


# ─── 路由 ──────────────────────────────────────────────────────────────────────


@router.get("/children", response_model=list[ChildInfo])
async def get_children(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前家长绑定的孩子列表"""
    if current_user.role != "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅家长可访问此接口",
        )

    result = await db.execute(
        select(User).where(User.parent_id == current_user.id).order_by(User.id)
    )
    children = result.scalars().all()

    return [
        {
            "id": child.id,
            "username": child.username,
            "email": child.email,
            "created_at": child.created_at.isoformat() if child.created_at else None,
        }
        for child in children
    ]


@router.get("/child/{child_id}/emotion-summary", response_model=EmotionSummaryResponse)
async def get_child_emotion_summary(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取孩子近7天情绪摘要

    基于每日签到心情分与会话情绪摘要聚合，不暴露具体对话内容。
    """
    child = await _verify_parent_child(current_user, child_id, db)

    since_date = date.today() - timedelta(days=6)
    since_dt = datetime.utcnow() - timedelta(days=7)

    # 近7天签到（按 date 列查询更语义化）
    checkin_result = await db.execute(
        select(DailyCheckin)
        .where(
            DailyCheckin.user_id == child_id,
            DailyCheckin.date >= since_date,
        )
        .order_by(DailyCheckin.date)
    )
    checkins = checkin_result.scalars().all()

    # 近7天会话（仅取元数据，不读取 messages）
    conv_result = await db.execute(
        select(Conversation)
        .where(
            Conversation.user_id == child_id,
            Conversation.created_at >= since_dt,
        )
        .order_by(desc(Conversation.created_at))
    )
    conversations = conv_result.scalars().all()

    # 平均心情（1-5 分映射到 0-10 分，便于展示）
    avg_mood: Optional[float] = None
    mood_trend = "stable"
    if checkins:
        scores = [c.mood_score for c in checkins]
        avg_mood = round(sum(scores) / len(scores) * 2, 1)
        if len(scores) >= 2:
            first_half = scores[: len(scores) // 2]
            second_half = scores[len(scores) // 2 :]
            diff = sum(second_half) / len(second_half) - sum(first_half) / len(first_half)
            if diff > 0.3:
                mood_trend = "improving"
            elif diff < -0.3:
                mood_trend = "declining"
            else:
                mood_trend = "stable"

    # 主导情绪统计
    emotion_counts: dict[str, int] = {}
    for conv in conversations:
        summary = _parse_emotion_summary(conv)
        dominant = summary.get("dominant_emotion") if isinstance(summary, dict) else None
        if dominant:
            emotion_counts[dominant] = emotion_counts.get(dominant, 0) + 1
    dominant_emotions = sorted(
        emotion_counts.keys(), key=lambda e: emotion_counts[e], reverse=True
    )[:3]

    return {
        "child_name": child.username,
        "avg_mood": avg_mood,
        "mood_trend": mood_trend,
        "dominant_emotions": dominant_emotions,
        "conversation_count": len(conversations),
    }


@router.get("/child/{child_id}/alerts", response_model=list[AlertItem])
async def get_child_alerts(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取孩子风险告警列表（risk_level >= medium）"""
    await _verify_parent_child(current_user, child_id, db)

    result = await db.execute(
        select(Alert)
        .where(
            Alert.user_id == child_id,
            Alert.severity.in_(["medium", "high", "critical"]),
        )
        .order_by(desc(Alert.created_at))
    )
    alerts = result.scalars().all()

    return [
        {
            "id": alert.id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "message": alert.message,
            "is_read": alert.is_read,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
        }
        for alert in alerts
    ]


@router.post("/child/{child_id}/alerts/{alert_id}/read")
async def mark_alert_read(
    child_id: int,
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """标记单条告警为已读"""
    await _verify_parent_child(current_user, child_id, db)

    result = await db.execute(
        select(Alert).where(Alert.id == alert_id, Alert.user_id == child_id)
    )
    alert = result.scalar_one_or_none()
    if alert is None:
        raise HTTPException(status_code=404, detail="告警不存在")

    alert.is_read = True
    await db.flush()
    return {"id": alert.id, "is_read": alert.is_read}


@router.get("/child/{child_id}/profile", response_model=ProfileSummarySanitized)
async def get_child_profile_summary(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取孩子心理档案摘要（脱敏版，不含对话详情）"""
    child = await _verify_parent_child(current_user, child_id, db)

    profile = await _get_or_create_profile(db, child_id)

    personality = _safe_json_loads(profile.personality_traits, {})
    issues = _safe_json_loads(profile.issue_history, [])
    interests = _safe_json_loads(profile.interests, [])
    coping = _safe_json_loads(profile.coping_styles, {})

    # 性格描述
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

    # 活跃问题
    active_issues = [
        item.get("issue", "未知")
        for item in issues
        if isinstance(item, dict) and item.get("status") == "ongoing"
    ]

    # 统计对话数
    count_result = await db.execute(
        select(func.count(Conversation.id)).where(Conversation.user_id == child_id)
    )
    total_conversations = count_result.scalar() or 0

    return {
        "user_id": child.id,
        "username": child.username,
        "personality_summary": (
            "、".join(personality_parts) if personality_parts else "尚无足够数据"
        ),
        "active_issues": active_issues,
        "interests": interests,
        "coping_styles": coping if isinstance(coping, dict) else {},
        "total_conversations": total_conversations,
        "last_updated": profile.updated_at.isoformat() if profile.updated_at else None,
    }


@router.get("/child/{child_id}/mood-history", response_model=list[MoodHistoryPoint])
async def get_child_mood_history(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取孩子近7天心情历史（用于情绪趋势折线图）"""
    await _verify_parent_child(current_user, child_id, db)

    since = date.today() - timedelta(days=6)
    result = await db.execute(
        select(DailyCheckin)
        .where(
            DailyCheckin.user_id == child_id,
            DailyCheckin.date >= since,
        )
        .order_by(DailyCheckin.date)
    )
    checkins = result.scalars().all()

    return [
        {
            "date": c.date.isoformat(),
            "mood_score": c.mood_score,
            "mood_note": c.mood_note,
        }
        for c in checkins
    ]


@router.get("/dashboard", response_model=DashboardResponse)
async def get_parent_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """家长仪表盘综合数据

    返回家长所有绑定孩子的情绪摘要、未读告警与最近告警。
    """
    if current_user.role != "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅家长可访问此接口",
        )

    result = await db.execute(
        select(User).where(User.parent_id == current_user.id).order_by(User.id)
    )
    children = result.scalars().all()

    cards: list[dict] = []
    for child in children:
        # 未读告警数
        unread_result = await db.execute(
            select(func.count(Alert.id)).where(
                Alert.user_id == child.id,
                Alert.is_read.is_(False),
                Alert.severity.in_(["medium", "high", "critical"]),
            )
        )
        unread_alerts = unread_result.scalar() or 0

        # 最新告警
        latest_alert = None
        latest_result = await db.execute(
            select(Alert)
            .where(
                Alert.user_id == child.id,
                Alert.severity.in_(["medium", "high", "critical"]),
            )
            .order_by(desc(Alert.created_at))
            .limit(1)
        )
        alert = latest_result.scalar_one_or_none()
        if alert:
            latest_alert = {
                "id": alert.id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message,
                "is_read": alert.is_read,
                "created_at": alert.created_at.isoformat() if alert.created_at else None,
            }

        # 情绪摘要
        since_date = date.today() - timedelta(days=6)
        since_dt = datetime.utcnow() - timedelta(days=7)
        checkin_result = await db.execute(
            select(DailyCheckin)
            .where(
                DailyCheckin.user_id == child.id,
                DailyCheckin.date >= since_date,
            )
            .order_by(DailyCheckin.date)
        )
        checkins = checkin_result.scalars().all()

        conv_result = await db.execute(
            select(func.count(Conversation.id)).where(
                Conversation.user_id == child.id,
                Conversation.created_at >= since_dt,
            )
        )
        conversation_count = conv_result.scalar() or 0

        avg_mood: Optional[float] = None
        mood_trend = "stable"
        if checkins:
            scores = [c.mood_score for c in checkins]
            avg_mood = round(sum(scores) / len(scores) * 2, 1)
            if len(scores) >= 2:
                mid = len(scores) // 2
                diff = sum(scores[mid:]) / len(scores[mid:]) - sum(scores[:mid]) / len(scores[:mid])
                if diff > 0.3:
                    mood_trend = "improving"
                elif diff < -0.3:
                    mood_trend = "declining"

        emotion_summary = {
            "child_name": child.username,
            "avg_mood": avg_mood,
            "mood_trend": mood_trend,
            "dominant_emotions": [],
            "conversation_count": conversation_count,
        }

        cards.append(
            {
                "child": {
                    "id": child.id,
                    "username": child.username,
                    "email": child.email,
                    "created_at": child.created_at.isoformat() if child.created_at else None,
                },
                "unread_alerts": unread_alerts,
                "latest_alert": latest_alert,
                "emotion_summary": emotion_summary,
            }
        )

    return {
        "parent_name": current_user.username,
        "children": cards,
    }
