#!/bin/bash
# MindMirror AI 一键部署脚本
# 使用方法：
#   1. SSH 到服务器: ssh root@43.156.249.166
#   2. 下载此脚本或将项目 clone 到服务器
#   3. 执行: bash deploy/deploy.sh

set -e

echo "=========================================="
echo "  MindMirror AI 一键部署"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 配置
APP_DIR="/opt/mindmirror-ai"
REPO_URL="https://github.com/opensourceForBox/mindmirror-ai.git"
COMPOSE_FILE="deploy/docker-compose.prod.yml"

# 错误处理函数
error_exit() {
    echo -e "${RED}[错误] $1${NC}"
    exit 1
}

# 成功提示函数
success_msg() {
    echo -e "${GREEN}[成功] $1${NC}"
}

# ========================================
# Step 1: 系统依赖安装
# ========================================
echo -e "${GREEN}[1/8] 安装系统依赖...${NC}"

# 检测包管理器
if command -v apt-get &> /dev/null; then
    apt-get update -qq
    apt-get install -y -qq docker.io docker-compose git curl > /dev/null 2>&1
elif command -v yum &> /dev/null; then
    yum install -y -q docker docker-compose git curl > /dev/null 2>&1
else
    error_exit "不支持的包管理器，请手动安装 Docker、Docker Compose、Git、Curl"
fi

# 启动 Docker
systemctl enable docker 2>/dev/null || true
systemctl start docker 2>/dev/null || true

# 配置 Docker 国内镜像加速
if [ ! -f /etc/docker/daemon.json ]; then
    echo -e "${YELLOW}配置 Docker 国内镜像加速...${NC}"
    mkdir -p /etc/docker
    cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.1panel.live",
    "https://docker.m.daocloud.io",
    "https://hub.rat.dev"
  ]
}
EOF
    systemctl daemon-reload
    systemctl restart docker
    success_msg "Docker 镜像加速已配置"
fi

success_msg "系统依赖安装完成"

# ========================================
# Step 2: 克隆/更新代码
# ========================================
echo -e "${GREEN}[2/8] 获取代码...${NC}"
if [ -d "$APP_DIR" ]; then
    echo "目录已存在，更新代码..."
    cd $APP_DIR
    git pull origin main || true
else
    git clone $REPO_URL $APP_DIR
fi
cd $APP_DIR/code/mindmirror

success_msg "代码获取完成"

# ========================================
# Step 3: 环境配置
# ========================================
echo -e "${GREEN}[3/8] 配置环境变量...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env

    # 适配 Docker 网络：将 localhost 替换为容器服务名
    sed -i 's/QDRANT_HOST=localhost/QDRANT_HOST=qdrant/' .env
    sed -i 's|REDIS_URL=redis://localhost:6379|REDIS_URL=redis://redis:6379|' .env

    echo -e "${YELLOW}请编辑 .env 文件配置 ZHIPU_API_KEY:${NC}"
    echo -e "${YELLOW}  nano $APP_DIR/code/mindmirror/.env${NC}"
    echo ""
    read -p "请输入你的智谱 API Key (或回车跳过): " ZHIPU_KEY
    if [ -n "$ZHIPU_KEY" ]; then
        sed -i "s/your_zhipu_api_key_here/$ZHIPU_KEY/" .env
        success_msg "API Key 已配置"
    else
        echo -e "${YELLOW}已跳过，请稍后手动配置 API Key${NC}"
    fi
else
    echo ".env 已存在，跳过"
    # 确保已有的 .env 也适配 Docker 网络
    if grep -q "QDRANT_HOST=localhost" .env; then
        sed -i 's/QDRANT_HOST=localhost/QDRANT_HOST=qdrant/' .env
        echo "已更新 QDRANT_HOST 为 Docker 服务名"
    fi
    if grep -q "redis://localhost:6379" .env; then
        sed -i 's|redis://localhost:6379|redis://redis:6379|' .env
        echo "已更新 REDIS_URL 为 Docker 服务名"
    fi
fi

success_msg "环境变量配置完成"

# ========================================
# Step 4: 构建前端
# ========================================
echo -e "${GREEN}[4/8] 构建前端...${NC}"

# 检查是否已有构建产物
if [ -d "frontend/dist" ] && [ -f "frontend/dist/index.html" ]; then
    echo "前端已构建，跳过"
else
    # 检查 Node.js 是否安装
    if ! command -v node &> /dev/null; then
        echo "安装 Node.js..."
        if command -v apt-get &> /dev/null; then
            curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
            apt-get install -y -qq nodejs > /dev/null 2>&1
        elif command -v yum &> /dev/null; then
            curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
            yum install -y -q nodejs > /dev/null 2>&1
        fi
    fi

    if command -v node &> /dev/null; then
        echo "构建前端静态文件..."
        cd frontend
        npm install --registry=https://registry.npmmirror.com 2>&1 | tail -5
        npm run build 2>&1 | tail -5
        cd ..
        if [ -f "frontend/dist/index.html" ]; then
            success_msg "前端构建完成"
        else
            echo -e "${YELLOW}前端构建可能失败，将使用 Nginx 默认页面${NC}"
        fi
    else
        echo -e "${YELLOW}Node.js 安装失败，跳过前端构建${NC}"
        echo -e "${YELLOW}请手动执行: cd frontend && npm install && npm run build${NC}"
    fi
fi

# ========================================
# Step 5: 构建 Docker 镜像
# ========================================
echo -e "${GREEN}[5/8] 构建 Docker 镜像...${NC}"
docker-compose -f $COMPOSE_FILE build --no-cache
success_msg "Docker 镜像构建完成"

# ========================================
# Step 6: 启动服务
# ========================================
echo -e "${GREEN}[6/8] 启动服务...${NC}"
docker-compose -f $COMPOSE_FILE down 2>/dev/null || true
docker-compose -f $COMPOSE_FILE up -d
success_msg "服务已启动"

# ========================================
# Step 7: 等待服务就绪
# ========================================
echo -e "${GREEN}[7/8] 等待服务启动...${NC}"
sleep 10

# 健康检查
MAX_RETRIES=30
RETRY=0
while [ $RETRY -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        success_msg "后端服务就绪！"
        break
    fi
    RETRY=$((RETRY+1))
    echo "  等待中... ($RETRY/$MAX_RETRIES)"
    sleep 3
done

if [ $RETRY -eq $MAX_RETRIES ]; then
    echo -e "${RED}服务启动超时，请检查日志:${NC}"
    echo "  docker-compose -f $COMPOSE_FILE logs"
    exit 1
fi

# ========================================
# Step 8: 配置防火墙
# ========================================
echo -e "${GREEN}[8/8] 配置防火墙...${NC}"
# 开放必要端口（仅 80 和 443 对外，8000 仅内部访问）
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp 2>/dev/null || true
    ufw allow 443/tcp 2>/dev/null || true
    ufw allow 22/tcp 2>/dev/null || true
    echo "UFW 防火墙已配置"
elif command -v iptables &> /dev/null; then
    iptables -A INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null || true
    iptables -A INPUT -p tcp --dport 443 -j ACCEPT 2>/dev/null || true
    echo "iptables 防火墙已配置"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}  部署完成！${NC}"
echo "=========================================="
echo ""
echo "服务地址："
echo "  前端页面:  http://43.156.249.166"
echo "  后端 API:  http://43.156.249.166/api/"
echo "  健康检查:  http://43.156.249.166/health"
echo "  API 文档:  http://43.156.249.166/docs"
echo ""
echo "常用命令（在 $APP_DIR/code/mindmirror 下执行）："
echo "  查看日志:     docker-compose -f $COMPOSE_FILE logs -f"
echo "  重启服务:     docker-compose -f $COMPOSE_FILE restart"
echo "  停止服务:     docker-compose -f $COMPOSE_FILE down"
echo "  更新部署:     bash deploy/update.sh"
echo ""
echo -e "${YELLOW}注意: 请确保 .env 中的 ZHIPU_API_KEY 已正确配置${NC}"
echo ""
