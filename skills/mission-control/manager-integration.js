/**
 * Mission Control 集成模块
 * 
 * 在 Manager 技能中引入此模块，实现实时触发同步
 * 
 * 使用方法：
 * const missionControl = require('/root/.openclaw/workspace/skills/mission-control/manager-integration.js');
 * 
 * // 在关键节点调用
 * await missionControl.syncTaskBoard();
 * await missionControl.logNotification(...);
 */

const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const CONFIG = {
    workspaceDir: '/root/.openclaw/workspace',
    missionControlDir: '/root/.openclaw/workspace/skills/mission-control',
    bitableApp: {
        taskTracking: 'OVB0b4GASaVnZgsyW7vcffwMnBh',
        taskTable: 'tblGKdhzAwBBqYKE',
        notifyLog: 'AMflbwg4YaGFWtsHtKEc55Venoc',
        notifyTable: 'tbl53G1yPcIduAOB',
        agentStatus: 'E8D2bR0Bca7QhssmTQwcNax2nCf',
        agentTable: 'tblG4SZePasROVWp'
    }
};

/**
 * 执行 Node.js 脚本
 */
function execScript(scriptName, args = []) {
    return new Promise((resolve, reject) => {
        const scriptPath = path.join(CONFIG.missionControlDir, scriptName);
        const cmd = `node ${scriptPath} ${args.join(' ')}`;
        
        console.log(`🎮 [Mission Control] 执行：${cmd}`);
        
        exec(cmd, { cwd: CONFIG.missionControlDir }, (error, stdout, stderr) => {
            if (error) {
                console.error(`❌ [Mission Control] 执行失败：`, error);
                reject(error);
            } else {
                console.log(`✅ [Mission Control] 执行成功`);
                if (stdout) console.log(stdout);
                resolve({ stdout, stderr });
            }
        });
    });
}

/**
 * 同步任务看板到 Bitable
 * 
 * 调用时机：
 * - Manager 创建/更新 TASK_BOARD.md 后
 * - Worker 完成任务后
 */
async function syncTaskBoard() {
    console.log('📋 [Mission Control] 同步任务看板...');
    try {
        await execScript('sync-task-board.js');
        console.log('✅ [Mission Control] 任务看板同步完成');
    } catch (error) {
        console.error('❌ [Mission Control] 任务看板同步失败:', error);
    }
}

/**
 * 监控智能体状态
 * 
 * 调用时机：
 * - Manager 派发任务后
 * - 定期状态更新
 */
async function monitorAgents() {
    console.log('📡 [Mission Control] 监控智能体状态...');
    try {
        await execScript('monitor-agents.js');
        console.log('✅ [Mission Control] 智能体状态同步完成');
    } catch (error) {
        console.error('❌ [Mission Control] 智能体状态监控失败:', error);
    }
}

/**
 * 记录通知日志
 * 
 * @param {string} from - 发送者 (Manager/Worker 名称)
 * @param {string} to - 接收者 (Worker 名称/User)
 * @param {string} type - 通知类型 (任务派发/任务完成/确认请求/进度更新)
 * @param {string} content - 通知内容
 * 
 * 调用时机：
 * - Manager 派发任务给 Worker
 * - Worker 完成任务通知 Manager
 * - Manager 向用户请求确认
 */
async function logNotification(from, to, type, content) {
    console.log(`📝 [Mission Control] 记录通知：${from} → ${to} (${type})`);
    
    const timestamp = Date.now();
    
    // 使用 log-notification.js 脚本
    const args = [
        `--from "${from}"`,
        `--to "${to}"`,
        `--type "${type}"`,
        `--content "${content}"`
    ];
    
    try {
        await execScript('log-notification.js', args);
        console.log('✅ [Mission Control] 通知记录完成');
    } catch (error) {
        console.error('❌ [Mission Control] 通知记录失败:', error);
    }
}

/**
 * 更新任务状态
 * 
 * @param {string} taskId - 任务 ID (如 TASK-101)
 * @param {string} phase - 阶段 (待确认/开发中/已完成等)
 * @param {number} progress - 进度百分比 (0-100)
 * 
 * 调用时机：
 * - 任务阶段变化时
 */
async function updateTaskStatus(taskId, phase, progress = 0) {
    console.log(`🔄 [Mission Control] 更新任务状态：${taskId} → ${phase} (${progress}%)`);
    
    // TODO: 直接调用 feishu_bitable_update_record
    // 这里需要通过 openclaw 工具调用
    console.log('⚠️  需要使用 feishu_bitable_update_record 工具更新');
    
    /*
    示例调用：
    await feishu_bitable_update_record({
        app_token: CONFIG.bitableApp.taskTracking,
        table_id: CONFIG.bitableApp.taskTable,
        record_id: taskId,  // 需要预先存储 record_id 映射
        fields: {
            '当前阶段': phase,
            '进度%': progress
        }
    });
    */
}

/**
 * 完整的工作流钩子
 * 
 * 在 Manager 的关键生命周期自动调用
 */
const hooks = {
    /**
     * Manager 创建/更新 TASK_BOARD.md 后
     */
    onTaskBoardUpdate: async function(version) {
        console.log(`🎯 [Hook] TASK_BOARD.md 更新 (v${version})`);
        await syncTaskBoard();
        await logNotification('Manager', 'System', '进度更新', `迭代 v${version} 任务看板已更新`);
    },
    
    /**
     * Manager 派发任务给 Worker 后
     */
    onTaskDispatch: async function(worker, taskName) {
        console.log(`🎯 [Hook] 任务派发：${worker} → ${taskName}`);
        await logNotification('Manager', worker, '任务派发', `开始 ${taskName}`);
        await monitorAgents();
    },
    
    /**
     * Worker 完成任务后
     */
    onWorkerComplete: async function(worker, result) {
        console.log(`🎯 [Hook] Worker 完成：${worker}`);
        await logNotification(worker, 'Manager', '任务完成', result.summary || '任务已完成');
        await syncTaskBoard();
        await monitorAgents();
    },
    
    /**
     * Manager 向用户请求确认
     */
    onRequestApproval: async function(approvalType, content) {
        console.log(`🎯 [Hook] 请求用户确认：${approvalType}`);
        await logNotification('Manager', 'user', '确认请求', content);
    }
};

// 导出
module.exports = {
    syncTaskBoard,
    monitorAgents,
    logNotification,
    updateTaskStatus,
    hooks,
    CONFIG
};
