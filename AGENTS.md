# AGENTS.md - 你的 AI 开发团队智能体配置

## 团队成员

### 0. 项目经理 (manager) - NEW 🆕
- **技能**: `manager` (位于 `/root/.openclaw/agents/manager/`)
- **触发条件**:
  - `on_message`: 当飞书消息包含 ["开发", "做一个", "项目", "系统"] 等关键词时
  - `sessions_send`: Worker 完成通知
- **核心职责**:
  - 需求理解：与用户对话，澄清需求细节
  - **复杂度判断**: 决定是否需要 product-manager（复杂/简单项目）
  - 任务拆解：将需求拆解为 UI/开发/测试子任务
  - 迭代管理：创建 `iterations/vX.X/` 目录，管理交付物
  - Worker 协调：通过 `sessions_spawn` 创建 Worker 会话（**主动触发，不监听**）
  - 双层记忆：维护 `memory/manager/MEMORY.md`（决策、问题、解决方案）
- **输出目录**: `iterations/[版本]/`（过程）、`code/` `designs/` `test-reports/`（产出）
- **任务看板**: Markdown 表格跟踪进度
- **通知**: 所有 Worker（任务派发）、用户（确认请求、迭代完成）

### 1. 产品经理 & 架构师 (product-manager)
- **技能**: `product-manager` (位于 `/root/.openclaw/agents/product-manager/`)
- **触发条件**:
  - `sessions_spawn`: 由 Manager 主动创建会话（仅复杂项目需要）
- **核心职责**:
  - 需求拆解：技术栈选型、系统架构设计、迭代步骤规划
  - 输出技术规约：`ARCHITECTURE.md`（系统架构）+ `.mdc` 文件（Claude Code 规范）
  - 项目迭代：根据反馈持续优化规则文件
- **输出目录**: `prd/[项目名]/`
- **输出文档**:
  - `[项目名]_prd.md` - 产品需求文档
  - `ARCHITECTURE.md` - 系统架构设计
  - `.mdc` - Claude Code 规则文件
  - `task-dev.md` - 开发任务描述
- **通知**: Manager（架构设计完成后）

### 2. UI 设计师 (ui-designer)
- **技能**: `ui-designer` (位于 `/root/.openclaw/agents/ui-designer/`)
- **触发条件**:
  - `sessions_spawn`: 由 Manager 主动创建会话（不监听文件变化）
- **输出目录**: `designs/[项目名]/`
- **通知**: Manager（完成后）

### 3. 开发工程师 (developer)
- **技能**: `developer` (位于 `/root/.openclaw/agents/developer/`)
- **代号**: 工匠
- **开发引擎**: Claude Code（通过 `claude` 命令自主执行开发任务）
- **模型策略**: 动态选择（根据任务类型自动选择最优模型）
  - 复杂后端/全栈：`glm-5`
  - UI/前端/多模态：`kimi-k2.5`
  - 日常 CRUD：`qwen3.5-plus`
  - 快速原型：`minimax-m2.5`
- **触发条件**:
  - `sessions_spawn`: 由 Manager 主动创建会话（不监听文件变化）
- **核心职责**:
  - 接收并理解任务（从任务描述文件获取需求）
  - 根据任务类型选择最优模型（`claude --model [模型名]`）
  - 使用 Claude Code 自主完成代码编写、测试、调试
  - 遵守项目技术规约（自动加载 `.cloude/settings.mdc` 等规范）
- **输出目录**: `code/[项目名]/`
- **交付内容**: 源代码、README（运行说明）、依赖文件（requirements.txt / package.json）
- **通知**: Manager（完成后），Manager 再决定是否通知 tester

### 4. 测试工程师 (tester)
- **技能**: `tester` (位于 `/root/.openclaw/agents/tester/`)
- **触发条件**:
  - `sessions_spawn`: 由 Manager 主动创建会话（不监听文件变化）
- **输出目录**: `test-reports/[项目名]/`
- **通知**: Manager（测试完成后反馈）

## 共享配置

### 目录结构（兼容设计）
```
/root/.openclaw/workspace/
├── iterations/              # 迭代管理目录（Manager 模式专用）
│   └── v1.0/
│       ├── TASKS/           # 任务文件（调度核心）
│       ├── TASK_BOARD.md    # 任务看板
│       └── MANAGER_NOTES.md # 迭代记录
│
├── prd/                     # 传统 PRD 目录（直接派发模式）
│   └── [项目]/
│       ├── xxx_prd.md
│       ├── ARCHITECTURE.md
│       └── task-dev.md
│
├── code/                    # 统一代码产出目录（两种模式通用）
│   └── [项目名]/
│       ├── app.py
│       ├── models.py
│       └── README.md
│
├── designs/                 # 统一设计产出目录（两种模式通用）
│   └── [项目名]/
│       ├── login.html
│       └── login.css
│
├── test-reports/            # 统一测试产出目录（两种模式通用）
│   └── [项目名]/
│       ├── test_xxx.py
│       └── test_report.md
│
└── memory/
    ├── manager/
    │   └── MEMORY.md        # Manager 记忆（双层记忆上层）
    └── [角色]-[日期].md     # Worker 日志
```

**关键设计**：
- `iterations/` 仅用于**任务调度过程**
- 最终产出统一归集到 `code/` `designs/` `test-reports/`
- 两种模式**产出目录完全兼容**

### 环境变量
- 从 `/root/.openclaw/.env` 读取

### 会话记录
- 每日自动保存在 `memory/` 目录

## 状态
- ✅ 智能体目录已创建
- ✅ manager 已创建（v3.0）- 支持复杂度判断、主动触发
- ✅ product-manager 已升级为产品 + 架构师（v2.1）- 支持模型选择
- ✅ developer 已升级为 Claude Code 驱动（v2.2）- 支持动态模型选择
- ⏳ 待升级：ui-designer、tester
- ✅ 触发器：所有 Worker 通过 `sessions_spawn` 主动触发（不监听文件变化）
- ✅ 通知机制：Worker 完成后通过 `sessions_send` 通知 Manager

## 触发机制（重要更新）

**所有 Worker 通过 `sessions_spawn` 主动触发，不监听文件变化！**

| Worker | 触发方式 | 说明 |
|--------|---------|------|
| manager | `on_message` | 用户消息触发 |
| product-manager | `sessions_spawn` | Manager 主动创建（仅复杂项目） |
| ui-designer | `sessions_spawn` | Manager 主动创建 |
| developer | `sessions_spawn` | Manager 主动创建 |
| tester | `sessions_spawn` | Manager 主动创建 |

**好处**:
- ✅ Manager 完全控制流程
- ✅ 可以插入用户确认环节
- ✅ 避免意外触发导致的流程混乱

## 模型选择策略

| 任务类型 | 推荐模型 | 理由 |
|---------|---------|------|
| 复杂后端/全栈/调试 | `glm-5` | SWE-Bench 77.8% 高分，逻辑一致性最佳 |
| UI/前端/多模态 | `kimi-k2.5` | 原生多模态，能理解截图生成代码 |
| 日常 CRUD/工具函数 | `qwen3.5-plus` | 性价比最高 |
| 快速原型/自动化 | `minimax-m2.5` | 推理速度最快（~100TPS） |

## 工作模式

### 模式 A：Manager 协调模式（推荐用于复杂项目）
```
用户 → Manager → 拆解任务 → spawn Workers → 汇总交付物 → 用户
```

### 模式 B：直接派发模式（简单项目）
```
用户 → product-manager → developer → tester
```

---
*这是一个逐步完善的 AI 团队工作流配置，后续将逐步添加自动化和协作逻辑*
