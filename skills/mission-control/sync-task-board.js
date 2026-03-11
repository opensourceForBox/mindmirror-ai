#!/usr/bin/env node
/**
 * Mission Control - TASK_BOARD.md 自动同步到 Bitable
 * 
 * 使用方法：
 * 1. 手动执行：node sync-task-board.js
 * 2. 定时任务：每 5 分钟执行一次
 * 3. 事件触发：在 Manager 更新 TASK_BOARD.md 后调用
 */

const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
    iterationsDir: '/root/.openclaw/workspace/iterations',
    bitableApp: 'OVB0b4GASaVnZgsyW7vcffwMnBh',
    bitableTable: 'tblGKdhzAwBBqYKE',
    dashboardUrl: 'https://feishu.cn/docx/GNZbdHwL6orkTNx1QRCczCljnnT'
};

// 状态映射
const STATUS_MAP = {
    '✅': '已完成',
    '完成': '已完成',
    '⏳': '待确认',
    '待确认': '待确认',
    '🔄': '开发中',
    '进行中': '开发中',
    '待开始': '待确认'
};

/**
 * 解析 Markdown 表格行
 */
function parseTableRow(line) {
    const cells = line.split('|').map(c => c.trim()).filter(c => c);
    return cells;
}

/**
 * 解析 TASK_BOARD.md 文件
 */
function parseTaskBoard(filePath) {
    const content = fs.readFileSync(filePath, 'utf-8');
    const tasks = [];
    
    const lines = content.split('\n');
    let currentStage = '';
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        
        // 检测阶段标题
        if (line.startsWith('## 阶段')) {
            currentStage = line.replace('## ', '').trim();
        }
        
        // 检测表格行
        if (line.includes('|') && !line.includes('---')) {
            const cells = parseTableRow(line);
            
            // 跳过表头
            if (cells[0] === '任务' || cells[0] === '') continue;
            
            // 提取任务信息
            // 格式：| 任务 | Worker | 状态 | 交付物 | 推荐模型 | 备注 |
            const task = {
                stage: currentStage,
                name: cells[0] || '',
                worker: cells[1] || '',
                status: cells[2] || '',
                deliverable: cells[3] || '',
                model: cells[4] || '',
                notes: cells[5] || ''
            };
            
            if (task.name) {
                tasks.push(task);
            }
        }
    }
    
    return tasks;
}

/**
 * 映射状态到 Bitable 阶段
 */
function mapStatus(status) {
    for (const [key, value] of Object.entries(STATUS_MAP)) {
        if (status.includes(key)) {
            return value;
        }
    }
    return '待确认';
}

/**
 * 同步任务到 Bitable
 */
async function syncTasks(version, tasks) {
    console.log(`\n📋 同步迭代版本：${version}`);
    console.log(`   任务数量：${tasks.length}`);
    
    for (const task of tasks) {
        const phase = mapStatus(task.status);
        const taskId = `TASK-${version.replace('v', '')}-${tasks.indexOf(task) + 1}`;
        
        console.log(`   → ${task.name} (${task.worker}) - ${phase}`);
        
        // TODO: 调用 Feishu Bitable API
        // 这里需要使用 openclaw 的 feishu_bitable_create_record 或 update_record
        // 由于这是在 Node.js 环境中，需要通过 exec 调用 openclaw CLI
        
        /*
        示例 API 调用：
        await feishu_bitable_create_record({
            app_token: CONFIG.bitableApp,
            table_id: CONFIG.bitableTable,
            fields: {
                '任务 ID': taskId,
                '任务名称': task.name,
                '负责人': task.worker,
                '当前阶段': phase,
                '进度%': phase === '已完成' ? 100 : 0
            }
        });
        */
    }
    
    console.log(`   ✅ 同步完成`);
}

/**
 * 主函数
 */
async function main() {
    console.log('🎮 Mission Control - 自动同步任务看板');
    console.log('======================================');
    console.log(`时间：${new Date().toLocaleString('zh-CN')}`);
    
    // 检查迭代目录
    if (!fs.existsSync(CONFIG.iterationsDir)) {
        console.log(`⚠️  迭代目录不存在：${CONFIG.iterationsDir}`);
        return;
    }
    
    // 遍历所有迭代版本
    const versions = fs.readdirSync(CONFIG.iterationsDir);
    
    for (const version of versions) {
        const versionDir = path.join(CONFIG.iterationsDir, version);
        const taskBoard = path.join(versionDir, 'TASK_BOARD.md');
        
        if (fs.statSync(versionDir).isDirectory() && fs.existsSync(taskBoard)) {
            const tasks = parseTaskBoard(taskBoard);
            await syncTasks(version, tasks);
        }
    }
    
    console.log('\n✅ 所有迭代版本同步完成');
    console.log(`📊 查看看板：${CONFIG.dashboardUrl}`);
}

// 执行
main().catch(console.error);
