---
name: blog-monitor
description: "博客监控 | Blog Monitor. 定时抓取技术博客（InfoQ、51CTO），自动摘要并存储到飞书多维表格。触发词：博客监控、文章抓取、技术资讯"
metadata:
  openclaw:
    emoji: "📰"
    category: "developer"
    tags: ["blog", "monitor", "feishu", "automation", "cron"]
    requires:
      bins: ["python3", "curl"]
---

# 博客监控

定时抓取技术博客文章，自动存储到飞书多维表格。

## 功能

- **定时抓取** - 每 2 小时自动检查新文章
- **来源支持** - InfoQ、51CTO
- **自动摘要** - 使用 AI 生成文章摘要
- **标签分类** - 自动检测文章标签（AI/架构/前端/后端等）
- **重要提醒** - 检测到重要文章时飞书私信通知
- **飞书集成** - 自动存入飞书多维表格

## 使用方式

### 手动触发

```
抓取最新技术文章
```

### 定时任务

```bash
openclaw cron add blog-monitor "0 */2 * * *"
```

## 输出示例

飞书多维表格记录：
| 文章标题 | 来源 | 标签 | 状态 |
|---------|------|------|------|
| XXX 架构实践 | InfoQ | AI, 架构 | 新 |

---

*技术资讯，一手掌握* 📰
