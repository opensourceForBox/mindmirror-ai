"""知识库检索模块

基于 Qdrant 向量数据库的心理学知识检索器，支持：
- 语义检索（向量相似度）
- 按分类过滤检索
- 混合检索（语义 + BM25 关键词匹配）
- 知识库统计信息
"""
import re
from collections import Counter
from typing import Dict, List, Optional, Tuple

from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from qdrant_client.http.exceptions import UnexpectedResponse

from src.utils.config import QDRANT_HOST, QDRANT_PORT
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 向量维度，与 embedding 模型对应
DEFAULT_VECTOR_DIM = 2048


class KnowledgeRetriever:
    """心理学知识库检索器

    支持语义检索、按分类过滤和混合检索。

    Attributes:
        client: Qdrant 客户端实例
        collection_name: 向量集合名称
        embeddings: Embedding 生成器
    """

    def __init__(
        self,
        qdrant_client: QdrantClient,
        embeddings: Embeddings,
        collection_name: str = "psychology_knowledge",
        vector_dim: int = DEFAULT_VECTOR_DIM,
    ):
        """初始化检索器

        Args:
            qdrant_client: Qdrant 客户端
            embeddings: Embedding 实现
            collection_name: Qdrant collection 名称
            vector_dim: 向量维度
        """
        self.client = qdrant_client
        self.embeddings = embeddings
        self.collection_name = collection_name
        self.vector_dim = vector_dim

        # BM25 关键词索引（内存中维护）
        self._bm25_docs: List[Dict] = []

        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """确保 Qdrant collection 存在，不存在则创建"""
        try:
            self.client.get_collection(self.collection_name)
            logger.info("Qdrant collection '%s' 已存在", self.collection_name)
        except (UnexpectedResponse, Exception):
            logger.info("创建 Qdrant collection '%s' (dim=%d)",
                        self.collection_name, self.vector_dim)
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qdrant_models.VectorParams(
                    size=self.vector_dim,
                    distance=qdrant_models.Distance.COSINE,
                ),
            )

    async def index_documents(self, documents: List[Document]) -> None:
        """索引文档到 Qdrant

        批量生成 Embedding 并上传到 Qdrant，同时构建 BM25 索引。

        Args:
            documents: 文档列表
        """
        if not documents:
            logger.warning("文档列表为空，跳过索引")
            return

        logger.info("开始索引 %d 个文档...", len(documents))

        # 生成 Embeddings
        texts = [doc.page_content for doc in documents]
        try:
            embeddings = self.embeddings.embed_documents(texts)
        except Exception as e:
            logger.error("生成 Embeddings 失败: %s", e)
            raise

        # 构建 Qdrant Points
        points = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            point_id = self._generate_point_id(doc, i)
            payload = {
                "text": doc.page_content,
                "category": doc.metadata.get("category", ""),
                "source": doc.metadata.get("source", ""),
                "title": doc.metadata.get("title", ""),
                "section_title": doc.metadata.get("section_title", ""),
                "chunk_index": doc.metadata.get("chunk_index", 0),
            }
            points.append(
                qdrant_models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload,
                )
            )

        # 批量上传（每批 100 个）
        batch_size = 100
        for start in range(0, len(points), batch_size):
            batch = points[start : start + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch,
            )

        # 构建 BM25 索引
        self._build_bm25_index(documents)

        logger.info("索引完成: %d 个文档已上传", len(documents))

    async def search(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
    ) -> List[Document]:
        """语义检索

        基于向量相似度的语义检索，支持按分类过滤。

        Args:
            query: 查询文本
            top_k: 返回结果数量
            category: 分类过滤（为 None 时不过滤）

        Returns:
            相关文档列表，按相似度降序
        """
        # 生成查询向量
        try:
            query_embedding = self.embeddings.embed_query(query)
        except Exception as e:
            logger.error("查询 Embedding 生成失败: %s", e)
            return []

        # 构建过滤条件
        query_filter = None
        if category:
            query_filter = qdrant_models.Filter(
                must=[
                    qdrant_models.FieldCondition(
                        key="category",
                        match=qdrant_models.MatchValue(value=category),
                    )
                ]
            )

        # 执行搜索
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=query_filter,
            )
        except Exception as e:
            logger.error("Qdrant 搜索失败: %s", e)
            return []

        # 转换为 Document
        documents = []
        for result in results:
            doc = Document(
                page_content=result.payload.get("text", ""),
                metadata={
                    "score": result.score,
                    "category": result.payload.get("category", ""),
                    "source": result.payload.get("source", ""),
                    "title": result.payload.get("title", ""),
                    "section_title": result.payload.get("section_title", ""),
                    "retrieval_method": "semantic",
                },
            )
            documents.append(doc)

        logger.debug("语义检索返回 %d 个结果", len(documents))
        return documents

    async def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ) -> List[Document]:
        """混合检索（语义 + 关键词 BM25）

        结合向量语义检索和 BM25 关键词匹配的结果，
        通过加权融合排序。

        Args:
            query: 查询文本
            top_k: 返回结果数量
            semantic_weight: 语义检索权重
            keyword_weight: 关键词检索权重

        Returns:
            融合排序的文档列表
        """
        # 语义检索（多取一些用于融合）
        semantic_results = await self.search(query, top_k=top_k * 2)

        # BM25 关键词检索
        keyword_results = self._bm25_search(query, top_k=top_k * 2)

        if not semantic_results and not keyword_results:
            return []

        # 融合排序
        scored_docs: Dict[str, Tuple[Document, float]] = {}

        for i, doc in enumerate(semantic_results):
            key = doc.page_content[:100]
            # 排名分数：1/(rank+1)
            semantic_score = semantic_weight * (1.0 / (i + 1))
            if key in scored_docs:
                scored_docs[key] = (doc, scored_docs[key][1] + semantic_score)
            else:
                scored_docs[key] = (doc, semantic_score)
                doc.metadata["retrieval_method"] = "hybrid"

        for i, doc in enumerate(keyword_results):
            key = doc.page_content[:100]
            keyword_score = keyword_weight * (1.0 / (i + 1))
            if key in scored_docs:
                existing_doc, existing_score = scored_docs[key]
                existing_doc.metadata["retrieval_method"] = "hybrid"
                scored_docs[key] = (existing_doc, existing_score + keyword_score)
            else:
                doc.metadata["retrieval_method"] = "hybrid_keyword"
                scored_docs[key] = (doc, keyword_score)

        # 按融合分数排序
        sorted_docs = sorted(scored_docs.values(), key=lambda x: x[1], reverse=True)
        result = [doc for doc, _ in sorted_docs[:top_k]]

        logger.debug("混合检索返回 %d 个结果", len(result))
        return result

    async def get_collection_stats(self) -> dict:
        """获取知识库统计信息

        Returns:
            包含文档数量、分类统计等信息的字典
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            total_points = collection_info.points_count or 0

            # 按分类统计
            category_stats = {}
            if total_points > 0:
                # 滚动获取所有 points 的 category
                offset = None
                while True:
                    records, next_offset = self.client.scroll(
                        collection_name=self.collection_name,
                        limit=100,
                        offset=offset,
                        with_payload=["category"],
                        with_vectors=False,
                    )
                    for record in records:
                        cat = record.payload.get("category", "unknown")
                        category_stats[cat] = category_stats.get(cat, 0) + 1
                    if next_offset is None:
                        break
                    offset = next_offset

            return {
                "collection_name": self.collection_name,
                "total_documents": total_points,
                "categories": category_stats,
                "vector_dim": self.vector_dim,
                "bm25_indexed_docs": len(self._bm25_docs),
            }
        except Exception as e:
            logger.error("获取统计信息失败: %s", e)
            return {"error": str(e)}

    def _generate_point_id(self, doc: Document, index: int) -> int:
        """生成唯一的 point ID

        使用 source + chunk_index 的哈希作为稳定 ID。

        Args:
            doc: 文档
            index: 全局索引

        Returns:
            整数 point ID
        """
        source = doc.metadata.get("source", "")
        chunk_idx = doc.metadata.get("chunk_index", index)
        # 使用简单哈希避免依赖 uuid 模块
        hash_str = f"{source}:{chunk_idx}"
        return abs(hash(hash_str)) % (2**63 - 1)

    def _build_bm25_index(self, documents: List[Document]) -> None:
        """构建 BM25 关键词索引

        Args:
            documents: 文档列表
        """
        self._bm25_docs = []
        for doc in documents:
            tokens = self._tokenize(doc.page_content)
            self._bm25_docs.append({
                "text": doc.page_content,
                "tokens": tokens,
                "metadata": dict(doc.metadata),
                "tf": Counter(tokens),
                "length": len(tokens),
            })

        # 计算 IDF
        if self._bm25_docs:
            n = len(self._bm25_docs)
            df: Dict[str, int] = {}
            for doc_info in self._bm25_docs:
                for token in set(doc_info["tokens"]):
                    df[token] = df.get(token, 0) + 1

            import math
            self._idf = {
                token: math.log((n - freq + 0.5) / (freq + 0.5) + 1)
                for token, freq in df.items()
            }
            self._avg_dl = sum(d["length"] for d in self._bm25_docs) / n
        else:
            self._idf = {}
            self._avg_dl = 1.0

        logger.info("BM25 索引构建完成: %d 个文档", len(self._bm25_docs))

    def _bm25_search(self, query: str, top_k: int = 10) -> List[Document]:
        """BM25 关键词检索

        Args:
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            按 BM25 分数排序的文档列表
        """
        if not self._bm25_docs:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        k1 = 1.5
        b = 0.75
        scored = []

        for doc_info in self._bm25_docs:
            score = 0.0
            dl = doc_info["length"]
            tf_map = doc_info["tf"]

            for token in query_tokens:
                if token in tf_map and token in self._idf:
                    tf = tf_map[token]
                    idf = self._idf[token]
                    norm_tf = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / self._avg_dl))
                    score += idf * norm_tf

            if score > 0:
                scored.append((score, doc_info))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, doc_info in scored[:top_k]:
            doc = Document(
                page_content=doc_info["text"],
                metadata={
                    **doc_info["metadata"],
                    "bm25_score": score,
                },
            )
            results.append(doc)

        return results

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """中文文本分词

        使用简单的正则分词（按非文字字符切分），
        避免引入 jieba 等重依赖。对中文检索已足够有效。

        Args:
            text: 输入文本

        Returns:
            词元列表
        """
        # 按非中文/非英文字符分割，保留中文连续片段和英文单词
        tokens = re.findall(r"[\u4e00-\u9fa5]+|[a-zA-Z]+", text.lower())
        # 过滤掉太短的 token（单字中文信息量低）
        return [t for t in tokens if len(t) >= 2]


def create_qdrant_client(
    host: str = None,
    port: int = None,
) -> QdrantClient:
    """创建 Qdrant 客户端

    Args:
        host: Qdrant 服务地址
        port: Qdrant 服务端口

    Returns:
        QdrantClient 实例
    """
    host = host or QDRANT_HOST
    port = port or QDRANT_PORT
    logger.info("连接 Qdrant: %s:%d", host, port)
    return QdrantClient(host=host, port=port)
