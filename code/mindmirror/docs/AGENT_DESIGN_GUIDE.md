# MindMirror AI — Agent 系统设计与知识库引用指南

> 本文档面向学习者，深入讲解 MindMirror AI 项目中各 Agent 的设计原理、工作方式，
> 以及知识库系统（RAG）如何被引用。所有代码示例均取自项目真实源码。

---

## 目录

- [一、项目概览](#一项目概览)
- [二、Agent 系统设计（LangGraph）](#二agent-系统设计langgraph)
- [三、CrewAI 多智能体协作](#三crewai-多智能体协作)
- [四、知识库系统（RAG）](#四知识库系统rag)
- [五、端到端数据流](#五端到端数据流)
- [六、关键设计模式](#六关键设计模式)
- [七、学习路径建议](#七学习路径建议)

---

## 一、项目概览

### 1.1 项目定位

MindMirror AI 是一款**面向青少年的 AI 心理健康伙伴**。它通过自然语言对话，
为用户提供情绪支持、心理评估、CBT（认知行为疗法）练习推荐和危机干预服务。

### 1.2 核心功能

| 功能模块 | 说明 |
|---------|------|
| LangGraph 对话引擎 | 基于状态图的对话编排，支持条件路由、检查点恢复 |
| CrewAI 多智能体协作 | 5 个专业化 Agent 协同完成深度心理分析 |
| RAG 知识库 | 基于 Qdrant 的心理学知识检索，支持语义+关键词混合检索 |
| 多模态情绪识别 | 文本情绪分析 + 视频/音频情绪融合 |
| 危机检测与干预 | 多层危机关键词检测 + 三层风险评分 + 热线自动推送 |

### 1.3 技术栈

```
┌──────────────────────────────────────────────────┐
│                   前端 / 客户端                     │
├──────────────────────────────────────────────────┤
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
即根据危机风险评估结果，动态决定对话走向**正常路径**还是**危机干预路径**。

```
                         ┌─────────────────────┐
                         │  emotion_perception  │  ← 入口节点
                         │    (情绪感知)         │
                         └──────────┬──────────┘
                                    │ 固定边
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
                       │                        │ 固定边
                       │                        ▼
                       │             ┌─────────────────────┐
                       │             │ response_generation │
                       │             │   (回复生成)         │
                       │             └──────────┬──────────┘
                       │                        │ 固定边
                       │                        ▼
                       │             ┌─────────────────────┐
                       │             │ exercise_suggestion │
                       │             │   (练习建议)         │
                       │             └──────────┬──────────┘
                       │                        │
                       ▼                        ▼
                    ┌─────────────────────────────┐
                    │            END               │
                    └─────────────────────────────┘
```

#### ConversationState 字段分层

`ConversationState` 是 LangGraph 状态图的核心数据结构，定义了对话流转过程中
所有需要维护的状态字段，共 **12 个字段**，分为 6 个语义层：

```python
class ConversationState(TypedDict):
    """对话状态"""

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

**设计要点**：每个节点函数只读取需要的字段、返回需要更新的字段，
LangGraph 会自动将返回值合并到全局状态中。

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

    # 入口
    graph.set_entry_point("emotion_perception")

    # 固定边：情绪感知 → 危机检查
    graph.add_edge("emotion_perception", "crisis_check")

    # 条件边：危机检查 → 路由决策
    graph.add_conditional_edges(
        "crisis_check",
        crisis_router,
        {
            "crisis_intervention": "crisis_intervention",
            "knowledge_retrieval": "knowledge_retrieval",
        },
    )

    # 正常对话路径
    graph.add_edge("knowledge_retrieval", "response_generation")
    graph.add_edge("response_generation", "exercise_suggestion")
    graph.add_edge("exercise_suggestion", END)

    # 危机干预路径 → 直接结束
    graph.add_edge("crisis_intervention", END)

    return graph
```

#### MemorySaver 检查点机制

LangGraph 的 `MemorySaver` 提供了**跨轮对话的状态恢复**能力。
每个会话通过 `thread_id`（即 `session_id`）关联一个独立的检查点：

```python
class ConversationManager:
    def __init__(self):
        self.checkpointer = MemorySaver()
        self.graph = build_conversation_graph()
        self.compiled_graph = self.graph.compile(checkpointer=self.checkpointer)
```

当用户发送新消息时，`ConversationManager` 会先尝试从检查点恢复历史状态：

```python
config = {"configurable": {"thread_id": session_id}}

# 尝试从检查点恢复历史状态
existing_state = await self.compiled_graph.aget_state(config)
if existing_state and existing_state.values:
    prev = existing_state.values
    input_state["messages"] = prev.get("messages", [])
    input_state["emotion_history"] = prev.get("emotion_history", [])
    input_state["turn_count"] = prev.get("turn_count", 0)
```

这样，即使用户的消息是独立请求，系统也能"记住"之前的对话内容和情绪变化趋势。

---

### 2.2 节点函数实现（src/agent/nodes.py）

#### 节点 1：emotion_perception_node（情绪感知）

**职责**：分析用户消息中的情绪信号，融合外部多模态数据，维护情绪历史。

```python
async def emotion_perception_node(state: dict) -> dict:
    user_message = state.get("user_message", "")

    # 1. 文本情绪分析（基于关键词字典）
    text_result = _analyze_text_emotion(user_message)

    # 2. 合并外部情绪数据（如来自视频/音频分析）
    external_emotion = state.get("emotion_result")
    if external_emotion and isinstance(external_emotion, dict):
        merged = {**text_result, **{
            k: v for k, v in external_emotion.items() if v is not None
        }}
    else:
        merged = text_result

    # 3. 更新情绪历史（保留最近 10 条）
    history = list(state.get("emotion_history") or [])
    history.append({
        "turn": state.get("turn_count", 0),
        "emotion": merged["dominant_emotion"],
        "score": merged["score"],
    })
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

```python
def _analyze_text_emotion(text: str) -> dict:
    scores = {emotion: 0.0 for emotion in _EMOTION_KEYWORDS}

    for emotion, keywords in _EMOTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                scores[emotion] += 1.0

    total = sum(scores.values())
    if total == 0:
        return {"dominant_emotion": "neutral", "score": 0.5, "emotions": {"neutral": 1.0}}

    normalized = {k: v / total for k, v in scores.items()}
    dominant = max(normalized, key=normalized.get)

    return {"dominant_emotion": dominant, "score": normalized[dominant], "emotions": normalized}
```

#### 节点 2：crisis_check_node（危机检查）

**职责**：检测危机关键词，结合情绪强度进行 3 层风险评分。

```python
# 危机关键词列表（32个，涵盖自杀、自残、轻生等表述）
CRISIS_KEYWORDS: list[str] = [
    "自杀", "自残", "不想活", "跳楼", "割腕", "结束生命", "去死", "死了算了",
    "活着没意思", "不想活了", "轻生", "寻死", "了结", "吞药", "上吊", "烧炭",
    "自我伤害", "伤害自己", "不想醒来", "消失", "世界没有我会更好",
    "活不下去", "没有意义", "累了不想活", "解脱", "最后", "遗书", "遗言",
    "告别", "再见了", "对不起大家", "是我的错我不该活着",
]
```

**3 层风险评分逻辑**：

```
┌─────────────────────────────────────────────────────────────┐
│                    危机风险评估决策树                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  有危机关键词?                                               │
│    ├─ 是 → 按命中数量分级:                                   │
│    │     ├─ ≥3 个关键词 → risk_level = "crisis"             │
│    │     ├─ 2 个关键词   → risk_level = "high"              │
│    │     └─ 1 个关键词   → risk_level = "medium"            │
│    │                                                        │
│    └─ 否 → 检查情绪强度:                                     │
│          ├─ sadness 且 score > 0.7 → "medium"              │
│          ├─ anxiety/anger 且 score > 0.8 → "medium"       │
│          └─ 其他 → "low"                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

```python
async def crisis_check_node(state: dict) -> dict:
    user_message = state.get("user_message", "")
    emotion_result = state.get("emotion_result") or {}

    # 检测危机关键词
    found_signals = [kw for kw in CRISIS_KEYWORDS if kw in user_message]

    dominant_emotion = emotion_result.get("dominant_emotion", "neutral")
    emotion_score = emotion_result.get("score", 0)

    if found_signals:
        if len(found_signals) >= 3:
            risk_level = "crisis"
        elif len(found_signals) >= 2:
            risk_level = "high"
        else:
            risk_level = "medium"
    elif dominant_emotion == "sadness" and emotion_score > 0.7:
        risk_level = "medium"
    elif dominant_emotion in ("anxiety", "anger") and emotion_score > 0.8:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {"risk_level": risk_level, "crisis_signals": found_signals}
```

#### 节点 3：crisis_router（条件路由）

**职责**：根据 `risk_level` 决定下一个节点。

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

**职责**：构建检索 query，调用 `KnowledgeManager.query()` 获取 top-3 知识片段。

```python
async def knowledge_retrieval_node(state: dict) -> dict:
    user_message = state.get("user_message", "")
    emotion_result = state.get("emotion_result") or {}
    dominant = emotion_result.get("dominant_emotion", "neutral")

    # 构建检索 query — 结合用户消息和情绪
    query_parts = [user_message]
    if dominant != "neutral":
        query_parts.append(f"{dominant}情绪 心理疏导")
    query = " ".join(query_parts)

    # 从知识库检索（失败时降级为空列表）
    try:
        from src.knowledge.manager import KnowledgeManager
        km = KnowledgeManager()
        await km.initialize()
        documents = await km.query(question=query, top_k=3)
        snippets = [doc.page_content for doc in documents if doc.page_content]
    except Exception as e:
        logger.warning("知识检索失败（降级处理）: %s", e)
        snippets = []

    return {"retrieved_knowledge": snippets}
```

**设计要点**：知识检索被包裹在 try/except 中，失败时降级为空列表，
不会阻断对话流程。这是项目"多层级容错"策略的体现。

#### 节点 5：response_generation_node（回复生成）

**职责**：组装 System Prompt + 上下文，调用 LLM 生成回复。

```python
async def response_generation_node(state: dict) -> dict:
    user_message = state.get("user_message", "")
    emotion_result = state.get("emotion_result")
    knowledge = state.get("retrieved_knowledge") or []
    history = state.get("messages") or []

    # 1. 加载 System Prompt（从 therapist.md 文件，延迟加载+缓存）
    system_prompt = _get_system_prompt()

    # 2. 构建情绪上下文（含情绪历史趋势摘要）
    emotion_context = None
    if emotion_result:
        emotion_context = {
            "dominant_emotion": emotion_result.get("dominant_emotion", "neutral"),
            "score": emotion_result.get("score", 0),
        }
        emotion_history = state.get("emotion_history") or []
        if len(emotion_history) >= 3:
            recent = emotion_history[-3:]
            trend = " → ".join(e.get("emotion", "?") for e in recent)
            emotion_context["history_summary"] = f"近期情绪变化: {trend}"

    # 3. 调用 LLM 生成回复
    llm = _get_llm()
    response = await llm.chat_with_context(
        user_message=user_message,
        emotion_context=emotion_context,
        knowledge_context=knowledge,
        history=history,
        system_prompt=system_prompt,
    )

    # 4. 更新对话历史（保留最近 20 条）
    messages = list(history)
    messages.append({"role": "user", "content": user_message})
    messages.append({"role": "assistant", "content": response})
    if len(messages) > 20:
        messages = messages[-20:]

    return {"response": response, "messages": messages, "turn_count": state.get("turn_count", 0) + 1}
```

#### 节点 6：crisis_intervention_node（危机干预）

**职责**：三层应对策略，确保用户安全。

```
┌──────────────────────────────────────────────────────────────┐
│                    危机干预三层策略                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  risk_level = "crisis"                                       │
│    → 直接使用 CRISIS_RESPONSE_TEMPLATE 模板回复               │
│    → 包含 4 条心理援助热线                                    │
│    → 设置 needs_human_intervention = True                    │
│                                                              │
│  risk_level = "high"                                         │
│    → LLM 生成个性化关怀回复（附加危机提示到 System Prompt）   │
│    → 确保回复包含热线信息 400-161-9995                       │
│    → 设置 needs_human_intervention = True                    │
│                                                              │
│  （medium/low 不会进入此节点，由 crisis_router 路由）          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

危机干预模板包含 4 条热线：

```python
CRISIS_RESPONSE_TEMPLATE = """我能感受到你现在正经历着非常艰难的时刻……

**请记住，你不是一个人在面对这些。**

🔴 **全国心理援助热线**：400-161-9995（24小时）
🔴 **北京心理危机研究与干预中心**：010-82951332
🔴 **生命热线**：400-821-1215
🔴 **紧急求助**：120 或 110

**你的生命是珍贵的，这些痛苦的感受是可以被帮助和改善的。**
我会一直在这里陪着你。💙"""
```

#### 节点 7：exercise_suggestion_node（练习建议）

**职责**：基于情绪类型映射 CBT 练习。

```python
exercise_map: dict[str, list[str]] = {
    "sadness": [
        "行为激活：列出3件能让你感到一点点开心的小事",
        "感恩日记：写下今天值得感恩的3件事",
        "正念呼吸：进行5分钟的专注呼吸练习",
    ],
    "anxiety": [
        "腹式呼吸：4-7-8 呼吸法（吸气4秒、屏息7秒、呼气8秒）",
        "渐进式肌肉放松：从脚趾到头顶逐步紧张-放松每组肌肉",
        "担忧时间：设定每天15分钟的专属担忧时间",
    ],
    "anger": [
        "情绪记录：写下触发愤怒的事件、想法和感受",
        "认知重评：尝试从对方的角度思考这件事",
        "冷却技巧：深呼吸并倒数从10到1",
    ],
    "joy": [
        "积极体验强化：细细品味此刻的好感觉，记录在日记中",
        "善意行动：为他人做一件小小的善事",
    ],
    "neutral": [
        "情绪觉察：花几分钟感受当下的身体和情绪状态",
        "价值探索：思考对你来说最重要的是什么",
    ],
}
```

---

### 2.3 LLM 封装（src/agent/llm.py）

#### MindMirrorLLM 类设计

`MindMirrorLLM` 提供了多模型统一接口，通过环境变量 `LLM_PROVIDER` 切换 DeepSeek 和 GLM-4：

```python
class MindMirrorLLM:
    """统一 LLM 接口 — 支持 DeepSeek 和 GLM-4 切换"""

    def __init__(self, provider: str = None):
        self.provider = provider or LLM_PROVIDER  # 从环境变量读取
        self._setup_client()

    def _setup_client(self):
        if self.provider == "deepseek":
            self.api_key = DEEPSEEK_API_KEY
            self.base_url = DEEPSEEK_BASE_URL
            self.model = DEEPSEEK_MODEL
        elif self.provider == "zhipu":
            self.api_key = ZHIPU_API_KEY
            self.base_url = ZHIPU_BASE_URL
            self.model = ZHIPU_MODEL

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
```

> **关键设计**：DeepSeek 和 GLM-4 都兼容 OpenAI API 格式，
> 因此使用 `openai` SDK 统一调用，只需切换 `api_key`、`base_url` 和 `model`。

#### 两个核心方法

**chat()** — 基础对话方法：

```python
async def chat(self, messages, temperature=0.7, max_tokens=2000, system_prompt=None) -> str:
    if not self.client:
        return self._fallback_response()

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
```

**chat_with_context()** — 上下文对话方法（被回复生成节点调用）：

```python
async def chat_with_context(self, user_message, emotion_context=None,
                             knowledge_context=None, history=None,
                             system_prompt="") -> str:
    # 构建上下文注入
    context_parts = []
    if emotion_context:
        emotion_str = f"当前用户情绪: {emotion_context.get('dominant_emotion', '未知')}"
        context_parts.append(emotion_str)

    if knowledge_context:
        knowledge_str = "相关专业知识:\n" + "\n".join([f"- {k}" for k in knowledge_context[:3]])
        context_parts.append(knowledge_str)

    # 组装完整系统提示
    full_system = system_prompt
    if context_parts:
        full_system += "\n\n[当前上下文]\n" + "\n".join(context_parts)

    # 构建消息列表（限制历史长度20条）
    messages = []
    if history:
        messages.extend(history[-20:])
    messages.append({"role": "user", "content": user_message})

    return await self.chat(messages, system_prompt=full_system)
```

#### 降级方案

当 LLM API 不可用时（如 API Key 未配置或网络故障），返回带有热线信息的降级回复：

```python
def _fallback_response(self) -> str:
    return (
        "我现在暂时无法为你提供完整的回复，但我想让你知道，你的感受是重要的。"
        "\n\n如果你正在经历困难，请拨打以下热线寻求帮助："
        "\n- 全国心理援助热线：400-161-9995"
        "\n- 北京心理危机研究与干预中心：010-82951332"
        f"\n\n[系统提示：LLM 服务未配置或不可用 (provider={self.provider})]"
    )
```

#### 单例模式

```python
_llm_instance: Optional[MindMirrorLLM] = None

def get_llm(provider: str = None) -> MindMirrorLLM:
    global _llm_instance
    if _llm_instance is None or (provider and provider != _llm_instance.provider):
        _llm_instance = MindMirrorLLM(provider=provider)
    return _llm_instance
```

---

## 三、CrewAI 多智能体协作

CrewAI 提供了**多智能体协作**能力，作为 LangGraph 对话流程的可选增强层，
进行更深度的心理分析。

### 3.1 五个专业化 Agent（src/crew/agents.py）

每个 Agent 都有明确的**角色（role）**、**目标（goal）**和**背景故事（backstory）**：

| Agent | 角色 | 核心目标 | 背景故事关键词 |
|-------|------|---------|--------------|
| assessment_agent | 心理评估专家 | 综合评估用户心理健康状态 | 临床心理评估、严谨客观 |
| emotion_agent | 情绪分析专家 | 识别情绪模式和变化趋势 | 情绪心理学、多维度解读 |
| knowledge_agent | 心理学知识顾问 | 检索专业心理学知识 | CBT、社会心理学、行为心理学 |
| crisis_agent | 危机干预专家 | 实时监控危机信号 | **宁误报毋漏报** |
| intervention_agent | CBT干预顾问 | 推荐CBT练习和干预策略 | 认知行为疗法实践专家 |

```python
# 示例：危机干预专家 Agent 的定义
crisis_agent = Agent(
    role="危机干预专家",
    goal="实时监控危机信号，确保用户安全，必要时触发紧急干预",
    backstory=(
        "你是一位训练有素的危机干预专家，擅长识别自杀/自伤风险信号。"
        "你的首要任务是确保用户安全，宁可误报也不能漏报。"
    ),
    verbose=True,
    **agent_kwargs,
)
```

> **设计要点**：`agent_kwargs` 在 LLM 不可用时为空字典，
> Agent 仍然创建但不绑定 `llm`，实现优雅降级。

### 3.2 五个核心 Task（src/crew/tasks.py）

每个 Task 都定义了详细的 `description`（含输入数据和输出要求）和 `expected_output`（JSON 格式说明）。

#### Task 1：心理评估任务

**输出 JSON 格式**：
```json
{
    "overall_score": 7,              // 整体心理健康评分 (1-10)
    "dominant_emotion": "anxiety",   // 主要情绪
    "emotion_intensity": 0.8,        // 情绪强度 (0-1)
    "potential_issues": ["焦虑倾向"], // 可能的心理问题
    "risk_factors": ["学业压力"],     // 风险因素
    "protective_factors": ["社交支持"], // 保护因素
    "recommendation": "建议进行放松训练" // 简要建议
}
```

#### Task 2：情绪分析任务

**输出 JSON 格式**：
```json
{
    "primary_emotion": "sadness",       // 主要情绪
    "secondary_emotions": ["anxiety"],  // 次要情绪
    "hidden_emotions": ["孤独感"],      // 隐藏情绪
    "emotional_triggers": ["考试失败"], // 情绪触发因素
    "emotion_trend": "从焦虑转向无助",   // 情绪变化趋势
    "empathy_suggestion": "先倾听再引导", // 回应建议
    "intensity_score": 0.75             // 情绪强度
}
```

#### Task 3：知识检索任务

**输出 JSON 格式**：
```json
{
    "relevant_theories": [
        {"name": "认知行为模型", "description": "...", "relevance": "..."}
    ],
    "cbt_techniques": [
        {"name": "认知重构", "steps": ["..."], "difficulty": "medium"}
    ],
    "psychoeducation": "心理教育内容...",
    "coping_strategies": ["策略1", "策略2", "策略3"]
}
```

#### Task 4：危机检测任务

**输出 JSON 格式**：
```json
{
    "risk_level": "high",           // 风险等级
    "crisis_signals": ["不想活"],    // 危机信号
    "self_harm_risk": true,         // 自伤风险
    "suicide_risk": true,           // 自杀风险
    "urgency": "immediate",         // 紧急程度
    "recommended_actions": ["推送热线"],
    "hotline_needed": true,         // 是否需要热线
    "assessment_note": "检测到自杀意念"
}
```

> Task 描述中特别强调：**"如果出现任何自杀/自伤相关表述，risk_level 必须设为 high 或 crisis"**

#### Task 5：干预建议任务

**输出 JSON 格式**：
```json
{
    "primary_intervention": {
        "type": "behavioral_activation",
        "name": "行为激活",
        "description": "...",
        "estimated_duration": "10分钟"
    },
    "exercises": [
        {"name": "腹式呼吸", "category": "breathing", "instructions": [...], "difficulty": "easy"}
    ],
    "follow_up_questions": ["你愿意聊聊最近的事吗？"],
    "safety_plan": {"hotlines": [...], "trusted_contacts": [...], "coping_cards": [...]}
}
```

### 3.3 Crew 编排逻辑（src/crew/crew.py）

#### MindMirrorCrew 类

`MindMirrorCrew` 编排 5 个 Agent 的协作流程，提供两种运行模式：

#### 完整分析模式：run_full_analysis（4 阶段）

```
┌─────────────────────────────────────────────────────────────────────┐
│                    run_full_analysis 执行流程                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  阶段1: 危机检测（独立执行，优先级最高）                              │
│    └─ crisis_agent 执行危机检测任务                                   │
│    └─ 如果 risk_level ∈ {high, crisis} → 立即返回，跳过后续阶段      │
│                                                                     │
│  阶段2: 情绪分析 + 心理评估（并行执行 asyncio.gather）                │
│    ├─ emotion_agent 执行情绪分析任务    ─┐                           │
│    └─ assessment_agent 执行心理评估任务  ─┘ 并行                      │
│                                                                     │
│  阶段3: 知识检索（基于评估结果构建查询）                              │
│    └─ knowledge_agent 执行知识检索任务                                │
│                                                                     │
│  阶段4: 干预建议（基于所有分析结果）                                  │
│    └─ intervention_agent 执行干预建议任务                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

```python
async def run_full_analysis(self, user_message, emotion_data=None, history=None):
    # 阶段1：危机检测（独立）
    crisis_result = await self._run_crisis_detection(user_message, emotion_data)

    # 高风险时立即返回
    if crisis_result.get("risk_level") in ("high", "crisis"):
        return {"crisis_result": crisis_result, "summary": "危机警报"}

    # 阶段2：情绪分析 + 心理评估（并行）
    emotion_analysis, assessment = await asyncio.gather(
        self._run_emotion_analysis(user_message, emotion_data),
        self._run_assessment(user_message, emotion_data, history),
    )

    # 阶段3：知识检索
    query = f"{user_message} {emotion_analysis.get('primary_emotion', '')}"
    knowledge = await self._run_knowledge_retrieval(query, emotion_context)

    # 阶段4：干预建议
    intervention = await self._run_intervention(
        json.dumps(assessment), json.dumps(emotion_analysis)
    )

    return {"crisis_result": crisis_result, "emotion_analysis": emotion_analysis,
            "assessment": assessment, "knowledge": knowledge,
            "intervention": intervention, "summary": summary}
```

#### 快速检查模式：run_quick_check（2 阶段）

```python
async def run_quick_check(self, user_message, emotion_data=None):
    # 并行执行危机检测和情绪分析
    crisis_result, emotion_analysis = await asyncio.gather(
        self._run_crisis_detection(user_message, emotion_data),
        self._run_emotion_analysis(user_message, emotion_data),
    )
    return {"crisis_result": crisis_result, "emotion_analysis": emotion_analysis}
```

#### JSON 多层级解析策略（5 层容错）

CrewAI 的 Task 输出是字符串，可能包含 JSON 块、Markdown 格式等。
`_parse_json_output` 函数实现了 5 层解析容错：

```python
def _parse_json_output(raw_output: str) -> dict:
    text = raw_output.strip()

    # 策略1：直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 策略2：提取 ```json ... ``` 代码块
    if "```json" in text:
        start = text.index("```json") + 7
        end = text.index("```", start)
        try:
            return json.loads(text[start:end].strip())
        except (json.JSONDecodeError, ValueError):
            pass

    # 策略3：提取 ``` ... ``` 代码块
    if "```" in text:
        start = text.index("```") + 3
        end = text.index("```", start)
        try:
            return json.loads(text[start:end].strip())
        except (json.JSONDecodeError, ValueError):
            pass

    # 策略4：查找第一个 { 到最后一个 }
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1:
        try:
            return json.loads(text[first_brace : last_brace + 1])
        except json.JSONDecodeError:
            pass

    # 策略5：全部失败，返回原始文本
    return {"raw": raw_output}
```

#### asyncio.to_thread 异步化

CrewAI 内部是同步执行的，通过 `asyncio.to_thread` 包装为异步调用：

```python
async def _run_crisis_detection(self, user_message, emotion_data):
    agent = self.agents["crisis"]
    task = create_crisis_detection_task(agent, user_message, emotion_data)
    crew = self._create_crew([agent], [task])
    # 同步的 crew.kickoff() 包装为异步
    result = await asyncio.to_thread(crew.kickoff)
    return _parse_json_output(str(result))
```

### 3.4 与 LangGraph 集成（src/crew/integration.py）

#### CrewIntegration 类

`CrewIntegration` 作为 LangGraph 的**可选增强节点**，根据对话上下文智能决定
是否启动多智能体分析。

#### 智能触发策略

```
┌──────────────────────────────────────────────────────────────────┐
│                    分析模式决策逻辑                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  risk_level ∈ {high, crisis}?                                    │
│    └─ 是 → "quick"（快速检查）                                   │
│                                                                  │
│  turn_count ≥ 3?                                                 │
│    └─ 是 → "full"（完整分析）                                    │
│                                                                  │
│  情绪波动 > 0.3?（最近3轮情绪分数最大差值）                       │
│    └─ 是 → "full"（完整分析）                                    │
│                                                                  │
│  turn_count ≥ 1?                                                 │
│    └─ 是 → "quick"（快速检查）                                   │
│                                                                  │
│  其他 → "skip"（跳过，不执行 CrewAI 分析）                        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

```python
# 触发阈值
_FULL_ANALYSIS_TURN_THRESHOLD = 3        # 对话轮次阈值
_EMOTION_VOLATILITY_THRESHOLD = 0.3      # 情绪波动阈值

def _determine_analysis_mode(self, turn_count, risk_level, emotion_history) -> str:
    if risk_level in ("high", "crisis"):
        return "quick"
    if turn_count >= _FULL_ANALYSIS_TURN_THRESHOLD:
        return "full"
    if self._detect_emotion_volatility(emotion_history):
        return "full"
    if turn_count >= 1:
        return "quick"
    return "skip"
```

#### 情绪波动检测

```python
@staticmethod
def _detect_emotion_volatility(emotion_history: list) -> bool:
    if len(emotion_history) < 2:
        return False

    recent = emotion_history[-3:]  # 最近 3 条
    scores = [entry.get("score", 0.5) for entry in recent if isinstance(entry, dict)]

    if len(scores) < 2:
        return False

    # 计算相邻分数的最大差值
    max_diff = max(abs(scores[i] - scores[i - 1]) for i in range(1, len(scores)))
    return max_diff > _EMOTION_VOLATILITY_THRESHOLD
```

#### enhance_response 作为可选 LangGraph 节点

```python
async def enhance_response(self, state: dict) -> dict:
    if not self.available or self.crew is None:
        return {"crew_analysis": None}   # 降级：返回 None

    analysis_mode = self._determine_analysis_mode(
        turn_count, risk_level, state.get("emotion_history") or []
    )

    if analysis_mode == "full":
        result = await self.crew.run_full_analysis(...)
    elif analysis_mode == "quick":
        result = await self.crew.run_quick_check(...)
    else:
        return {"crew_analysis": None}   # skip 模式

    return {"crew_analysis": result}
```

---

## 四、知识库系统（RAG）

知识库系统为对话提供**专业心理学知识支撑**（RAG），包含文档加载、向量嵌入、
检索和统一管理四个模块。

### 4.1 文档加载与切分（src/knowledge/loader.py）

#### KnowledgeLoader 类

**职责**：递归扫描 `knowledge_base/` 下的 `*.md` 文件，按标题层级拆分并切分为
适合 Embedding 的文档片段。

```python
class KnowledgeLoader:
    def __init__(self, knowledge_base_dir: Path):
        self.knowledge_base_dir = knowledge_base_dir
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", "。", "；"],
        )
```

**切分参数**：
- `chunk_size=500`：每个文档片段约 500 字符
- `chunk_overlap=100`：相邻片段重叠 100 字符，保证语义连续性

**分隔符优先级**（从高到低）：
```

##  >  
###  >  
####  >  

  >  
  >  。  >  ；
 二级标题   三级标题   四级标题    段落    换行   句号  分号
```

这意味着切分器会**优先在标题边界切分**，保持每个片段的语义完整性。

#### 元数据结构

每个切分后的 Document 携带 5 个元数据字段：

```python
doc = Document(
    page_content=chunk,
    metadata={
        "source": str(file_path.relative_to(self.knowledge_base_dir)),  # 相对路径
        "category": category,         # 分类（目录名，如 cbt, crisis）
        "title": title,               # 文件标题（一级标题）
        "section_title": section["heading"],  # 段落标题
        "chunk_index": i,             # 片段序号
    },
)
```

#### 按标题层级预拆分

在 RecursiveCharacterTextSplitter 之前，先用正则按 `##` / `###` 标题预拆分，
确保每个片段保留标题上下文：

```python
def _split_by_headings(self, content: str) -> List[dict]:
    pattern = r"(?=^#{2,3}\s)"
    sections = re.split(pattern, content, flags=re.MULTILINE)

    result = []
    for section in sections:
        heading = ""
        for line in section.split("\n"):
            if line.strip().startswith("##"):
                heading = line.strip().lstrip("#").strip()
                break
        result.append({"heading": heading, "text": section})

    return result if result else [{"heading": "", "text": content}]
```

### 4.2 向量嵌入（src/knowledge/embeddings.py）

支持两种 Embedding 后端，均兼容 LangChain `Embeddings` 接口：

| 后端 | 类名 | 模型 | 维度 | 特点 |
|------|------|------|------|------|
| 在线 API | `ZhipuEmbeddings` | embedding-3 | 2048 | 需 API Key，效果好 |
| 本地离线 | `LocalEmbeddings` | bge-large-zh-v1.5 | 1024 | 无需 API，离线可用 |

```python
class ZhipuEmbeddings(Embeddings):
    MODEL_NAME = "embedding-3"
    EMBEDDING_DIM = 2048

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # 分批处理（每批 20 个）
        batch_size = 20
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = self.client.embeddings.create(model=self.MODEL_NAME, input=batch)
            embeddings.extend([item.embedding for item in response.data])
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        response = self.client.embeddings.create(model=self.MODEL_NAME, input=[text])
        return response.data[0].embedding
```

#### 工厂函数

```python
def get_embeddings(backend: str = "zhipu", **kwargs) -> Embeddings:
    if backend == "zhipu":
        return ZhipuEmbeddings(**kwargs)
    elif backend == "local":
        return LocalEmbeddings(**kwargs)
    else:
        raise ValueError(f"不支持的 Embedding 后端: {backend}")
```

### 4.3 知识检索（src/knowledge/retriever.py）

#### Qdrant 向量数据库

使用 Qdrant 作为向量数据库，距离度量为 **COSINE（余弦相似度）**：

```python
self.client.create_collection(
    collection_name=self.collection_name,
    vectors_config=qdrant_models.VectorParams(
        size=self.vector_dim,                          # 2048 或 1024
        distance=qdrant_models.Distance.COSINE,        # 余弦距离
    ),
)
```

#### 三种检索方式

**1. 语义检索 search()**

```python
async def search(self, query: str, top_k: int = 5, category: Optional[str] = None):
    # 生成查询向量
    query_embedding = self.embeddings.embed_query(query)

    # 构建分类过滤条件
    query_filter = None
    if category:
        query_filter = qdrant_models.Filter(
            must=[qdrant_models.FieldCondition(
                key="category",
                match=qdrant_models.MatchValue(value=category),
            )]
        )

    # 执行向量搜索
    results = self.client.search(
        collection_name=self.collection_name,
        query_vector=query_embedding,
        limit=top_k,
        query_filter=query_filter,
    )
    return [Document(page_content=r.payload.get("text", ""), metadata={...}) for r in results]
```

**2. 混合检索 hybrid_search()（语义 0.7 + BM25 0.3）**

```python
async def hybrid_search(self, query: str, top_k: int = 5,
                         semantic_weight: float = 0.7,
                         keyword_weight: float = 0.3):
    # 分别执行语义检索和 BM25 检索（各取 top_k*2）
    semantic_results = await self.search(query, top_k=top_k * 2)
    keyword_results = self._bm25_search(query, top_k=top_k * 2)

    # 加权融合排序（排名分数 = weight × 1/(rank+1)）
    scored_docs = {}
    for i, doc in enumerate(semantic_results):
        key = doc.page_content[:100]
        semantic_score = semantic_weight * (1.0 / (i + 1))
        scored_docs[key] = (doc, scored_docs.get(key, (doc, 0))[1] + semantic_score)

    for i, doc in enumerate(keyword_results):
        key = doc.page_content[:100]
        keyword_score = keyword_weight * (1.0 / (i + 1))
        if key in scored_docs:
            scored_docs[key] = (doc, scored_docs[key][1] + keyword_score)
        else:
            scored_docs[key] = (doc, keyword_score)

    # 按融合分数排序，取 top_k
    sorted_docs = sorted(scored_docs.values(), key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in sorted_docs[:top_k]]
```

**3. BM25 关键词检索**

BM25（Best Matching 25）是一种基于词频和逆文档频率的经典关键词检索算法。

```python
def _bm25_search(self, query: str, top_k: int = 10) -> List[Document]:
    query_tokens = self._tokenize(query)
    k1 = 1.5   # 词频饱和参数
    b = 0.75   # 文档长度归一化参数

    for doc_info in self._bm25_docs:
        score = 0.0
        dl = doc_info["length"]
        tf_map = doc_info["tf"]

        for token in query_tokens:
            if token in tf_map and token in self._idf:
                tf = tf_map[token]
                idf = self._idf[token]
                # BM25 核心公式
                norm_tf = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / self._avg_dl))
                score += idf * norm_tf

        if score > 0:
            scored.append((score, doc_info))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [Document(page_content=d["text"], metadata={**d["metadata"], "bm25_score": s})
            for s, d in scored[:top_k]]
```

**中文分词**使用简单正则，避免引入 jieba 等重依赖：

```python
@staticmethod
def _tokenize(text: str) -> List[str]:
    # 按非中文/非英文字符分割，保留中文连续片段和英文单词
    tokens = re.findall(r"[\u4e00-\u9fa5]+|[a-zA-Z]+", text.lower())
    # 过滤掉太短的 token（单字中文信息量低）
    return [t for t in tokens if len(t) >= 2]
```

#### 索引流程

```python
async def index_documents(self, documents: List[Document]) -> None:
    # 1. 批量生成 Embedding
    texts = [doc.page_content for doc in documents]
    embeddings = self.embeddings.embed_documents(texts)

    # 2. 构建 Qdrant Points
    points = []
    for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
        point_id = self._generate_point_id(doc, i)  # 基于 source+chunk_index 的哈希
        payload = {"text": doc.page_content, "category": ..., "source": ..., ...}
        points.append(qdrant_models.PointStruct(id=point_id, vector=embedding, payload=payload))

    # 3. 批量上传（每批 100 个）
    batch_size = 100
    for start in range(0, len(points), batch_size):
        self.client.upsert(collection_name=self.collection_name, points=points[start:start+batch_size])

    # 4. 构建 BM25 索引
    self._build_bm25_index(documents)
```

### 4.4 统一管理器（src/knowledge/manager.py）

`KnowledgeManager` 封装了 Loader、Embeddings、Retriever，对外提供统一的异步 API：

```python
class KnowledgeManager:
    def __init__(self, knowledge_base_dir=None, embeddings_backend="zhipu",
                 qdrant_client=None, collection_name="psychology_knowledge"):
        # 延迟初始化
        self.loader = None
        self.embeddings = None
        self.retriever = None
        self._initialized = False
```

#### initialize()：懒加载 + 全量索引

```python
async def initialize(self) -> None:
    if self._initialized:
        return  # 避免重复初始化

    # 1. 初始化 Loader
    self.loader = KnowledgeLoader(self.knowledge_base_dir)

    # 2. 初始化 Embeddings
    self.embeddings = get_embeddings(self.embeddings_backend)

    # 3. 初始化 Qdrant 客户端和检索器
    if self._qdrant_client is None:
        self._qdrant_client = create_qdrant_client()
    self.retriever = KnowledgeRetriever(self._qdrant_client, self.embeddings, ...)

    # 4. 检查是否已有索引数据（避免重复索引）
    stats = await self.retriever.get_collection_stats()
    if stats.get("total_documents", 0) > 0:
        logger.info("Qdrant 中已有数据，跳过全量索引")
    else:
        # 5. 加载并索引文档
        documents = self.loader.load_all()
        await self.retriever.index_documents(documents)

    self._initialized = True
```

#### query()：统一查询接口

```python
async def query(self, question: str, category=None, top_k=5, method="hybrid"):
    self._ensure_initialized()

    if method == "hybrid":
        return await self.retriever.hybrid_search(question, top_k=top_k)
    else:
        return await self.retriever.search(question, top_k=top_k, category=category)
```

#### update()：增量更新 & rebuild()：完全重建

```python
async def update(self, category: str) -> int:
    """增量更新指定分类（重新加载该分类文档并重新索引）"""
    documents = self.loader.load_category(category)
    await self.retriever.index_documents(documents)  # upsert 覆盖同 ID 旧文档
    return len(documents)

async def rebuild(self) -> int:
    """完全重建（删除旧 collection → 重新创建 → 重新索引所有文档）"""
    self._qdrant_client.delete_collection(self.collection_name)
    self.retriever = KnowledgeRetriever(...)  # 自动创建新 collection
    documents = self.loader.load_all()
    await self.retriever.index_documents(documents)
    return len(documents)
```

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

每个 Markdown 文件按 `##` / `###` 标题预拆分，再按 500 字符切分为片段，
最终生成带有 `category`、`source`、`title`、`section_title`、`chunk_index`
元数据的 Document，索引到 Qdrant。

---

## 五、端到端数据流

### 5.1 完整对话流程

```
用户消息
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│  FastAPI POST /api/chat/message                                  │
│  └─ ChatRequest {session_id, message, emotion_data?}            │
│     └─ routes/chat.py → get_conversation_manager()              │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  ConversationManager.chat()                                      │
│  ┌─ 1. 构建初始 input_state                                      │
│  ├─ 2. 检查点恢复 (aget_state)                                   │
│  │     └─ 合并历史 messages, emotion_history, turn_count         │
│  ├─ 3. 执行状态图 (ainvoke)                                      │
│  └─ 4. 返回结果                                                   │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  LangGraph 状态图执行                                             │
│                                                                  │
│  emotion_perception → crisis_check → [crisis_router]            │
│                                            │                     │
│                              ┌─────────────┴─────────────┐       │
│                              ▼                           ▼       │
│                    crisis_intervention          knowledge_retrieval
│                    (high/crisis路径)              (low/medium路径) │
│                              │                           │       │
│                              │                           ▼       │
│                              │                  response_generation│
│                              │                           │       │
│                              │                           ▼       │
│                              │                  exercise_suggestion│
│                              │                           │       │
│                              ▼                           ▼       │
│                          ┌───────┐                   ┌───────┐   │
│                          │  END  │                   │  END  │   │
│                          └───────┘                   └───────┘   │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  检查点保存 (MemorySaver 自动保存状态)                            │
│  └─ messages, emotion_history, turn_count 等被持久化             │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  返回 ChatResponse                                               │
│  {response, emotion, risk_level, suggested_exercises,           │
│   needs_human_intervention}                                      │
└──────────────────────────────────────────────────────────────────┘
```

### 5.2 模块间调用关系

```
FastAPI (routes/chat.py)
  └─→ ConversationManager (agent/manager.py)
        ├─→ build_conversation_graph (agent/graph.py)
        │     ├─→ emotion_perception_node (agent/nodes.py)
        │     │     └─→ _analyze_text_emotion (关键词字典)
        │     ├─→ crisis_check_node (agent/nodes.py)
        │     │     └─→ CRISIS_KEYWORDS 匹配
        │     ├─→ crisis_router (agent/nodes.py)
        │     ├─→ knowledge_retrieval_node (agent/nodes.py)
        │     │     └─→ KnowledgeManager (knowledge/manager.py)
        │     │           ├─→ KnowledgeLoader (knowledge/loader.py)
        │     │           ├─→ get_embeddings (knowledge/embeddings.py)
        │     │           └─→ KnowledgeRetriever (knowledge/retriever.py)
        │     │                 └─→ QdrantClient (向量搜索 + BM25)
        │     ├─→ response_generation_node (agent/nodes.py)
        │     │     └─→ MindMirrorLLM (agent/llm.py)
        │     │           └─→ OpenAI SDK → DeepSeek/GLM-4 API
        │     ├─→ crisis_intervention_node (agent/nodes.py)
        │     │     └─→ CRISIS_RESPONSE_TEMPLATE / MindMirrorLLM
        │     └─→ exercise_suggestion_node (agent/nodes.py)
        │           └─→ exercise_map (情绪→CBT练习映射)
        │
        └─→ [可选] CrewIntegration (crew/integration.py)
              └─→ MindMirrorCrew (crew/crew.py)
                    ├─→ create_psychology_agents (crew/agents.py)
                    ├─→ create_*_task (crew/tasks.py)
                    └─→ CrewAI Crew (多智能体协作)
```

---

## 六、关键设计模式

### 6.1 异步编程策略

项目广泛使用 Python 异步编程，确保 I/O 密集型操作不阻塞：

```python
# 1. async/await — 所有节点函数和 API 路由
async def emotion_perception_node(state: dict) -> dict: ...

# 2. asyncio.gather — 并行执行独立任务（情绪分析 + 心理评估）
emotion_analysis, assessment = await asyncio.gather(
    self._run_emotion_analysis(user_message, emotion_data),
    self._run_assessment(user_message, emotion_data, history),
)

# 3. asyncio.to_thread — 将同步调用包装为异步
#    CrewAI 的 crew.kickoff() 是同步的，通过 to_thread 避免阻塞事件循环
result = await asyncio.to_thread(crew.kickoff)

#    同样用于 OpenAI SDK 的同步调用
response = await asyncio.to_thread(
    self.client.chat.completions.create, ...
)
```

### 6.2 多层级容错

```
┌──────────────────────────────────────────────────────────────┐
│                      容错层级                                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  层级1: LLM 降级                                             │
│    └─ API不可用 → _fallback_response() 返回带热线的默认回复  │
│                                                              │
│  层级2: 知识库跳过                                           │
│    └─ Qdrant/Embedding失败 → snippets=[] 继续对话            │
│                                                              │
│  层级3: JSON 解析多策略（5层容错）                           │
│    └─ 直接解析 → ```json块 → ```块 → 首尾{} → 返回原始文本   │
│                                                              │
│  层级4: CrewAI 降级                                          │
│    └─ API Key未配置 → enhance_response 返回 {crew_analysis: None} │
│                                                              │
│  层级5: 状态图执行异常                                       │
│    └─ ainvoke 失败 → 返回友好错误消息                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 6.3 单例模式

项目中多个重量级组件使用单例模式，避免重复初始化：

```python
# LLM 单例 (agent/llm.py)
_llm_instance: Optional[MindMirrorLLM] = None
def get_llm(provider: str = None) -> MindMirrorLLM:
    global _llm_instance
    if _llm_instance is None or (provider and provider != _llm_instance.provider):
        _llm_instance = MindMirrorLLM(provider=provider)
    return _llm_instance

# ConversationManager 单例 (agent/manager.py)
_manager: Optional[ConversationManager] = None
def get_conversation_manager() -> ConversationManager:
    global _manager
    if _manager is None:
        _manager = ConversationManager()
    return _manager

# 节点级单例 (agent/nodes.py)
_llm: MindMirrorLLM | None = None
_system_prompt: str | None = None
```

### 6.4 状态管理

对话状态通过两个限长列表管理，避免内存无限增长：

```python
# 对话历史 — 保留最近 20 条消息
if len(messages) > 20:
    messages = messages[-20:]

# 情绪历史 — 保留最近 10 条记录
if len(history) > 10:
    history = history[-10:]
```

### 6.5 安全性设计

```
┌──────────────────────────────────────────────────────────────┐
│                    多层安全防护                               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  第1层: 关键词检测（32个危机关键词）                          │
│    └─ crisis_check_node: 命中数量决定风险等级                 │
│                                                              │
│  第2层: 情绪强度辅助判断                                     │
│    └─ sadness > 0.7 或 anxiety/anger > 0.8 → 提升到 medium  │
│                                                              │
│  第3层: 条件路由（crisis_router）                             │
│    └─ high/crisis → 直接进入危机干预，跳过正常流程            │
│                                                              │
│  第4层: 危机干预三层策略                                      │
│    ├─ crisis → 模板回复（4条热线）                            │
│    └─ high → LLM关怀回复 + 确保包含热线信息                  │
│                                                              │
│  第5层: needs_human_intervention 标志                        │
│    └─ 前端/后台可据此触发人工介入流程                         │
│                                                              │
│  第6层: CrewAI 危机检测 Agent                                │
│    └─ 独立的多智能体危机评估（宁误报毋漏报）                  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 七、学习路径建议

### 7.1 代码阅读推荐顺序

```
第一阶段：理解对话主流程
  1. src/utils/config.py          → 了解配置和环境变量
  2. src/agent/graph.py           → 理解状态图结构和条件路由
  3. src/agent/manager.py         → 理解检查点恢复和会话管理
  4. src/agent/nodes.py           → 逐个理解6个节点函数
  5. src/api/routes/chat.py       → 理解API入口和请求/响应模型

第二阶段：理解LLM和知识库
  6. src/agent/llm.py             → 理解多模型封装和降级策略
  7. src/knowledge/loader.py      → 理解文档加载和切分
  8. src/knowledge/embeddings.py  → 理解两种Embedding后端
  9. src/knowledge/retriever.py   → 理解语义/混合/BM25检索
  10. src/knowledge/manager.py    → 理解统一管理器API

第三阶段：理解多智能体协作
  11. src/crew/agents.py          → 理解5个Agent的角色设计
  12. src/crew/tasks.py           → 理解5个Task的输入输出
  13. src/crew/crew.py            → 理解两种运行模式和编排逻辑
  14. src/crew/integration.py     → 理解智能触发策略和集成方式
```

### 7.2 核心概念优先级

| 优先级 | 概念 | 关键文件 | 学习要点 |
|-------|------|---------|---------|
| P0 | LangGraph 状态图 | graph.py, nodes.py | 条件路由、状态流转、检查点 |
| P0 | 危机检测机制 | nodes.py | 关键词匹配、3层评分、路由分叉 |
| P1 | LLM 封装 | llm.py | 多模型切换、上下文注入、降级 |
| P1 | RAG 知识检索 | retriever.py, manager.py | 混合检索、BM25、懒加载 |
| P2 | CrewAI 多智能体 | crew.py, agents.py | 并行编排、JSON解析容错 |
| P2 | 集成触发策略 | integration.py | 轮次阈值、情绪波动检测 |
| P3 | 异步编程模式 | 全项目 | gather、to_thread、async/await |
| P3 | 单例与容错 | 全项目 | 延迟初始化、多层级降级 |

### 7.3 扩展方向

1. **持久化检查点**：将 `MemorySaver` 替换为 `SqliteSaver` 或 `PostgresSaver`，
   实现跨重启的会话恢复。

2. **更多情绪类型**：扩展 `_EMOTION_KEYWORDS` 字典，增加如"羞耻"、"嫉妒"等
   细分情绪，提升情绪分析精度。

3. **流式回复**：将 `response_generation_node` 改为流式输出，
   通过 FastAPI 的 `StreamingResponse` 实现逐字返回。

4. **知识库自动更新**：添加文件监听机制，当 `knowledge_base/` 下文件变化时
   自动触发 `KnowledgeManager.update()`。

5. **多模态深度集成**：将视频情绪识别（OpenCV/MediaPipe）的结果作为
   `emotion_data` 传入 `ConversationManager.chat()`，
   在 `emotion_perception_node` 中与文本情绪融合。

6. **A/B 测试框架**：对不同的 System Prompt、CBT练习推荐策略进行 A/B 测试，
   评估用户体验和干预效果。

---

> **文档版本**：v1.0
> **对应代码版本**：MindMirror AI 当前主干
> **维护者**：MindMirror AI Team
