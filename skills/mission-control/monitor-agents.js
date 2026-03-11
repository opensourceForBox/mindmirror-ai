#!/usr/bin/env node
/**
 * Mission Control - 智能体状态监控
 * 
 * 功能：
 * 1. 获取当前活跃会话 (sessions_list)
 * 2. 解析智能体状态
 * 3. 同步到 Bitable 智能体状态表
 * 
 * 使用方法：
 * node monitor-agents.js
 */

const CONFIG = {
    bitableApp: 'E8D2bR0Bca7QhssmTQwcNax2nCf',
    bitableTable: 'tblG4SZePasROVWp',
    dashboardUrl: 'https://feishu.cn/docx/GNZbdHwL6orkTNx1QRCczCljnnT'
};

// 智能体映射
const AGENTS = {
    'manager': { name: 'Manager (项目经理)', outputDir: 'iterations/[版本]/TASKS/' },
    'product-manager': { name: 'Product Manager (架构师)', outputDir: 'prd/[项目名]/' },
    'ui-designer': { name: 'UI Designer', outputDir: 'designs/[项目名]/' },
    'developer': { name: 'Developer (工匠)', outputDir: 'code/[项目名]/' },
    'tester': { name: 'Tester (测试工程师)', outputDir: 'test-reports/[项目名]/' }
};

/**
 * 模拟 sessions_list 输出
 * 实际使用时需要调用 openclaw sessions list 命令
 */
async function getSessions() {
    // TODO: 实际调用 openclaw sessions list
    // 这里使用模拟数据
    return [
        { sessionKey: 'session-001', label: 'manager', active: true, lastActivity: Date.now() },
        { sessionKey: 'session-002', label: 'product-manager', active: false, lastActivity: Date.now() - 3600000 },
        { sessionKey: 'session-003', label: 'developer', active: false, lastActivity: Date.now() - 7200000 },
    ];
}

/**
 * 判断智能体状态
 */
function getStatus(agentKey, sessions) {
    const session = sessions.find(s => s.label === agentKey);
    
    if (!session) return '空闲';
    if (session.active) return '在线';
    
    const minutesSinceActive = (Date.now() - session.lastActivity) / 60000;
    if (minutesSinceActive < 5) return '忙碌';
    if (minutesSinceActive < 30) return '空闲';
    return '离线';
}

/**
 * 获取当前任务
 */
function getCurrentTask(agentKey, sessions) {
    const session = sessions.find(s => s.label === agentKey);
    
    if (!session) return '等待 Manager 派发';
    if (session.active) return '处理任务中...';
    
    const minutesSinceActive = (Date.now() - session.lastActivity) / 60000;
    if (minutesSinceActive < 5) return '刚刚完成任务';
    return '等待 Manager 派发';
}

/**
 * 同步智能体状态到 Bitable
 */
async function syncAgentStatus(agentKey, status, currentTask) {
    const agent = AGENTS[agentKey];
    if (!agent) return;
    
    console.log(`  → ${agent.name}: ${status} - ${currentTask}`);
    
    // TODO: 调用 feishu_bitable_update_record
    /*
    await feishu_bitable_update_record({
        app_token: CONFIG.bitableApp,
        table_id: CONFIG.bitableTable,
        record_id: getRecordId(agentKey), // 需要预先存储 record_id 映射
        fields: {
            '状态': status,
            '当前任务': currentTask,
            '最后活跃时间': Date.now()
        }
    });
    */
}

/**
 * 主函数
 */
async function main() {
    console.log('🎮 Mission Control - 智能体状态监控');
    console.log('==================================');
    console.log(`时间：${new Date().toLocaleString('zh-CN')}`);
    console.log('');
    
    // 获取会话列表
    console.log('📡 获取智能体会话状态...');
    const sessions = await getSessions();
    console.log(`   找到 ${sessions.length} 个会话`);
    console.log('');
    
    // 同步每个智能体状态
    console.log('🔄 同步智能体状态到 Bitable...');
    for (const agentKey of Object.keys(AGENTS)) {
        const status = getStatus(agentKey, sessions);
        const currentTask = getCurrentTask(agentKey, sessions);
        await syncAgentStatus(agentKey, status, currentTask);
    }
    
    console.log('');
    console.log('✅ 智能体状态同步完成');
    console.log(`📊 查看看板：${CONFIG.dashboardUrl}`);
}

// 执行
main().catch(console.error);
