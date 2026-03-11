# Mission Control 技能

智能体任务控制中心 - 基于 Manager 协调模式的智能体监控系统

## 功能

1. **状态监控** - 实时获取 Manager 和 Worker 状态
2. **任务追踪** - 跟踪 iterations/ 目录下的任务流转
3. **通知聚合** - 记录 Manager ↔ Worker 的任务派发和完成通知
4. **资源统计** - Token 消耗、运行时长等指标

## 数据表

| 表名 | Bitable URL | 用途 |
|------|-------------|------|
| 智能体状态 | https://ccnatqob3gk9.feishu.cn/base/E8D2bR0Bca7QhssmTQwcNax2nCf | Manager + Worker 实时状态 |
| 任务流转 | https://ccnatqob3gk9.feishu.cn/base/OVB0b4GASaVnZgsyW7vcffwMnBh | 任务进度追踪 |
| 通知日志 | https://ccnatqob3gk9.feishu.cn/base/AMflbwg4YaGFWtsHtKEc55Venoc | Manager ↔ Worker 通知记录 |

## 主看板

🔗 [Mission Control 看板](https://feishu.cn/docx/GNZbdHwL6orkTNx1QRCczCljnnT)

## 智能体架构

```
用户 → Manager → sessions_spawn → Workers → 汇总 → 用户
              ↓
        复杂度判断
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
复杂项目            简单项目
(PM+Dev+Test)        (Dev 直接)
```

### 智能体列表

| 智能体 | 触发方式 | 输出目录 |
|--------|----------|----------|
| Manager | on_message | iterations/[版本]/TASKS/ |
| Product Manager | sessions_spawn | prd/[项目名]/ |
| UI Designer | sessions_spawn | designs/[项目名]/ |
| Developer | sessions_spawn | code/[项目名]/ |
| Tester | sessions_spawn | test-reports/[项目名]/ |

## 使用方法

### 1. 手动同步任务看板

```bash
cd /root/.openclaw/workspace/skills/mission-control
node sync-task-board.js
```

### 2. 在 Manager 技能中集成自动同步

在 Manager 更新 `TASK_BOARD.md` 后，调用同步函数：

```javascript
// 在 manager 技能中添加
async function syncTaskBoard() {
    await sessions_send({
        agentId: 'mission-control',
        message: 'sync iterations/v1.0/TASK_BOARD.md'
    });
}
```

### 3. 配置定时任务

```bash
# 每 5 分钟同步一次
crontab -e
*/5 * * * * cd /root/.openclaw/workspace/skills/mission-control && node sync-task-board.js
```

### 4. 使用 openclaw CLI 直接调用

```bash
# 更新智能体状态
openclaw sessions list

# 使用 feishu_bitable_update_record 更新记录
# (需要通过 openclaw 工具调用)
```

## 自动化集成

### Manager 技能集成点

在 Manager 的以下操作后触发同步：

1. **创建新迭代** - `iterations/vX.X/TASK_BOARD.md` 创建后
2. **更新任务状态** - 任务阶段变化时
3. **Worker 完成通知** - 收到 Worker 完成消息后

### 示例代码

```javascript
// Manager 更新 TASK_BOARD.md 后
await writeFile('iterations/v1.0/TASK_BOARD.md', content);
await syncToBitable(); // 调用同步函数
```

## API 端点

- `app_token` (智能体状态): `E8D2bR0Bca7QhssmTQwcNax2nCf`
- `app_token` (任务流转): `OVB0b4GASaVnZgsyW7vcffwMnBh`
- `app_token` (通知日志): `AMflbwg4YaGFWtsHtKEc55Venoc`

## 相关文件

- `/root/.openclaw/workspace/AGENTS.md` - 智能体配置
- `/root/.openclaw/workspace/memory/manager/MEMORY.md` - Manager 记忆
- `/root/.openclaw/workspace/iterations/` - 迭代管理目录
