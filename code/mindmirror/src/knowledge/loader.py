"""知识库文档加载和切分模块

负责递归扫描 knowledge_base/ 下所有 Markdown 文件，
按分类加载并切分为适合 Embedding 和向量检索的文档片段。
"""
import re
from pathlib import Path
from typing import List, Optional

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.utils.logger import get_logger

logger = get_logger(__name__)


class KnowledgeLoader:
    """心理学知识库文档加载器

    Attributes:
        knowledge_base_dir: 知识库根目录
        text_splitter: 文档切分器
    """

    def __init__(self, knowledge_base_dir: Path):
        self.knowledge_base_dir = knowledge_base_dir
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", "。", "；"],
        )

    def load_all(self) -> List[Document]:
        """加载所有知识库文档

        Returns:
            切分后的 Document 列表，每个 Document 包含 category、source、title 等元数据
        """
        all_docs: List[Document] = []

        if not self.knowledge_base_dir.exists():
            logger.warning("知识库目录不存在: %s", self.knowledge_base_dir)
            return all_docs

        md_files = sorted(self.knowledge_base_dir.rglob("*.md"))
        logger.info("发现 %d 个 Markdown 文件", len(md_files))

        for file_path in md_files:
            try:
                docs = self._load_markdown(file_path)
                all_docs.extend(docs)
            except Exception as e:
                logger.error("加载文件失败 %s: %s", file_path, e)

        logger.info("共加载 %d 个文档片段", len(all_docs))
        return all_docs

    def load_category(self, category: str) -> List[Document]:
        """加载指定分类的知识文档

        Args:
            category: 分类名称（对应目录名，如 'cbt', 'crisis', 'social_psych' 等）

        Returns:
            该分类下的文档片段列表
        """
        category_dir = self.knowledge_base_dir / category
        if not category_dir.exists():
            logger.warning("分类目录不存在: %s", category_dir)
            return []

        docs: List[Document] = []
        md_files = sorted(category_dir.rglob("*.md"))
        logger.info("分类 '%s' 中发现 %d 个文件", category, len(md_files))

        for file_path in md_files:
            try:
                file_docs = self._load_markdown(file_path)
                docs.extend(file_docs)
            except Exception as e:
                logger.error("加载文件失败 %s: %s", file_path, e)

        return docs

    def get_categories(self) -> List[str]:
        """获取所有知识分类名称

        Returns:
            分类名称列表
        """
        if not self.knowledge_base_dir.exists():
            return []

        return [
            d.name
            for d in sorted(self.knowledge_base_dir.iterdir())
            if d.is_dir() and not d.name.startswith(".")
        ]

    def _load_markdown(self, file_path: Path) -> List[Document]:
        """加载单个 Markdown 文件并添加元数据

        Args:
            file_path: Markdown 文件路径

        Returns:
            切分后的 Document 列表
        """
        content = file_path.read_text(encoding="utf-8")

        # 提取文件标题（第一个 # 开头的行）
        title = self._extract_title(content)

        # 确定分类（取 knowledge_base_dir 下的第一级目录名）
        category = self._get_category(file_path)

        # 按标题层级拆分内容为带上下文的片段
        sections = self._split_by_headings(content)

        documents: List[Document] = []
        for section in sections:
            chunks = self.text_splitter.split_text(section["text"])
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": str(file_path.relative_to(self.knowledge_base_dir)),
                        "category": category,
                        "title": title,
                        "section_title": section.get("heading", title),
                        "chunk_index": i,
                    },
                )
                documents.append(doc)

        logger.debug("文件 %s 切分为 %d 个片段", file_path.name, len(documents))
        return documents

    def _extract_title(self, content: str) -> str:
        """从 Markdown 内容中提取一级标题

        Args:
            content: Markdown 文件内容

        Returns:
            标题文本，如果没有找到则返回空字符串
        """
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("# ") and not stripped.startswith("## "):
                return stripped[2:].strip()
        return ""

    def _get_category(self, file_path: Path) -> str:
        """根据文件路径确定分类

        Args:
            file_path: 文件路径

        Returns:
            分类名称
        """
        try:
            relative = file_path.relative_to(self.knowledge_base_dir)
            parts = relative.parts
            if len(parts) > 1:
                return parts[0]
        except ValueError:
            pass
        return "general"

    def _split_by_headings(self, content: str) -> List[dict]:
        """按标题层级将 Markdown 内容拆分为多个片段

        每个片段保留其标题上下文，便于后续检索时提供完整语义。

        Args:
            content: Markdown 文件内容

        Returns:
            包含 heading 和 text 的字典列表
        """
        # 按 ## 或 ### 标题分割
        pattern = r"(?=^#{2,3}\s)"
        sections = re.split(pattern, content, flags=re.MULTILINE)

        result = []
        for section in sections:
            section = section.strip()
            if not section:
                continue

            # 提取该段落的标题
            heading = ""
            for line in section.split("\n"):
                stripped = line.strip()
                if stripped.startswith("##"):
                    heading = stripped.lstrip("#").strip()
                    break

            result.append({
                "heading": heading,
                "text": section,
            })

        # 如果没有按标题拆分出结果，回退为整个内容作为一个片段
        if not result:
            result = [{"heading": "", "text": content}]

        return result
