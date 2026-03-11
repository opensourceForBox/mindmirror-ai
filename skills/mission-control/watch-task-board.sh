#!/bin/bash
# Mission Control - 文件监听器
# 监听 iterations/*/TASK_BOARD.md 文件变化并自动同步

set -e

ITERATIONS_DIR="/root/.openclaw/workspace/iterations"
SYNC_SCRIPT="/root/.openclaw/workspace/skills/mission-control/sync-task-board.sh"
LOCK_FILE="/tmp/mission-control-sync.lock"

echo "🎮 Mission Control - 文件监听器启动"
echo "===================================="
echo "监听目录：$ITERATIONS_DIR"
echo "同步脚本：$SYNC_SCRIPT"
echo ""

# 检查 inotifywait 是否可用
if ! command -v inotifywait &> /dev/null; then
    echo "⚠️  inotifywait 未安装，使用轮询模式"
    echo "安装方法：yum install inotify-tools (CentOS/RHEL) 或 apt install inotify-tools (Debian/Ubuntu)"
    echo ""
    
    # 轮询模式（备用方案）
    LAST_SYNC=""
    while true; do
        CURRENT_SYNC=$(find "$ITERATIONS_DIR" -name "TASK_BOARD.md" -exec stat -c %Y {} \; 2>/dev/null | sort -r | head -1)
        
        if [ "$CURRENT_SYNC" != "$LAST_SYNC" ]; then
            echo "📄 检测到 TASK_BOARD.md 变化，触发同步..."
            bash "$SYNC_SCRIPT"
            LAST_SYNC="$CURRENT_SYNC"
        fi
        
        sleep 30  # 每 30 秒检查一次
    done
else
    # inotify 模式（实时监听）
    echo "✅ 使用 inotify 实时监听模式"
    echo ""
    
    # 创建监听列表
    WATCH_DIRS=""
    for version_dir in "$ITERATIONS_DIR"/*/; do
        if [ -d "$version_dir" ]; then
            WATCH_DIRS="$WATCH_DIRS $version_dir"
        fi
    done
    
    # 开始监听
    inotifywait -m -r -e modify,create,move \
        --format '%w%f %e' \
        $WATCH_DIRS 2>/dev/null | \
    while read file event; do
        if [[ "$file" == *"TASK_BOARD.md"* ]]; then
            echo "📄 检测到文件变化：$file ($event)"
            
            # 防止并发执行
            if [ -f "$LOCK_FILE" ]; then
                echo "⚠️  同步正在进行中，跳过"
                continue
            fi
            
            touch "$LOCK_FILE"
            bash "$SYNC_SCRIPT"
            rm -f "$LOCK_FILE"
        fi
    done
fi
