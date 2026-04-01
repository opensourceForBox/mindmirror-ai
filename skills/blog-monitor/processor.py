#!/usr/bin/env python3
"""
博客监控处理器 - 创建飞书记录并发送通知
由 cron 定时调用（抓取后 1 分钟）

使用方法:
python3 /root/.openclaw/workspace/skills/blog-monitor/processor.py
"""

import json
import hashlib
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path

# 配置
CONFIG = {
    "bitable_app_token": "NrxNbCA9qaFkjfsx7VRcGTnNnBe",
    "bitable_table_id": "tbllP3KSxWDsnVem",
    "state_file": Path("/root/.openclaw/workspace/data/blog_monitor_state.json"),
    "pending_file": Path("/root/.openclaw/workspace/data/blog_pending.json"),
    "user_id": "ou_1d9442018ffd3eefc8f4baac97235f6c",
    "log_file": Path("/root/.openclaw/workspace/logs/blog_processor.log")
}

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {msg}"
    print(log_msg)
    try:
        CONFIG["log_file"].parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG["log_file"], "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
    except:
        pass

def load_state():
    if CONFIG["state_file"].exists():
        with open(CONFIG["state_file"], "r", encoding="utf-8") as f:
            return json.load(f)
    return {"articles": {}}

def save_state(state):
    CONFIG["state_file"].parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG["state_file"], "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_pending():
    if not CONFIG["pending_file"].exists():
        return []
    with open(CONFIG["pending_file"], "r", encoding="utf-8") as f:
        return json.load(f)

def save_pending(pending):
    with open(CONFIG["pending_file"], "w", encoding="utf-8") as f:
        json.dump(pending, f, ensure_ascii=False, indent=2)

def create_bitable_record(article):
    """创建飞书多维表格记录 - 使用 sessions_spawn 调用"""
    fields = {
        "待读文章": article["title"],
        "文章标题": article["title"],
        "来源": article["source"],
        "原文链接": {"link": article["url"]},
        "核心摘要": f"自动抓取的技术文章",
        "状态": "新",
        "标签": article.get("tags", ["技术"]),
        "重要程度": "重要" if article.get("is_important") else "普通",
        "抓取时间": int(datetime.now().timestamp() * 1000),
        "发布时间": int(datetime.now().timestamp() * 1000)
    }
    
    # 使用 openclaw sessions_spawn 调用
    task = f'''
from openclaw.tools import feishu_bitable_create_record
import json

fields = {json.dumps(fields, ensure_ascii=False)}

result = feishu_bitable_create_record(
    action="create_record",
    app_token="{CONFIG['bitable_app_token']}",
    table_id="{CONFIG['bitable_table_id']}",
    fields=fields
)

print(json.dumps(result if result else {{}}))
'''
    
    # 写入临时文件
    temp_script = CONFIG["log_file"].parent / "temp_create.py"
    with open(temp_script, "w", encoding="utf-8") as f:
        f.write(task)
    
    try:
        # 设置环境变量
        env = os.environ.copy()
        env['PATH'] = '/root/.nvm/versions/node/v22.22.0/bin:/usr/bin:/bin'
        
        result = subprocess.run(
            ["python3", str(temp_script)],
            capture_output=True, text=True, timeout=60,
            env=env,
            cwd="/root/.openclaw/workspace"
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout.strip())
            if "error" not in data:
                record_id = data.get("record", {}).get("record_id", data.get("record_id", "N/A"))
                return True, record_id
            else:
                return False, data.get("error", "Unknown error")
        else:
            return False, result.stderr.strip()[:200]
    finally:
        try:
            temp_script.unlink()
        except:
            pass

def send_notification(new_articles, important_articles):
    """发送飞书通知"""
    if not new_articles:
        return
    
    important_text = ""
    if important_articles:
        important_text = "\n🔥 **重要文章**:\n" + "\n".join(
            [f"• {a['title'][:50]}" for a in important_articles[:5]]
        )
    
    normal_text = "\n📰 **普通文章**:\n" + "\n".join(
        [f"• {a['title'][:50]}" for a in new_articles[:10] if a not in important_articles]
    ) if len(new_articles) > len(important_articles) else ""
    
    msg = f"""📊 博客监控报告

{important_text}{normal_text}

✅ 本次新增：{len(new_articles)} 篇
🔥 重要文章：{len(important_articles)} 篇
⏰ 抓取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

[查看详细多维表格](https://bytedance.feishu.cn/base/{CONFIG['bitable_app_token']})
"""
    
    task = f'''
from openclaw.tools import message
import json

result = message(
    action="send",
    target="user:{CONFIG['user_id']}",
    message={json.dumps(msg, ensure_ascii=False)}
)

print(json.dumps(result if result else {{}}))
'''
    
    temp_script = CONFIG["log_file"].parent / "temp_notify.py"
    with open(temp_script, "w", encoding="utf-8") as f:
        f.write(task)
    
    try:
        env = os.environ.copy()
        env['PATH'] = '/root/.nvm/versions/node/v22.22.0/bin:/usr/bin:/bin'
        
        result = subprocess.run(
            ["python3", str(temp_script)],
            capture_output=True, text=True, timeout=60,
            env=env,
            cwd="/root/.openclaw/workspace"
        )
        
        return result.returncode == 0
    finally:
        try:
            temp_script.unlink()
        except:
            pass

def main():
    log("🚀 开始处理博客文章")
    
    # 加载数据
    state = load_state()
    pending = load_pending()
    
    if not pending:
        log("⚠️ 没有待处理的文章")
        return
    
    log(f"📄 找到 {len(pending)} 篇待处理文章")
    
    new_articles = []
    important_articles = []
    processed_pending = []
    
    for article in pending:
        article_id = hashlib.md5(article["url"].encode()).hexdigest()
        
        # 检查是否已存在
        if article_id in state["articles"]:
            log(f"  ⏭️  已存在：{article['title'][:30]}...")
            processed_pending.append(article)
            continue
        
        # 创建飞书记录
        success, record_id = create_bitable_record(article)
        
        if success:
            log(f"  ✅ 创建成功：{article['title'][:30]}... ({record_id})")
            state["articles"][article_id] = {
                "url": article["url"],
                "title": article["title"],
                "created_at": datetime.now().isoformat(),
                "record_id": record_id
            }
            new_articles.append(article)
            if article.get("is_important"):
                important_articles.append(article)
        else:
            log(f"  ❌ 创建失败：{article['title'][:30]}... - {record_id}")
    
    # 保存状态
    save_state(state)
    
    # 移除已处理的
    remaining = [a for a in pending if a not in processed_pending]
    save_pending(remaining)
    
    # 发送通知
    if new_articles:
        log("📤 发送通知...")
        send_notification(new_articles, important_articles)
    
    log(f"✅ 处理完成 - 新增 {len(new_articles)} 篇，重要 {len(important_articles)} 篇，累计 {len(state['articles'])} 篇")

if __name__ == "__main__":
    main()
