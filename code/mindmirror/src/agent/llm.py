"""LLM 大模型接口封装 — 支持 DeepSeek 和 GLM-4"""
import asyncio
from typing import List, Dict, Optional
from openai import OpenAI
from src.utils.config import (
    LLM_PROVIDER,
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL,
    ZHIPU_API_KEY, ZHIPU_BASE_URL, ZHIPU_MODEL
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MindMirrorLLM:
    """统一 LLM 接口 — 支持 DeepSeek 和 GLM-4 切换

    通过环境变量 LLM_PROVIDER 控制使用哪个模型：
    - "deepseek": 使用 DeepSeek API
    - "zhipu": 使用智谱 GLM-4 API

    两者都兼容 OpenAI API 格式，使用 openai SDK 统一调用。
    """

    def __init__(self, provider: str = None):
        """初始化 LLM

        Args:
            provider: 指定使用的模型提供商 ("deepseek" 或 "zhipu")，
                     为 None 时使用环境变量 LLM_PROVIDER 的值
        """
        self.provider = provider or LLM_PROVIDER
        self._setup_client()

    def _setup_client(self):
        """根据 provider 设置 OpenAI 兼容客户端"""
        if self.provider == "deepseek":
            self.api_key = DEEPSEEK_API_KEY
            self.base_url = DEEPSEEK_BASE_URL
            self.model = DEEPSEEK_MODEL
        elif self.provider == "zhipu":
            self.api_key = ZHIPU_API_KEY
            self.base_url = ZHIPU_BASE_URL
            self.model = ZHIPU_MODEL
        else:
            logger.warning(f"未知的 LLM provider: {self.provider}，回退到 deepseek")
            self.api_key = DEEPSEEK_API_KEY
            self.base_url = DEEPSEEK_BASE_URL
            self.model = DEEPSEEK_MODEL

        if not self.api_key:
            logger.warning(f"LLM API Key 未配置 (provider={self.provider})")
            self.client = None
        else:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
            logger.info(f"LLM 初始化成功: provider={self.provider}, model={self.model}")

    async def chat(self, messages: List[Dict[str, str]],
                   temperature: float = 0.7,
                   max_tokens: int = 2000,
                   system_prompt: str = None) -> str:
        """发送对话请求

        Args:
            messages: 消息列表 [{"role": "user/assistant/system", "content": "..."}]
            temperature: 生成温度
            max_tokens: 最大生成 token 数
            system_prompt: 可选的 system prompt（会插入到消息列表最前面）

        Returns:
            AI 回复文本
        """
        if not self.client:
            return self._fallback_response()

        try:
            # 如果提供了 system_prompt，插入到消息列表最前面
            full_messages = []
            if system_prompt:
                full_messages.append({"role": "system", "content": system_prompt})
            full_messages.extend(messages)

            # 使用 asyncio.to_thread 异步化同步调用
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM 调用失败 ({self.provider}): {e}")
            return self._fallback_response()

    async def chat_with_context(self,
                                 user_message: str,
                                 emotion_context: dict = None,
                                 knowledge_context: list = None,
                                 history: list = None,
                                 system_prompt: str = "") -> str:
        """带上下文的对话

        Args:
            user_message: 用户消息
            emotion_context: 情绪分析结果
            knowledge_context: RAG 检索的知识片段列表
            history: 对话历史
            system_prompt: 系统提示词

        Returns:
            AI 回复文本
        """
        # 构建上下文注入
        context_parts = []

        if emotion_context:
            emotion_str = f"当前用户情绪: {emotion_context.get('dominant_emotion', '未知')}, "
            emotion_str += f"效价: {emotion_context.get('valence', 0):.2f}, "
            emotion_str += f"唤醒度: {emotion_context.get('arousal', 0):.2f}"
            context_parts.append(emotion_str)

        if knowledge_context:
            knowledge_str = "相关专业知识:\n" + "\n".join(
                [f"- {k}" for k in knowledge_context[:3]]
            )
            context_parts.append(knowledge_str)

        # 组装完整系统提示
        full_system = system_prompt
        if context_parts:
            full_system += "\n\n[当前上下文]\n" + "\n".join(context_parts)

        # 构建消息列表
        messages = []
        if history:
            messages.extend(history[-20:])  # 限制历史长度
        messages.append({"role": "user", "content": user_message})

        return await self.chat(messages, system_prompt=full_system)

    def _fallback_response(self) -> str:
        """API 不可用时的降级回复"""
        return (
            "我现在暂时无法为你提供完整的回复，但我想让你知道，你的感受是重要的。"
            "\n\n如果你正在经历困难，请拨打以下热线寻求帮助："
            "\n- 全国心理援助热线：400-161-9995"
            "\n- 北京心理危机研究与干预中心：010-82951332"
            "\n- 生命热线：400-821-1215"
            f"\n\n[系统提示：LLM 服务未配置或不可用 (provider={self.provider})，"
            f"请检查 .env 中的 API Key 配置]"
        )


# 全局单例
_llm_instance: Optional[MindMirrorLLM] = None


def get_llm(provider: str = None) -> MindMirrorLLM:
    """获取 LLM 单例"""
    global _llm_instance
    if _llm_instance is None or (provider and provider != _llm_instance.provider):
        _llm_instance = MindMirrorLLM(provider=provider)
    return _llm_instance
