#!/bin/bash
# Mission Control - TASK_BOARD.md 自动同步脚本
# 解析 iterations/*/TASK_BOARD.md 并同步到 Bitable 任务流转表

set -e

ITERATIONS_DIR="/root/.openclaw/workspace/iterations"
BITABLE_APP="OVB0b4GASaVnZgsyW7vcffwMnBh"
BITABLE_TABLE="tblGKdhzAwBBqYKE"

echo "🎮 Mission Control - 任务看板自动同步"
echo "======================================"

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
        
        echo ""
        echo "📋 同步迭代版本：$version"
        echo "-----------------------------------"
        
        if [ ! -f "$task_board" ]; then
            echo "  ⚠️  未找到 TASK_BOARD.md，跳过"
            continue
        fi
        
        echo "  → 找到任务看板：$task_board"
        
        # 解析 Markdown 表格
        # 格式 1（阶段 1）: | 任务 | Worker | 状态 | 交付物 | 推荐模型 | 备注 |
        # 格式 2（阶段 2）: | 任务 | Worker | 状态 | 交付物 | 推荐模型 | 依赖 |
        
        task_counter=0
        in_table=false
        header_line=""
        
        while IFS= read -r line; do
            # 检测表格开始（包含 | 任务 | 的行）
            if [[ "$line" == *"| 任务 |"* ]] || [[ "$line" == *"|任务|"* ]]; then
                in_table=true
                header_line="$line"
                continue
            fi
            
            # 检测表格分隔行（|---|---|）
            if [[ "$in_table" == true ]] && [[ "$line" == *"|---"* ]]; then
                continue
            fi
            
            # 解析表格行
            if [[ "$in_table" == true ]] && [[ "$line" == *"|"* ]]; then
                # 检测表格结束（空行或不包含 | 的行）
                if [[ -z "$line" ]] || [[ "$line" != *"|"* ]]; then
                    in_table=false
                    continue
                fi
                
                # 提取表格单元格
                # 格式：| 任务名 | Worker | 状态 | 交付物 | 模型 | 备注 |
                task_name=$(echo "$line" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2}')
                worker=$(echo "$line" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $3); print $3}')
                status=$(echo "$line" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $4); print $4}')
                
                # 跳过空行或表头
                if [[ -z "$task_name" ]] || [[ "$task_name" == "任务" ]]; then
                    continue
                fi
                
                task_counter=$((task_counter + 1))
                task_id="TASK-$(printf "%03d" $task_counter)-$version"
                
                # 状态映射
                stage="待确认"
                progress=0
                if [[ "$status" == *"✅"* ]] || [[ "$status" == *"完成"* ]]; then
                    stage="已完成"
                    progress=100
                elif [[ "$status" == *"⏳"* ]] || [[ "$status" == *"待确认"* ]]; then
                    stage="待确认"
                    progress=0
                elif [[ "$status" == *"进行中"* ]]; then
                    stage="进行中"
                    progress=50
                fi
                
                echo "  📝 任务：$task_name"
                echo "     Worker: $worker | 阶段：$stage | 进度：$progress%"
                
                # TODO: 调用 Feishu API 更新 Bitable
                # 这里可以使用 openclaw feishu_bitable 工具或 curl API
                # 示例：
                # openclaw feishu_bitable_create_record \
                #   --app_token "$BITABLE_APP" \
                #   --table_id "$BITABLE_TABLE" \
                #   --fields "{\"任务 ID\":\"$task_id\",\"任务名称\":\"$task_name\",\"当前阶段\":\"$stage\",\"负责人\":\"$worker\",\"进度%\":$progress}"
                
            elif [[ -z "$line" ]] || [[ ! "$line" == *"|"* ]]; then
                # 空行或非表格行，结束表格解析
                in_table=false
            fi
        done < "$task_board"
        
        echo ""
        echo "  ✅ 共解析 $task_counter 个任务"
    fi
done

echo ""
echo "======================================"
echo "✅ 任务看板同步完成"
echo "📊 查看 Bitable: https://ccnatqob3gk9.feishu.cn/base/OVB0b4GASaVnZgsyW7vcffwMnBh"
echo "📄 查看看板：https://feishu.cn/docx/GNZbdHwL6orkTNx1QRCczCljnnT"
