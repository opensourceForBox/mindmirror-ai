#!/bin/bash
# GitHub Trending 每日推送脚本
# 每天早上 8 点执行，推送 GitHub Trending 到飞书

set -e

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/github_trending.log"
USER_ID="ou_1d9442018ffd3eefc8f4baac97235f6c"
BITABLE_APP="VMbQbI8kna8J98sFGEOc0864nvf"
BITABLE_TABLE="tbl8ZLGKBR0sE5M0"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🚀 GitHub Trending 每日推送启动"

# 使用 openclaw agent 来获取 GitHub Trending
log "📈 获取 GitHub Trending..."

# 创建一个临时任务文件
TASK_FILE="$WORKSPACE/data/trending_task.txt"
mkdir -p "$WORKSPACE/data"

cat > "$TASK_FILE" << 'EOF'
你是一个技术资讯助手。请获取 GitHub 今日热门项目（前 10 个），并按以下格式输出：

📈 GitHub Trending 每日播报
📅 日期

1. 仓库名 ⭐ Star 数 (+今日增长) - 语言
   描述

2. ...

最多列出前 10 个项目。如果无法获取实时数据，请说明原因并提供 GitHub Trending 链接。
EOF

# 使用 openclaw agent 执行任务
MESSAGE=$(openclaw agent --message "获取 GitHub 今日热门项目（前 10 个），按格式输出榜单" 2>/dev/null || echo "⚠️ 暂时无法获取 GitHub Trending 数据")

# 构建推送消息
PUSH_MSG="📈 GitHub Trending 每日播报
📅 $(date '+%Y-%m-%d %A')

$MESSAGE

🔗 查看完整榜单：https://github.com/trending

_每天早上 8 点自动推送_"

# 发送飞书消息
openclaw message send --target "user:$USER_ID" --message "$PUSH_MSG" 2>/dev/null && \
    log "✅ 推送成功" || \
    log "⚠️ 推送失败"

log "✅ 任务完成"
