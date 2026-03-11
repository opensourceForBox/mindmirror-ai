# 任务调度机制说明

## 核心问题

**之前的问题**：
- ❌ 开发者只从 `prd/[项目]/` 读取任务
- ❌ 记忆目录 `memory/developer-[日期].md` 只是日志，无法调度

**现在的解决方案**：
- ✅ Manager 创建任务文件 `iterations/v1.0/TASKS/*.md`
- ✅ 通过 `sessions_spawn` 触发 Worker
- ✅ 通过 `sessions_send` 通知进度

---

## 调度架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      Manager（调度者）                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 创建任务文件                                             │
│     iterations/v1.0/TASKS/                                  │
│     ├── ui-task.md                                          │
│     ├── developer-task.md                                   │
│     └── tester-task.md                                      │
│                                                             │
│  2. Spawn Worker（触发机制）                                 │
│     sessions_spawn --task="读取 TASKS/xxx-task.md"          │
│                                                             │
│  3. 更新任务看板                                             │
│     TASK_BOARD.md（实时进度）                                │
│                                                             │
│  4. 接收通知（完成反馈）                                     │
│     sessions_send from Worker                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │
         │ sessions_spawn
         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Worker（执行者）                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 读取任务文件                                             │
│     read iterations/v1.0/TASKS/xxx-task.md                  │
│                                                             │
│  2. 执行任务                                                 │
│     - UI: 设计页面                                           │
│     - Dev: 调用 claude 开发                                  │
│     - Test: 编写测试用例                                     │
│                                                             │
│  3. 输出交付物                                               │
│     iterations/v1.0/DELIVERABLES/[角色]/                    │
│                                                             │
│  4. 通知 Manager                                             │
│     sessions_send --label="manager" --message="完成"        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 关键文件说明

### 1. 任务文件（调度核心）

**位置**: `iterations/v1.0/TASKS/[worker]-task.md`

**作用**: 
- 定义任务目标
- 指定输出目录
- 说明依赖关系
- 推荐模型选择

**示例** (`developer-task.md`):
```markdown
# 开发任务 - 登录 API

## 输出要求
- 目录：`iterations/v1.0/DELIVERABLES/code/`
- 文件：app.py, models.py, routes.py, requirements.txt, README.md

## 依赖
- UI 设计：`iterations/v1.0/DELIVERABLES/ui/login.html`

## 推荐模型
glm-5（复杂后端逻辑）
```

### 2. 任务看板（进度跟踪）

**位置**: `iterations/v1.0/TASK_BOARD.md`

**作用**: 实时跟踪所有 Worker 进度

**示例**:
```markdown
# 任务看板 - v1.0

| 任务 | Worker | 状态 | 交付物 | 备注 |
|------|--------|------|--------|------|
| UI 设计 | ui-designer | ✅ 完成 | DELIVERABLES/ui/ | - |
| 后端 API | developer | 🔄 进行中 | DELIVERABLES/code/ | 等待 UI |
| 测试用例 | tester | ⏳ 待开始 | DELIVERABLES/test/ | 等待代码 |
```

### 3. 交付物目录

**位置**: `iterations/v1.0/DELIVERABLES/[角色]/`

**结构**:
```
DELIVERABLES/
├── ui/          # UI Worker 交付
│   ├── login.html
│   ├── login.css
│   └── login.js
├── code/        # Developer Worker 交付
│   ├── app.py
│   ├── models.py
│   ├── routes.py
│   ├── requirements.txt
│   └── README.md
└── test/        # Tester Worker 交付
    ├── test_login.py
    └── test_report.md
```

### 4. Manager 记忆（双层记忆上层）

**位置**: `memory/manager/MEMORY.md`

**作用**: 
- 记录项目决策
- 记录问题与解决方案
- Worker 表现评估

**注意**: 这只是日志，**不用于调度**

---

## 调度流程示例

### 场景：开发用户登录系统

```
Step 1: Manager 创建迭代目录
        ↓
        mkdir -p iterations/v1.0/{TASKS,DELIVERABLES/{ui,code,test}}
        ↓
Step 2: Manager 创建任务文件
        ↓
        TASKS/ui-task.md
        TASKS/developer-task.md
        TASKS/tester-task.md
        ↓
Step 3: Manager 初始化任务看板
        ↓
        TASK_BOARD.md（全部标记为⏳待开始）
        ↓
Step 4: Manager spawn UI Worker
        ↓
        sessions_spawn --label="ui-login" \
          --task="读取 TASKS/ui-task.md 并执行"
        ↓
Step 5: UI Worker 执行
        ├─ 读取 TASKS/ui-task.md
        ├─ 设计登录页面
        └─ 输出到 DELIVERABLES/ui/
        ↓
Step 6: UI Worker 通知 Manager
        ↓
        sessions_send --label="manager" --message="UI 完成"
        ↓
Step 7: Manager 更新看板
        ↓
        UI 设计：✅ 完成
        后端 API：🔄 进行中
        ↓
Step 8: Manager spawn Developer Worker
        ↓
        sessions_spawn --label="dev-login" \
          --task="读取 TASKS/developer-task.md，参考 UI 设计"
        ↓
Step 9: Developer Worker 执行
        ├─ 读取 TASKS/developer-task.md
        ├─ 读取 DELIVERABLES/ui/login.html（依赖）
        ├─ 调用 claude --model glm-5 开发
        └─ 输出到 DELIVERABLES/code/
        ↓
... 重复直到所有任务完成
```

---

## 两种模式对比

| 特性 | Manager 协调模式 | 直接派发模式 |
|------|-----------------|-------------|
| **适用场景** | 复杂项目、多模块、多迭代 | 简单项目、单功能 |
| **目录结构** | `iterations/v1.0/` | `prd/[项目]/` |
| **任务传递** | `TASKS/*.md` 文件 | `task-dev.md` 文件 |
| **交付物** | `DELIVERABLES/[角色]/` | `code/` `designs/` |
| **进度跟踪** | `TASK_BOARD.md` | 无 |
| **记忆** | `memory/manager/MEMORY.md` | `memory/[角色]-[日期].md` |
| **调度复杂度** | 高（适合多 Worker 协作） | 低（线性流程） |

---

## 常见问题

### Q1: memory/ 目录的作用是什么？
**A**: 只是日志记录，**不用于调度**。调度核心是 `TASKS/*.md` 文件。

### Q2: Manager 如何知道 Worker 完成了？
**A**: Worker 通过 `sessions_send` 主动通知 Manager。

### Q3: 如何处理任务依赖？
**A**: 在任务文件中明确指定依赖，Manager 按顺序 spawn Worker。

### Q4: 可以并行执行多个 Worker 吗？
**A**: 可以！无依赖的任务可以并行 spawn。

---

## 总结

**调度三要素**：
1. **任务文件**（`TASKS/*.md`）- 定义任务
2. **sessions_spawn** - 触发执行
3. **sessions_send** - 通知反馈

**记忆是日志，文件是调度** ✅
