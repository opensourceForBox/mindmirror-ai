# MindMirror AI - 自动提交配置

## 🤖 自动提交方案

### 方案 A: Cron 定时任务（推荐）

**适用场景**: 服务器常开，定时自动提交

#### 1. 手动测试脚本
```bash
cd /root/.openclaw/workspace
./scripts/auto-commit.sh "feat: 初始化项目"
```

#### 2. 配置 Cron 定时任务

**选项 1: 每小时提交一次**
```bash
crontab -e
# 添加以下行：
0 * * * * cd /root/.openclaw/workspace && ./scripts/auto-commit.sh "chore: 每小时自动提交" >> /root/.openclaw/workspace/logs/auto-commit.log 2>&1
```

**选项 2: 每 30 分钟提交一次**
```bash
crontab -e
# 添加以下行：
*/30 * * * * cd /root/.openclaw/workspace && ./scripts/auto-commit.sh "chore: 自动提交" >> /root/.openclaw/workspace/logs/auto-commit.log 2>&1
```

**选项 3: 每天提交 3 次（9:00, 14:00, 20:00）**
```bash
crontab -e
# 添加以下行：
0 9,14,20 * * * cd /root/.openclaw/workspace && ./scripts/auto-commit.sh "chore: 每日自动提交" >> /root/.openclaw/workspace/logs/auto-commit.log 2>&1
```

#### 3. 查看 Cron 日志
```bash
# 查看提交日志
tail -f /root/.openclaw/workspace/logs/auto-commit.log

# 查看 Cron 执行日志
grep CRON /var/log/syslog | tail -20
```

#### 4. 管理 Cron 任务
```bash
# 查看当前 Cron 任务
crontab -l

# 编辑 Cron 任务
crontab -e

# 删除所有 Cron 任务（谨慎！）
crontab -r
```

---

### 方案 B: Git Hook（提交前自动触发）

**适用场景**: 想要每次文件变更后立即提交

#### 1. 创建 Git Post-Commit Hook
```bash
cat > /root/.openclaw/workspace/.git/hooks/post-commit << 'EOF'
#!/bin/bash
cd /root/.openclaw/workspace
git push origin main
EOF

chmod +x /root/.openclaw/workspace/.git/hooks/post-commit
```

#### 2. 配合 inotify 实现文件监控自动提交
```bash
# 安装 inotify-tools
apt-get install -y inotify-tools

# 创建监控脚本
cat > /root/.openclaw/workspace/scripts/watch-and-commit.sh << 'EOF'
#!/bin/bash
cd /root/.openclaw/workspace

inotifywait -m -r -e modify,create,delete \
    --exclude '(.git|node_modules|logs|\.log$)' \
    . | while read directory event file; do
    echo "检测到文件变更：$directory$file ($event)"
    sleep 2  # 等待文件写入完成
    ./scripts/auto-commit.sh "chore: $file $event"
done
EOF

chmod +x /root/.openclaw/workspace/scripts/watch-and-commit.sh
```

#### 3. 启动监控（后台运行）
```bash
nohup ./scripts/watch-and-commit.sh > logs/watch.log 2>&1 &
```

---

### 方案 C: GitHub Actions（推送后自动 CI/CD）

**适用场景**: 代码推送到 GitHub 后自动运行测试、部署

#### 1. 创建 Workflow 文件
文件位置：`.github/workflows/ci.yml`

```yaml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: npm ci
        working-directory: ./code/mindmirror/backend
      
      - name: Run tests
        run: npm test
        working-directory: ./code/mindmirror/backend

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to production
        run: echo "Deploying..."
```

---

## 📋 推荐配置

**对于 MindMirror AI 项目，推荐组合使用：**

1. **开发阶段**: 方案 A (Cron 每 30 分钟提交)
2. **生产阶段**: 方案 C (GitHub Actions CI/CD)

### 快速启动（推荐）

```bash
# 1. 创建日志目录
mkdir -p /root/.openclaw/workspace/logs

# 2. 测试脚本
cd /root/.openclaw/workspace
./scripts/auto-commit.sh "feat: 初始化 MindMirror AI 项目"

# 3. 配置 Cron（每 30 分钟自动提交）
(crontab -l 2>/dev/null; echo "*/30 * * * * cd /root/.openclaw/workspace && ./scripts/auto-commit.sh 'chore: 自动提交' >> /root/.openclaw/workspace/logs/auto-commit.log 2>&1") | crontab -

# 4. 验证 Cron 配置
crontab -l
```

---

## ⚠️ 注意事项

1. **敏感信息**: 确保 `.gitignore` 已配置，不要提交 `.env`、密钥等敏感文件
2. **大文件**: 使用 Git LFS 管理大文件（模型、数据集）
3. **提交频率**: 避免过于频繁的提交（建议 >= 30 分钟）
4. **网络问题**: 确保服务器能访问 GitHub（可能需要配置代理）

---

## 🔧 故障排查

### 问题 1: Cron 不执行
```bash
# 检查 Cron 服务状态
systemctl status cron

# 启动 Cron 服务
systemctl start cron
systemctl enable cron
```

### 问题 2: Git 推送失败
```bash
# 检查 Git 配置
git config --list

# 测试推送
cd /root/.openclaw/workspace
git push origin main
```

### 问题 3: 查看日志
```bash
# 自动提交日志
tail -f /root/.openclaw/workspace/logs/auto-commit.log

# Cron 日志
grep CRON /var/log/syslog | tail -50
```

---

*配置时间：2026-04-01*
