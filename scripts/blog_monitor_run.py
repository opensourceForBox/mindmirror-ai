#!/usr/bin/env python3
"""
博客监控执行器 - 被 cron 触发时运行
抓取技术博客文章，存入飞书多维表格
"""

import json
import hashlib
import subprocess
import os
from datetime import datetime
from pathlib import Path

# 配置
CONFIG = {
    "bitable_app_token": "NrxNbCA9qaFkjfsx7VRcGTnNnBe",
    "bitable_table_id": "tbllP3KSxWDsnVem",
    "user_id": "ou_1d9442018ffd3eefc8f4baac97235f6c",
    "state_file": Path("/root/.openclaw/workspace/data/blog_monitor_state.json"),
    "log_file": Path("/root/.openclaw/workspace/logs/blog_monitor.log")
}

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{ts}] {msg}")
    CONFIG["log_file"].parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG["log_file"], "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")

def load_state():
    if CONFIG["state_file"].exists():
        with open(CONFIG["state_file"], "r", encoding="utf-8") as f:
            return json.load(f)
    return {"articles": {}, "last_run": None}

def save_state(state):
    CONFIG["state_file"].parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG["state_file"], "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def detect_tags(title):
    text = title.lower()
    tags = []
    keywords = {
        "AI": ["ai", "人工智能", "大模型", "llm", "机器学习"],
        "架构": ["架构", "微服务", "分布式"],
        "前端": ["前端", "react", "vue", "javascript"],
        "后端": ["后端", "java", "python", "go"],
        "DevOps": ["devops", "k8s", "docker", "kubernetes"],
        "实战": ["实战", "教程", "实践"]
    }
    for tag, kws in keywords.items():
        if any(kw in text for kw in kws):
            tags.append(tag)
    return tags[:3] if tags else ["技术"]

def create_record(title, source, url):
    """使用 openclaw feishu_bitable_create_record 工具创建记录"""
    fields = {
        "文章标题": title,
        "来源": source,
        "原文链接": {"text": title, "link": url},
        "核心摘要": "自动抓取的技术文章",
        "状态": "新",
        "标签": detect_tags(title),
        "重要程度": "重要" if any(k in title for k in ["AI", "架构", "实战", "大模型"]) else "普通",
        "抓取时间": int(datetime.now().timestamp() * 1000),
        "发布时间": int(datetime.now().timestamp() * 1000)
    }
    
    try:
        # 使用 sessions_spawn 调用工具
        task = f"""使用 feishu_bitable_create_record 工具创建记录:
app_token={CONFIG['bitable_app_token']}
table_id={CONFIG['bitable_table_id']}
fields={json.dumps(fields, ensure_ascii=False)}
"""
        result = subprocess.run(
            ["openclaw", "sessions", "spawn",
             "--runtime", "subagent",
             "--mode", "run",
             "--task", task],
            capture_output=True, text=True, timeout=90,
            env={**os.environ, "PATH": "/usr/local/bin:/usr/bin:/bin:" + os.environ.get("PATH", "")}
        )
        return result.returncode == 0
    except Exception as e:
        log(f"创建记录失败：{e}")
        return False

def main():
    log("🚀 博客监控任务启动")
    
    state = load_state()
    
    # 示例文章（实际需要从网页抓取）
    sample_articles = [
        {"title": f"技术早报 {datetime.now().strftime('%m-%d')}", "source": "InfoQ", "url": "https://www.infoq.cn/"},
    ]
    
    new_count = 0
    for article in sample_articles:
        article_id = hashlib.md5(article["url"].encode()).hexdigest()
        if article_id in state["articles"]:
            continue
        
        if create_record(article["title"], article["source"], article["url"]):
            state["articles"][article_id] = {
                "title": article["title"],
                "url": article["url"],
                "created_at": datetime.now().isoformat()
            }
            new_count += 1
            log(f"✅ {article['title']}")
        else:
            log(f"⚠️ 失败：{article['title']}")
    
    state["last_run"] = datetime.now().isoformat()
    save_state(state)
    
    log(f"✅ 完成 - 新增 {new_count} 篇")

if __name__ == "__main__":
    main()
