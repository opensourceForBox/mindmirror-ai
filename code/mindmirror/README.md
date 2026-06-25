# MindMirror AI

> AI-powered mental health companion for youth（青少年 AI 心理健康伙伴）

## 项目概述

MindMirror AI 是一款面向青少年的心理健康辅助系统，通过多模态情绪识别（视频+音频）、大语言模型对话（GLM-4）和心理学知识库（RAG），提供温暖、专业、安全的心理健康支持。

## 技术栈

| 领域 | 技术 |
|------|------|
| 智能体框架 | LangGraph + CrewAI |
| LLM | GLM-4（智谱 AI） |
| 情绪识别（视频） | DeepFace + MediaPipe + OpenCV |
| 情绪识别（音频） | OpenSMILE |
| 多模态融合 | XGBoost |
| 向量数据库 | Qdrant |
| API 框架 | FastAPI |
| 部署 | Docker Compose |

## 快速开始

### 1. 环境准备

```bash
# 复制环境变量文件并填写 API Key
cp .env.example .env
# 编辑 .env，填入 ZHIPU_API_KEY 等配置
```

### 2. Docker 一键启动

```bash
docker-compose up --build
```

服务启动后访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 3. 本地开发（可选）

```bash
# 安装依赖（推荐 uv）
pip install -e ".[dev]"

# 启动开发服务器
uvicorn src.api.main:app --reload
```

## 项目结构

```
mindmirror/
├── src/
│   ├── agent/        # LangGraph 智能体核心（对话状态图）
│   ├── knowledge/    # 知识库管理（RAG 检索增强生成）
│   ├── emotion/      # 情绪识别（视频/音频/多模态融合）
│   ├── multimodal/   # 多模态处理管道
│   ├── avatar/       # 数字人界面（TTS）
│   ├── api/          # FastAPI 接口
│   ├── crew/         # CrewAI 多智能体协作
│   └── utils/        # 工具函数
├── knowledge_base/   # 心理学知识库文档
├── models/           # 本地模型文件
├── configs/          # 配置文件与 Prompt 模板
└── tests/            # 单元测试
```

## 安全说明

本系统内置危机检测机制，当识别到用户存在自伤/自杀风险时，将立即提供危机干预热线信息：

- 全国心理援助热线：**400-161-9995**
- 北京心理危机研究与干预中心：**010-82951332**
- 生命热线：**400-821-1215**

> ⚠️ 本系统为 AI 辅助工具，不替代专业心理咨询或医疗诊断。

## License

MIT
