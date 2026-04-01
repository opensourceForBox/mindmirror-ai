#!/bin/bash
# 开发者技术雷达 - 只抓取对开发效率有价值的内容
# 过滤商业噪音，聚焦实战技术

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/dev_radar.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🎯 开发者技术雷达启动"

# 使用 sessions_spawn 创建临时会话执行任务
openclaw sessions_spawn --runtime=subagent --mode=run --task="
你是一个资深技术专家，请帮我筛选真正对开发者有价值的技术内容。

## 任务

1. 使用 web_fetch 抓取 https://www.infoq.cn/ (maxChars=15000, extractMode=text)

2. **严格过滤**，只保留对开发者真正有价值的内容：

   ✅ **保留**（高价值）：
   - 实战技术：新框架/工具、性能优化、最佳实践、代码案例
   - 效率工具：CLI 工具、IDE 插件、自动化、工作流优化
   - 技术深度：源码分析、架构设计、技术选型、踩坑总结
   - 趋势技术：新语言特性、新兴框架、潜力开源项目

   ❌ **过滤**（噪音）：
   - 高管变动、融资新闻
   - 大会预告/回顾、会议报告
   - 纯产品发布（无技术细节）
   - 市场分析、商业合作

3. 对每篇高价值文章，生成**开发者视角**的摘要：

【技术类别】标题

核心价值：一句话说明能解决什么开发问题

关键要点：
• 要点 1（含具体技术/工具/数据）
• 要点 2
• 要点 3

适用场景：什么开发场景用得上

行动建议：值得深入/可以了解/跳过

4. 使用 feishu_bitable_create_record 存入表格：
   - app_token: NrxNbCA9qaFkjfsx7VRcGTnNnBe
   - table_id: tbllP3KSxWDsnVem
   - 字段：文章标题、来源、原文链接、核心摘要（用上面格式）、状态 (新)、标签、重要程度、抓取时间

5. 只通知真正值得关注的文章（含实战代码/新工具/效率提升）

## 输出要求

最后给我一个汇总：
- 抓取总数
- 过滤后高价值数量
- 每篇的摘要（按上面格式）
- 推荐优先阅读哪篇
" 2>&1 | tee -a "$LOG_FILE"

log "✅ 完成"
