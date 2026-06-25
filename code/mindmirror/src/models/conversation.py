"""对话历史模型

持久化存储每次对话会话的完整消息、情绪摘要和主题信息。
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base


class Conversation(Base):
    """对话会话记录

    一个 session 对应一条记录，存储完整对话消息（JSON 数组）。
    user_id 可为空，兼容未登录用户的匿名对话。
    """

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True, index=True
    )

    # 完整对话消息 — JSON 数组, 如 [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    messages: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 本次对话情绪摘要 — JSON, 如 {"dominant_emotion": "sadness", "avg_valence": -0.3, "trend": "declining"}
    emotion_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 对话主题
    topic: Mapped[str | None] = mapped_column(String(200), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # 对话时长（分钟）
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # 关系（单向，不修改已有 User 模型）
    user: Mapped[Optional["User"]] = relationship("User")  # noqa: F821
