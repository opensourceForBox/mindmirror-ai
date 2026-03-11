# 🎮 Mission Control - 智能体任务控制中心

> 实时监控和管理你的 AI 智能体团队

## 📋 概述

基于 OpenClaw 智能体架构，构建一个类似 NASA 任务控制中心的可视化看板系统，用于：

- 📊 **实时监控** - 查看各智能体状态、任务进度
- 🔔 **通知聚合** - 追踪智能体间的协作消息
- 📈 **数据统计** - Token 消耗、任务完成率等指标
- ⚙️ **自动化** - 定时同步、文件监听、告警推送

## 🚀 快速开始

### 1. 访问看板

🔗 **[Mission Control 主看板](https://feishu.cn/docx/AnChdwlgHoI216xoDKyccorInDq)**

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

### 4. 配置定时任务 (可选)

```bash
crontab -e
# 每 5 分钟同步一次任务看板
*/5 * * * * cd /root/.openclaw/workspace/skills/mission-control && node sync-task-board.js
```

## 📁 文件结构

```
mission-control/
├── README.md           # 本文件
├── SKILL.md            # 技能说明
├── ARCHITECTURE.md     # 系统架构文档
├── update-status.sh    # 状态同步脚本
└── (待添加)
    ├── track-task.sh   # 任务追踪脚本
    ├── log-notify.sh   # 通知记录脚本
    └── alert.sh        # 告警脚本
```

## 🎯 智能体工作流

```
用户请求 → 产品经理 → UI 设计师 → 开发架构师 → 测试工程师 → 完成
            ↓           ↓            ↓            ↓
          prd/      designs/       code/      test-reports/
```

### 智能体列表

| 智能体 | 触发条件 | 输出目录 | 通知对象 |
|--------|----------|----------|----------|
| 产品经理 | 需求关键词 | prd/ | UI 设计师 |
| UI 设计师 | prd/ 新文件 | designs/ | 开发架构师 |
| 开发架构师 | designs/ 新文件 | code/ | 测试工程师 |
| 测试工程师 | code/ 新文件 | test-reports/ | 飞书反馈 |

## 📊 看板功能

### 智能体状态面板
- 🟢 在线 - 正在处理任务
- 🟡 忙碌 - 队列中有任务
- 🔵 空闲 - 等待新任务
- ⚪ 离线 - 未激活

### 任务流转追踪
- 需求分析 → UI 设计 → 开发中 → 测试中 → ✅ 已完成
- 实时进度条
- 各阶段耗时统计

### 通知日志
- 时间线视图
- 发送者/接收者过滤
- 通知类型分类

## ⚙️ 配置

### Bitable App Tokens

```bash
AGENT_STATUS_APP="E8D2bR0Bca7QhssmTQwcNax2nCf"
TASK_TRACKING_APP="OVB0b4GASaVnZgsyW7vcffwMnBh"
NOTIFY_LOG_APP="AMflbwg4YaGFWtsHtKEc55Venoc"
```

### 环境变量

从 `/root/.openclaw/.env` 读取 Feishu API 凭证。

## 🔧 扩展开发

### 添加新智能体

1. 在 `AGENTS.md` 中添加智能体配置
2. 在智能体状态 Bitable 中添加记录
3. 更新 `update-status.sh` 中的映射

### 添加新指标

1. 在对应 Bitable 表中创建新字段
2. 更新监控脚本采集逻辑
3. 在看板文档中添加展示

### 集成告警

```bash
# 示例：智能体离线告警
if [ "$status" == "离线" ]; then
    openclaw message send --channel feishu --target "ou_xxx" "⚠️ $agent_name 离线告警"
fi
```

## 📝 待办事项

- [ ] 实现文件监听器 (inotify/fswatch)
- [ ] 集成 sessions_list API 实时状态
- [ ] 添加 Token 消耗统计
- [ ] 实现告警规则引擎
- [ ] 生成日报/周报
- [ ] 添加图表可视化 (Bitable 仪表盘)

## 📚 相关文档

- [系统架构](ARCHITECTURE.md)
- [技能说明](SKILL.md)
- [AGENTS.md](/root/.openclaw/workspace/AGENTS.md)

---

*Mission Control v1.0 - Built for OpenClaw*
