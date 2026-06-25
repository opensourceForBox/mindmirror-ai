"""视频处理安全模块

确保：
1. 年龄验证完成
2. 未成年人已获家长同意
3. 视频数据不存储、不上传
4. 仅传输情绪标签
5. 会话超时自动断开
"""

import hashlib
import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# 枚举 & 数据类
# ---------------------------------------------------------------------------

class ConsentStatus(Enum):
    NOT_REQUESTED = "not_requested"
    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"
    EXPIRED = "expired"


@dataclass
class UserSafetyProfile:
    """用户安全档案"""
    user_id: str
    is_minor: bool = False
    age: Optional[int] = None
    parental_consent: ConsentStatus = ConsentStatus.NOT_REQUESTED
    consent_timestamp: Optional[datetime] = None
    consent_expiry: Optional[datetime] = None
    data_retention_days: int = 30
    video_processing_enabled: bool = False


@dataclass
class SessionInfo:
    """活跃会话信息"""
    session_id: str
    user_id: str
    started_at: datetime
    last_activity: datetime


@dataclass
class DataAccessLog:
    """数据访问审计日志"""
    timestamp: datetime
    user_id: str
    action: str
    data_type: str


# ---------------------------------------------------------------------------
# 安全管理器
# ---------------------------------------------------------------------------

class VideoSafetyManager:
    """视频处理安全管理器"""

    # 家长同意有效期（天）
    _CONSENT_VALIDITY_DAYS = 365
    # 最大会话时长
    _DEFAULT_SESSION_TIMEOUT = timedelta(hours=1)
    # 家长同意验证码前缀
    _CONSENT_CODE_PREFIX = "MC-"

    def __init__(self, session_timeout: timedelta = None):
        self.user_profiles: dict[str, UserSafetyProfile] = {}
        self.sessions: dict[str, SessionInfo] = {}          # session_id -> SessionInfo
        self._consent_codes: dict[str, str] = {}            # code_hash -> user_id
        self._access_logs: list[DataAccessLog] = []
        self.session_timeout = session_timeout or self._DEFAULT_SESSION_TIMEOUT
        logger.info("VideoSafetyManager 初始化完成 | session_timeout=%s", self.session_timeout)

    # ------------------------------------------------------------------
    # 用户注册 & 权限检查
    # ------------------------------------------------------------------

    def register_user(
        self,
        user_id: str,
        age: int,
        parental_consent: bool = False,
    ) -> UserSafetyProfile:
        """注册用户并进行安全检查

        - 年龄 < 18 → 未成年人，需要家长同意
        - parental_consent=True 表示家长已预先同意
        """
        is_minor = age < 18
        consent_status = ConsentStatus.NOT_REQUESTED

        if is_minor:
            consent_status = ConsentStatus.GRANTED if parental_consent else ConsentStatus.PENDING
        else:
            # 成年人默认授予
            consent_status = ConsentStatus.GRANTED

        now = datetime.utcnow()
        profile = UserSafetyProfile(
            user_id=user_id,
            is_minor=is_minor,
            age=age,
            parental_consent=consent_status,
            consent_timestamp=now if consent_status == ConsentStatus.GRANTED else None,
            consent_expiry=(
                now + timedelta(days=self._CONSENT_VALIDITY_DAYS)
                if consent_status == ConsentStatus.GRANTED
                else None
            ),
            video_processing_enabled=(consent_status == ConsentStatus.GRANTED),
        )
        self.user_profiles[user_id] = profile
        self.log_data_access(user_id, "register", "user_profile")

        logger.info(
            "用户注册 | user_id=%s age=%d minor=%s consent=%s",
            user_id, age, is_minor, consent_status.value,
        )
        return profile

    def check_video_permission(self, user_id: str) -> tuple[bool, str]:
        """检查用户是否有权限使用视频功能

        Returns:
            (allowed: bool, reason: str)
        """
        profile = self.user_profiles.get(user_id)
        if profile is None:
            return False, "用户未注册，请先完成注册"

        # 检查同意状态
        if profile.parental_consent == ConsentStatus.DENIED:
            return False, "家长已拒绝视频功能使用"

        if profile.parental_consent == ConsentStatus.EXPIRED:
            return False, "家长同意已过期，请重新申请"

        if profile.is_minor and profile.parental_consent not in (
            ConsentStatus.GRANTED,
        ):
            return False, "未成年人需要家长同意才能使用视频功能"

        # 检查同意有效期
        if profile.consent_expiry and datetime.utcnow() > profile.consent_expiry:
            profile.parental_consent = ConsentStatus.EXPIRED
            profile.video_processing_enabled = False
            return False, "家长同意已过期，请重新申请"

        if not profile.video_processing_enabled:
            return False, "视频处理功能未启用"

        self.log_data_access(user_id, "permission_check", "video_access")
        return True, "权限检查通过"

    # ------------------------------------------------------------------
    # 家长同意流程
    # ------------------------------------------------------------------

    def generate_consent_request(self, user_id: str, parent_email: str) -> str:
        """生成家长同意请求，返回验证码

        验证码格式：MC-XXXXXXXX（8 位随机 hex）
        """
        profile = self.user_profiles.get(user_id)
        if profile is None:
            raise ValueError(f"用户 {user_id} 未注册")
        if not profile.is_minor:
            raise ValueError(f"用户 {user_id} 已成年，无需家长同意")

        # 生成验证码
        code = self._CONSENT_CODE_PREFIX + secrets.token_hex(4).upper()
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        self._consent_codes[code_hash] = user_id

        profile.parental_consent = ConsentStatus.PENDING
        self.log_data_access(user_id, "consent_request", "parental_consent")

        logger.info(
            "家长同意请求已生成 | user_id=%s parent_email=%s code=%s",
            user_id, parent_email, code,
        )
        # 注意：实际生产环境应通过邮件服务发送验证码
        return code

    def verify_parental_consent(self, user_id: str, consent_code: str) -> bool:
        """验证家长同意验证码"""
        code_hash = hashlib.sha256(consent_code.encode()).hexdigest()
        expected_user = self._consent_codes.get(code_hash)

        if expected_user is None or expected_user != user_id:
            logger.warning("家长同意验证失败 | user_id=%s code=%s", user_id, consent_code)
            self.log_data_access(user_id, "consent_verify_fail", "parental_consent")
            return False

        # 验证通过
        profile = self.user_profiles.get(user_id)
        if profile:
            now = datetime.utcnow()
            profile.parental_consent = ConsentStatus.GRANTED
            profile.consent_timestamp = now
            profile.consent_expiry = now + timedelta(days=self._CONSENT_VALIDITY_DAYS)
            profile.video_processing_enabled = True

        # 清理已使用的验证码
        del self._consent_codes[code_hash]

        self.log_data_access(user_id, "consent_granted", "parental_consent")
        logger.info("家长同意验证通过 | user_id=%s", user_id)
        return True

    # ------------------------------------------------------------------
    # 会话管理
    # ------------------------------------------------------------------

    def create_session(self, user_id: str) -> str:
        """创建视频处理会话，返回 session_id"""
        allowed, reason = self.check_video_permission(user_id)
        if not allowed:
            raise PermissionError(reason)

        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        self.sessions[session_id] = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            started_at=now,
            last_activity=now,
        )
        self.log_data_access(user_id, "session_create", "video_session")
        logger.info("会话已创建 | session_id=%s user_id=%s", session_id, user_id)
        return session_id

    def check_session_validity(self, session_id: str) -> bool:
        """检查会话是否有效（超时检查）"""
        session = self.sessions.get(session_id)
        if session is None:
            return False
        if datetime.utcnow() - session.started_at > self.session_timeout:
            logger.info("会话已超时 | session_id=%s", session_id)
            self.close_session(session_id)
            return False
        # 更新最后活动时间
        session.last_activity = datetime.utcnow()
        return True

    def close_session(self, session_id: str):
        """关闭会话"""
        session = self.sessions.pop(session_id, None)
        if session:
            self.log_data_access(session.user_id, "session_close", "video_session")
            logger.info("会话已关闭 | session_id=%s", session_id)

    # ------------------------------------------------------------------
    # 数据政策 & 审计
    # ------------------------------------------------------------------

    def get_data_policy(self) -> dict:
        """获取数据处理政策"""
        return {
            "video_storage": "none",             # 不存储视频
            "face_templates": "none",            # 不保存面部模板
            "emotion_labels": "session_only",    # 仅会话期间保留情绪标签
            "retention_period_days": 30,
            "encryption": "AES-256",
            "transmission": "TLS 1.3",
            "third_party_sharing": "none",
        }

    def log_data_access(self, user_id: str, action: str, data_type: str):
        """记录数据访问日志（审计）"""
        entry = DataAccessLog(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            action=action,
            data_type=data_type,
        )
        self._access_logs.append(entry)
        logger.debug(
            "审计日志 | user=%s action=%s type=%s",
            user_id, action, data_type,
        )

    def get_access_logs(self, user_id: str = None, limit: int = 100) -> list[dict]:
        """获取审计日志（可按 user_id 过滤）"""
        logs = self._access_logs
        if user_id:
            logs = [l for l in logs if l.user_id == user_id]
        return [
            {
                "timestamp": l.timestamp.isoformat(),
                "user_id": l.user_id,
                "action": l.action,
                "data_type": l.data_type,
            }
            for l in logs[-limit:]
        ]
