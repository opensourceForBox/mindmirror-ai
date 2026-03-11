# Manager-Worker 双层记忆模型

## 架构对比

### 之前：线性流程
```
用户 → product-manager → developer → tester
```

### 现在：Manager 协调模式
```
                    ┌─→ UI Worker ─────┐
用户 → Manager ──┼─→ Developer Worker ─┼→ Manager 汇总 → 用户
                    └─→ Tester Worker ─┘
                         ↑
                    双层记忆
              Manager MEMORY.md + Worker 记忆
```

## 核心特性

### 1. Manager 职责
- **需求理解**：与用户对话，澄清需求
- **任务拆解**：自动拆分为 UI/开发/测试子任务
- **Worker 协调**：创建会话、传递依赖、监控进度
- **迭代管理**：`iterations/v1.0/` 目录结构
- **双层记忆**：决策、问题、解决方案记录

### 2. 迭代目录结构
```
iterations/v1.0/
├── DELIVERABLES/
│   ├── ui/          # UI Worker 交付
│   ├── code/        # Developer Worker 交付
│   └── test/        # Tester Worker 交付
├── MANAGER_NOTES.md # 本次迭代记录
└── TASK_BOARD.md    # 任务看板
```

### 3. 双层记忆

#### Manager 记忆 (`memory/manager/MEMORY.md`)
- 项目决策及原因
- 遇到的问题与解决方案
- Worker 表现评估
- 技术栈偏好

#### Worker 记忆 (各 Worker 自行维护)
- 技术实现细节
- 代码架构决策
- 测试策略

## 使用示例

### 用户输入
```
"开发一个用户登录系统"
```

### Manager 处理流程
1. **理解需求**：用户需要登录系统（包含 UI+ 后端 + 测试）
2. **拆解任务**：
   - UI 设计登录页面 → UI Worker
   - 实现后端 API → Developer Worker
   - 编写测试用例 → Tester Worker
3. **创建迭代**：`iterations/v1.0/`
4. **派发任务**：
   ```bash
   sessions_spawn --label="ui-login" --task="设计登录页面"
   sessions_spawn --label="dev-login" --task="实现登录 API"
   sessions_spawn --label="test-login" --task="编写测试用例"
   ```
5. **更新看板**：实时跟踪进度
6. **汇总交付物**：迭代完成后反馈用户
7. **记录记忆**：决策、问题、解决方案写入 `MEMORY.md`

## 何时使用 Manager 模式？

| 场景 | 推荐模式 | 理由 |
|------|---------|------|
| 复杂项目（多模块） | Manager 协调 | 需要统一协调 |
| 简单项目（单功能） | 直接派发 | 减少 overhead |
| 多轮迭代 | Manager 协调 | 版本管理清晰 |
| 快速原型 | 直接派发 | 速度优先 |

## 迁移策略

### 兼容现有流程
- `prd/` 目录继续保留（直接派发模式）
- `iterations/` 目录用于 Manager 协调模式
- 两种方式可并行使用

### 逐步迁移
1. 新项目优先使用 Manager 模式
2. 简单需求继续使用直接派发
3. 根据反馈调整
