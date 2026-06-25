# MindMirror AI 技术架构文档

## 项目概述

MindMirror AI 是一个面向青少年的心理健康 AI 智能体系统，定位为"家庭心理医生"。系统通过多模态情绪识别（视频+音频+文本）实时感知用户情绪状态，结合专业心理学知识库，提供温暖、专业的心理支持对话。

**双重用途定位**：
1. **学习智能体** — 学习心理学知识、AI 框架使用、算法研究
2. **项目开发** — 构建可运行的心理健康 AI 产品原型

---

## 系统架构全景

```
┌─────────────────────────────────────────────────────────────┐
│                    前端层 (React Web)                         │
│  React 18 + TypeScript + Vite + TailwindCSS                 │
│  SVG 卡通头像(6种表情) + 对话界面 + 情绪仪表盘              │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API / WebSocket
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    API 网关层 (FastAPI)                       │
│  /api/chat/* — 对话接口                                      │
│  /api/emotion/* — 情绪分析接口                               │
│  /api/video/* — 视频流 WebSocket                             │
└────────┬──────────────────┬──────────────────┬──────────────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────────┐
│ LangGraph      │ │ 情绪识别引擎   │ │ 视频流管道          │
│ 对话状态图      │ │ 多模态融合     │ │ WebRTC + 安全模块   │
└───────┬────────┘ └────────────────┘ └────────────────────┘
        │
        ▼
┌────────────────────────────────────────────────┐
│            CrewAI 多智能体协作层                 │
│  评估Agent / 情绪Agent / 知识Agent /           │
│  危机Agent / 干预Agent                          │
└────────────────────┬───────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────────┐ ┌────────┐ ┌──────────┐
│ GLM-4 (智谱) │ │ Qdrant │ │  Redis   │
│ 对话生成      │ │ 向量库  │ │  缓存    │
└──────────────┘ └────────┘ └──────────┘
```

---

## 技术栈总览

| 层次 | 技术选型 | 版本要求 | 作用 |
|------|---------|---------|------|
| 智能体框架 | LangGraph | >=0.2.0 | 对话状态图、流程编排 |
| 多智能体 | CrewAI | >=0.80.0 | 专业化 Agent 协作 |
| 知识库/RAG | LangChain + Qdrant | >=0.3.0 / >=1.12.0 | 心理学知识检索增强 |
| 大模型 | GLM-4 (智谱 AI) | zhipuai >=2.1.0 | 对话生成、知识注入 |
| 视频情绪 | DeepFace + MediaPipe | >=0.0.93 / >=0.10.0 | 面部表情分类 |
| 音频情绪 | OpenSMILE + XGBoost | >=2.5.0 / >=2.1.0 | 语音情感分析 |
| 后端框架 | FastAPI + Uvicorn | >=0.115.0 | 异步高性能 API |
| 前端框架 | React + TypeScript | 18.x + 5.x | Web 交互界面 |
| 前端构建 | Vite | 5.x | 快速 HMR 开发体验 |
| 样式 | TailwindCSS | 3.4.x | 原子化 CSS |
| 容器化 | Docker + docker-compose | — | 一键部署 |
| 向量数据库 | Qdrant | latest | Embedding 存储和检索 |
| 缓存 | Redis | 7.x | 会话缓存 |

---

## 核心技术点详解

### 1. LangGraph 对话状态图

**作用**：管理心理对话的完整生命周期，确保每一轮对话经过情绪感知、安全检查、知识检索、回复生成的完整流程。

**核心设计**：

```python
# 状态定义
class ConversationState(TypedDict):
    user_message: str              # 用户输入
    emotion_result: Optional[dict] # 情绪分析结果
    emotion_history: list[dict]    # 情绪历史
    messages: list[dict]           # 对话历史
    retrieved_knowledge: list[str] # RAG 检索结果
    risk_level: str                # 风险等级
    crisis_signals: list[str]      # 危机信号
    response: str                  # AI 回复
    needs_human_intervention: bool # 人工干预标记
```

**状态图流程**：

```
emotion_perception → crisis_check → [条件路由]
                                        │
                    ┌───────────────────┤
                    ▼                    ▼
          crisis_intervention    knowledge_retrieval
                    │                    │
                    ▼                    ▼
                   END          response_generation
                                        │
                                        ▼
                                exercise_suggestion
                                        │
                                        ▼
                                       END
```

**关键特性**：
- `MemorySaver` 检查点：持久化对话状态，支持会话恢复
- 条件边路由：risk_level 为 high/crisis 时走危机干预通道
- Human-in-the-loop：高危情况标记需要人工介入
- 对话历史限制 20 条，避免上下文过长

---

### 2. CrewAI 多智能体协作

**作用**：多维度专业化分析，模拟心理咨询团队协作。

**5 个专业 Agent**：

| Agent | 角色 | 职责 |
|-------|------|------|
| 心理评估专家 | Assessment | 综合评估心理状态（1-10分） |
| 情绪分析专家 | Emotion | 深度解读情绪模式和变化趋势 |
| 心理学知识顾问 | Knowledge | 从知识库检索相关理论和技术 |
| 危机干预专家 | Crisis | 识别自杀/自伤风险信号 |
| CBT 干预顾问 | Intervention | 推荐个性化 CBT 练习方案 |

**执行模式**：

```
完整分析 (run_full_analysis):
  危机检测 → [高危中断] → 情绪+评估并行 → 知识检索 → 干预建议

快速检查 (run_quick_check):
  危机检测 + 情绪分析（并行）
```

**触发条件**：
- 对话轮次 > 3 时启动完整分析
- 情绪波动 > 0.3 时触发深度分析
- 高风险场景立即触发

**LLM 接入**：通过智谱 AI 的 OpenAI 兼容端点 (`https://open.bigmodel.cn/api/paas/v4/`) 连接 GLM-4。

---

### 3. RAG 知识库系统

**作用**：为 AI 对话注入专业心理学知识，确保回复有据可依。

**架构**：

```
知识文档(.md) → LangChain 加载切分 → Embedding 生成 → Qdrant 存储
                                                          │
用户问题 → Query Embedding → 混合检索(语义+关键词) → Top-K 结果
                                                          │
                                                          ▼
                                                   注入 LLM 上下文
```

**知识库内容**：

| 分类 | 内容 |
|------|------|
| CBT 认知行为疗法 | 认知三角、10种认知扭曲、ABC模型、行为激活 |
| CBT 练习指南 | 思维记录表、认知重构、肌肉放松、正念呼吸 |
| 社会心理学 | 归因理论、从众/服从、群体极化、依恋理论 |
| 行为心理学 | 条件反射、社会学习、行为塑造、习惯养成 |
| 心理测评 | PHQ-9、GAD-7、SCL-90、K-10 完整量表 |
| 危机干预 | SAD PERSONS、危机信号识别、安全计划 |
| 青少年心理 | Erikson 身份认同、校园欺凌、情绪调节 |

**技术细节**：
- **文档切分**：RecursiveCharacterTextSplitter（chunk_size=500, overlap=100）
- **Embedding**：智谱 embedding-3 模型（备选 BAAI/bge-large-zh-v1.5 本地模型）
- **检索策略**：混合检索 = 语义相似度 + BM25 关键词匹配
- **元数据过滤**：支持按 category 过滤（如只检索 CBT 相关知识）

---

### 4. 多模态情绪识别

**作用**：从视频、音频、文本三个维度综合判断用户情绪状态。

#### 4.1 视频情绪识别

| 组件 | 技术 | 功能 |
|------|------|------|
| 人脸检测 | MediaPipe / Haar Cascade | 定位人脸区域 |
| 表情分类 | DeepFace | 7种基本情绪概率分布 |
| 预处理 | CLAHE + 拉普拉斯锐化 | 低光照/模糊帧增强 |

**输出**：
```python
@dataclass
class VideoEmotionResult:
    dominant_emotion: str       # 主要情绪
    emotion_scores: Dict[str, float]  # 7种情绪概率
    confidence: float           # 置信度 (0-1)
    valence: float             # 效价 (-1到1)
    arousal: float             # 唤醒度 (0-1)
    face_detected: bool
```

#### 4.2 音频情绪识别

| 组件 | 技术 | 功能 |
|------|------|------|
| 特征提取 | OpenSMILE eGeMAPS | 88维标准化特征 |
| 分类器 | XGBoost | 9类情绪分类 |
| 降级方案 | 规则方法 | OpenSMILE 不可用时的 fallback |

**9 类情绪输出**：neutral, happy, sad, angry, fearful, surprised, disgusted, anxious, depressed

**规则方法逻辑**：
- 高音调 + 高能量 → 愤怒/兴奋
- 低音调 + 低能量 → 悲伤/抑郁
- 高语速 → 焦虑
- 正常范围 → 平静

#### 4.3 多模态融合

**融合策略**：晚融合 + 动态加权 + 冲突规则

```
视频情绪(7类) ─┐
               ├→ 标签统一(9类) → 动态加权 → 融合结果 → 危机检测
音频情绪(9类) ─┘
```

**动态权重规则**：

| 情绪类型 | 视频权重 | 音频权重 | 理由 |
|---------|---------|---------|------|
| 焦虑 | 0.3 | 0.7 | 音调/节奏最敏感 |
| 抑郁 | 0.7 | 0.3 | 面部表情最直观 |
| 愤怒 | 0.5 | 0.5 | 平等权重 |
| 默认 | 0.6 | 0.4 | 视频略优先 |

**冲突处理**：危机情绪保守原则 > 置信度差距 > 视频优先

**危机检测阈值**：

| 情绪 | 阈值 | 风险级别 |
|------|------|---------|
| sad | >0.8 | high |
| fearful | >0.85 | high |
| depressed | >0.7 | high |
| 极低效价(valence < -0.8) | — | crisis |

---

### 5. 视频流实时处理

**作用**：安全地接收和处理用户视频流，实时分析情绪。

**处理管道**：

```
WebSocket 接收 base64 帧
    ↓
帧采样（target_fps=2，不需要每帧分析）
    ↓
CLAHE 自适应预处理
    ↓
EmotionAnalyzer.analyze_video_stream()
    ↓
滑动窗口平滑（window_size=5）
    ↓
返回情绪标签（不返回原始帧数据）
```

**安全机制**：

| 措施 | 实现 |
|------|------|
| 视频不存储 | 帧处理即丢弃，不写磁盘 |
| 面部模板不保存 | 仅提取情绪标签 |
| 年龄验证 | 未成年人(<18)需家长同意 |
| 家长同意 | 验证码机制（SHA256 存储） |
| 会话超时 | 默认 1 小时自动断开 |
| 审计日志 | 完整数据访问记录 |
| 数据保留 | 情绪标签最多 30 天 |

**数据政策**：
```json
{
  "video_storage": "none",
  "face_templates": "none",
  "emotion_labels": "session_only",
  "retention_period_days": 30,
  "encryption": "AES-256",
  "transmission": "TLS 1.3",
  "third_party_sharing": "none"
}
```

---

### 6. GLM-4 大模型对话

**作用**：生成温暖、专业的心理支持回复。

**接入方式**：
- SDK：zhipuai Python SDK
- 兼容端点：`https://open.bigmodel.cn/api/paas/v4/`（OpenAI 格式）
- 异步化：`asyncio.to_thread` 包装同步调用

**System Prompt 核心原则**：
1. 温暖与同理心：始终以接纳态度回应
2. 非评判性：不评判用户感受或行为
3. 安全第一：危机信号立即触发安全协议
4. 专业边界：不诊断、不开药、不替代专业治疗

**上下文注入格式**：
```
[System Prompt: 心理咨询师角色]
[情绪上下文: 当前情绪状态、效价、唤醒度]
[知识上下文: RAG 检索的相关心理学知识]
[对话历史: 最近 20 条消息]
[用户消息]
```

**安全护栏**：
- 危机回复强制附加热线信息
- API Key 缺失时返回安全提示 + 热线号码
- 对话历史限制 20 条避免 token 溢出

---

### 7. 危机预警系统

**作用**：实时监控用户安全状态，确保高危情况及时干预。

**触发机制**：

```
文本关键词检测（30+ 中文危机词）
    + 情绪分析阈值
    + 多模态融合结果
        ↓
    4 级风险评估
        ↓
    low → 正常对话
    medium → 增加关注，温和引导
    high → 触发危机干预模板
    crisis → 中断对话，强制输出热线 + 标记人工介入
```

**危机关键词示例**：自杀、自残、不想活、跳楼、割腕、结束生命、活着没意思、死了算了...

**危机干预回复模板**：
- 情感验证（"我感受到你现在很痛苦"）
- 安全确认（"你现在安全吗？"）
- 热线信息（全国心理援助热线 400-161-9995）
- 人工介入标记

---

### 8. 前端界面

**作用**：提供青少年友好的交互界面。

**技术实现**：

| 功能 | 实现方式 |
|------|---------|
| 卡通头像 | SVG 内联绘制，6种表情 CSS transition |
| 对话窗口 | 消息列表 + 自动滚动 + Markdown 渲染 |
| 打字机效果 | 逐字显示 AI 回复 |
| 情绪仪表盘 | SVG 圆弧 + 颜色编码 |
| 情绪趋势图 | Canvas 折线图 |
| 快速评估 | 4题弹窗式心理评估 |
| 暗色模式 | prefers-color-scheme 自动切换 |
| 响应式 | 移动端上下排列，桌面端左右布局 |

**配色方案**：
- 主色：薰衣草紫 #7C5CFC
- 暖白：#FFF8F0
- 浅蓝：#E8F4FD
- 圆角设计（16px+），柔和阴影

**头像表情**：neutral / happy / empathy / thinking / concerned / encouraging

---

## 数据流全链路

```
用户输入（文本/视频帧/音频）
    │
    ├─[文本] → POST /api/chat/message
    │              ↓
    │         LangGraph 状态图执行
    │              ↓
    │         emotion_perception（关键词情感分析）
    │              ↓
    │         crisis_check（30+ 关键词 + 阈值）
    │              ↓
    │         [高危] → crisis_intervention → 热线信息
    │         [正常] → knowledge_retrieval（Qdrant RAG）
    │                       ↓
    │                  response_generation（GLM-4）
    │                       ↓
    │                  exercise_suggestion（CBT推荐）
    │                       ↓
    │                  返回 ChatResponse
    │
    ├─[视频帧] → WebSocket /api/video/stream
    │              ↓
    │         安全检查（权限+会话有效性）
    │              ↓
    │         帧解码（base64 → numpy）
    │              ↓
    │         帧采样（2fps）+ CLAHE 预处理
    │              ↓
    │         DeepFace 表情分类
    │              ↓
    │         滑动窗口平滑 → 返回情绪标签
    │
    └─[音频] → POST /api/emotion/analyze/audio
                   ↓
              OpenSMILE eGeMAPS 特征提取
                   ↓
              XGBoost 分类 / 规则方法
                   ↓
              返回 AudioEmotionResult
```

---

## 基础设施

### Docker 服务编排

```yaml
services:
  app:        # FastAPI 应用 (port 8000)
  qdrant:     # 向量数据库 (port 6333/6334)
  redis:      # 缓存 (port 6379)
```

### 快速启动

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 ZHIPU_API_KEY

# 2. 启动后端服务
docker-compose up -d

# 3. 启动 API（开发模式）
uvicorn src.api.main:app --reload --port 8000

# 4. 启动前端（开发模式）
cd frontend && npm install && npm run dev
```

---

## 项目目录结构

```
f:\Agent\mindmirror-ai\code\mindmirror\
├── pyproject.toml              # Python 依赖和项目配置
├── Dockerfile                  # 容器化构建
├── docker-compose.yml          # 服务编排
├── .env.example                # 环境变量模板
├── src/
│   ├── agent/                  # LangGraph 对话引擎
│   │   ├── graph.py            # 状态图定义
│   │   ├── nodes.py            # 节点函数实现
│   │   ├── llm.py              # GLM-4 封装
│   │   └── manager.py          # 对话管理器
│   ├── knowledge/              # RAG 知识库
│   │   ├── loader.py           # 文档加载切分
│   │   ├── embeddings.py       # Embedding 生成
│   │   ├── retriever.py        # 向量检索
│   │   └── manager.py          # 知识库管理器
│   ├── emotion/                # 情绪识别
│   │   ├── video.py            # 视频情绪（DeepFace）
│   │   ├── audio.py            # 音频情绪（OpenSMILE）
│   │   ├── fusion.py           # 多模态融合
│   │   └── analyzer.py         # 统一接口
│   ├── multimodal/             # 视频流处理
│   │   ├── pipeline.py         # 处理管道
│   │   ├── webrtc.py           # WebRTC 接入
│   │   └── safety.py           # 安全模块
│   ├── crew/                   # CrewAI 多智能体
│   │   ├── agents.py           # Agent 定义
│   │   ├── tasks.py            # Task 定义
│   │   ├── crew.py             # Crew 编排
│   │   └── integration.py      # LangGraph 集成
│   ├── api/                    # FastAPI 接口
│   │   ├── main.py             # 应用入口
│   │   └── routes/             # 路由（chat/emotion/video/health）
│   └── utils/                  # 工具
│       ├── config.py           # 配置管理
│       └── logger.py           # 日志
├── knowledge_base/             # 心理学知识文档
│   ├── cbt/                    # CBT 认知行为疗法
│   ├── social_psych/           # 社会心理学 + 青少年心理
│   ├── behavioral/             # 行为心理学
│   ├── assessments/            # 心理测评量表
│   └── crisis/                 # 危机干预指南
├── models/                     # 本地模型文件
├── configs/
│   ├── prompts/therapist.md    # 心理咨询师 System Prompt
│   └── settings.yaml           # 应用配置
├── tests/                      # 测试
├── frontend/                   # React Web 前端
│   ├── src/components/         # UI 组件
│   ├── src/hooks/              # 自定义 Hooks
│   ├── src/services/           # API 调用
│   └── ...
└── docs/                       # 文档
```

---

## 后续迭代方向

| 方向 | 内容 | 优先级 |
|------|------|--------|
| 大模型微调 | LoRA/QLoRA 指令微调心理咨询对话 | P1 |
| 心理测评 | PHQ-9、GAD-7 完整评测流程 | P1 |
| Live2D 升级 | 替换 SVG 为真实 Live2D 模型 | P2 |
| TTS 语音合成 | Azure TTS / Edge TTS 集成 | P2 |
| 性能优化 | 全链路延迟 <2s | P2 |
| 安全合规 | COPPA 合规审计 + 法律审查 | P0 |

---

## 风险与注意事项

1. **API Key 必需**：GLM-4 对话功能需要有效的 `ZHIPU_API_KEY`
2. **OpenSMILE 兼容性**：Windows 下可能有问题，已内置规则方法 fallback
3. **合规要求**：生产部署前需法律审查隐私政策和未成年人保护合规
4. **模型精度**：开源情绪识别准确率 70-78%，可通过数据微调提升
5. **不可替代专业治疗**：系统明确定位为辅助工具，不替代专业心理咨询

---

*文档版本：v1.0 | 更新时间：2026-06-25*
