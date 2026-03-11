# Mission Control 系统架构

## 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    Mission Control Dashboard                     │
│                  (Feishu Doc + Bitable 看板)                      │
└─────────────────────────────────────────────────────────────────┘
                              ↑ ↓ 同步
┌─────────────────────────────────────────────────────────────────┐
│                      数据层 (Data Layer)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ 智能体状态表 │  │ 任务流转表  │  │ 通知日志表  │              │
│  │   Bitable   │  │   Bitable   │  │   Bitable   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              ↑ ↓ CRUD
┌─────────────────────────────────────────────────────────────────┐
│                     控制层 (Control Layer)                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              mission-control 技能                        │    │
│  │  • update-status.sh  - 定时状态同步                       │    │
│  │  • track-task.sh   - 任务流转追踪                         │    │
│  │  • log-notify.sh   - 通知日志记录                         │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↑ ↓ 监听/触发
┌─────────────────────────────────────────────────────────────────┐
│                    智能体层 (Agent Layer)                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Manager (核心协调者)                   │    │
│  │  • 需求理解、复杂度判断、任务拆解                         │    │
│  │  • sessions_spawn 主动派发任务                           │    │
│  │  • 维护 memory/manager/MEMORY.md                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              ↓ sessions_spawn                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │    PM    │  │    UI    │  │   Dev    │  │  Test    │        │
│  │ (架构师)  │  │ Designer │  │  (工匠)  │  │          │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│       ↓             ↓              ↓             ↓              │
│    prd/         designs/        code/       test-reports/       │
└─────────────────────────────────────────────────────────────────┘
```

## 数据流

### 1. 智能体状态同步
```
sessions_list → 解析活跃会话 → 更新 Bitable → 看板自动刷新
     ↓
每 5 分钟执行一次
```

### 2. 任务流转追踪 (Manager 协调模式)
```
用户请求 → Manager → 复杂度判断
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
复杂项目            简单项目
sessions_spawn      sessions_spawn
PM → Dev → Test     Dev → Test
    ↓                   ↓
iterations/vX.X/    iterations/vX.X/
TASK_BOARD.md       TASK_BOARD.md
    ↓                   ↓
更新 Bitable        更新 Bitable
```

### 3. 通知日志记录
```
Manager → sessions_send → Worker (任务派发)
                ↓
        写入通知日志表
                ↓
          看板通知流更新

Worker → sessions_send → Manager (任务完成)
                ↓
        写入通知日志表
                ↓
          看板状态更新
```

## 核心组件

### Bitable 数据表

| 表名 | App Token | 主要字段 |
|------|-----------|----------|
| 智能体状态 | `E8D2bR0Bca7QhssmTQwcNax2nCf` | Manager/Worker 名称、状态、当前任务、输出目录 |
| 任务流转 | `OVB0b4GASaVnZgsyW7vcffwMnBh` | 任务 ID、名称、阶段、负责人 (Manager/Worker)、进度% |
| 通知日志 | `AMflbwg4YaGFWtsHtKEc55Venoc` | 时间戳、发送者 (Manager/Worker)、接收者、通知类型、内容 |

### 监控脚本

| 脚本 | 功能 | 触发方式 |
|------|------|----------|
| `update-status.sh` | 同步智能体状态 | 定时任务 (5min) |
| `track-task.sh` | 追踪任务流转 | 文件监听 |
| `log-notify.sh` | 记录通知消息 | 事件钩子 |

### Feishu 集成

- **Doc**: 主看板页面 (嵌入 Bitable 视图)
- **Bitable**: 数据存储 + 筛选视图
- **消息**: 告警通知推送

## 扩展能力

### 可添加的模块

1. **资源监控**
   - Token 消耗趋势图
   - 会话时长统计
   - 模型使用分布

2. **告警系统**
   - 智能体离线告警
   - 任务超时告警
   - Token 超支告警

3. **报表导出**
   - 日报/周报自动生成
   - PDF 导出
   - 数据导出 (CSV/Excel)

4. **权限管理**
   - 查看权限控制
   - 操作权限分级
   - 审计日志

## 部署清单

- [x] Bitable 数据表创建 (3 个)
- [x] 主看板文档创建
- [x] 技能框架搭建
- [x] 基于 Manager 协调模式更新架构
- [ ] 定时任务配置 (cron)
- [ ] sessions_spawn/sessions_send 事件监听
- [ ] 通知钩子集成
- [ ] iterations/ 目录任务看板同步
- [ ] 告警规则配置

## 快速开始

```bash
# 1. 查看看板
open https://feishu.cn/docx/AnChdwlgHoI216xoDKyccorInDq

# 2. 手动更新状态
cd /root/.openclaw/workspace/skills/mission-control
bash update-status.sh

# 3. 配置定时任务
crontab -e
# 添加：*/5 * * * * /root/.openclaw/workspace/skills/mission-control/update-status.sh
```
