# Mission Control 集成指南

## 自动同步方案

### 方案 A：文件监听器（推荐）

**实时监听** `iterations/*/TASK_BOARD.md` 文件变化，自动触发同步。

#### 启动监听器

```bash
# 后台运行监听器
nohup bash /root/.openclaw/workspace/skills/mission-control/watch-task-board.sh > /tmp/mission-control.log 2>&1 &

# 查看日志
tail -f /tmp/mission-control.log

# 停止监听器
pkill -f watch-task-board.sh
```

#### 依赖检查

```bash
# 检查 inotifywait 是否可用
which inotifywait

# 如未安装（CentOS/RHEL）：
yum install inotify-tools

# 如未安装（Debian/Ubuntu）：
apt install inotify-tools
```

---

### 方案 B：定时任务（备用）

**每 5 分钟** 检查并同步一次。

#### 配置 crontab

```bash
crontab -e

# 添加以下行：
*/5 * * * * /root/.openclaw/workspace/skills/mission-control/sync-task-board.sh >> /tmp/mission-control.log 2>&1
```

---

### 方案 C：Manager 技能集成（最佳）

在 Manager 技能中，每次更新 `TASK_BOARD.md` 后**直接调用同步脚本**。

#### 集成点

在 Manager 技能的以下位置添加同步调用：

1. **创建新迭代时**
   ```bash
   # 创建 iterations/vX.X/TASK_BOARD.md 后
   bash /root/.openclaw/workspace/skills/mission-control/sync-task-board.sh
   ```

2. **更新任务状态时**
   ```bash
   # 更新 TASK_BOARD.md 中的任务状态后
   bash /root/.openclaw/workspace/skills/mission-control/sync-task-board.sh
   ```

3. **Worker 完成任务时**
   ```bash
   # 更新 TASK_BOARD.md 标记任务完成后
   bash /root/.openclaw/workspace/skills/mission-control/sync-task-board.sh
   ```

#### 示例代码（Manager 技能中）

```bash
# 更新 TASK_BOARD.md
update_task_board "架构设计" "✅ 完成"

# 自动同步到 Bitable
bash /root/.openclaw/workspace/skills/mission-control/sync-task-board.sh

# 发送通知给用户
send_message "✅ 任务看板已更新，查看：https://feishu.cn/docx/GNZbdHwL6orkTNx1QRCczCljnnT"
```

---

## Bitable API 集成

### 在脚本中直接调用 Feishu API

修改 `sync-task-board.sh` 中的 TODO 部分：

```bash
# 调用 openclaw feishu_bitable 工具
openclaw feishu_bitable_create_record \
  --app_token "$BITABLE_APP" \
  --table_id "$BITABLE_TABLE" \
  --fields "{\"任务 ID\":\"$task_id\",\"任务名称\":\"$task_name\",\"当前阶段\":\"$stage\",\"负责人\":\"$worker\",\"进度%\":$progress}"
```

### 或使用 curl 直接调用 Feishu API

```bash
curl -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$BITABLE_APP/tables/$BITABLE_TABLE/records" \
  -H "Authorization: Bearer $FEISHU_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"fields\": {
      \"任务 ID\": \"$task_id\",
      \"任务名称\": \"$task_name\",
      \"当前阶段\": \"$stage\",
      \"负责人\": \"$worker\",
      \"进度%\": $progress
    }
  }"
```

---

## 测试验证

### 手动触发同步

```bash
bash /root/.openclaw/workspace/skills/mission-control/sync-task-board.sh
```

### 查看 Bitable 数据

访问：https://ccnatqob3gk9.feishu.cn/base/OVB0b4GASaVnZgsyW7vcffwMnBh

### 查看主看板

访问：https://feishu.cn/docx/GNZbdHwL6orkTNx1QRCczCljnnT

---

## 故障排查

### 同步脚本执行失败

```bash
# 检查脚本权限
chmod +x /root/.openclaw/workspace/skills/mission-control/sync-task-board.sh

# 检查 Feishu 凭证
openclaw feishu_app_scopes

# 手动测试 Bitable API
openclaw feishu_bitable_list_records --app_token OVB0b4GASaVnZgsyW7vcffwMnBh --table_id tblGKdhzAwBBqYKE
```

### 文件监听器未触发

```bash
# 检查监听器进程
ps aux | grep watch-task-board

# 查看监听器日志
tail -f /tmp/mission-control.log

# 测试文件变化
echo "test" >> /root/.openclaw/workspace/iterations/v1.0/TASK_BOARD.md
```

---

## 推荐配置

**生产环境推荐**：

1. **方案 C（Manager 技能集成）** + **方案 B（定时任务备用）**
   - Manager 更新时立即同步
   - 定时任务作为兜底，防止遗漏

2. **监听器作为开发环境调试工具**
   - 本地测试时使用
   - 生产环境使用技能集成

---

*Mission Control v1.0 | 2026-03-11*
