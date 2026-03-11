# Mission Control 集成指南

> 如何在 Manager 和其他智能体中集成 Mission Control 功能

---

## 📋 概述

Mission Control 提供 3 个核心功能：

1. **任务看板同步** - `sync-task-board.js`
2. **智能体状态监控** - `monitor-agents.js`
3. **通知日志记录** - `log-notification.js`

---

## 🔧 在 Manager 中集成

### 1. 任务派发时记录通知

```javascript
// 在 manager 技能中，派发任务给 Worker 时
async function dispatchTask(worker, taskDescription) {
    // ... 创建 Worker 会话 ...
    
    // 记录通知日志
    await logNotification({
        from: 'Manager',
        to: worker,
        type: '任务派发',
        content: `开始 ${taskDescription.name} 任务`
    });
    
    // 同步任务看板
    await syncTaskBoard();
}
```

### 2. 收到 Worker 完成通知时

```javascript
// 在 manager 技能中，收到 Worker 完成消息时
async function onWorkerComplete(worker, result) {
    // 记录通知日志
    await logNotification({
        from: worker,
        to: 'Manager',
        type: '任务完成',
        content: `${worker} 完成任务：${result.summary}`
    });
    
    // 更新任务看板
    await updateTaskStatus(result.taskId, '已完成', 100);
    
    // 同步到 Bitable
    await syncTaskBoard();
}
```

### 3. 请求用户确认时

```javascript
// 在 manager 技能中，请求用户确认时
async function requestUserConfirmation(stage, details) {
    // 记录通知日志
    await logNotification({
        from: 'Manager',
        to: 'user',
        type: '确认请求',
        content: `${stage} 完成，${details}`
    });
}
```

---

## 📁 在 Worker 中集成

### Developer 示例

```javascript
// 在 developer 技能中，任务完成时
async function completeTask() {
    // ... 完成开发任务 ...
    
    // 通知 Manager
    await sessions_send({
        label: 'manager',
        message: JSON.stringify({
            type: 'task_complete',
            worker: 'developer',
            result: { ... }
        })
    });
    
    // 记录通知日志（可选，通常由 Manager 记录）
    // await logNotification({ ... });
}
```

---

## ⏰ 定时任务配置

### crontab 配置

```bash
# 编辑 crontab
crontab -e

# 每 5 分钟同步任务看板
*/5 * * * * cd /root/.openclaw/workspace/skills/mission-control && node sync-task-board.js

# 每 10 分钟监控智能体状态
*/10 * * * * cd /root/.openclaw/workspace/skills/mission-control && node monitor-agents.js
```

### systemd timer (推荐)

```ini
# /etc/systemd/system/mission-control-sync.timer
[Unit]
Description=Mission Control Task Board Sync

[Timer]
OnBootSec=1min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/mission-control-sync.service
[Unit]
Description=Mission Control Task Board Sync

[Service]
Type=oneshot
WorkingDirectory=/root/.openclaw/workspace/skills/mission-control
ExecStart=/usr/bin/node sync-task-board.js
```

---

## 📊 Bitable API 调用示例

### 创建任务记录

```javascript
await feishu_bitable_create_record({
    app_token: 'OVB0b4GASaVnZgsyW7vcffwMnBh',
    table_id: 'tblGKdhzAwBBqYKE',
    fields: {
        '任务 ID': 'TASK-101',
        '任务名称': '录像诊断功能 - 架构设计',
        '负责人': 'product-manager',
        '当前阶段': '已完成',
        '进度%': 100
    }
});
```

### 更新任务状态

```javascript
await feishu_bitable_update_record({
    app_token: 'OVB0b4GASaVnZgsyW7vcffwMnBh',
    table_id: 'tblGKdhzAwBBqYKE',
    record_id: 'recvdwcUCDMcdm',
    fields: {
        '当前阶段': '开发中',
        '进度%': 50
    }
});
```

### 记录通知

```javascript
await feishu_bitable_create_record({
    app_token: 'AMflbwg4YaGFWtsHtKEc55Venoc',
    table_id: 'tbl53G1yPcIduAOB',
    fields: {
        '时间戳': Date.now(),
        '发送者': 'Manager',
        '接收者': 'developer',
        '通知类型': '任务派发',
        '消息内容': '开始后端 API 开发'
    }
});
```

### 更新智能体状态

```javascript
await feishu_bitable_update_record({
    app_token: 'E8D2bR0Bca7QhssmTQwcNax2nCf',
    table_id: 'tblG4SZePasROVWp',
    record_id: 'recvdw3mIUnga1',
    fields: {
        '状态': '在线',
        '当前任务': '处理录像诊断功能',
        '最后活跃时间': Date.now()
    }
});
```

---

## 🎯 完整集成示例

### Manager 技能中的完整流程

```javascript
const { logNotification } = require('./mission-control/log-notification');
const { syncTaskBoard } = require('./mission-control/sync-task-board');

async function handleUserRequest(request) {
    // 1. 理解需求
    const project = await analyzeRequest(request);
    
    // 2. 记录通知
    await logNotification({
        from: 'user',
        to: 'Manager',
        type: '新需求',
        content: request
    });
    
    // 3. 判断复杂度
    const isComplex = await judgeComplexity(project);
    
    // 4. 创建迭代目录
    const version = await createIteration(project);
    
    // 5. 派发任务给 PM (复杂项目)
    if (isComplex) {
        await logNotification({
            from: 'Manager',
            to: 'product-manager',
            type: '任务派发',
            content: `开始 ${project.name} 架构设计`
        });
        
        const pmResult = await spawnWorker('product-manager', project);
        
        // 6. 记录 PM 完成
        await logNotification({
            from: 'product-manager',
            to: 'Manager',
            type: '任务完成',
            content: '架构设计完成'
        });
        
        // 7. 同步任务看板
        await syncTaskBoard();
        
        // 8. 请求用户确认
        await logNotification({
            from: 'Manager',
            to: 'user',
            type: '确认请求',
            content: '架构设计完成，请确认'
        });
    }
    
    // ... 继续后续流程
}
```

---

## 📝 注意事项

1. **性能优化**
   - 批量更新 Bitable 记录，避免频繁 API 调用
   - 使用增量同步，只更新变化的数据

2. **错误处理**
   - Bitable API 调用失败时重试
   - 记录错误日志到 `memory/manager/MEMORY.md`

3. **数据一致性**
   - TASK_BOARD.md 是主数据源
   - Bitable 是同步视图，定期校准

4. **权限管理**
   - 确保 Feishu app 有 Bitable 读写权限
   - 敏感信息不记录到通知日志

---

## 🔗 相关文档

- [技能说明](SKILL.md)
- [系统架构](ARCHITECTURE.md)
- [README](README.md)
- [AGENTS.md](/root/.openclaw/workspace/AGENTS.md)
