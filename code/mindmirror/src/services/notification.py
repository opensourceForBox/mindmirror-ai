"""家长通知服务

当孩子触发高风险或危机信号时，通知绑定家长。
支持数据库告警记录与可选的邮件通知（aiosmtplib）。
"""
import logging
import os
from email.message import EmailMessage

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.alert import Alert
from src.models.database import async_session_factory
from src.models.user import User

logger = logging.getLogger(__name__)


class NotificationService:
    """家长通知服务"""

    def __init__(self) -> None:
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")

    async def notify_parent(
        self,
        child_user_id: int,
        alert_type: str,
        message: str,
        severity: str = "high",
    ) -> Alert | None:
        """当孩子触发高风险时通知家长

        流程:
        1. 创建 Alert 记录
        2. 查找孩子的家长 (通过 parent_id 关系)
        3. 发送邮件通知 (如果配置了 SMTP)
        4. 如果未配置 SMTP，仅记录到数据库（家长登录后可看到）

        Args:
            child_user_id: 孩子的用户 ID
            alert_type: 告警类型，如 "high_risk" / "crisis" / "mood_decline"
            message: 告警描述
            severity: 严重等级 low/medium/high/critical

        Returns:
            创建的 Alert 对象，或 None（创建失败时）
        """
        try:
            # 1. 创建告警记录并立即提交，确保即使邮件失败也不会丢失告警
            async with async_session_factory() as session:
                alert = await self._create_alert(
                    session, child_user_id, alert_type, message, severity
                )
                if alert is None:
                    return None
                await session.commit()

            # 2. 查找家长并发送邮件（在独立会话中，避免长时间占用数据库连接）
            parent_email: str | None = None
            parent_name: str = ""
            async with async_session_factory() as session:
                parent = await self._find_parent(session, child_user_id)
                if parent:
                    parent_email = parent.email
                    parent_name = parent.username

            if parent_email:
                await self.send_email(
                    to_email=parent_email,
                    subject=f"【MindMirror】孩子{self._severity_label(severity)}告警",
                    body=self._build_email_body(parent_name, child_user_id, message),
                )
            else:
                logger.info(
                    "孩子 %d 未绑定家长或家长无邮箱，仅记录告警到数据库",
                    child_user_id,
                )

            return alert
        except Exception as e:
            logger.warning("通知家长失败 (child_user_id=%d): %s", child_user_id, e)
            return None

    async def _create_alert(
        self,
        session: AsyncSession,
        child_user_id: int,
        alert_type: str,
        message: str,
        severity: str,
    ) -> Alert | None:
        """在数据库中创建 Alert 记录"""
        alert = Alert(
            user_id=child_user_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            is_read=False,
        )
        session.add(alert)
        await session.flush()
        await session.refresh(alert)
        logger.info(
            "创建告警: child=%d, type=%s, severity=%s, id=%d",
            child_user_id,
            alert_type,
            severity,
            alert.id,
        )
        return alert

    async def _find_parent(self, session: AsyncSession, child_user_id: int) -> User | None:
        """通过 parent_id 查找孩子的家长"""
        result = await session.execute(
            select(User).where(User.id == child_user_id)
        )
        child = result.scalar_one_or_none()
        if child is None or child.parent_id is None:
            return None

        result = await session.execute(
            select(User).where(User.id == child.parent_id)
        )
        return result.scalar_one_or_none()

    async def send_email(self, to_email: str, subject: str, body: str) -> None:
        """发送邮件（可选，依赖 SMTP 配置）

        从环境变量读取: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
        如果未配置，静默跳过并记录日志。
        """
        if not (self.smtp_host and self.smtp_user and self.smtp_password):
            logger.info("SMTP 未配置，跳过邮件发送")
            return

        try:
            import aiosmtplib

            msg = EmailMessage()
            msg["From"] = self.smtp_user
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.set_content(body)

            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True,
            )
            logger.info("邮件已发送至 %s", to_email)
        except ImportError:
            logger.warning("aiosmtplib 未安装，无法发送邮件")
        except Exception as e:
            logger.warning("邮件发送失败 (%s): %s", to_email, e)

    def _build_email_body(self, parent_name: str, child_user_id: int, message: str) -> str:
        """构建邮件正文"""
        return (
            f"尊敬的 {parent_name}，您好：\n\n"
            f"MindMirror 系统检测到您绑定的孩子（用户ID: {child_user_id}）"
            f"出现了需要关注的心理健康信号：\n\n"
            f"{message}\n\n"
            f"请尽快登录家长守护中心查看详情，并在必要时与孩子沟通或寻求专业帮助。\n\n"
            f"MindMirror AI\n"
        )

    @staticmethod
    def _severity_label(severity: str) -> str:
        """严重等级中文标签"""
        labels = {
            "critical": "紧急",
            "high": "高风险",
            "medium": "中等风险",
            "low": "低风险",
        }
        return labels.get(severity, "风险")
