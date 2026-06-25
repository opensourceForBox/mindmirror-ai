"""配置管理模块"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# LLM 配置（支持 deepseek / glm-4 切换）
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek")  # deepseek 或 zhipu

# DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# Zhipu GLM-4 (保留)
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
ZHIPU_BASE_URL = os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
ZHIPU_MODEL = os.getenv("ZHIPU_MODEL", "glm-4")

# Qdrant
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

# FastAPI
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# 知识库路径
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"

# 模型路径
MODELS_DIR = PROJECT_ROOT / "models"
