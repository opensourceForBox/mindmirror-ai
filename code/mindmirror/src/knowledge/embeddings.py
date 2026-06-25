"""Embedding 管理模块

支持两种 Embedding 后端：
1. 智谱 AI 的 embedding-3 模型（通过 zhipuai SDK，在线 API）
2. sentence-transformers 本地模型（如 BAAI/bge-large-zh-v1.5，离线可用）

两个实现均兼容 LangChain Embeddings 接口。
"""
import os
from typing import List, Optional

from langchain.embeddings.base import Embeddings

from src.utils.config import ZHIPU_API_KEY
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ZhipuEmbeddings(Embeddings):
    """智谱 Embedding 实现

    使用智谱 AI 的 embedding-3 模型生成文本向量。
    需要有效的 ZHIPU_API_KEY 环境变量或构造参数。
    """

    MODEL_NAME = "embedding-3"
    EMBEDDING_DIM = 2048

    def __init__(self, api_key: Optional[str] = None):
        """初始化智谱 Embedding

        Args:
            api_key: 智谱 API Key，默认从环境变量 ZHIPU_API_KEY 获取
        """
        self.api_key = api_key or ZHIPU_API_KEY
        if not self.api_key:
            raise ValueError(
                "未提供 ZHIPU_API_KEY。请设置环境变量或在初始化时传入。"
            )

        try:
            from zhipuai import ZhipuAI
            self.client = ZhipuAI(api_key=self.api_key)
            logger.info("智谱 Embedding 初始化成功，模型: %s", self.MODEL_NAME)
        except ImportError:
            raise ImportError(
                "zhipuai 包未安装。请运行: pip install zhipuai"
            )
        except Exception as e:
            logger.error("智谱 Embedding 初始化失败: %s", e)
            raise

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量生成文档文本的 Embedding

        Args:
            texts: 文档文本列表

        Returns:
            向量列表，每个向量为 float 列表
        """
        if not texts:
            return []

        embeddings = []
        # 智谱 API 每次最多处理一定数量的文本，分批处理
        batch_size = 20
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                response = self.client.embeddings.create(
                    model=self.MODEL_NAME,
                    input=batch,
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error("智谱 Embedding 批量调用失败 (batch %d-%d): %s",
                             i, i + len(batch), e)
                raise

        logger.debug("生成 %d 个文档 Embedding", len(embeddings))
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """生成查询文本的 Embedding

        Args:
            text: 查询文本

        Returns:
            文本的向量表示
        """
        try:
            response = self.client.embeddings.create(
                model=self.MODEL_NAME,
                input=[text],
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error("智谱 Embedding 查询调用失败: %s", e)
            raise


class LocalEmbeddings(Embeddings):
    """本地 Embedding 实现

    使用 sentence-transformers 加载本地模型（默认 BAAI/bge-large-zh-v1.5）。
    无需 API Key，支持离线使用。
    """

    DEFAULT_MODEL = "BAAI/bge-large-zh-v1.5"
    EMBEDDING_DIM = 1024

    def __init__(self, model_name: Optional[str] = None, device: str = "cpu"):
        """初始化本地 Embedding 模型

        Args:
            model_name: HuggingFace 模型名称或本地路径
            device: 运行设备 ('cpu' 或 'cuda')
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self.device = device

        try:
            from sentence_transformers import SentenceTransformer
            logger.info("正在加载本地 Embedding 模型: %s (device=%s)",
                        self.model_name, self.device)
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info("本地 Embedding 模型加载成功")
        except ImportError:
            raise ImportError(
                "sentence-transformers 包未安装。请运行: pip install sentence-transformers"
            )
        except Exception as e:
            logger.error("本地 Embedding 模型加载失败: %s", e)
            raise

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量生成文档文本的 Embedding

        Args:
            texts: 文档文本列表

        Returns:
            向量列表
        """
        if not texts:
            return []

        try:
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=True,
                show_progress_bar=len(texts) > 100,
            )
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error("本地 Embedding 批量编码失败: %s", e)
            raise

    def embed_query(self, text: str) -> List[float]:
        """生成查询文本的 Embedding

        bge 模型推荐在查询前添加 '为这个句子生成表示以用于检索中文文档：' 前缀，
        但为保持通用性，此处不做强制处理。

        Args:
            text: 查询文本

        Returns:
            文本的向量表示
        """
        try:
            embedding = self.model.encode(
                [text],
                normalize_embeddings=True,
            )
            return embedding[0].tolist()
        except Exception as e:
            logger.error("本地 Embedding 查询编码失败: %s", e)
            raise


def get_embeddings(backend: str = "zhipu", **kwargs) -> Embeddings:
    """工厂函数：根据配置获取 Embedding 实例

    Args:
        backend: 后端类型 ('zhipu' 或 'local')
        **kwargs: 传递给具体实现的参数

    Returns:
        Embeddings 实例
    """
    if backend == "zhipu":
        return ZhipuEmbeddings(**kwargs)
    elif backend == "local":
        return LocalEmbeddings(**kwargs)
    else:
        raise ValueError(f"不支持的 Embedding 后端: {backend}。可选: 'zhipu', 'local'")
