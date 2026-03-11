# Worker 触发机制说明

## 核心原则

**所有 Worker 通过 `sessions_spawn` 主动触发，不监听文件变化！** ✅

---

## 为什么不用监听模式？

### ❌ 监听模式的问题

```
场景：复杂项目（录像诊断功能）

product-manager 完成架构设计 → 输出到 prd/video-diagnosis/
    ↓
触发监听器！
    ├─ ui-designer 被触发？❌ 但架构还没用户确认
    ├─ developer 被触发？❌ 但任务还没拆解
    └─ Manager 被触发？❌ 但 Manager 已经在流程中了

结果：流程混乱，多个 Worker 同时启动
```

### ✅ 主动触发模式

```
场景：复杂项目（录像诊断功能）

product-manager 完成架构设计
    ↓
通知 Manager（通过 sessions_send）
    ↓
Manager 汇总架构文档 → 请求用户确认
    ↓
用户"确认"
    ↓
Manager 读取架构 → 创建 Worker 任务
    ↓
Manager 决定 spawn 哪个 Worker
    ├─ 先 spawn UI Worker（无依赖）
    └─ 等待 UI 完成后再 spawn Developer Worker（有依赖）

结果：流程清晰，Manager 完全控制
```

---

## Worker 触发方式

| Worker | 触发方式 | 说明 |
|--------|---------|------|
| **product-manager** | `sessions_spawn` | Manager 主动创建 |
| **ui-designer** | `sessions_spawn` | Manager 主动创建 |
| **developer** | `sessions_spawn` | Manager 主动创建 |
| **tester** | `sessions_spawn` | Manager 主动创建 |

**没有文件监听触发！**

---

## Manager 控制流程

### 复杂项目流程

```
Manager spawn product-manager
    ↓
product-manager 完成 → sessions_send 通知 Manager
    ↓
Manager 请求用户确认【确认点 1】
    ↓
用户"确认"
    ↓
Manager 创建 TASKS/*.md
    ↓
Manager 请求用户确认【确认点 2】
    ↓
用户"确认"
    ↓
Manager spawn UI Worker
    ↓
UI Worker 完成 → sessions_send 通知 Manager
    ↓
Manager spawn Developer Worker（依赖 UI）
    ↓
Developer Worker 完成 → sessions_send 通知 Manager
    ↓
Manager spawn Tester Worker
    ↓
Tester Worker 完成 → sessions_send 通知 Manager
    ↓
Manager 请求用户确认【确认点 3】
    ↓
用户"确认" → 项目完成
```

### 简单项目流程

```
Manager 创建 TASKS/developer-task.md
    ↓
Manager 请求用户确认
    ↓
用户"确认"
    ↓
Manager spawn developer
    ↓
Developer Worker 完成 → sessions_send 通知 Manager
    ↓
Manager 请求用户确认
    ↓
用户"确认" → 项目完成
```

---

## 通知机制

### Worker 完成通知

Worker 完成后，主动通知 Manager：

```bash
sessions_send --label="manager" --message="UI Worker 完成：designs/video-diagnosis/"
```

### Manager 进度通知

Manager 通过飞书通知用户：

```
📋 架构设计完成，请确认

## PRD 摘要
- 功能：录像诊断功能
- 用户故事：3 个
- 验收标准：5 个

## 技术架构
- 后端：Flask 3.x + ffmpeg-python
- 前端：HTML/CSS/JS（响应式）

请回复"确认"开始任务拆解，或提出修改意见。
```

---

## 目录监听 vs 主动触发

| 特性 | 目录监听 | 主动触发 |
|------|---------|---------|
| **触发方式** | 文件变化自动触发 | Manager 手动 spawn |
| **流程控制** | 分散（多个监听器） | 集中（Manager 控制） |
| **依赖管理** | 困难（需要复杂的条件判断） | 简单（Manager 决定顺序） |
| **用户确认** | 难以插入确认点 | 容易（Manager 控制节奏） |
| **适用场景** | 简单、线性流程 | 复杂、多阶段流程 |

**结论**: Manager 模式使用**主动触发**，避免流程混乱 ✅

---

## 历史遗留问题

### 之前的设计（已废弃）

```yaml
# AGENTS.md 中的旧设计（已删除）
on_file_change:
  - prd/  # 监听 PRD 目录 → 触发 ui-designer
  - designs/  # 监听设计目录 → 触发 developer
  - code/  # 监听代码目录 → 触发 tester
```

**问题**:
- 无法插入用户确认环节
- 复杂项目流程混乱
- 依赖关系难以管理

### 现在的设计

```yaml
# 所有 Worker 通过 sessions_spawn 主动触发
# 不监听任何目录
```

**优点**:
- Manager 完全控制流程
- 可以轻松插入用户确认
- 依赖关系清晰

---

## 总结

**核心原则**: 所有 Worker 通过 `sessions_spawn` 主动触发，不监听文件变化！

**好处**:
- ✅ Manager 完全控制流程
- ✅ 可以轻松插入用户确认环节
- ✅ 依赖关系清晰（Manager 决定顺序）
- ✅ 避免意外触发导致的流程混乱

**实现**:
- Worker 完成后通过 `sessions_send` 通知 Manager
- Manager 根据进度和依赖关系决定下一步 spawn 哪个 Worker
- 用户在关键节点确认后再继续
