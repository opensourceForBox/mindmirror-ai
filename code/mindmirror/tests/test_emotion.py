"""Emotion 模块测试"""
import pytest


def test_emotion_module_import():
    """测试情绪识别模块可正常导入"""
    from src.emotion import video, audio, fusion
    assert video is not None
    assert audio is not None
    assert fusion is not None
