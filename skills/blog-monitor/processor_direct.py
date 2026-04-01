#!/usr/bin/env python3
"""
博客监控直接处理器 - 由 monitor.py 调用
创建飞书记录并发送通知
"""

import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path

# 添加 openclaw 到路径
sys.path.insert(0, '/root/.openclaw')

from openclaw.tools import feishu_bitable_create_record, message

# 配置
CONFIG = {
    "bitable_app_token": "NrxNbCA9qaFkjfsx7VRcGTnNnBe",
    "bitable_table_id": "tbllP3KSxWDsnVem",
    "state_file": Path("/root/.openclaw/workspace/data/blog_monitor_state.json"),
    "user_id": "ou_1d9442018ffd3eefc8f4baac97235f6c"
}

def load_state():
    if CONFIG["state_file"].exists():
        with open(CONFIG["state_file"], "r", encoding="utf-8") as f:
            return json.load(f)
    return {"articles": {}}

def save_state(state):
    CONFIG["state_file"].parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG["state_file"], "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def create_bitable_record(article):
    """创建飞书多维表格记录"""
    fields = {
        "待读文章": article["title"],
        "文章标题": article["title"],
        "来源": article["source"],
        "原文链接": {"link": article["url"]},
        "核心摘要": f"自动抓取的技术文章 - {article['source']}",
        "状态": "新",
        "标签": article.get("tags", ["技术"]),
        "重要程度": "重要" if article.get("is_important") else "普通",
        "抓取时间": int(datetime.now().timestamp() * 1000),
        "发布时间": int(datetime.now().timestamp() * 1000)
    }
    
    result = feishu_bitable_create_record(
        action="create_record",
        app_token=CONFIG['bitable_app_token'],
        table_id=CONFIG['bitable_table_id'],
        fields=fields
    )
    
    if result and isinstance(result, dict):
        record_id = result.get("record", {}).get("record_id", "N/A")
        return True, record_id
    else:
        return False, str(result)

def send_notification(new_articles, important_articles):
    """发送飞书通知"""
    if not new_articles:
        return False
    
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
    
    result = message(
        action="send",
        target=f"user:{CONFIG['user_id']}",
        message=msg
    )
    return True

def main():
    # 从命令行参数获取文章列表
    if len(sys.argv) < 2:
        print("⚠️ 没有文章数据")
        return
    
    articles = json.loads(sys.argv[1])
    
    print(f"📄 处理 {len(articles)} 篇文章")
    
    state = load_state()
    new_articles = []
    important_articles = []
    
    for article in articles:
        article_id = hashlib.md5(article["url"].encode()).hexdigest()
        
        # 检查是否已存在
        if article_id in state["articles"]:
            print(f"  ⏭️  已存在：{article['title'][:30]}...")
            continue
        
        # 创建飞书记录
        success, record_id = create_bitable_record(article)
        
        if success:
            print(f"  ✅ 创建成功：{article['title'][:30]}... ({record_id})")
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
            print(f"  ❌ 创建失败：{article['title'][:30]}... - {record_id}")
    
    # 保存状态
    save_state(state)
    
    # 发送通知
    if new_articles:
        print("📤 发送通知...")
        send_notification(new_articles, important_articles)
    
    print(f"✅ 处理完成 - 新增 {len(new_articles)} 篇，重要 {len(important_articles)} 篇，累计 {len(state['articles'])} 篇")

if __name__ == "__main__":
    main()
