# 技术监控系统 - 使用说明

## 系统架构

```
每天早上 9:00 (自动)
    ↓
monitor.py 抓取 InfoQ + GitHub Trending
    ↓
保存到 data/tech_pending.json
    ↓
📢 您说"处理技术监控"
    ↓
我运行 process_manual.py 创建飞书记录 + 发送通知
```

## 配置文件

### 监控脚本
- **路径**: `/root/.openclaw/workspace/skills/blog-monitor/monitor.py`
- **触发**: 每天 9:00 (crontab)
- **功能**: 抓取 InfoQ 文章 + GitHub Trending 项目

### 处理器脚本
- **路径**: `/root/.openclaw/workspace/skills/blog-monitor/process_manual.py`
- **触发**: 手动（您告诉我后我运行）
- **功能**: 创建飞书记录 + 发送通知

### 数据文件
- **状态**: `/root/.openclaw/workspace/data/tech_monitor_state.json`
- **待处理**: `/root/.openclaw/workspace/data/tech_pending.json`
- **日志**: `/root/.openclaw/workspace/logs/tech_monitor.log`

## 兴趣规则

### 高优先级关键词 (P0/P1)
```
AI/LLM: AI, 人工智能，大模型，LLM, GPT, Claude, Agent, 智能体，RAG, 微调，推理
开发效率：OpenClaw, Claude Code, Cursor, Copilot, AI Coding, MCP, Skills
技术栈：Python, Node.js, Rust, Go, Kubernetes, Docker
架构工程：架构，微服务，分布式，性能优化，源码，实战
```

### 过滤关键词
```
微信公众号，下载，福利，平台，更多，扫码，关注，首页，专题，广告，推广，会议，大会，报名
```

## 使用方式

### 查看抓取结果
```bash
cat /root/.openclaw/workspace/data/tech_pending.json | python3 -m json.tool | head -50
```

### 查看日志
```bash
tail -30 /root/.openclaw/workspace/logs/tech_monitor.log
```

### 手动触发处理
在飞书对话中告诉我：
- "处理技术监控"
- "处理待处理文章"
- "运行处理器"

我会运行 `process_manual.py` 创建飞书记录并发送通知给您。

## 定时任务

```bash
# 查看
crontab -l

# 编辑
crontab -e

# 当前配置
0 9 * * * cd /root/.openclaw/workspace && python3 skills/blog-monitor/monitor.py >> logs/tech_monitor.log 2>&1
```

## 飞书多维表格

- **App Token**: `NrxNbCA9qaFkjfsx7VRcGTnNnBe`
- **Table ID**: `tbllP3KSxWDsnVem`
- **链接**: https://bytedance.feishu.cn/base/NrxNbCA9qaFkjfsx7VRcGTnNnBe

### 字段说明
| 字段 | 类型 | 说明 |
|------|------|------|
| 待读文章 | Text | 主字段（标题） |
| 文章标题 | Text | 完整标题 |
| 来源 | Text | InfoQ / GitHub Trending |
| 原文链接 | URL | 可点击链接 |
| 核心摘要 | Text | 自动生成的摘要 |
| 状态 | SingleSelect | 新/待阅读/阅读中/已读/已归档 |
| 标签 | MultiSelect | AI/OpenClaw/Python/实战等 |
| 重要程度 | SingleSelect | 普通/重要/必读 |
| 优先级 | SingleSelect | 🔥 P0 / ⭐ P1 / 📌 P2 / 普通 |
| 抓取时间 | DateTime | 自动记录 |
| 发布时间 | DateTime | 自动记录 |

## 常见问题

### Q: 为什么 GitHub Trending 有时抓取失败？
A: GitHub 有反爬机制，可能需要添加代理或降低频率。

### Q: 如何修改兴趣关键词？
A: 编辑 `monitor.py` 中的 `CONFIG["interest_keywords"]` 数组。

### Q: 如何更改抓取时间？
A: 运行 `crontab -e` 修改 cron 表达式。

---
*最后更新：2026-03-23*
