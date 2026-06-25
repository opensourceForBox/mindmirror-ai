"""知识库管理器 — 统一入口

提供知识库的统一操作接口，包括：
- 初始化（加载文档、生成 Embedding、索引到 Qdrant）
- 查询（语义检索 / 混合检索）
- 增量更新
- 状态统计
"""
from pathlib import Path
from typing import List, Optional

from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from qdrant_client import QdrantClient

from src.knowledge.embeddings import get_embeddings
from src.knowledge.loader import KnowledgeLoader
from src.knowledge.retriever import KnowledgeRetriever, create_qdrant_client
from src.utils.config import KNOWLEDGE_BASE_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)


class KnowledgeManager:
    """知识库管理器

    封装 Loader、Embeddings、Retriever，对外提供统一的异步接口。

    Attributes:
        loader: 文档加载器
        embeddings: Embedding 生成器
        retriever: 知识检索器
    """

    def __init__(
        self,
        knowledge_base_dir: Optional[Path] = None,
        embeddings_backend: str = "zhipu",
        qdrant_client: Optional[QdrantClient] = None,
        collection_name: str = "psychology_knowledge",
        embedding_kwargs: Optional[dict] = None,
    ):
        """初始化知识库管理器

        Args:
            knowledge_base_dir: 知识库目录，默认使用配置中的路径
            embeddings_backend: Embedding 后端 ('zhipu' 或 'local')
            qdrant_client: Qdrant 客户端（为 None 时自动创建）
            collection_name: 向量集合名称
            embedding_kwargs: 传递给 Embedding 工厂的额外参数
        """
        self.knowledge_base_dir = knowledge_base_dir or KNOWLEDGE_BASE_DIR
        self.embeddings_backend = embeddings_backend
        self.collection_name = collection_name
        self._embedding_kwargs = embedding_kwargs or {}

        # 延迟初始化
        self.loader: Optional[KnowledgeLoader] = None
        self.embeddings: Optional[Embeddings] = None
        self.retriever: Optional[KnowledgeRetriever] = None
        self._qdrant_client = qdrant_client
        self._initialized = False

    async def initialize(self) -> None:
        """初始化知识库

        完整流程：初始化组件 → 加载文档 → 生成 Embedding → 索引到 Qdrant。
        如果 Qdrant 中已有数据则跳过索引。
        """
        if self._initialized:
            logger.info("知识库已初始化，跳过重复初始化")
            return

        logger.info("开始初始化知识库...")

        # 1. 初始化 Loader
        self.loader = KnowledgeLoader(self.knowledge_base_dir)
        logger.info("文档加载器就绪，目录: %s", self.knowledge_base_dir)

        # 2. 初始化 Embeddings
        self.embeddings = get_embeddings(
            self.embeddings_backend, **self._embedding_kwargs
        )
        logger.info("Embedding 后端就绪: %s", self.embeddings_backend)

        # 3. 初始化 Qdrant 客户端和检索器
        if self._qdrant_client is None:
            self._qdrant_client = create_qdrant_client()

        self.retriever = KnowledgeRetriever(
            qdrant_client=self._qdrant_client,
            embeddings=self.embeddings,
            collection_name=self.collection_name,
        )

        # 4. 检查是否已有索引数据
        stats = await self.retriever.get_collection_stats()
        existing_count = stats.get("total_documents", 0)

        if existing_count > 0:
            logger.info("Qdrant 中已有 %d 个文档，跳过全量索引", existing_count)
        else:
            # 5. 加载并索引文档
            documents = self.loader.load_all()
            if documents:
                await self.retriever.index_documents(documents)
            else:
                logger.warning("未加载到任何文档")

        self._initialized = True
        logger.info("知识库初始化完成")

    async def query(
        self,
        question: str,
        category: Optional[str] = None,
        top_k: int = 5,
        method: str = "hybrid",
    ) -> List[Document]:
        """查询知识库

        Args:
            question: 查询问题
            category: 分类过滤（为 None 时不限制）
            top_k: 返回结果数量
            method: 检索方法 ('semantic', 'hybrid')

        Returns:
            相关文档列表
        """
        self._ensure_initialized()

        if method == "hybrid":
            return await self.retriever.hybrid_search(question, top_k=top_k)
        else:
            return await self.retriever.search(
                question, top_k=top_k, category=category
            )

    async def update(self, category: str) -> int:
        """增量更新指定分类的知识库

        重新加载指定分类的文档并重新索引该分类的内容。

        Args:
            category: 分类名称（如 'cbt', 'crisis' 等）

        Returns:
            更新的文档片段数量
        """
        self._ensure_initialized()

        logger.info("增量更新分类: %s", category)

        # 加载指定分类的文档
        documents = self.loader.load_category(category)
        if not documents:
            logger.warning("分类 '%s' 中没有加载到文档", category)
            return 0

        # 索引新文档（会覆盖同 ID 的旧文档）
        await self.retriever.index_documents(documents)

        logger.info("分类 '%s' 更新完成: %d 个文档片段", category, len(documents))
        return len(documents)

    async def rebuild(self) -> int:
        """完全重建知识库

        删除现有 collection 并重新索引所有文档。

        Returns:
            索引的文档片段数量
        """
        self._ensure_initialized()

        logger.info("开始完全重建知识库...")

        # 删除旧 collection
        from qdrant_client.http import models as qdrant_models
        try:
            self._qdrant_client.delete_collection(self.collection_name)
            logger.info("已删除旧 collection: %s", self.collection_name)
        except Exception as e:
            logger.warning("删除 collection 失败（可能不存在）: %s", e)

        # 重新创建 retriever（会自动创建新 collection）
        self.retriever = KnowledgeRetriever(
            qdrant_client=self._qdrant_client,
            embeddings=self.embeddings,
            collection_name=self.collection_name,
        )

        # 重新加载和索引所有文档
        documents = self.loader.load_all()
        if documents:
            await self.retriever.index_documents(documents)
            logger.info("知识库重建完成: %d 个文档片段", len(documents))
        else:
            logger.warning("未加载到任何文档")

        return len(documents)

    async def stats(self) -> dict:
        """获取知识库状态统计

        Returns:
            统计信息字典
        """
        self._ensure_initialized()

        qdrant_stats = await self.retriever.get_collection_stats()

        return {
            "knowledge_base_dir": str(self.knowledge_base_dir),
            "categories": self.loader.get_categories(),
            "embeddings_backend": self.embeddings_backend,
            "collection_name": self.collection_name,
            **qdrant_stats,
        }

    def _ensure_initialized(self) -> None:
        """确保知识库已初始化

        Raises:
            RuntimeError: 如果尚未调用 initialize()
        """
        if not self._initialized:
            raise RuntimeError(
                "知识库尚未初始化。请先调用 await manager.initialize()"
            )
