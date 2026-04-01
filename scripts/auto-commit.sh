#!/bin/bash
# MindMirror AI - 自动提交脚本
# 用法：./scripts/auto-commit.sh [commit_message]

set -e

WORKSPACE="/root/.openclaw/workspace"
cd "$WORKSPACE"

# 配置
GIT_USER_NAME="MindMirror AI Bot"
GIT_USER_EMAIL="mindmirror-ai@localhost"
COMMIT_MESSAGE="${1:-auto: $(date '+%Y-%m-%d %H:%M:%S') - 自动提交}"

# 检查是否有变更
if [ -z "$(git status --porcelain)" ]; then
    echo "✅ 没有变更，跳过提交"
    exit 0
fi

# 配置 Git 用户
git config user.name "$GIT_USER_NAME"
git config user.email "$GIT_USER_EMAIL"

# 添加所有变更
echo "📦 添加文件变更..."
git add -A

# 提交
echo "💾 提交变更..."
git commit -m "$COMMIT_MESSAGE"

# 推送
echo "🚀 推送到 GitHub..."
git push origin main

echo "✅ 自动提交完成！"
echo "提交信息：$COMMIT_MESSAGE"
