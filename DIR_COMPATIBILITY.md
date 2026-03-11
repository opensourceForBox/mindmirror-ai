# 目录兼容性说明

## 问题背景

之前的问题：
- Manager 模式产出：`iterations/v1.0/DELIVERABLES/code/`
- 直接派发产出：`code/[项目名]/`
- ❌ 两种模式产出不兼容，Tester 无法统一监听

## 解决方案

**核心设计**：
- `iterations/` 仅用于**任务调度过程**
- 最终产出统一归集到 `code/` `designs/ `test-reports/`

## 目录结构

```
/workspace/
├── iterations/                    # 迭代管理（过程）
│   └── v1.0/
│       ├── TASKS/                 # 任务文件（调度核心）
│       │   ├── ui-task.md
│       │   ├── developer-task.md
│       │   └── tester-task.md
│       ├── TASK_BOARD.md          # 任务看板
│       └── MANAGER_NOTES.md       # 迭代记录
│
├── prd/                           # PRD 目录（直接派发模式）
│   └── todo-api/
│       ├── todo-api_prd.md
│       ├── ARCHITECTURE.md
│       └── task-dev.md
│
├── code/                          # 统一代码产出 ✅
│   ├── todo-api/                  # 直接派发模式产出
│   │   ├── app.py
│   │   └── README.md
│   └── login-system/              # Manager 模式产出
│       ├── app.py
│       └── README.md
│
├── designs/                       # 统一设计产出 ✅
│   ├── todo-api/
│   └── login-system/
│
└── test-reports/                  # 统一测试产出 ✅
    ├── todo-api/
    └── login-system/
```

## 两种模式对比

| 方面 | Manager 协调模式 | 直接派发模式 |
|------|-----------------|-------------|
| **任务来源** | `iterations/v1.0/TASKS/` | `prd/[项目]/` |
| **调度方式** | `sessions_spawn` + 任务文件 | `sessions_spawn` + task-dev.md |
| **产出目录** | `code/[项目名]/` | `code/[项目名]/` |
| **进度跟踪** | `TASK_BOARD.md` | 无 |
| **记忆** | `memory/manager/MEMORY.md` | `memory/[角色]-[日期].md` |
| **适用场景** | 复杂项目、多模块 | 简单项目、单功能 |

## 兼容性保证

### ✅ 产出目录统一
- 两种模式都输出到 `code/[项目名]/`
- Tester 只需监听 `code/` 目录
- 历史项目可以复用

### ✅ 可以混合使用
```
项目 A（简单）→ 直接派发 → code/project-a/
项目 B（复杂）→ Manager 模式 → code/project-b/
```

### ✅ Tester 兼容
```yaml
# tester 触发条件
on_file_change:
  - code/           # 监听统一目录
  - designs/        # 监听设计变更
```

## 使用示例

### 场景 1：简单项目（直接派发）
```
用户："做一个 Todo API"
  ↓
product-manager 创建 prd/todo-api/
  ↓
spawn developer → code/todo-api/
  ↓
tester 监听 code/ → test-reports/todo-api/
```

### 场景 2：复杂项目（Manager 协调）
```
用户："开发一个用户登录系统"
  ↓
Manager 创建 iterations/v1.0/TASKS/
  ↓
spawn ui-designer → designs/login-system/
  ↓
spawn developer → code/login-system/
  ↓
spawn tester → test-reports/login-system/
```

### 场景 3：混合使用
```
项目 A（简单）→ 直接派发 → code/project-a/
项目 B（复杂）→ Manager 模式 → code/project-b/
  ↓
Tester 统一监听 code/ → 两种项目都能处理
```

## 总结

**关键设计原则**：
1. `iterations/` 仅用于**过程管理**
2. 最终产出统一到 `code/` `designs/` `test-reports/`
3. 两种模式**完全兼容**，可以混合使用

**好处**：
- ✅ Tester 无需关心任务来源
- ✅ 历史项目可以复用
- ✅ 可以根据项目复杂度选择模式
- ✅ 交付物集中管理
