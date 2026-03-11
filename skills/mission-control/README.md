# 🎮 Mission Control - 智能体任务控制中心

> **Manager 协调模式** - 实时监控你的 AI 开发团队

---

## 📋 概述

基于 OpenClaw Manager 协调模式，构建类似 NASA 任务控制中心的可视化看板系统。

**核心功能**:
- 📊 **实时监控** - 查看 Manager 和 Worker 状态、任务进度
- 🔔 **通知聚合** - 追踪 Manager ↔ Worker ↔ User 的协作消息
- 📈 **数据统计** - 任务完成率、智能体工作量分析
- ⚙️ **自动化** - 定时同步 TASK_BOARD.md、自动记录通知

---

## 🚀 快速开始

### 1. 访问看板

| 看板 | 用途 | 链接 |
|------|------|------|
| 🎮 主看板 | 智能体状态 + 任务概览 | [打开](https://feishu.cn/docx/GNZbdHwL6orkTNx1QRCczCljnnT) |
| 📈 通知日志 | 通知消息时间线 | [打开](https://feishu.cn/docx/J0hadm7Qdoyj6UxdSghcmPEXnRc) |
| 📊 统计看板 | 工作效率分析 | [打开](https://feishu.cn/docx/Afutd07NsoJ9poxtNhncO3Ndnvg) |

### 2. 数据表

| 表名 | 用途 | 链接 |
|------|------|------|
| 智能体状态 | 实时状态监控 | [打开](https://ccnatqob3gk9.feishu.cn/base/E8D2bR0Bca7QhssmTQwcNax2nCf) |
| 任务流转 | 任务进度追踪 | [打开](https://ccnatqob3gk9.feishu.cn/base/OVB0b4GASaVnZgsyW7vcffwMnBh) |
| 通知日志 | 协作消息记录 | [打开](https://ccnatqob3gk9.feishu.cn/base/AMflbwg4YaGFWtsHtKEc55Venoc) |

### 3. 手动同步任务看板

```bash
cd /root/.openclaw/workspace/skills/mission-control
node sync-task-board.js
```

### 4. 定时任务 (已暂停⏸️)

为节省 Token 消耗，定时任务已暂停。**改用 Manager 实时触发**。

手动同步：
```bash
cd /root/.openclaw/workspace/skills/mission-control

# 同步任务看板
node sync-task-board.js

# 监控智能体状态
node monitor-agents.js
```

日志文件：`cron.log`

---

## 📁 文件结构

```
mission-control/
├── README.md               # 本文件
├── SKILL.md                # 技能说明
├── ARCHITECTURE.md         # 系统架构文档
├── INTEGRATION.md          # Manager 集成指南
├── MANAGER_EXAMPLES.md     # Manager 集成示例
├── task-templates.md       # 任务拆解标准模板 ✅
├── manager-integration.js  # Manager 集成模块 ✅
├── sync-task-board.js      # 任务看板同步脚本 ✅
├── monitor-agents.js       # 智能体状态监控 ✅
├── log-notification.js     # 通知日志记录 ✅
├── sync-to-bitable.sh      # Bitable 同步脚本
└── auto-sync.sh            # 自动同步脚本
```

---

## 🎯 Manager 协调模式工作流

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

---

## 📊 看板功能

### 智能体状态面板
- 🟢 在线 - 正在处理任务
- 🟡 忙碌 - 队列中有任务
- 🔵 空闲 - 等待 Manager 派发
- ⚪ 离线 - 未激活

### 任务流转追踪
- 需求分析 → 架构设计 → UI 设计 → 开发中 → 测试中 → ✅ 已完成
- 实时进度条
- 各阶段耗时统计

### 通知日志
- 时间线视图
- 发送者/接收者过滤
- 通知类型分类（任务派发、任务完成、确认请求）

---

## ⚙️ 配置

### Bitable App Tokens

```bash
AGENT_STATUS_APP="E8D2bR0Bca7QhssmTQwcNax2nCf"
TASK_TRACKING_APP="OVB0b4GASaVnZgsyW7vcffwMnBh"
NOTIFY_LOG_APP="AMflbwg4YaGFWtsHtKEc55Venoc"
```

### 环境变量

从 `/root/.openclaw/.env` 读取 Feishu API 凭证。

---

## 🔧 集成到 Manager 技能

### 示例代码

```javascript
// 在 Manager 更新 TASK_BOARD.md 后
const { logNotification } = require('./mission-control/log-notification');

// 派发任务时记录
await logNotification({
    from: 'Manager',
    to: 'developer',
    type: '任务派发',
    content: '开始后端 API 开发'
});

// 任务完成后记录
await logNotification({
    from: 'developer',
    to: 'Manager',
    type: '任务完成',
    content: '后端 API 开发完成'
});
```

详细集成指南见 [INTEGRATION.md](INTEGRATION.md)

---

## 📝 完成状态

- [x] Bitable 数据表创建 (3 个)
- [x] 主看板文档创建
- [x] 任务看板同步脚本 (sync-task-board.js) ✅ 已测试
- [x] 智能体状态监控脚本 (monitor-agents.js) ✅ 已测试
- [x] 通知日志记录脚本 (log-notification.js) ✅ 已测试
- [x] 集成指南文档 (INTEGRATION.md + MANAGER_EXAMPLES.md)
- [x] Manager 集成模块 (manager-integration.js) ✅ 已完成
- [x] 任务拆解标准模板 (task-templates.md) ✅ 已完成
- [x] Manager SOUL.md 集成 (模板 + Mission Control) ✅ 已完成
- [x] 定时任务配置 (crontab) ⏸️ 已暂停 (节省 Token)
- [ ] 告警规则引擎
- [ ] 日报/周报生成

---

## 📚 相关文档

- [技能说明](SKILL.md)
- [系统架构](ARCHITECTURE.md)
- [集成指南](INTEGRATION.md)
- [AGENTS.md](/root/.openclaw/workspace/AGENTS.md)

---

*Mission Control v1.0 - Built for OpenClaw Manager 协调模式*
