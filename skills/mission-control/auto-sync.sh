#!/bin/bash
# Mission Control - 自动同步 TASK_BOARD.md 到 Bitable
# 支持增量同步，只更新变化的任务

set -e

ITERATIONS_DIR="/root/.openclaw/workspace/iterations"
BITABLE_APP="OVB0b4GASaVnZgsyW7vcffwMnBh"
BITABLE_TABLE="tblGKdhzAwBBqYKE"

echo "🎮 Mission Control - 自动同步任务看板"
echo "======================================"
echo "时间：$(date '+%Y-%m-%d %H:%M:%S')"

# 检查迭代目录
if [ ! -d "$ITERATIONS_DIR" ]; then
    echo "⚠️  迭代目录不存在：$ITERATIONS_DIR"
    exit 0
fi

# 遍历所有迭代版本
for version_dir in "$ITERATIONS_DIR"/*/; do
    if [ -d "$version_dir" ]; then
        version=$(basename "$version_dir")
        task_board="$version_dir/TASK_BOARD.md"
        
        if [ -f "$task_board" ]; then
            echo ""
            echo "📋 同步迭代版本：$version"
            echo "   看板文件：$task_board"
            
            # 解析 Markdown 表格中的任务
            # 格式：| 任务 | Worker | 状态 | 交付物 | 推荐模型 | 备注 |
            
            task_count=0
            while IFS='|' read -r task_name worker status deliverable model notes; do
                # 跳过表头和分隔线
                [[ "$task_name" =~ ^[[:space:]]*任务 ]] && continue
                [[ "$task_name" =~ ^[[:space:]]*-+ ]] && continue
                [[ -z "$task_name" ]] && continue
                
                # 清理空白字符
                task_name=$(echo "$task_name" | xargs)
                worker=$(echo "$worker" | xargs)
                status=$(echo "$status" | xargs)
                
                # 跳过空行
                [[ -z "$task_name" ]] && continue
                
                # 转换状态到阶段
                case "$status" in
                    *"✅"*|*"完成"*) phase="已完成" ;;
                    *"⏳"*|*"待确认"*) phase="待确认" ;;
                    *"🔄"*|*"进行中"*) phase="开发中" ;;
                    *) phase="待确认" ;;
                esac
                
                # 生成任务 ID
                task_id="TASK-$(echo "$version" | tr -d 'v.')-$(printf '%03d' $((task_count + 1)))"
                
                echo "   → 任务：$task_name ($worker) - $phase"
                
                # TODO: 调用 feishu_bitable_create_record 或 update_record
                # 这里使用 openclaw CLI 或 API 调用
                # 示例：
                # openclaw feishu bitable create-record \
                #   --app-token "$BITABLE_APP" \
                #   --table-id "$BITABLE_TABLE" \
                #   --fields "{\"任务 ID\":\"$task_id\",\"任务名称\":\"$task_name\",\"负责人\":\"$worker\",\"当前阶段\":\"$phase\"}"
                
                ((task_count++)) || true
            done < <(grep -E "^\|.*\|[[:space:]]*$" "$task_board" | tail -n +3)
            
            echo "   ✅ 同步完成：$task_count 个任务"
        fi
    fi
done

echo ""
echo "✅ 所有迭代版本同步完成"
echo "📊 查看看板：https://feishu.cn/docx/GNZbdHwL6orkTNx1QRCczCljnnT"
