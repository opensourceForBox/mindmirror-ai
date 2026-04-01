#!/bin/bash
# 开发者技术雷达 - 清理表格空白行并重新创建
# 用于清理飞书多维表格创建时自动生成的空白记录

APP_TOKEN="VZNcbAXqXaMO0lsSsGgc7fEwnwe"
TABLE_ID="tblCCmA8F8sVIrFe"

echo "📊 当前表格记录数："
openclaw feishu_bitable_list_records --app-token $APP_TOKEN --table-id $TABLE_ID --page-size 1 | grep -E '"total"|"id"'

echo ""
echo "⚠️  飞书多维表格的空白行无法通过 API 删除"
echo "✅  建议方案：在定时任务中先查询现有记录，避免重复写入"
echo ""
echo "📌 表格链接：https://ccnatqob3gk9.feishu.cn/base/$APP_TOKEN"
