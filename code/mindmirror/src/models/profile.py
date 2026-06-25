"""心理档案模型

存储用户的长期心理画像信息，包括性格特征、问题历史、进展记录等。
为 AI 回复提供个性化上下文。
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base


class PsychProfile(Base):
    """用户长期心理档案

    每个用户最多一条记录（user_id unique）。
    所有 JSON 字段以 Text 存储，读写时通过 json 模块序列化/反序列化。
    """

    __tablename__ = "psych_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True
    )

    # 性格特征 — JSON 字符串, 如 {"introversion": 0.7, "sensitivity": 0.8}
    personality_traits: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 问题历史 — JSON 数组, 如 [{"issue": "学业压力", "first_seen": "2024-01", "status": "ongoing"}]
    issue_history: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 进展记录 — JSON 数组, 记录每次档案更新的摘要
    progress_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 兴趣爱好 — JSON 数组
    interests: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 常用应对方式 — JSON 字符串
    coping_styles: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=True
    )

    # 关系（单向，不修改已有 User 模型）
    user: Mapped["User"] = relationship("User")  # noqa: F821
