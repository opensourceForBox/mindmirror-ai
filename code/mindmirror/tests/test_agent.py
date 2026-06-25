"""Agent 模块测试"""
import pytest


def test_conversation_state_init():
    """测试对话状态初始化"""
    from src.agent.graph import ConversationState

    state = ConversationState(
        messages=[],
        emotion_context={},
        user_profile={},
        safety_flag=False,
    )
    assert state["messages"] == []
    assert state["safety_flag"] is False
