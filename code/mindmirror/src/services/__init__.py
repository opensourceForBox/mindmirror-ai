"""MindMirror 服务层"""
from src.services.profile_service import (
    should_update_profile,
    update_profile_from_conversation,
)

__all__ = [
    "should_update_profile",
    "update_profile_from_conversation",
]
