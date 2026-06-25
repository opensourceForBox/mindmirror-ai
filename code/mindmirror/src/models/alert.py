"""告警模型

存储系统产生的风险告警，供家长端查看与通知。
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base


class Alert(Base):
    """风险告警记录

    当孩子触发高风险、危机信号或情绪持续下降时生成，
    关联到孩子的 user_id，家长可通过 parent_id 关系查询。
    """

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )

    # 告警类型: high_risk / crisis / mood_decline / self_harm 等
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # 严重等级: low / medium / high / critical
    severity: Mapped[str] = mapped_column(String(20), nullable=False)

    # 告警描述
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # 家长是否已读
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # 关系（单向，不修改已有 User 模型）
    user: Mapped["User"] = relationship("User")  # noqa: F821
