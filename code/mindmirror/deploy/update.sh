#!/bin/bash
# MindMirror AI 快速更新脚本
# 使用方法: cd /opt/mindmirror-ai/code/mindmirror && bash deploy/update.sh

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

COMPOSE_FILE="deploy/docker-compose.prod.yml"
MAX_RETRIES=30

echo "=========================================="
echo "  MindMirror AI 快速更新"
echo "=========================================="

# 确保在正确的目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "工作目录: $(pwd)"

# Step 1: 拉取最新代码
echo -e "${GREEN}[1/5] 拉取最新代码...${NC}"
git pull origin main
echo ""

# Step 2: 重新构建前端（如果 package.json 有变化）
echo -e "${GREEN}[2/5] 检查前端是否需要重新构建...${NC}"
if [ -f "frontend/package.json" ]; then
    # 检查 package.json 是否有变化
    if git diff --name-only HEAD@{1} HEAD 2>/dev/null | grep -q "frontend/package.json\|frontend/src/\|frontend/index.html\|frontend/tailwind"; then
        echo "前端文件有变化，重新构建..."
        cd frontend
        npm install --registry=https://registry.npmmirror.com 2>&1 | tail -3
        npm run build 2>&1 | tail -3
        cd ..
        echo -e "${GREEN}前端构建完成${NC}"
    else
        echo "前端无变化，跳过构建"
    fi
else
    echo -e "${YELLOW}前端目录不存在，跳过${NC}"
fi
echo ""

# Step 3: 重新构建 Docker 镜像
echo -e "${GREEN}[3/5] 重新构建 Docker 镜像...${NC}"
docker-compose -f $COMPOSE_FILE build
echo ""

# Step 4: 重启服务（尽量减少停机时间）
echo -e "${GREEN}[4/5] 重启服务...${NC}"
docker-compose -f $COMPOSE_FILE up -d --force-recreate
echo ""

# Step 5: 等待服务就绪
echo -e "${GREEN}[5/5] 等待服务就绪...${NC}"
sleep 5

RETRY=0
while [ $RETRY -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}服务正常!${NC}"
        break
    fi
    RETRY=$((RETRY+1))
    echo "  等待中... ($RETRY/$MAX_RETRIES)"
    sleep 3
done

if [ $RETRY -eq $MAX_RETRIES ]; then
    echo -e "${RED}服务启动超时，请检查日志:${NC}"
    echo "  docker-compose -f $COMPOSE_FILE logs --tail=50"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}  更新完成！${NC}"
echo "=========================================="
echo ""
echo "服务状态:"
docker-compose -f $COMPOSE_FILE ps
echo ""
echo "访问地址: http://43.156.249.166"
echo ""
