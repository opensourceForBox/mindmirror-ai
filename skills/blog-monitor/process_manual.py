#!/usr/bin/env python3
"""
技术监控处理器 - 手动触发
读取待处理文件，创建飞书记录并发送通知

使用方式：
python3 /root/.openclaw/workspace/skills/blog-monitor/process_manual.py
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
    "state_file": Path("/root/.openclaw/workspace/data/tech_monitor_state.json"),
    "pending_file": Path("/root/.openclaw/workspace/data/tech_pending.json"),
    "user_id": "ou_1d9442018ffd3eefc8f4baac97235f6c"
}

def load_state():
    if CONFIG["state_file"].exists():
        with open(CONFIG["state_file"], "r", encoding="utf-8") as f:
            return json.load(f)
    return {"articles": {}, "repos": {}}

def save_state(state):
    CONFIG["state_file"].parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG["state_file"], "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_pending():
    if not CONFIG["pending_file"].exists():
        return []
    with open(CONFIG["pending_file"], "r", encoding="utf-8") as f:
        return json.load(f)

def create_bitable_record(item):
    """创建飞书多维表格记录"""
    is_repo = item.get("type") == "repo"
    
    fields = {
        "待读文章": item.get("title", item.get("name", "")),
        "文章标题": item.get("title", item.get("name", "")),
        "来源": item.get("source", "Unknown"),
        "原文链接": {"link": item.get("url", "")},
        "核心摘要": item.get("description", f"自动抓取的技术内容 - {item.get('source', '')}"),
        "状态": "新",
        "标签": item.get("tags", ["技术"]),
        "重要程度": "重要" if item.get("priority") in ["🔥 P0", "⭐ P1"] else "普通",
        "优先级": item.get("priority", "普通"),
        "抓取时间": int(datetime.now().timestamp() * 1000),
        "发布时间": int(datetime.now().timestamp() * 1000)
    }
    
    # GitHub repo 额外字段
    if is_repo:
        fields["核心摘要"] = f"GitHub Trending - {item.get('language', '')} | ⭐ {item.get('stars', '?')}"
    
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

def send_notification(items, priority_items):
    """发送飞书通知"""
    if not items:
        return False
    
    # 高优先级
    p0_text = ""
    if priority_items:
        p0 = [i for i in priority_items if i.get("priority") == "🔥 P0"]
        if p0:
            p0_text = "\n🔥 **P0 必读**:\n" + "\n".join(
                [f"• {i.get('title', i.get('name', ''))[:50]}" for i in p0[:5]]
            )
    
    p1_text = ""
    if priority_items:
        p1 = [i for i in priority_items if i.get("priority") == "⭐ P1"]
        if p1:
            p1_text = "\n⭐ **P1 推荐**:\n" + "\n".join(
                [f"• {i.get('title', i.get('name', ''))[:50]}" for i in p1[:5]]
            )
    
    # 普通
    normal_items = [i for i in items if i not in priority_items]
    normal_text = ""
    if normal_items:
        normal_text = "\n📰 **普通**:\n" + "\n".join(
            [f"• {i.get('title', i.get('name', ''))[:50]}" for i in normal_items[:10]]
        )
    
    msg = f"""📊 技术监控报告

{p0_text}{p1_text}{normal_text}

✅ 本次新增：{len(items)} 条
🔥 P0 必读：{len([i for i in items if i.get('priority')=='🔥 P0'])} 条
⭐ P1 推荐：{len([i for i in items if i.get('priority')=='⭐ P1'])} 条
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
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 开始处理技术监控内容")
    
    # 加载数据
    state = load_state()
    pending = load_pending()
    
    if not pending:
        print("⚠️ 没有待处理的内容")
        return
    
    print(f"📄 找到 {len(pending)} 条待处理内容")
    
    new_items = []
    priority_items = []
    processed = []
    
    for item in pending:
        item_id = hashlib.md5(item.get("url", item.get("name", "")).encode()).hexdigest()
        
        # 检查是否已存在
        if item_id in state.get("articles", {}) or item_id in state.get("repos", {}):
            print(f"  ⏭️  已存在：{item.get('title', item.get('name', ''))[:30]}...")
            processed.append(item)
            continue
        
        # 创建飞书记录
        success, record_id = create_bitable_record(item)
        
        if success:
            print(f"  ✅ 创建成功 [{item.get('priority', '')}]: {item.get('title', item.get('name', ''))[:30]}... ({record_id})")
            
            # 更新状态
            if item.get("type") == "repo":
                state.setdefault("repos", {})[item_id] = {
                    "name": item.get("name", ""),
                    "url": item.get("url", ""),
                    "created_at": datetime.now().isoformat(),
                    "record_id": record_id
                }
            else:
                state.setdefault("articles", {})[item_id] = {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "created_at": datetime.now().isoformat(),
                    "record_id": record_id
                }
            
            new_items.append(item)
            if item.get("priority") in ["🔥 P0", "⭐ P1"]:
                priority_items.append(item)
        else:
            print(f"  ❌ 创建失败：{item.get('title', item.get('name', ''))[:30]}... - {record_id}")
    
    # 保存状态
    save_state(state)
    
    # 发送通知
    if new_items:
        print("📤 发送通知...")
        send_notification(new_items, priority_items)
        print("✅ 通知已发送")
    
    print(f"\n✅ 处理完成 - 新增 {len(new_items)} 条，高优先级 {len(priority_items)} 条，累计 {len(state.get('articles', {})) + len(state.get('repos', {}))} 条")

if __name__ == "__main__":
    main()
