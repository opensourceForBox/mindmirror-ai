"""GLM-4 大模型接口封装

提供 MindMirror 对话引擎与 GLM-4 模型的交互接口，
支持普通对话和带上下文（情绪 + 知识 + 历史）的对话。
"""
import asyncio
from typing import Dict, List, Optional

from zhipuai import ZhipuAI

from src.utils.config import ZHIPU_API_KEY
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 当 API Key 缺失时的降级回复
_FALLBACK_REPLY = (
    "抱歉，MindMirror 当前无法连接到 AI 服务。"
    "请检查 ZHIPU_API_KEY 配置是否正确。"
    "如果你正在经历困难时刻，请拨打全国心理援助热线：400-161-9995。"
)


class MindMirrorLLM:
    """GLM-4 对话模型封装

    Attributes:
        client: ZhipuAI 客户端实例
        model: 使用的模型名称
        available: 模型是否可用（API Key 是否配置）
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "glm-4"):
        """初始化 LLM 客户端

        Args:
            api_key: ZhipuAI API Key，默认从配置中读取
            model: 模型名称，默认 glm-4
        """
        self.model = model
        self.available = False
        self.client: Optional[ZhipuAI] = None

        key = api_key or ZHIPU_API_KEY
        if not key:
            logger.warning("ZHIPU_API_KEY 未配置，LLM 将处于不可用状态")
            return

        try:
            self.client = ZhipuAI(api_key=key)
            self.available = True
            logger.info("MindMirrorLLM 初始化完成，模型: %s", model)
        except Exception as e:
            logger.error("ZhipuAI 客户端初始化失败: %s", e)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> str:
        """发送对话请求

        Args:
            messages: 消息列表 [{"role": "user/assistant", "content": "..."}]
            temperature: 生成温度
            system_prompt: 可选的系统提示（会插入到消息列表最前）

        Returns:
            模型回复文本
        """
        if not self.available:
            return _FALLBACK_REPLY

        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        try:
            # zhipuai SDK 是同步的，用 to_thread 放到线程池
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=messages,
                temperature=temperature,
            )
            content = response.choices[0].message.content
            logger.debug("GLM-4 回复长度: %d", len(content))
            return content
        except Exception as e:
            logger.error("GLM-4 调用失败: %s", e, exc_info=True)
            return _FALLBACK_REPLY

    async def chat_with_context(
        self,
        user_message: str,
        emotion_context: Optional[dict] = None,
        knowledge_context: Optional[List[str]] = None,
        history: Optional[List[dict]] = None,
        system_prompt: str = "",
    ) -> str:
        """带上下文的对话 — 组装完整 prompt

        Args:
            user_message: 用户当前消息
            emotion_context: 情绪分析结果 {"dominant_emotion": "...", "score": ...}
            knowledge_context: 检索到的知识片段
            history: 对话历史 [{"role": "...", "content": "..."}]
            system_prompt: System Prompt 文本

        Returns:
            模型回复文本
        """
        # 构建上下文注入文本
        context_parts: List[str] = []

        if emotion_context:
            dominant = emotion_context.get("dominant_emotion", "未知")
            score = emotion_context.get("score", 0)
            context_parts.append(
                f"[情绪感知] 用户当前情绪：{dominant}（置信度 {score:.0%}）"
            )
            # 如果有情绪历史摘要
            history_summary = emotion_context.get("history_summary", "")
            if history_summary:
                context_parts.append(f"[情绪趋势] {history_summary}")

        if knowledge_context:
            knowledge_text = "\n".join(
                f"  - {snippet}" for snippet in knowledge_context[:5]
            )
            context_parts.append(f"[参考知识]\n{knowledge_text}")

        context_injection = "\n".join(context_parts) if context_parts else ""

        # 构建消息列表
        messages = self._build_messages(
            system_prompt=system_prompt,
            history=history or [],
            context_injection=context_injection,
            user_message=user_message,
        )

        return await self.chat(messages, temperature=0.7)

    def _build_messages(
        self,
        system_prompt: str,
        history: List[dict],
        context_injection: str,
        user_message: str,
    ) -> List[dict]:
        """构建发送给模型的消息列表

        Args:
            system_prompt: 系统提示词
            history: 对话历史
            context_injection: 上下文注入文本
            user_message: 用户消息

        Returns:
            完整的消息列表
        """
        messages: List[dict] = []

        # 系统消息（如果有上下文注入则附加）
        if context_injection:
            system_content = f"{system_prompt}\n\n---\n当前对话上下文信息：\n{context_injection}"
        else:
            system_content = system_prompt

        messages.append({"role": "system", "content": system_content})

        # 对话历史（最多保留最近 10 轮）
        recent_history = history[-20:] if len(history) > 20 else history
        messages.extend(recent_history)

        # 当前用户消息
        messages.append({"role": "user", "content": user_message})

        return messages
