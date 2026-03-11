# Manager 技能集成 Mission Control 示例

## 快速开始

在 Manager 技能的关键节点添加 Mission Control 调用。

---

## 集成代码示例

### 1. 在 SOUL.md 中添加集成说明

```markdown
# Mission Control 集成

在以下关键节点自动同步到 Mission Control 看板：

## 触发点

### 派发任务给 Worker
```javascript
const missionControl = require('/root/.openclaw/workspace/skills/mission-control/manager-integration.js');

// 在 sessions_spawn 后
await sessions_spawn({ task, agentId: worker });
await missionControl.hooks.onTaskDispatch(worker, task.name);
```

### Worker 完成任务
```javascript
// 收到 sessions_send 后
await missionControl.hooks.onWorkerComplete(worker, result);
```

### 更新 TASK_BOARD.md
```javascript
// 写入 TASK_BOARD.md 后
await writeFile('iterations/v1.0/TASK_BOARD.md', content);
await missionControl.hooks.onTaskBoardUpdate('1.0');
```

### 请求用户确认
```javascript
// 发送确认请求前
await missionControl.hooks.onRequestApproval('架构设计', 'PRD 和架构已就绪，请确认');
await message.send({ target: 'user', message: '请确认架构设计...' });
```
```

---

## 完整示例：任务派发流程

```javascript
// Manager 技能中的任务派发

const missionControl = require('/root/.openclaw/workspace/skills/mission-control/manager-integration.js');

async function dispatchTask(worker, task) {
    console.log(`📤 派发任务给 ${worker}: ${task.name}`);
    
    try {
        // 1. 创建任务文件
        const taskFile = `iterations/v1.0/TASKS/${worker}-task.md`;
        await writeFile(taskFile, task.description);
        
        // 2. 创建 Worker 会话
        const session = await sessions_spawn({
            task: task.description,
            agentId: worker,
            mode: 'session'
        });
        
        // 3. 【Mission Control 集成】记录任务派发
        await missionControl.hooks.onTaskDispatch(worker, task.name);
        
        // 4. 更新 TASK_BOARD.md
        const taskBoard = await readTaskBoard();
        const taskEntry = taskBoard.tasks.find(t => t.id === task.id);
        if (taskEntry) {
            taskEntry.status = '🔄 进行中';
            taskEntry.sessionKey = session.sessionKey;
        }
        await writeTaskBoard(taskBoard);
        
        // 5. 【Mission Control 集成】同步任务看板
        await missionControl.syncTaskBoard();
        
        console.log(`✅ 任务派发完成，看板已同步`);
        
    } catch (error) {
        console.error('❌ 任务派发失败:', error);
        throw error;
    }
}
```

---

## 完整示例：Worker 完成处理

```javascript
// Manager 技能中的 Worker 完成处理

async function onWorkerComplete(worker, result) {
    console.log(`✅ 收到 ${worker} 完成通知`);
    
    try {
        // 1. 读取 Worker 输出
        const outputDir = getWorkerOutputDir(worker);
        const deliverables = await scanDeliverables(outputDir);
        
        // 2. 更新 TASK_BOARD.md
        const taskBoard = await readTaskBoard();
        const taskEntry = taskBoard.tasks.find(t => t.worker === worker);
        if (taskEntry) {
            taskEntry.status = '✅ 已完成';
            taskEntry.deliverables = deliverables;
        }
        await writeTaskBoard(taskBoard);
        
        // 3. 【Mission Control 集成】记录完成通知 + 同步看板
        await missionControl.hooks.onWorkerComplete(worker, {
            summary: `${worker} 完成，交付物：${deliverables.join(', ')}`
        });
        
        // 4. 决定下一步
        const nextStep = determineNextStep(worker);
        if (nextStep) {
            await dispatchTask(nextStep.worker, nextStep.task);
        } else {
            // 所有任务完成，请求用户确认
            await missionControl.hooks.onRequestApproval(
                '交付物确认',
                `所有任务完成，交付物：${deliverables.join(', ')}`
            );
            await message.send({
                target: 'user',
                message: `✅ 项目完成！交付物：${deliverables.join('\n')}`
            });
        }
        
    } catch (error) {
        console.error('❌ Worker 完成处理失败:', error);
        throw error;
    }
}
```

---

## 完整示例：用户确认流程

```javascript
// Manager 技能中的用户确认

async function requestApproval(approvalType, content, documents) {
    console.log(`📋 请求用户确认：${approvalType}`);
    
    // 1. 准备确认内容
    const approvalMessage = `
## ${approvalType} 确认

${content}

### 相关文档
${documents.map(d => `- ${d}`).join('\n')}

---
**请回复**:
- "确认" → 继续执行
- "需要修改 XX" → 重新设计
`;
    
    // 2. 【Mission Control 集成】记录确认请求
    await missionControl.hooks.onRequestApproval(approvalType, content);
    
    // 3. 发送给用户
    await message.send({
        target: 'user',
        message: approvalMessage
    });
    
    // 4. 等待用户回复（由 Manager 的 on_message 处理）
}

// 在 on_message 中处理用户确认
async function onMessage(message) {
    const userReply = message.content;
    
    if (userReply.includes('确认')) {
        // 用户确认，继续流程
        await proceedToNextStep();
    } else if (userReply.includes('修改')) {
        // 用户要求修改，重新执行
        await redoTask(userReply);
    }
}
```

---

## 在 SOUL.md 中添加工具使用说明

```markdown
# 工具使用

| 工具 | 用途 |
|------|------|
| `sessions_spawn` | 创建 Worker 会话 |
| `sessions_send` | 向 Worker 发送消息 |
| `read`/`write` | 读写文件 |
| `message` | 飞书通知用户 |
| **`missionControl`** | **Mission Control 集成** |

## Mission Control 集成

```javascript
const missionControl = require('/root/.openclaw/workspace/skills/mission-control/manager-integration.js');

// 同步任务看板
await missionControl.syncTaskBoard();

// 监控智能体状态
await missionControl.monitorAgents();

// 记录通知
await missionControl.logNotification(from, to, type, content);

// 使用钩子（推荐）
await missionControl.hooks.onTaskDispatch(worker, taskName);
await missionControl.hooks.onWorkerComplete(worker, result);
await missionControl.hooks.onTaskBoardUpdate(version);
await missionControl.hooks.onRequestApproval(type, content);
```
```

---

## 最小化集成（仅关键节点）

如果不想大规模修改代码，至少在这两个点集成：

### 1. 派发任务时（1 行代码）

```javascript
// 在 sessions_spawn 后添加
await require('/root/.openclaw/workspace/skills/mission-control/manager-integration.js')
    .hooks.onTaskDispatch(worker, task.name);
```

### 2. Worker 完成时（1 行代码）

```javascript
// 在收到 Worker 完成通知后添加
await require('/root/.openclaw/workspace/skills/mission-control/manager-integration.js')
    .hooks.onWorkerComplete(worker, result);
```

---

## 测试集成

```bash
# 1. 手动测试集成模块
cd /root/.openclaw/workspace/skills/mission-control
node -e "const mc = require('./manager-integration.js'); mc.syncTaskBoard();"

# 2. 查看日志
tail -f cron.log

# 3. 查看 Bitable 是否更新
# 打开 https://ccnatqob3gk9.feishu.cn/base/OVB0b4GASaVnZgsyW7vcffwMnBh
```

---

## 故障排除

### 问题：集成模块找不到
```
Error: Cannot find module '/root/.openclaw/workspace/skills/mission-control/manager-integration.js'
```

**解决**: 确认文件存在
```bash
ls -la /root/.openclaw/workspace/skills/mission-control/manager-integration.js
```

### 问题：权限不足
```
Error: Permission denied
```

**解决**: 确保脚本可执行
```bash
chmod +x /root/.openclaw/workspace/skills/mission-control/*.js
```

### 问题：Feishu API 调用失败
```
Error: Request failed with status code 400
```

**解决**: 检查 `.env` 中的 Feishu 凭证配置
