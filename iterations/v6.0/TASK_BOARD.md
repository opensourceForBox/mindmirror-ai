# 第 6 周任务看板 - 实时对话系统

**更新时间**: 2026-04-01  
**阶段**: 第二阶段（核心功能开发）- 第 6 周 - 实时对话系统  
**状态**: 🟡 进行中

---

## 任务概览

| 任务 | 负责人 | 模型 | 状态 | 交付物 | 截止时间 |
|------|--------|------|------|--------|---------|
| 01-对话引擎集成（LLM） | ai-engineer | qwencode/glm-5 | ⚪ 进行中 | 对话 API | 第 6 周末 |
| 02-上下文管理模块 | backend-architect | qwencode/glm-5 | ⚪ 进行中 | 会话状态管理 | 第 6 周末 |
| 03-心理话术库设计 | psychology-advisor | qwencode/qwen3.5-plus | ⚪ 进行中 | 话术模板库 | 第 6 周末 |
| 04-对话 UI 实现 | frontend-developer | qwencode/kimi-k2.5 | ⚪ 进行中 | 聊天界面 v1 | 第 6 周末 |

---

## 任务详情

### 任务 01: 对话引擎集成（LLM）
**负责人**: ai-engineer  
**模型**: `qwencode/glm-5` (复杂 AI 任务)  
**输入**: API_SPEC.md, ARCHITECTURE.md  
**输出**: `/root/.openclaw/workspace/code/mindmirror/backend/src/modules/chat/`  
**验收标准**: 
- [ ] 集成 LLM（GLM-4 / GPT-4o / 智谱）
- [ ] 实现 POST /chat/message 接口
- [ ] 实现 WS /chat/stream 流式对话
- [ ] 响应延迟 <500ms
- [ ] 支持上下文记忆（多轮对话）
- [ ] 情绪感知回复（基于情绪状态调整话术）
- [ ] 完整的错误处理和日志

---

### 任务 02: 上下文管理模块
**负责人**: backend-architect  
**模型**: `qwencode/glm-5` (复杂后端)  
**输入**: DATABASE_DESIGN.md, API_SPEC.md  
**输出**: `/root/.openclaw/workspace/code/mindmirror/backend/src/modules/chat/context/`  
**验收标准**: 
- [ ] 会话状态管理（ConversationManager）
- [ ] 上下文窗口（最近 N 轮对话）
- [ ] 长期记忆（用户偏好、历史摘要）
- [ ] 上下文压缩（摘要生成）
- [ ] Redis 缓存会话状态
- [ ] 并发会话支持（多用户）

---

### 任务 03: 心理话术库设计
**负责人**: psychology-advisor  
**模型**: `qwencode/qwen3.5-plus` (日常任务)  
**输入**: CBT_FRAMEWORK.md, PRD_v1.0.md  
**输出**: `/root/.openclaw/workspace/prd/mindmirror/THERAPY_TECHNIQUES.md`  
**验收标准**: 
- [ ] 积极倾听话术（反映、澄清、总结）
- [ ] 共情回应模板（认可、理解、支持）
- [ ] 认知重构话术（挑战负性思维）
- [ ] 危机干预话术（安抚、资源引导）
- [ ] CBT 练习引导话术
- [ ] 话术与情绪映射关系
- [ ] 禁忌用语清单

---

### 任务 04: 对话 UI 实现
**负责人**: frontend-developer  
**模型**: `qwencode/kimi-k2.5` (UI/前端)  
**输入**: UI_PROTOTYPES/CHAT_SCREEN.md  
**输出**: `/root/.openclaw/workspace/code/mindmirror/android/app/src/main/java/com/mindmirror/android/chat/`  
**验收标准**: 
- [ ] 聊天界面（消息列表、输入框、发送按钮）
- [ ] WebSocket 实时消息接收
- [ ] 流式响应显示（打字机效果）
- [ ] 情绪状态指示器（AI 感知用户情绪）
- [ ] 消息历史记录（本地缓存）
- [ ] 输入状态指示（正在输入...）
- [ ] 错误处理和重连机制

---

## 里程碑

| 里程碑 | 计划时间 | 状态 |
|--------|----------|------|
| M3: 对话系统完成 | 第 6 周末 | 🟡 本周验收 |

---

## 依赖关系

```
任务 01 (对话 API) ← 依赖 → 任务 02 (上下文管理)
       ↓
任务 03 (话术库) → 被任务 01 依赖
       ↓
任务 04 (对话 UI) ← 依赖 → 任务 01 (API)
```

---

*创建时间：2026-04-01*
