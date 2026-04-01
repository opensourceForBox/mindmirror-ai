#!/usr/bin/env python3
"""
技术监控 - 每天早上运行
抓取 InfoQ 技术博客 + GitHub Trending
保存待处理文件，等待手动处理飞书 API
"""

import json
import hashlib
import os
import re
from datetime import datetime
from pathlib import Path
import urllib.request

# ==================== 配置区域 ====================
CONFIG = {
    # InfoQ 配置
    "infoq_url": "https://www.infoq.cn/",
    
    # GitHub Trending 配置
    "github_trending_url": "https://github.com/trending",
    "github_languages": ["Python", "JavaScript", "TypeScript", "Go", "Rust"],  # 关注的语言
    
    # 用户兴趣关键词（高优先级）
    "interest_keywords": [
        # AI/LLM
        "AI", "人工智能", "大模型", "LLM", "GPT", "Claude", "Agent", "智能体",
        "RAG", "微调", "推理", "transformer", "diffusion",
        
        # 开发效率
        "OpenClaw", "Claude Code", "Cursor", "Copilot", "AI Coding",
        "MCP", "Skills", "插件", "IDE", "自动化",
        
        # 技术栈
        "Python", "Node.js", "Rust", "Go", "Kubernetes", "Docker",
        
        # 架构/工程
        "架构", "微服务", "分布式", "性能优化", "源码", "实战"
    ],
    
    # 过滤关键词（低质量内容）
    "exclude_keywords": [
        "微信公众号", "下载", "福利", "平台", "更多", "扫码", "关注",
        "首页", "专题", "广告", "推广", "会议", "大会", "报名"
    ],
    
    # 输出配置
    "state_file": Path("/root/.openclaw/workspace/data/tech_monitor_state.json"),
    "pending_file": Path("/root/.openclaw/workspace/data/tech_pending.json"),
    "log_file": Path("/root/.openclaw/workspace/logs/tech_monitor.log"),
    "workspace": "/root/.openclaw/workspace"
}

# ==================== 日志函数 ====================
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

# ==================== 状态管理 ====================
def load_state():
    if CONFIG["state_file"].exists():
        with open(CONFIG["state_file"], "r", encoding="utf-8") as f:
            return json.load(f)
    return {"articles": {}, "repos": {}, "last_run": None}

def save_state(state):
    CONFIG["state_file"].parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG["state_file"], "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# ==================== InfoQ 抓取 ====================
def fetch_infoq():
    """抓取 InfoQ 首页文章"""
    articles = []
    
    try:
        req = urllib.request.Request(
            CONFIG["infoq_url"],
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        pattern = r'<a[^>]*href="([^"]*infoq\.cn/article[^"]*)"[^>]*>(.*?)</a>'
        matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
        
        seen_urls = set()
        
        for url, title_html in matches:
            url = url.strip()
            if not url.startswith('http'):
                url = 'https://www.infoq.cn/' + url.lstrip('/')
            
            if url in seen_urls:
                continue
            
            clean_title = re.sub(r'<[^>]+>', ' ', title_html).strip()
            
            # 过滤
            if any(kw in clean_title for kw in CONFIG["exclude_keywords"]):
                continue
            
            if 10 < len(clean_title) < 150:
                seen_urls.add(url)
                articles.append({
                    "title": clean_title,
                    "url": url,
                    "source": "InfoQ",
                    "type": "article"
                })
            
            if len(articles) >= 20:
                break
        
        log(f"  ✅ InfoQ: 抓取 {len(articles)} 篇文章")
            
    except Exception as e:
        log(f"  ⚠️ InfoQ 抓取失败：{e}")
    
    return articles

# ==================== GitHub Trending 抓取 ====================
def fetch_github_trending():
    """抓取 GitHub Trending - 使用 web_fetch 工具"""
    repos = []
    
    try:
        # 使用 web_fetch 工具（可能绕过反爬）
        import subprocess
        result = subprocess.run(
            ["python3", "-c", '''
import sys
sys.path.insert(0, "/root/.openclaw")
from openclaw.tools import web_fetch
import json

result = web_fetch(url="https://github.com/trending", maxChars=50000, extractMode="text")
print(json.dumps(result if result else {}))
'''],
            capture_output=True, text=True, timeout=60,
            env={**os.environ, "PYTHONPATH": "/root/.openclaw"}
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            text = data.get("text", "")
            
            # 解析文本格式的 trending 数据
            lines = text.strip().split('\n')
            seen_repos = set()
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # 匹配 repo 名称 (格式：owner/repo)
                repo_match = re.match(r'^([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)\s*$', line)
                if repo_match:
                    repo_name = f"{repo_match.group(1)}/{repo_match.group(2)}"
                    
                    if repo_name in seen_repos or len(repo_name) < 5:
                        continue
                    
                    seen_repos.add(repo_name)
                    
                    # 尝试获取下一行的描述
                    description = ""
                    language = ""
                    stars = "?"
                    
                    if i + 1 < len(lines):
                        desc_line = lines[i + 1].strip()
                        if len(desc_line) > 10 and not desc_line.startswith('·'):
                            description = desc_line[:200]
                    
                    # 查找语言和 stars
                    for j in range(i, min(i + 5, len(lines))):
                        check_line = lines[j].strip()
                        if '·' in check_line:
                            parts = check_line.split('·')
                            for part in parts:
                                part = part.strip()
                                if part in CONFIG["github_languages"]:
                                    language = part
                                elif re.match(r'^\d+\.?\d*k?$', part):
                                    stars = part
                    
                    repos.append({
                        "name": repo_name,
                        "url": f"https://github.com/{repo_name}",
                        "source": "GitHub Trending",
                        "type": "repo",
                        "language": language,
                        "stars": stars,
                        "description": description or f"GitHub Trending - {language or 'Mixed'}"
                    })
                    
                    if len(repos) >= 15:
                        break
            
            log(f"  ✅ GitHub: 抓取 {len(repos)} 个项目")
        else:
            log(f"  ⚠️ GitHub web_fetch 失败：{result.stderr[:200]}")
            
    except Exception as e:
        log(f"  ⚠️ GitHub 抓取失败：{e}")
    
    return repos

# ==================== 兴趣匹配 ====================
def calculate_priority(item):
    """计算优先级分数"""
    title = item.get("title", item.get("name", "")).lower()
    score = 0
    
    # 兴趣关键词匹配
    for kw in CONFIG["interest_keywords"]:
        if kw.lower() in title:
            score += 2
    
    # 特殊加分
    if any(kw in title for kw in ["OpenClaw", "Claude", "AI Coding", "Agent"]):
        score += 5
    
    # 根据分数返回优先级
    if score >= 6:
        return "🔥 P0"
    elif score >= 3:
        return "⭐ P1"
    elif score >= 1:
        return "📌 P2"
    else:
        return "普通"

def detect_tags(item):
    """自动检测标签"""
    text = (item.get("title", "") + " " + item.get("description", "")).lower()
    tags = []
    
    tag_map = {
        "AI": ["ai", "人工智能", "大模型", "llm", "gpt", "claude", "agent", "智能体"],
        "OpenClaw": ["openclaw", "claude code", "cursor", "copilot"],
        "Python": ["python"],
        "Node.js": ["nodejs", "node.js", "javascript", "typescript"],
        "Rust": ["rust"],
        "Go": ["golang", "go"],
        "架构": ["架构", "微服务", "分布式"],
        "实战": ["实战", "教程", "实践", "指南"],
        "效率工具": ["ide", "插件", "工具", "自动化"],
        "开源": ["github", "开源", "trending"]
    }
    
    for tag, keywords in tag_map.items():
        if any(kw in text for kw in keywords):
            tags.append(tag)
    
    return tags[:5] if tags else ["技术"]

# ==================== 主流程 ====================
def main():
    log("🚀 开始技术监控")
    
    state = load_state()
    
    # 抓取数据
    infoq_articles = fetch_infoq()
    github_repos = fetch_github_trending()
    
    all_items = infoq_articles + github_repos
    log(f"📄 共找到 {len(all_items)} 条内容")
    
    # 去重和筛选
    new_items = []
    priority_items = []
    
    for item in all_items:
        # 生成 ID
        item_id = hashlib.md5(item.get("url", item.get("name", "")).encode()).hexdigest()
        
        # 检查是否已存在
        if item_id in state.get("articles", {}) or item_id in state.get("repos", {}):
            log(f"  ⏭️  已存在：{item.get('title', item.get('name', ''))[:30]}...")
            continue
        
        # 计算优先级和标签
        item["priority"] = calculate_priority(item)
        item["tags"] = detect_tags(item)
        item["timestamp"] = datetime.now().isoformat()
        
        new_items.append(item)
        
        if item["priority"] in ["🔥 P0", "⭐ P1"]:
            priority_items.append(item)
        
        log(f"  ✅ 新增 [{item['priority']}]: {item.get('title', item.get('name', ''))[:40]}...")
    
    if not new_items:
        log("✅ 监控完成 - 没有新内容")
        return
    
    # 保存到待处理文件
    try:
        CONFIG["pending_file"].parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG["pending_file"], "w", encoding="utf-8") as f:
            json.dump(new_items, f, ensure_ascii=False, indent=2)
        log(f"  📝 已保存 {len(new_items)} 条到待处理队列")
    except Exception as e:
        log(f"  ⚠️ 保存失败：{e}")
    
    # 输出摘要
    log(f"\n{'='*50}")
    log(f"✅ 监控完成")
    log(f"   InfoQ 文章：{len(infoq_articles)} 篇")
    log(f"   GitHub 项目：{len(github_repos)} 个")
    log(f"   新增内容：{len(new_items)} 条")
    log(f"   高优先级：{len(priority_items)} 条")
    log(f"\n📝 待处理文件：{CONFIG['pending_file']}")
    log(f"📢 请运行：我来处理飞书记录和通知")
    log(f"{'='*50}")
    
    # 更新状态
    state["last_run"] = datetime.now().isoformat()
    save_state(state)

if __name__ == "__main__":
    main()
