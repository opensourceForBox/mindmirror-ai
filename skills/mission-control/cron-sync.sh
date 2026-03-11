#!/bin/bash
# Mission Control - 定时同步任务
# 添加到 crontab: */5 * * * * /root/.openclaw/workspace/skills/mission-control/cron-sync.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/cron.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🎮 Mission Control - 定时同步开始"

# 1. 同步任务看板
log "📋 同步任务看板..."
cd "$SCRIPT_DIR" && node sync-task-board.js >> "$LOG_FILE" 2>&1

# 2. 监控智能体状态
log "📡 监控智能体状态..."
cd "$SCRIPT_DIR" && node monitor-agents.js >> "$LOG_FILE" 2>&1

log "✅ 定时同步完成"
log ""
