# MindMirror AI — Agent 系统设计与知识库引用指南

> 本文档面向学习者，深入讲解 MindMirror AI 项目中各 Agent 的设计原理、工作方式，
> 以及知识库系统（RAG）如何被引用。所有代码示例均取自项目真实源码。

---

## 一、项目概览

MindMirror AI 是一款**面向青少年的 AI 心理健康伙伴**，通过自然语言对话为用户提供
情绪支持、心理评估、CBT 练习推荐和危机干预服务。

**核心功能**：LangGraph 对话引擎、CrewAI 多智能体协作、RAG 知识库、多模态情绪识别、
危机检测与干预。

**技术栈**：LangGraph、CrewAI、FastAPI、Qdrant、DeepSeek/GLM-4、OpenCV、MediaPipe。

```
┌──────────────────────────────────────────────────┐
│  FastAPI (Web API 层)                             │
├──────────────┬───────────────┬───────────────────┤
│  LangGraph   │   CrewAI      │   Qdrant          │
│  (对话引擎)   │  (多智能体)    │   (向量数据库)     │
├──────────────┴───────────────┴───────────────────┤
│  DeepSeek / GLM-4 (LLM)  +  Zhipu Embedding      │
├──────────────────────────────────────────────────┤
│  OpenCV / MediaPipe (多模态情绪识别)               │
└──────────────────────────────────────────────────┘
```

---

## 二、Agent 系统设计（LangGraph）

LangGraph 是本项目的**对话编排核心**，负责协调情绪感知、危机检查、知识检索、
回复生成等节点之间的状态流转。

### 2.1 LangGraph 状态图架构（src/agent/graph.py）

#### 设计思路：一图多路

整个对话流程被建模为一张**有向状态图**，通过条件边实现"一图多路"——
根据危机风险评估结果，动态决定对话走向**正常路径**还是**危机干预路径**。

```
                    ┌─────────────────────┐
                    │  emotion_perception  │  ← 入口
                    │    (情绪感知)         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    crisis_check      │
                    │    (危机检查)         │
                    └──────────┬──────────┘
                               │ 条件边 (crisis_router)
                    ┌──────────┴──────────┐
               high/crisis            low/medium
                    │                      │
                    ▼                      ▼
         ┌──────────────────┐   ┌─────────────────────┐
         │ crisis_intervention│   │ knowledge_retrieval │
         │   (危机干预)       │   │   (知识检索)         │
         └────────┬─────────┘   └──────────┬──────────┘
                  │                        ▼
                  │             ┌─────────────────────┐
                  │             │ response_generation │→ exercise_suggestion
                  │             └──────────┬──────────┘
                  ▼                        ▼
               ┌─────────────────────────────┐
               │            END               │
               └─────────────────────────────┘
```

#### ConversationState 字段分层

`ConversationState` 是状态图的核心数据结构，共 **12 个字段**，分为 6 个语义层：

```python
class ConversationState(TypedDict):
    # ── 输入层 ──
    user_message: str                    # 用户当前消息
    # ── 情绪识别层 ──
    emotion_result: Optional[dict]       # 情绪分析结果
    emotion_history: list[dict]          # 近期情绪历史（保留最近10条）
    # ── 对话管理层 ──
    messages: list[dict]                 # 对话历史（保留最近20条）
    session_id: str                      # 会话ID（用于检查点恢复）
    turn_count: int                      # 对话轮次计数
    needs_human_intervention: bool       # 是否需要人工干预
    # ── 危机评估层 ──
    risk_level: str                      # low / medium / high / crisis
    crisis_signals: list[str]            # 检测到的危机信号
    # ── 检索增强层 ──
    retrieved_knowledge: list[str]       # RAG检索到的知识片段
    # ── 输出层 ──
    response: str                        # AI回复文本
    suggested_exercises: list[str]       # 建议的CBT练习
```

**设计要点**：每个节点函数只返回需要更新的字段，LangGraph 自动合并到全局状态。

#### 6 个节点的编排

```python
def build_conversation_graph() -> StateGraph:
    graph = StateGraph(ConversationState)

    # 注册6个节点
    graph.add_node("emotion_perception", emotion_perception_node)
    graph.add_node("crisis_check", crisis_check_node)
    graph.add_node("knowledge_retrieval", knowledge_retrieval_node)
    graph.add_node("response_generation", response_generation_node)
    graph.add_node("crisis_intervention", crisis_intervention_node)
    graph.add_node("exercise_suggestion", exercise_suggestion_node)

    graph.set_entry_point("emotion_perception")
    graph.add_edge("emotion_perception", "crisis_check")           # 固定边

    # 条件边：危机检查 → 路由决策
    graph.add_conditional_edges("crisis_check", crisis_router, {
        "crisis_intervention": "crisis_intervention",
        "knowledge_retrieval": "knowledge_retrieval",
    })

    # 正常对话路径
    graph.add_edge("knowledge_retrieval", "response_generation")
    graph.add_edge("response_generation", "exercise_suggestion")
    graph.add_edge("exercise_suggestion", END)
    # 危机干预路径 → 直接结束
    graph.add_edge("crisis_intervention", END)
    return graph
```

#### MemorySaver 检查点机制

`MemorySaver` 提供**跨轮对话的状态恢复**能力。每个会话通过 `thread_id`（即 `session_id`）
关联一个独立的检查点。当用户发送新消息时，`ConversationManager` 先尝试恢复历史状态：

```python
config = {"configurable": {"thread_id": session_id}}
existing_state = await self.compiled_graph.aget_state(config)
if existing_state and existing_state.values:
    prev = existing_state.values
    input_state["messages"] = prev.get("messages", [])
    input_state["emotion_history"] = prev.get("emotion_history", [])
    input_state["turn_count"] = prev.get("turn_count", 0)
```

这样，即使用户的消息是独立 HTTP 请求，系统也能"记住"之前的对话内容和情绪变化趋势。

---

### 2.2 节点函数实现（src/agent/nodes.py）

#### 节点 1：emotion_perception_node（情绪感知）

分析用户消息中的情绪信号，融合外部多模态数据，维护情绪历史。

```python
async def emotion_perception_node(state: dict) -> dict:
    user_message = state.get("user_message", "")
    # 1. 文本情绪分析（基于关键词字典）
    text_result = _analyze_text_emotion(user_message)
    # 2. 合并外部情绪数据（如来自视频/音频分析）
    external_emotion = state.get("emotion_result")
    if external_emotion and isinstance(external_emotion, dict):
        merged = {**text_result, **{k: v for k, v in external_emotion.items() if v is not None}}
    else:
        merged = text_result
    # 3. 更新情绪历史（保留最近 10 条）
    history = list(state.get("emotion_history") or [])
    history.append({"turn": state.get("turn_count", 0),
                    "emotion": merged["dominant_emotion"], "score": merged["score"]})
    if len(history) > 10:
        history = history[-10:]
    return {"emotion_result": merged, "emotion_history": history}
```

**文本情绪分析**使用轻量级关键词字典，覆盖 5 种情绪类型：

| 情绪类型 | 关键词数量 | 示例关键词 |
|---------|-----------|-----------|
| sadness（悲伤） | 18 | 难过、伤心、绝望、崩溃、委屈… |
| anxiety（焦虑） | 16 | 焦虑、紧张、恐惧、失眠、心慌… |
| anger（愤怒） | 14 | 生气、愤怒、暴躁、发火、恨… |
| joy（喜悦） | 16 | 开心、幸福、感恩、兴奋、治愈… |
| neutral（中性） | 6 | 还行、一般、没什么、普通… |

分析逻辑：统计各情绪关键词命中次数 → 归一化 → 取最高分情绪为主导情绪。
无任何命中时返回 `neutral`，score=0.5。

#### 节点 2：crisis_check_node（危机检查）

检测 32 个危机关键词，结合情绪强度进行 **3 层风险评分**：

```
┌─────────────────────────────────────────────────────────────┐
│  有危机关键词?                                               │
│    ├─ 是 → 按命中数量分级:                                   │
│    │     ├─ ≥3 个 → "crisis"                                │
│    │     ├─ 2 个   → "high"                                 │
│    │     └─ 1 个   → "medium"                               │
│    └─ 否 → 检查情绪强度:                                     │
│          ├─ sadness 且 score > 0.7 → "medium"              │
│          ├─ anxiety/anger 且 score > 0.8 → "medium"       │
│          └─ 其他 → "low"                                    │
└─────────────────────────────────────────────────────────────┘
```

危机关键词涵盖自杀、自残、轻生等表述，如 `"自杀", "自残", "不想活", "跳楼",
"割腕", "结束生命", "活着没意思", "轻生", "寻死", "吞药", "上吊", "烧炭",
"世界没有我会更好", "遗书", "再见了"` 等。

#### 节点 3：crisis_router（条件路由）

```python
def crisis_router(state: dict) -> Literal["crisis_intervention", "knowledge_retrieval"]:
    risk_level = state.get("risk_level", "low")
    if risk_level in ("high", "crisis"):
        return "crisis_intervention"    # → 危机干预路径
    return "knowledge_retrieval"        # → 正常对话路径
```

这是整个图的**关键分叉点**——高风险对话不会进入知识检索和回复生成，
而是直接走危机干预路径，确保安全优先。

#### 节点 4：knowledge_retrieval_node（知识检索）

构建检索 query（用户消息 + 情绪关键词），调用 `KnowledgeManager.query()` 获取 top-3 片段：

```python
async def knowledge_retrieval_node(state: dict) -> dict:
    user_message = state.get("user_message", "")
    dominant = emotion_result.get("dominant_emotion", "neutral")
    # 构建 query — 结合用户消息和情绪
    query_parts = [user_message]
    if dominant != "neutral":
        query_parts.append(f"{dominant}情绪 心理疏导")
    query = " ".join(query_parts)
    # 从知识库检索（失败时降级为空列表，不阻断对话）
    try:
        km = KnowledgeManager()
        await km.initialize()
        documents = await km.query(question=query, top_k=3)
        snippets = [doc.page_content for doc in documents if doc.page_content]
    except Exception as e:
        snippets = []   # 降级处理
    return {"retrieved_knowledge": snippets}
```

#### 节点 5：response_generation_node（回复生成）

组装 System Prompt + 情绪上下文 + 知识片段 + 对话历史，调用 LLM 生成回复：

```python
async def response_generation_node(state: dict) -> dict:
    # 1. 加载 System Prompt（从 therapist.md 文件，延迟加载+缓存）
    system_prompt = _get_system_prompt()
    # 2. 构建情绪上下文（含情绪历史趋势摘要）
    emotion_context = {
        "dominant_emotion": emotion_result.get("dominant_emotion"),
        "score": emotion_result.get("score", 0),
    }
    if len(emotion_history) >= 3:
        trend = " → ".join(e.get("emotion", "?") for e in emotion_history[-3:])
        emotion_context["history_summary"] = f"近期情绪变化: {trend}"
    # 3. 调用 LLM 生成回复
    response = await llm.chat_with_context(
        user_message=user_message, emotion_context=emotion_context,
        knowledge_context=knowledge, history=history, system_prompt=system_prompt)
    # 4. 更新对话历史（保留最近 20 条）
    messages.append({"role": "user", "content": user_message})
    messages.append({"role": "assistant", "content": response})
    if len(messages) > 20:
        messages = messages[-20:]
    return {"response": response, "messages": messages, "turn_count": turn_count + 1}
```

#### 节点 6：crisis_intervention_node（危机干预）

三层应对策略：

```
risk_level = "crisis" → 直接使用 CRISIS_RESPONSE_TEMPLATE 模板回复（含4条热线）
                        设置 needs_human_intervention = True

risk_level = "high"   → LLM 生成个性化关怀回复（System Prompt 附加危机提示）
                        确保回复包含热线 400-161-9995
                        设置 needs_human_intervention = True
```

危机干预模板包含 4 条热线：全国心理援助热线 400-161-9995、北京心理危机研究与干预中心
010-82951332、生命热线 400-821-1215、紧急求助 120 或 110。

#### 节点 7：exercise_suggestion_node（练习建议）

基于情绪类型映射 CBT 练习：

| 情绪 | 推荐练习 |
|------|---------|
| sadness | 行为激活、感恩日记、正念呼吸 |
| anxiety | 腹式呼吸(4-7-8法)、渐进式肌肉放松、担忧时间 |
| anger | 情绪记录、认知重评、冷却技巧 |
| joy | 积极体验强化、善意行动 |
| neutral | 情绪觉察、价值探索 |

---

### 2.3 LLM 封装（src/agent/llm.py）

`MindMirrorLLM` 提供多模型统一接口，通过环境变量 `LLM_PROVIDER` 切换 DeepSeek 和 GLM-4。
两者都兼容 OpenAI API 格式，使用 `openai` SDK 统一调用：

```python
class MindMirrorLLM:
    def __init__(self, provider: str = None):
        self.provider = provider or LLM_PROVIDER  # 环境变量：deepseek 或 zhipu
        self._setup_client()  # 根据 provider 设置 api_key/base_url/model

    async def chat(self, messages, temperature=0.7, max_tokens=2000, system_prompt=None):
        # 使用 asyncio.to_thread 异步化同步的 OpenAI 调用
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model, messages=full_messages, ...)
        return response.choices[0].message.content

    async def chat_with_context(self, user_message, emotion_context=None,
                                 knowledge_context=None, history=None, system_prompt=""):
        # 构建上下文注入：情绪信息 + 知识片段 → 追加到 system_prompt
        # 限制历史长度 20 条
        return await self.chat(messages, system_prompt=full_system)

    def _fallback_response(self):
        # API 不可用时的降级回复（包含热线信息）
        return "我现在暂时无法为你提供完整的回复……请拨打 400-161-9995"
```

**单例模式**：通过 `get_llm()` 全局单例，避免重复初始化。节点中通过 `_get_llm()`
延迟初始化并缓存。

---

## 三、CrewAI 多智能体协作

CrewAI 提供多智能体协作能力，作为 LangGraph 对话流程的**可选增强层**，
进行更深度的心理分析。

### 3.1 五个专业化 Agent（src/crew/agents.py）

| Agent | 角色 | 核心目标 | 背景故事关键词 |
|-------|------|---------|--------------|
| assessment_agent | 心理评估专家 | 综合评估用户心理健康状态 | 临床心理评估、严谨客观 |
| emotion_agent | 情绪分析专家 | 识别情绪模式和变化趋势 | 情绪心理学、多维度解读 |
| knowledge_agent | 心理学知识顾问 | 检索专业心理学知识 | CBT、社会心理学、行为心理学 |
| crisis_agent | 危机干预专家 | 实时监控危机信号 | **宁误报毋漏报** |
| intervention_agent | CBT干预顾问 | 推荐CBT练习和干预策略 | 认知行为疗法实践专家 |

```python
crisis_agent = Agent(
    role="危机干预专家",
    goal="实时监控危机信号，确保用户安全，必要时触发紧急干预",
    backstory="你是一位训练有素的危机干预专家……宁可误报也不能漏报。",
    verbose=True, **agent_kwargs,
)
```

> **降级设计**：`agent_kwargs` 在 LLM 不可用时为空字典，Agent 仍创建但不绑定 `llm`。

### 3.2 五个核心 Task（src/crew/tasks.py）

每个 Task 定义了 `description`（含输入数据和输出要求）和 `expected_output`（JSON 格式）。

| Task | Agent | 输出 JSON 核心字段 |
|------|-------|-------------------|
| 心理评估 | assessment | `overall_score`, `dominant_emotion`, `potential_issues`, `risk_factors`, `protective_factors` |
| 情绪分析 | emotion | `primary_emotion`, `secondary_emotions`, `hidden_emotions`, `emotional_triggers`, `emotion_trend` |
| 知识检索 | knowledge | `relevant_theories`, `cbt_techniques`, `psychoeducation`, `coping_strategies` |
| 危机检测 | crisis | `risk_level`, `crisis_signals`, `self_harm_risk`, `suicide_risk`, `urgency`, `hotline_needed` |
| 干预建议 | intervention | `primary_intervention`, `exercises`, `follow_up_questions`, `safety_plan` |

危机检测 Task 特别强调：**"如果出现任何自杀/自伤相关表述，risk_level 必须设为 high 或 crisis"**。

### 3.3 Crew 编排逻辑（src/crew/crew.py）

#### 完整分析模式：run_full_analysis（4 阶段）

```
阶段1: 危机检测（独立执行，优先级最高）
  └─ 如果 risk_level ∈ {high, crisis} → 立即返回，跳过后续

阶段2: 情绪分析 + 心理评估（并行 asyncio.gather）
  ├─ emotion_agent    ─┐
  └─ assessment_agent ─┘ 并行

阶段3: 知识检索（基于评估结果构建查询）
  └─ knowledge_agent

阶段4: 干预建议（基于所有分析结果）
  └─ intervention_agent
```

```python
async def run_full_analysis(self, user_message, emotion_data=None, history=None):
    # 阶段1
    crisis_result = await self._run_crisis_detection(user_message, emotion_data)
    if crisis_result.get("risk_level") in ("high", "crisis"):
        return {"crisis_result": crisis_result, "summary": "危机警报"}
    # 阶段2（并行）
    emotion_analysis, assessment = await asyncio.gather(
        self._run_emotion_analysis(user_message, emotion_data),
        self._run_assessment(user_message, emotion_data, history))
    # 阶段3
    knowledge = await self._run_knowledge_retrieval(query, emotion_context)
    # 阶段4
    intervention = await self._run_intervention(
        json.dumps(assessment), json.dumps(emotion_analysis))
    return {...}  # 所有结果 + summary
```

#### 快速检查模式：run_quick_check（2 阶段）

仅并行执行危机检测 + 情绪分析，用于实时场景。

#### JSON 多层级解析策略（5 层容错）

CrewAI 的 Task 输出是字符串，可能包含 JSON 块或 Markdown 格式。
`_parse_json_output` 实现了 5 层解析容错：

```
策略1: 直接 json.loads(text)
策略2: 提取 ```json ... ``` 代码块
策略3: 提取 ``` ... ``` 代码块
策略4: 查找第一个 { 到最后一个 }
策略5: 全部失败 → 返回 {"raw": raw_output}
```

#### asyncio.to_thread 异步化

CrewAI 内部是同步执行的，通过 `asyncio.to_thread` 包装为异步：

```python
result = await asyncio.to_thread(crew.kickoff)  # 同步→异步
parsed = _parse_json_output(str(result))
```

### 3.4 与 LangGraph 集成（src/crew/integration.py）

`CrewIntegration` 作为 LangGraph 的可选增强节点，根据对话上下文智能决定分析模式：

```
risk_level ∈ {high, crisis}?    → "quick"（快速检查）
turn_count ≥ 3?                 → "full"（完整分析）
情绪波动 > 0.3?                 → "full"（完整分析）
turn_count ≥ 1?                 → "quick"（快速检查）
其他                            → "skip"（跳过）
```

**情绪波动检测**：比较最近 3 轮情绪分数，如果相邻分数最大差值 > 0.3 则触发完整分析。

```python
_FULL_ANALYSIS_TURN_THRESHOLD = 3        # 对话轮次阈值
_EMOTION_VOLATILITY_THRESHOLD = 0.3      # 情绪波动阈值
```

`enhance_response` 方法可直接作为 LangGraph 节点调用，返回 `{"crew_analysis": result}`，
不可用时返回 `{"crew_analysis": None}` 实现降级。

---

## 四、知识库系统（RAG）

知识库系统为对话提供专业心理学知识支撑（RAG），包含文档加载、向量嵌入、
检索和统一管理四个模块。

### 4.1 文档加载与切分（src/knowledge/loader.py）

`KnowledgeLoader` 递归扫描 `knowledge_base/` 下的 `*.md` 文件，按标题层级拆分并切分。

```python
self.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # 每个片段约 500 字符
    chunk_overlap=100,    # 相邻片段重叠 100 字符
    separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", "。", "；"],
)
```

**分隔符优先级**：`## > ### > #### > \n\n > \n > 。 > ；`，
优先在标题边界切分，保持语义完整性。

切分前先用正则按 `##`/`###` 标题预拆分，每个片段保留标题上下文。
每个 Document 携带 5 个元数据字段：`title`, `category`, `source`, `section_title`, `chunk_index`。

### 4.2 向量嵌入（src/knowledge/embeddings.py）

| 后端 | 类名 | 模型 | 维度 | 特点 |
|------|------|------|------|------|
| 在线 API | `ZhipuEmbeddings` | embedding-3 | 2048 | 需 API Key，效果好 |
| 本地离线 | `LocalEmbeddings` | bge-large-zh-v1.5 | 1024 | 无需 API，离线可用 |

两者均兼容 LangChain `Embeddings` 接口。`ZhipuEmbeddings` 分批处理（每批 20 个），
`LocalEmbeddings` 使用 `sentence-transformers` 加载本地模型。

工厂函数 `get_embeddings(backend="zhipu")` 根据配置返回对应实现。

### 4.3 知识检索（src/knowledge/retriever.py）

使用 Qdrant 向量数据库，距离度量为 **COSINE（余弦相似度）**。

#### 三种检索方式

**1. 语义检索 search()**：生成查询向量 → Qdrant 向量搜索 → 返回 top_k 结果。
支持按 `category` 过滤。

**2. 混合检索 hybrid_search()**（语义 0.7 + BM25 0.3）：
分别执行语义检索和 BM25 检索（各取 top_k×2），通过加权融合排序：

```python
# 排名分数 = weight × 1/(rank+1)
semantic_score = 0.7 * (1.0 / (i + 1))   # 语义检索排名分
keyword_score = 0.3 * (1.0 / (i + 1))   # BM25排名分
# 合并同文档分数，按总分降序取 top_k
```

**3. BM25 关键词检索**：经典基于词频和逆文档频率的算法，参数 k1=1.5, b=0.75。
中文分词使用简单正则 `[\u4e00-\u9fa5]+|[a-zA-Z]+`，过滤单字 token，避免引入 jieba。

#### 索引流程

```
批量生成 Embedding → 构建 Qdrant Points（payload含text+metadata）
→ 批量上传（每批100个 upsert）→ 构建 BM25 索引（tf + idf + avg_dl）
```

Point ID 基于 `source:chunk_index` 的哈希，保证幂等性。

### 4.4 统一管理器（src/knowledge/manager.py）

`KnowledgeManager` 封装 Loader、Embeddings、Retriever，对外提供异步 API：

| 方法 | 说明 |
|------|------|
| `initialize()` | 懒加载 + 全量索引。检查 Qdrant 已有数据则跳过索引 |
| `query(question, method="hybrid")` | 统一查询：`hybrid` 混合检索 / `semantic` 语义检索 |
| `update(category)` | 增量更新指定分类（upsert 覆盖同 ID 旧文档） |
| `rebuild()` | 完全重建（删除 collection → 重新创建 → 重新索引） |
| `stats()` | 获取知识库状态统计 |

### 4.5 知识库内容一览

```
knowledge_base/
├── cbt/
│   ├── cbt_core.md          # CBT核心理论（十种认知扭曲等）
│   └── cbt_exercises.md     # CBT练习方法
├── crisis/
│   └── crisis_intervention.md  # SAD PERSONS量表、风险评估
├── social_psych/
│   ├── social_psychology.md    # 社会心理学
│   └── youth_psychology.md     # 青少年心理学
├── behavioral/
│   └── behavioral_psychology.md  # 行为心理学
└── assessments/
    └── scales.md              # 心理测评量表
```

---

## 五、端到端数据流

### 完整对话流程

```
用户消息
    │
    ▼
FastAPI POST /api/chat/message  (routes/chat.py)
    │  ChatRequest {session_id, message, emotion_data?}
    ▼
ConversationManager.chat()  (agent/manager.py)
    ├─ 1. 构建初始 input_state
    ├─ 2. 检查点恢复 (aget_state) → 合并历史 messages/emotion_history/turn_count
    ├─ 3. 执行状态图 (ainvoke)
    │     emotion_perception → crisis_check → [crisis_router]
    │         ├─ high/crisis → crisis_intervention → END
    │         └─ low/medium  → knowledge_retrieval → response_generation
    │                          → exercise_suggestion → END
    └─ 4. 返回结果
    │
    ▼
检查点保存 (MemorySaver 自动持久化状态)
    │
    ▼
返回 ChatResponse {response, emotion, risk_level,
                   suggested_exercises, needs_human_intervention}
```

### 模块间调用关系

```
FastAPI (routes/chat.py)
  └─→ ConversationManager (agent/manager.py)
        ├─→ LangGraph 状态图 (agent/graph.py)
        │     ├─→ emotion_perception_node → _analyze_text_emotion (关键词字典)
        │     ├─→ crisis_check_node → CRISIS_KEYWORDS 匹配
        │     ├─→ crisis_router → 条件路由
        │     ├─→ knowledge_retrieval_node → KnowledgeManager
        │     │     └─→ KnowledgeLoader + get_embeddings + KnowledgeRetriever
        │     │           └─→ Qdrant (向量搜索 + BM25)
        │     ├─→ response_generation_node → MindMirrorLLM
        │     │     └─→ OpenAI SDK → DeepSeek/GLM-4 API
        │     ├─→ crisis_intervention_node → 模板/LLM + 热线
        │     └─→ exercise_suggestion_node → exercise_map (情绪→CBT映射)
        │
        └─→ [可选] CrewIntegration (crew/integration.py)
              └─→ MindMirrorCrew → 5个Agent协作 (CrewAI)
```

---

## 六、关键设计模式

### 6.1 异步编程策略

```python
# async/await — 所有节点函数和 API 路由
async def emotion_perception_node(state: dict) -> dict: ...

# asyncio.gather — 并行执行独立任务（情绪分析 + 心理评估）
emotion_analysis, assessment = await asyncio.gather(
    self._run_emotion_analysis(...), self._run_assessment(...))

# asyncio.to_thread — 将同步调用包装为异步（CrewAI kickoff / OpenAI SDK）
result = await asyncio.to_thread(crew.kickoff)
```

### 6.2 多层级容错

| 层级 | 场景 | 降级策略 |
|------|------|---------|
| LLM 降级 | API 不可用 | `_fallback_response()` 返回带热线的默认回复 |
| 知识库跳过 | Qdrant/Embedding 失败 | `snippets=[]` 继续对话 |
| JSON 解析 | CrewAI 输出格式不规范 | 5 层解析策略，最终返回 `{"raw": text}` |
| CrewAI 降级 | API Key 未配置 | `enhance_response` 返回 `{crew_analysis: None}` |
| 状态图异常 | ainvoke 失败 | 返回友好错误消息 |

### 6.3 单例模式

LLM、ConversationManager、节点级 LLM/Prompt 均使用单例模式，延迟初始化避免启动开销。

### 6.4 状态管理

- `messages` 限 20 条（保留最近对话上下文）
- `emotion_history` 限 10 条（保留近期情绪趋势）
- 通过 MemorySaver 检查点跨轮持久化

### 6.5 安全性设计

```
第1层: 关键词检测（32个危机关键词）→ 命中数量决定风险等级
第2层: 情绪强度辅助判断 → sadness>0.7 或 anxiety/anger>0.8 提升到 medium
第3层: 条件路由 → high/crisis 直接进入危机干预，跳过正常流程
第4层: 危机干预三层策略 → crisis:模板回复 / high:LLM关怀+热线
第5层: needs_human_intervention 标志 → 前端/后台可触发人工介入
第6层: CrewAI 危机检测 Agent → 独立多智能体评估（宁误报毋漏报）
```

---

## 七、学习路径建议

### 代码阅读推荐顺序

```
第一阶段：理解对话主流程
  1. src/utils/config.py        → 配置和环境变量
  2. src/agent/graph.py         → 状态图结构和条件路由
  3. src/agent/manager.py       → 检查点恢复和会话管理
  4. src/agent/nodes.py         → 6个节点函数
  5. src/api/routes/chat.py     → API入口

第二阶段：理解LLM和知识库
  6. src/agent/llm.py           → 多模型封装和降级
  7. src/knowledge/loader.py    → 文档加载和切分
  8. src/knowledge/retriever.py → 语义/混合/BM25检索
  9. src/knowledge/manager.py   → 统一管理器API

第三阶段：理解多智能体协作
  10. src/crew/agents.py        → 5个Agent角色设计
  11. src/crew/tasks.py         → 5个Task输入输出
  12. src/crew/crew.py          → 编排逻辑和JSON解析
  13. src/crew/integration.py   → 智能触发策略
```

### 核心概念优先级

| 优先级 | 概念 | 学习要点 |
|-------|------|---------|
| P0 | LangGraph 状态图 | 条件路由、状态流转、检查点 |
| P0 | 危机检测机制 | 关键词匹配、3层评分、路由分叉 |
| P1 | LLM 封装 | 多模型切换、上下文注入、降级 |
| P1 | RAG 知识检索 | 混合检索、BM25、懒加载 |
| P2 | CrewAI 多智能体 | 并行编排、JSON解析容错 |
| P2 | 集成触发策略 | 轮次阈值、情绪波动检测 |

### 扩展方向

1. **持久化检查点**：将 `MemorySaver` 替换为 `SqliteSaver`/`PostgresSaver`
2. **流式回复**：通过 `StreamingResponse` 实现逐字返回
3. **知识库自动更新**：文件监听 + 自动触发 `update()`
4. **多模态深度集成**：视频情绪识别结果作为 `emotion_data` 传入对话引擎
5. **A/B 测试框架**：评估不同 System Prompt 和 CBT 策略的效果

---

> **文档版本**：v1.0 | **对应代码**：MindMirror AI 当前主干 | **维护者**：MindMirror AI Team
