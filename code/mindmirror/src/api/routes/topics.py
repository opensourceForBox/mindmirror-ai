"""话题推荐与每日签到 API"""
import logging
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.checkin import DailyCheckin
from src.models.database import get_db
from src.models.user import User
from src.services.topic_engine import topic_engine
from src.utils.auth import get_current_user, verify_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/topics", tags=["话题与签到"])

# 用于可选认证的 security（不自动报错）
_optional_security = HTTPBearer(auto_error=False)


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_optional_security),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """可选认证：有 token 就解析，没有就返回 None"""
    if credentials is None:
        return None
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            return None
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        return user if user and user.is_active else None
    except Exception:
        return None


# ─── 请求/响应模型 ────────────────────────────────────────────────────────────

class CheckinRequest(BaseModel):
    mood_score: int = Field(..., ge=1, le=5, description="心情评分 1-5")
    mood_note: str | None = Field(None, max_length=500, description="一句话描述")


class CheckinResponse(BaseModel):
    message: str
    streak_days: int
    mood_score: int
    date: str


class CheckinHistoryItem(BaseModel):
    date: str
    mood_score: int
    mood_note: str | None = None

    model_config = {"from_attributes": True}


class TodayCheckinStatus(BaseModel):
    checked_in: bool
    mood_score: int | None = None
    streak_days: int = 0


class TopicRecommendation(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    prompt: str


# ─── 路由 ──────────────────────────────────────────────────────────────────────

@router.get("/recommendations", response_model=list[TopicRecommendation])
async def get_recommendations(
    user: User | None = Depends(get_optional_user),
):
    """获取今日推荐话题（可选认证，未登录也可用）"""
    recent_emotion = None  # 可扩展：从历史记录获取用户最近情绪
    topics = topic_engine.get_recommendations(
        user_id=user.id if user else None,
        recent_emotion=recent_emotion,
    )
    return topics


@router.post("/checkin", response_model=CheckinResponse)
async def daily_checkin(
    body: CheckinRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """每日签到（需认证）"""
    today = date.today()

    # 检查今天是否已签到
    result = await db.execute(
        select(DailyCheckin).where(
            DailyCheckin.user_id == current_user.id,
            DailyCheckin.date == today,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="今天已经签到过了",
        )

    # 创建签到记录
    checkin = DailyCheckin(
        user_id=current_user.id,
        mood_score=body.mood_score,
        mood_note=body.mood_note,
        date=today,
    )
    db.add(checkin)
    await db.flush()

    # 计算连续签到天数
    streak = await _calc_streak(db, current_user.id)

    # 鼓励语
    messages = {
        1: "感谢你记录今天的心情，每一天都值得被看见 🌱",
        2: "心情记录下来啦，明天继续加油 💪",
        3: "签到成功！保持记录是个好习惯 ✨",
        4: "太棒了，你的坚持让 MindMirror 更了解你 🌟",
        5: "心情日记已更新，愿你每天都有好心情 🌈",
    }
    msg = messages.get(min(streak, 5), messages[3])

    logger.info("用户 %s 签到: mood=%d, streak=%d", current_user.username, body.mood_score, streak)
    return CheckinResponse(
        message=msg,
        streak_days=streak,
        mood_score=body.mood_score,
        date=today.isoformat(),
    )


@router.get("/checkin/history", response_model=list[CheckinHistoryItem])
async def get_checkin_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取签到历史（最近 30 天）"""
    thirty_days_ago = date.today() - timedelta(days=30)
    result = await db.execute(
        select(DailyCheckin)
        .where(
            DailyCheckin.user_id == current_user.id,
            DailyCheckin.date >= thirty_days_ago,
        )
        .order_by(desc(DailyCheckin.date))
    )
    records = result.scalars().all()
    return [
        CheckinHistoryItem(
            date=r.date.isoformat(),
            mood_score=r.mood_score,
            mood_note=r.mood_note,
        )
        for r in records
    ]


@router.get("/checkin/today", response_model=TodayCheckinStatus)
async def get_today_checkin(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """检查今天是否已签到"""
    today = date.today()
    result = await db.execute(
        select(DailyCheckin).where(
            DailyCheckin.user_id == current_user.id,
            DailyCheckin.date == today,
        )
    )
    checkin = result.scalar_one_or_none()
    if checkin:
        streak = await _calc_streak(db, current_user.id)
        return TodayCheckinStatus(
            checked_in=True,
            mood_score=checkin.mood_score,
            streak_days=streak,
        )
    return TodayCheckinStatus(checked_in=False)


async def _calc_streak(db: AsyncSession, user_id: int) -> int:
    """计算连续签到天数（从今天往前回溯）"""
    streak = 0
    check_date = date.today()
    while True:
        result = await db.execute(
            select(DailyCheckin).where(
                DailyCheckin.user_id == user_id,
                DailyCheckin.date == check_date,
            )
        )
        if result.scalar_one_or_none() is None:
            break
        streak += 1
        check_date -= timedelta(days=1)
    return streak
