#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开发者技术雷达 - 定时任务入口
通过 OpenClaw sessions_spawn 触发子代理执行抓取任务
"""

import subprocess
import sys
from datetime import datetime

WORKSPACE = "/root/.openclaw/workspace"
LOG_FILE = f"{WORKSPACE}/logs/dev_radar.log"

def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    with open(LOG_FILE, 'a') as f:
        f.write(log_line + '\n')

def main():
    log("🎯 开发者技术雷达启动")
    
    # 使用 openclaw 命令触发子代理执行任务
    task_description = """
你是一个资深技术专家，请帮我筛选真正对开发者有价值的技术内容。

## 任务

1. 使用 web_fetch 抓取 https://www.infoq.cn/ (maxChars=15000, extractMode=text)

2. **严格过滤**，只保留对开发者真正有价值的内容：

   ✅ **保留**（高价值）：
   - 实战技术：新框架/工具、性能优化、最佳实践、代码案例
   - 效率工具：CLI 工具、IDE 插件、自动化、工作流优化
   - 技术深度：源码分析、架构设计、技术选型、踩坑总结
   - 趋势技术：新语言特性、新兴框架、潜力开源项目

   ❌ **过滤**（噪音）：
   - 高管变动、融资新闻
   - 大会预告/回顾、会议报告
   - 纯产品发布（无技术细节）
   - 市场分析、商业合作

3. 对每篇高价值文章，生成**开发者视角**的摘要：

【技术类别】标题

核心价值：一句话说明能解决什么开发问题

关键要点：
• 要点 1（含具体技术/工具/数据）
• 要点 2
• 要点 3

适用场景：什么开发场景用得上

行动建议：值得深入/可以了解/跳过

4. 使用 feishu_bitable_create_record 存入表格：
   - app_token: NrxNbCA9qaFkjfsx7VRcGTnNnBe
   - table_id: tbllP3KSxWDsnVem
   - 字段：文章标题、来源、原文链接、核心摘要（用上面格式）、状态 (新)、标签、重要程度、抓取时间

5. 只通知真正值得关注的文章（含实战代码/新工具/效率提升）

## 输出要求

最后给我一个汇总：
- 抓取总数
- 过滤后高价值数量
- 每篇的摘要（按上面格式）
- 推荐优先阅读哪篇
"""
    
    # 将任务写入临时文件
    task_file = f"{WORKSPACE}/data/dev_radar_task.txt"
    with open(task_file, 'w') as f:
        f.write(task_description)
    
    log(f"任务描述已写入：{task_file}")
    log("请手动执行：openclaw --task-file {task_file}")
    log("✅ 准备完成")

if __name__ == "__main__":
    main()
