#!/usr/bin/env python3
"""
GitHub Trending 每日推送 - 被 cron 触发时运行
抓取 GitHub Trending 并推送给用户
"""

import json
import subprocess
import os
from datetime import datetime
from pathlib import Path

# 配置
CONFIG = {
    "user_id": "ou_1d9442018ffd3eefc8f4baac97235f6c",
    "bitable_app_token": "VMbQbI8kna8J98sFGEOc0864nvf",
    "bitable_table_id": "tbl8ZLGKBR0sE5M0",
    "log_file": Path("/root/.openclaw/workspace/logs/github_trending.log")
}

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{ts}] {msg}")
    CONFIG["log_file"].parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG["log_file"], "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")

def fetch_trending():
    """获取 GitHub Trending"""
    try:
        # 使用 openclaw sessions spawn 调用 github-trending-cn 技能
        result = subprocess.run(
            ["openclaw", "sessions", "spawn",
             "--runtime", "subagent",
             "--mode", "run",
             "--task", "获取 GitHub 今日热门项目，返回前 10 个，格式：排名、仓库名、Star 数、今日增长、语言、描述"],
            capture_output=True, text=True, timeout=90,
            env={**os.environ, "PATH": "/usr/local/bin:/usr/bin:/bin:" + os.environ.get("PATH", "")}
        )
        return result.stdout
    except Exception as e:
        log(f"获取 Trending 失败：{e}")
        return None

def send_message(message):
    """发送飞书消息"""
    try:
        cmd = [
            "openclaw", "message", "send",
            "--target", f"user:{CONFIG['user_id']}",
            "--message", message
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
            env={**os.environ, "PATH": "/usr/local/bin:/usr/bin:/bin:" + os.environ.get("PATH", "")})
        return result.returncode == 0
    except Exception as e:
        log(f"发送消息失败：{e}")
        return False

def save_to_bitable(projects):
    """保存项目到飞书多维表格"""
    for proj in projects[:5]:  # 只保存前 5 个
        fields = {
            "仓库名称": proj.get("name", ""),
            "描述": proj.get("description", ""),
            "Star 数": proj.get("stars", 0),
            "语言": proj.get("language", "Other"),
            "作者": proj.get("author", ""),
            "仓库链接": {"text": proj.get("name", ""), "link": proj.get("url", "")},
            "抓取日期": int(datetime.now().timestamp() * 1000),
            "标签": ["AI/ML"] if any(kw in proj.get("description", "").lower() for kw in ["ai", "ml", "llm"]) else []
        }
        
        try:
            fields_json = json.dumps(fields, ensure_ascii=False)
            subprocess.run(
                ["openclaw", "feishu", "bitable", "create-record",
                 "--app-token", CONFIG["bitable_app_token"],
                 "--table-id", CONFIG["bitable_table_id"],
                 "--fields", fields_json],
                capture_output=True, text=True, timeout=30,
                env={**os.environ, "PATH": "/usr/local/bin:/usr/bin:/bin:" + os.environ.get("PATH", "")}
            )
        except Exception as e:
            log(f"保存项目失败：{e}")

def main():
    log("🚀 GitHub Trending 每日推送启动")
    
    # 构建推送消息
    message = f"""📈 GitHub Trending 每日播报
📅 {datetime.now().strftime('%Y-%m-%d %A')}

正在获取今日热门项目...
"""
    
    # 发送初始消息
    send_message(message)
    
    # 获取 Trending 数据
    trending = fetch_trending()
    
    if trending:
        # 格式化推送
        report = f"""
{trending}

🔗 查看完整榜单：https://github.com/trending

_每天早上 8 点自动推送_
"""
        send_message(report)
        log("✅ 推送成功")
    else:
        send_message("⚠️ 今日暂时无法获取 GitHub Trending，请稍后查看 https://github.com/trending")
        log("⚠️ 获取失败")
    
    log("✅ 任务完成")

if __name__ == "__main__":
    main()
