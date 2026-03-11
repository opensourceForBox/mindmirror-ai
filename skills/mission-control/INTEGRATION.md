# Manager 技能集成指南

在 Manager 技能中嵌入 Mission Control 同步调用，实现**实时触发**。

## 集成点

### 1. 更新 TASK_BOARD.md 后

```javascript
// 在 manager 技能中，更新任务看板后添加：

async function updateTaskBoard(content) {
    // 1. 写入 TASK_BOARD.md
    await writeFile('iterations/v1.0/TASK_BOARD.md', content);
    
    // 2. 同步到 Bitable (实时触发)
    await syncToMissionControl();
}
```

### 2. 派发任务给 Worker 后

```javascript
// 在 sessions_spawn 创建 Worker 后：

async function dispatchTask(worker, task) {
    // 1. 创建 Worker 会话
    await sessions_spawn({ task, agentId: worker });
    
    // 2. 记录通知日志
    await logNotification('Manager', worker, '任务派发', task.name);
    
    // 3. 同步到 Bitable
    await syncToMissionControl();
}
```

### 3. 收到 Worker 完成通知后

```javascript
// 在收到 sessions_send 后：

async function onWorkerComplete(worker, result) {
    // 1. 更新 TASK_BOARD.md 状态
    await updateTaskStatus(worker, '已完成');
    
    // 2. 记录通知日志
    await logNotification(worker, 'Manager', '任务完成', result.summary);
    
    // 3. 同步到 Bitable
    await syncToMissionControl();
}
```

## 同步函数实现

### 方式 A: 调用 Node.js 脚本

```javascript
const { exec } = require('child_process');
const path = require('path');

async function syncToMissionControl() {
    return new Promise((resolve, reject) => {
        const scriptPath = path.join(__dirname, '../mission-control/sync-task-board.js');
        exec(`node ${scriptPath}`, (error, stdout, stderr) => {
            if (error) {
                console.error('同步失败:', error);
                reject(error);
            } else {
                console.log('同步成功:', stdout);
                resolve();
            }
        });
    });
}
```

### 方式 B: 直接调用 Feishu API

```javascript
// 在 manager 技能中直接调用 feishu_bitable_create_record

async function syncTaskToBitable(task) {
    await feishu_bitable_create_record({
        app_token: 'OVB0b4GASaVnZgsyW7vcffwMnBh',
        table_id: 'tblGKdhzAwBBqYKE',
        fields: {
            '任务 ID': task.id,
            '任务名称': task.name,
            '负责人': task.worker,
            '当前阶段': task.phase,
            '进度%': task.progress
        }
    });
}

async function logNotificationToBitable(from, to, type, content) {
    await feishu_bitable_create_record({
        app_token: 'AMflbwg4YaGFWtsHtKEc55Venoc',
        table_id: 'tbl53G1yPcIduAOB',
        fields: {
            '时间戳': Date.now(),
            '发送者': from,
            '接收者': to,
            '通知类型': type,
            '消息内容': content
        }
    });
}
```

## 完整示例

```javascript
// manager 技能中的任务派发流程

async function dispatchTask(worker, task) {
    console.log(`📤 派发任务给 ${worker}: ${task.name}`);
    
    try {
        // 1. 创建 Worker 会话
        const session = await sessions_spawn({
            task: task.description,
            agentId: worker,
            mode: 'session'
        });
        
        // 2. 更新 TASK_BOARD.md
        const taskBoard = await readTaskBoard();
        taskBoard.tasks.find(t => t.id === task.id).status = '🔄 进行中';
        await writeTaskBoard(taskBoard);
        
        // 3. 同步到 Bitable (实时触发)
        await feishu_bitable_update_record({
            app_token: 'OVB0b4GASaVnZgsyW7vcffwMnBh',
            table_id: 'tblGKdhzAwBBqYKE',
            record_id: task.bitableId,
            fields: {
                '当前阶段': '开发中',
                '进度%': 0
            }
        });
        
        // 4. 记录通知日志
        await feishu_bitable_create_record({
            app_token: 'AMflbwg4YaGFWtsHtKEc55Venoc',
            table_id: 'tbl53G1yPcIduAOB',
            fields: {
                '时间戳': Date.now(),
                '发送者': 'Manager',
                '接收者': worker,
                '通知类型': '任务派发',
                '消息内容': `开始 ${task.name}`
            }
        });
        
        console.log(`✅ 任务派发完成，看板已同步`);
        
    } catch (error) {
        console.error('❌ 任务派发失败:', error);
        throw error;
    }
}
```

## 配置文件

### crontab 配置（定时方案）

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每 5 分钟同步一次）
*/5 * * * * /root/.openclaw/workspace/skills/mission-control/cron-sync.sh
```

### 或者使用 systemd timer（更可靠）

```ini
# /etc/systemd/system/mission-control.service
[Unit]
Description=Mission Control Sync
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory=/root/.openclaw/workspace/skills/mission-control
ExecStart=/usr/bin/node sync-task-board.js
```

```ini
# /etc/systemd/system/mission-control.timer
[Unit]
Description=Run Mission Control Sync every 5 minutes
Requires=mission-control.service

[Timer]
OnBootSec=1min
OnUnitActiveSec=5min
Unit=mission-control.service

[Install]
WantedBy=timers.target
```

```bash
# 启用定时器
systemctl daemon-reload
systemctl enable mission-control.timer
systemctl start mission-control.timer
```

## 推荐方案

**最佳实践**：Manager 集成 + crontab 备份

1. **主要触发**: Manager 更新 TASK_BOARD.md 时实时同步
2. **备份同步**: crontab 每 5 分钟检查一次，防止遗漏

这样既保证实时性，又有容错机制。
