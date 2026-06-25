# MindMirror AI 部署指南

> 目标服务器: Linux (IP: 43.156.249.166)
> 部署方式: Docker + Docker Compose + Nginx

---

## 目录

- [服务器要求](#服务器要求)
- [架构概览](#架构概览)
- [快速部署](#快速部署)
- [手动部署](#手动部署)
- [环境变量说明](#环境变量说明)
- [常用运维命令](#常用运维命令)
- [日志查看](#日志查看)
- [故障排除](#故障排除)
- [备份和恢复](#备份和恢复)
- [HTTPS 配置（可选）](#https-配置可选)

---

## 服务器要求

### 最低配置

| 资源 | 要求 |
|------|------|
| CPU | 2 核 |
| 内存 | 4 GB |
| 磁盘 | 40 GB SSD |
| 带宽 | 5 Mbps |
| 系统 | Ubuntu 20.04+ / CentOS 7+ / Debian 11+ |

### 推荐配置

| 资源 | 要求 |
|------|------|
| CPU | 4 核 |
| 内存 | 8 GB |
| 磁盘 | 80 GB SSD |
| 带宽 | 10 Mbps |
| 系统 | Ubuntu 22.04 LTS |

### 需要开放的端口

| 端口 | 用途 | 对外 |
|------|------|------|
| 22 | SSH | 是 |
| 80 | HTTP | 是 |
| 443 | HTTPS（可选） | 是 |
| 8000 | 后端 API（内部） | 否 |
| 6333 | Qdrant（内部） | 否 |
| 6379 | Redis（内部） | 否 |

> **注意**: 生产环境中，Qdrant 和 Redis 仅在 Docker 内部网络中通信，不对外暴露端口。

---

## 架构概览

```
                    ┌──────────────┐
                    │   客户端浏览器   │
                    └──────┬───────┘
                           │ :80/:443
                    ┌──────▼───────┐
                    │    Nginx     │
                    │  (反向代理)    │
                    └──┬────────┬──┘
           静态文件    │        │  API 代理
     ┌──────────────┘  │        │
     │                 │        │
     ▼                 │   ┌────▼────┐
┌─────────┐           │   │  App    │
│  前端    │           │   │ FastAPI │
│  dist/  │           │   └─┬───┬───┘
└─────────┘           │     │   │
               ┌───────┘    │   │
               ▼            │   │
         ┌──────────┐  ┌────▼┐ ┌▼──────┐
         │ Qdrant   │  │Redis│ │ Models │
         │ 向量数据库 │  │缓存 │ │ 模型   │
         └──────────┘  └─────┘ └───────┘
```

### 服务组件

| 服务 | 镜像 | 说明 |
|------|------|------|
| nginx | nginx:alpine | 反向代理、静态文件服务、负载均衡 |
| app | 自建 (python:3.11-slim) | FastAPI 后端，含 AI 模型推理 |
| qdrant | qdrant/qdrant:latest | 向量数据库，存储知识库 |
| redis | redis:7-alpine | 缓存、会话管理 |

---

## 快速部署

### 一键部署（推荐）

```bash
# 1. SSH 到服务器
ssh root@43.156.249.166

# 2. 执行一键部署脚本
curl -fsSL https://raw.githubusercontent.com/opensourceForBox/mindmirror-ai/main/code/mindmirror/deploy/deploy.sh | bash
```

或手动 clone 后执行：

```bash
git clone https://github.com/opensourceForBox/mindmirror-ai.git /opt/mindmirror-ai
cd /opt/mindmirror-ai/code/mindmirror
bash deploy/deploy.sh
```

脚本会自动完成：
1. 安装系统依赖（Docker、Docker Compose、Git、Curl）
2. 配置 Docker 国内镜像加速
3. 克隆/更新代码
4. 配置环境变量（.env）
5. 构建前端静态文件
6. 构建 Docker 镜像
7. 启动所有服务
8. 健康检查
9. 配置防火墙

---

## 手动部署

如果一键脚本不适合你的环境，可以手动执行以下步骤：

### Step 1: 安装 Docker

```bash
# Ubuntu/Debian
apt-get update
apt-get install -y docker.io docker-compose git curl

# CentOS/RHEL
yum install -y docker docker-compose git curl

# 启动 Docker
systemctl enable docker
systemctl start docker
```

### Step 2: 配置 Docker 镜像加速（国内服务器）

```bash
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
```

### Step 3: 获取代码

```bash
git clone https://github.com/opensourceForBox/mindmirror-ai.git /opt/mindmirror-ai
cd /opt/mindmirror-ai/code/mindmirror
```

### Step 4: 配置环境变量

```bash
cp .env.example .env

# 修改为 Docker 服务名（非 localhost）
sed -i 's/QDRANT_HOST=localhost/QDRANT_HOST=qdrant/' .env
sed -i 's|redis://localhost:6379|redis://redis:6379|' .env

# 配置智谱 API Key
nano .env
# 修改 ZHIPU_API_KEY=your_actual_api_key
```

### Step 5: 构建前端

```bash
# 安装 Node.js（如果没有）
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# 构建前端
cd frontend
npm install --registry=https://registry.npmmirror.com
npm run build
cd ..
```

### Step 6: 启动服务

```bash
docker-compose -f deploy/docker-compose.prod.yml build
docker-compose -f deploy/docker-compose.prod.yml up -d
```

### Step 7: 验证部署

```bash
# 检查服务状态
docker-compose -f deploy/docker-compose.prod.yml ps

# 健康检查
curl http://localhost:8000/health
```

---

## 环境变量说明

编辑 `.env` 文件配置环境变量：

```bash
# ─── 必填 ────────────────────────────────────
# 智谱 AI API Key（用于 GLM-4 对话模型）
ZHIPU_API_KEY=your_zhipu_api_key_here

# ─── Docker 网络配置（生产环境使用服务名）─────────
# Qdrant 向量数据库地址（Docker 内部使用服务名）
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Redis 缓存地址（Docker 内部使用服务名）
REDIS_URL=redis://redis:6379

# ─── FastAPI 配置 ────────────────────────────
API_HOST=0.0.0.0
API_PORT=8000
```

### 获取智谱 API Key

1. 访问 [智谱 AI 开放平台](https://open.bigmodel.cn/)
2. 注册并登录
3. 在「API Keys」页面创建新的 Key
4. 将 Key 填入 `.env` 文件的 `ZHIPU_API_KEY` 字段

---

## 常用运维命令

> 以下命令在 `/opt/mindmirror-ai/code/mindmirror` 目录下执行

```bash
COMPOSE="docker-compose -f deploy/docker-compose.prod.yml"

# 查看服务状态
$COMPOSE ps

# 查看所有服务日志（实时）
$COMPOSE logs -f

# 查看指定服务日志
$COMPOSE logs -f app        # 后端日志
$COMPOSE logs -f nginx      # Nginx 日志
$COMPOSE logs -f qdrant     # Qdrant 日志
$COMPOSE logs -f redis      # Redis 日志

# 查看最近 100 行日志
$COMPOSE logs --tail=100 app

# 重启单个服务
$COMPOSE restart app

# 重启所有服务
$COMPOSE restart

# 停止所有服务
$COMPOSE down

# 启动所有服务
$COMPOSE up -d

# 重新构建并启动
$COMPOSE up -d --build

# 进入容器
$COMPOSE exec app bash

# 快速更新部署
bash deploy/update.sh
```

---

## 日志查看

### Docker 日志

```bash
# 实时查看所有日志
docker-compose -f deploy/docker-compose.prod.yml logs -f

# 查看 app 服务最近 200 行
docker-compose -f deploy/docker-compose.prod.yml logs --tail=200 app

# 查看指定时间段日志
docker-compose -f deploy/docker-compose.prod.yml logs --since="2024-01-01T00:00:00" app
```

### Nginx 访问日志

```bash
docker-compose -f deploy/docker-compose.prod.yml exec nginx cat /var/log/nginx/access.log
```

### Nginx 错误日志

```bash
docker-compose -f deploy/docker-compose.prod.yml exec nginx cat /var/log/nginx/error.log
```

### 日志轮转

生产环境已配置日志轮转，防止磁盘写满：

| 服务 | 单文件最大 | 保留文件数 |
|------|-----------|-----------|
| app | 50 MB | 5 个 |
| nginx | 10 MB | 3 个 |
| qdrant | 20 MB | 3 个 |
| redis | 20 MB | 3 个 |

---

## 故障排除

### 1. 服务无法启动

```bash
# 查看服务状态
docker-compose -f deploy/docker-compose.prod.yml ps

# 查看日志定位问题
docker-compose -f deploy/docker-compose.prod.yml logs app
```

**常见原因**:
- `.env` 文件中 `ZHIPU_API_KEY` 未配置
- Qdrant 或 Redis 未就绪（检查健康状态）
- 端口被占用

### 2. 端口被占用

```bash
# 查看端口占用
ss -tlnp | grep :80
ss -tlnp | grep :8000

# 停止占用端口的进程
kill -9 <PID>

# 或修改 docker-compose.prod.yml 中的端口映射
```

### 3. 前端无法访问

```bash
# 检查前端是否已构建
ls -la frontend/dist/

# 如果 dist 不存在，重新构建
cd frontend && npm install && npm run build && cd ..

# 重启 Nginx
docker-compose -f deploy/docker-compose.prod.yml restart nginx
```

### 4. API 请求超时

```bash
# 检查后端服务是否正常
curl http://localhost:8000/health

# 检查 Nginx 代理是否正常
curl http://localhost/api/

# 检查智谱 API Key 是否有效
docker-compose -f deploy/docker-compose.prod.yml exec app python -c "
from src.utils.config import get_config
print(get_config().ZHIPU_API_KEY[:8] + '...')
"
```

### 5. Docker 磁盘空间不足

```bash
# 清理未使用的镜像和容器
docker system prune -a --volumes

# 查看 Docker 磁盘使用
docker system df
```

### 6. Qdrant 连接失败

```bash
# 检查 Qdrant 健康
docker-compose -f deploy/docker-compose.prod.yml exec app curl http://qdrant:6333/healthz

# 重启 Qdrant
docker-compose -f deploy/docker-compose.prod.yml restart qdrant
```

### 7. Redis 连接失败

```bash
# 检查 Redis 健康
docker-compose -f deploy/docker-compose.prod.yml exec redis redis-cli ping

# 重启 Redis
docker-compose -f deploy/docker-compose.prod.yml restart redis
```

### 8. 视频流 WebSocket 连接失败

```bash
# 检查 Nginx WebSocket 代理配置
docker-compose -f deploy/docker-compose.prod.yml exec nginx nginx -t

# 查看 Nginx 错误日志
docker-compose -f deploy/docker-compose.prod.yml logs nginx | grep -i websocket
```

---

## 备份和恢复

### 备份

```bash
# 创建备份目录
BACKUP_DIR="/opt/backups/mindmirror-$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# 1. 备份 Qdrant 数据
docker-compose -f deploy/docker-compose.prod.yml exec qdrant \
  tar czf /tmp/qdrant_backup.tar.gz -C /qdrant storage
docker cp $(docker-compose -f deploy/docker-compose.prod.yml ps -q qdrant):/tmp/qdrant_backup.tar.gz $BACKUP_DIR/

# 2. 备份 Redis 数据
docker-compose -f deploy/docker-compose.prod.yml exec redis \
  redis-cli SAVE
docker cp $(docker-compose -f deploy/docker-compose.prod.yml ps -q redis):/data/dump.rdb $BACKUP_DIR/

# 3. 备份配置文件
cp .env $BACKUP_DIR/
cp -r configs $BACKUP_DIR/

# 4. 备份知识库
tar czf $BACKUP_DIR/knowledge_base.tar.gz knowledge_base/

echo "备份完成: $BACKUP_DIR"
```

### 一键备份脚本

将以上命令保存为 `/opt/mindmirror-ai/code/mindmirror/deploy/backup.sh`：

```bash
#!/bin/bash
set -e
BACKUP_DIR="/opt/backups/mindmirror-$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
cd /opt/mindmirror-ai/code/mindmirror

docker-compose -f deploy/docker-compose.prod.yml exec -T qdrant \
  tar czf /tmp/qdrant_backup.tar.gz -C /qdrant storage 2>/dev/null
docker cp $(docker-compose -f deploy/docker-compose.prod.yml ps -q qdrant):/tmp/qdrant_backup.tar.gz $BACKUP_DIR/

docker-compose -f deploy/docker-compose.prod.yml exec -T redis redis-cli SAVE 2>/dev/null
docker cp $(docker-compose -f deploy/docker-compose.prod.yml ps -q redis):/data/dump.rdb $BACKUP_DIR/

cp .env $BACKUP_DIR/
cp -r configs $BACKUP_DIR/
tar czf $BACKUP_DIR/knowledge_base.tar.gz knowledge_base/

# 保留最近 7 个备份
ls -dt /opt/backups/mindmirror-* | tail -n +8 | xargs rm -rf
echo "备份完成: $BACKUP_DIR"
```

### 恢复

```bash
# 1. 停止服务
docker-compose -f deploy/docker-compose.prod.yml down

# 2. 恢复 Qdrant 数据
docker volume rm mindmirror_qdrant_data
docker volume create mindmirror_qdrant_data
# 启动 Qdrant 临时容器恢复
docker run --rm -v mindmirror_qdrant_data:/qdrant/storage -v /opt/backups/mindmirror-XXXXXX:/backup alpine \
  tar xzf /backup/qdrant_backup.tar.gz -C /

# 3. 恢复 Redis 数据
docker volume rm mindmirror_redis_data
docker volume create mindmirror_redis_data
docker run --rm -v mindmirror_redis_data:/data -v /opt/backups/mindmirror-XXXXXX:/backup alpine \
  cp /backup/dump.rdb /data/

# 4. 恢复配置文件
cp /opt/backups/mindmirror-XXXXXX/.env .env

# 5. 重新启动服务
docker-compose -f deploy/docker-compose.prod.yml up -d
```

### 定时备份

```bash
# 添加定时任务（每天凌晨 3 点备份）
crontab -e
# 添加以下行:
0 3 * * * /opt/mindmirror-ai/code/mindmirror/deploy/backup.sh >> /var/log/mindmirror-backup.log 2>&1
```

---

## HTTPS 配置（可选）

### 使用 Let's Encrypt 免费证书

```bash
# 1. 安装 Certbot
apt-get install -y certbot

# 2. 停止 Nginx 释放 80 端口
docker-compose -f deploy/docker-compose.prod.yml stop nginx

# 3. 获取证书（替换 your-domain.com）
certbot certonly --standalone -d your-domain.com

# 4. 修改 docker-compose.prod.yml 添加证书挂载
#    nginx 服务 volumes 增加:
#      - /etc/letsencrypt/live/your-domain.com/fullchain.pem:/etc/ssl/certs/mindmirror.crt:ro
#      - /etc/letsencrypt/live/your-domain.com/privkey.pem:/etc/ssl/certs/mindmirror.key:ro

# 5. 修改 nginx.conf 添加 HTTPS server 块
```

### nginx.conf HTTPS 配置

在 `nginx.conf` 中添加：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/mindmirror.crt;
    ssl_certificate_key /etc/ssl/certs/mindmirror.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # ... 其余 location 配置与 80 端口相同 ...
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$host$request_uri;
}
```

### 自动续期

```bash
# 添加定时任务（每月 1 号续期）
crontab -e
# 添加:
0 3 1 * * certbot renew --quiet && docker-compose -f /opt/mindmirror-ai/code/mindmirror/deploy/docker-compose.prod.yml restart nginx
```

---

## 资源使用参考

生产环境资源限制配置：

| 服务 | 内存限制 | CPU 限制 |
|------|---------|---------|
| app | 4 GB | 2 核 |
| qdrant | 2 GB | - |
| redis | 512 MB | - |
| nginx | 256 MB | - |
| **总计** | ~6.8 GB | - |

> 建议服务器内存 ≥ 8 GB，预留系统和其他进程的开销。

---

## 部署文件结构

```
code/mindmirror/
├── deploy/
│   ├── deploy.sh              # 一键部署脚本
│   ├── docker-compose.prod.yml # 生产环境 Docker Compose
│   ├── nginx.conf             # Nginx 反向代理配置
│   ├── update.sh              # 快速更新脚本
│   └── README.md              # 本文件
├── docker-compose.yml         # 开发环境 Docker Compose
├── Dockerfile                 # 应用 Docker 镜像
├── .env.example               # 环境变量模板
├── .env                       # 环境变量（部署时生成）
├── frontend/                  # 前端源码
│   ├── dist/                  # 前端构建产物（npm run build 生成）
│   ├── src/
│   ├── package.json
│   └── ...
├── src/                       # 后端源码
├── knowledge_base/            # 知识库数据
├── models/                    # AI 模型文件
├── configs/                   # 配置文件
└── ...
```

---

## 联系与支持

如有部署问题，请检查：
1. 服务日志: `docker-compose -f deploy/docker-compose.prod.yml logs`
2. 健康检查: `curl http://localhost:8000/health`
3. API 文档: `http://43.156.249.166/docs`
