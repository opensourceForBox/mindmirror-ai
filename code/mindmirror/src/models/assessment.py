"""心理测评模型"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    scale_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    answers: Mapped[str] = mapped_column(Text, nullable=False)
    total_score: Mapped[int] = mapped_column(Integer, nullable=False)
    interpretation: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # 关系
    user: Mapped["User"] = relationship("User", lazy="selectin")
