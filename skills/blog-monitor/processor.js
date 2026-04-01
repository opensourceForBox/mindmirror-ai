#!/usr/bin/env node
/**
 * 博客监控处理器 - Node.js 版本
 * 创建飞书记录并发送通知
 */

const { feishu_bitable_create_record, message } = require('openclaw/tools');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// 配置
const CONFIG = {
    bitable_app_token: "NrxNbCA9qaFkjfsx7VRcGTnNnBe",
    bitable_table_id: "tbllP3KSxWDsnVem",
    state_file: "/root/.openclaw/workspace/data/blog_monitor_state.json",
    user_id: "ou_1d9442018ffd3eefc8f4baac97235f6c"
};

function loadState() {
    if (fs.existsSync(CONFIG.state_file)) {
        return JSON.parse(fs.readFileSync(CONFIG.state_file, 'utf-8'));
    }
    return { articles: {} };
}

function saveState(state) {
    const dir = path.dirname(CONFIG.state_file);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(CONFIG.state_file, JSON.stringify(state, null, 2));
}

async function createBitableRecord(article) {
    const fields = {
        "待读文章": article.title,
        "文章标题": article.title,
        "来源": article.source,
        "原文链接": { link: article.url },
        "核心摘要": `自动抓取的技术文章 - ${article.source}`,
        "状态": "新",
        "标签": article.tags || ["技术"],
        "重要程度": article.is_important ? "重要" : "普通",
        "抓取时间": Date.now(),
        "发布时间": Date.now()
    };
    
    const result = await feishu_bitable_create_record({
        action: "create_record",
        app_token: CONFIG.bitable_app_token,
        table_id: CONFIG.bitable_table_id,
        fields: fields
    });
    
    if (result && result.record) {
        return { success: true, record_id: result.record.record_id };
    }
    return { success: false, error: JSON.stringify(result) };
}

async function sendNotification(newArticles, importantArticles) {
    if (!newArticles.length) return false;
    
    let importantText = "";
    if (importantArticles.length) {
        importantText = "\n🔥 **重要文章**:\n" + importantArticles.slice(0, 5)
            .map(a => `• ${a.title.slice(0, 50)}`).join('\n');
    }
    
    const normalArticles = newArticles.filter(a => !importantArticles.includes(a));
    let normalText = "";
    if (normalArticles.length) {
        normalText = "\n📰 **普通文章**:\n" + normalArticles.slice(0, 10)
            .map(a => `• ${a.title.slice(0, 50)}`).join('\n');
    }
    
    const msg = `📊 博客监控报告

${importantText}${normalText}

✅ 本次新增：${newArticles.length} 篇
🔥 重要文章：${importantArticles.length} 篇
⏰ 抓取时间：${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}

[查看详细多维表格](https://bytedance.feishu.cn/base/${CONFIG.bitable_app_token})
`;
    
    const result = await message({
        action: "send",
        target: `user:${CONFIG.user_id}`,
        message: msg
    });
    
    return true;
}

async function main() {
    const args = process.argv.slice(2);
    if (args.length < 1) {
        console.log("⚠️ 没有文章数据");
        process.exit(1);
    }
    
    const articles = JSON.parse(args[0]);
    console.log(`📄 处理 ${articles.length} 篇文章`);
    
    const state = loadState();
    const newArticles = [];
    const importantArticles = [];
    
    for (const article of articles) {
        const articleId = crypto.createHash('md5').update(article.url).digest('hex');
        
        if (state.articles[articleId]) {
            console.log(`  ⏭️  已存在：${article.title.slice(0, 30)}...`);
            continue;
        }
        
        const result = await createBitableRecord(article);
        
        if (result.success) {
            console.log(`  ✅ 创建成功：${article.title.slice(0, 30)}... (${result.record_id})`);
            state.articles[articleId] = {
                url: article.url,
                title: article.title,
                created_at: new Date().toISOString(),
                record_id: result.record_id
            };
            newArticles.push(article);
            if (article.is_important) importantArticles.push(article);
        } else {
            console.log(`  ❌ 创建失败：${article.title.slice(0, 30)}... - ${result.error}`);
        }
    }
    
    saveState(state);
    
    if (newArticles.length) {
        console.log("📤 发送通知...");
        await sendNotification(newArticles, importantArticles);
    }
    
    console.log(`✅ 处理完成 - 新增 ${newArticles.length} 篇，重要 ${importantArticles.length} 篇，累计 ${Object.keys(state.articles).length} 篇`);
}

main().catch(err => {
    console.error("错误:", err.message);
    process.exit(1);
});
