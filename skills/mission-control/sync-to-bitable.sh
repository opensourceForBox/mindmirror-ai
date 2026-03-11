#!/bin/bash
# Mission Control - 同步任务到 Bitable (实际 API 调用版本)
# 使用 openclaw feishu_bitable_* 工具

set -e

BITABLE_APP="OVB0b4GASaVnZgsyW7vcffwMnBh"
BITABLE_TABLE="tblGKdhzAwBBqYKE"

echo "🎮 Mission Control - 同步任务到 Bitable"
echo "======================================="

# 任务数据（从 TASK_BOARD.md 解析）
# 格式：任务 ID|任务名称|负责人|阶段|进度

TASKS=(
    "TASK-101|录像诊断功能 - 架构设计|product-manager|已完成|100"
    "TASK-102|录像诊断功能 - UI 设计|ui-designer|待确认|0"
    "TASK-103|录像诊断功能 - 后端 API|developer|待确认|0"
    "TASK-104|录像诊断功能 - 测试用例|tester|待确认|0"
)

for task_data in "${TASKS[@]}"; do
    IFS='|' read -r task_id task_name worker phase progress <<< "$task_data"
    
    echo "→ 创建任务：$task_name ($worker)"
    
    # 使用 openclaw 工具创建记录
    # 注意：这里需要通过 openclaw 的会话系统调用 feishu_bitable_create_record
    # 实际使用时，在 Manager 技能中直接调用 feishu_bitable_create_record 工具
    
    cat <<EOF
[待调用]
feishu_bitable_create_record:
  app_token: $BITABLE_APP
  table_id: $BITABLE_TABLE
  fields:
    任务 ID: $task_id
    任务名称: $task_name
    负责人: $worker
    当前阶段: $phase
    进度%: $progress
EOF
    echo ""
done

echo "✅ 同步指令生成完成"
echo ""
echo "📝 使用方法："
echo "在 Manager 技能中，更新 TASK_BOARD.md 后调用："
echo ""
echo "  feishu_bitable_create_record("
echo "    app_token='OVB0b4GASaVnZgsyW7vcffwMnBh',"
echo "    table_id='tblGKdhzAwBBqYKE',"
echo "    fields={'任务 ID': 'TASK-xxx', ...}"
echo "  )"
