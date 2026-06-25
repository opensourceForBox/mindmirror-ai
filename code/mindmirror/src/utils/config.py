"""配置管理模块"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# API Keys
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")

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
