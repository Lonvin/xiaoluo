#!/usr/bin/env python3
"""your AI主动记忆召回 — 回复前自动搜索相关历史"""
import os, sys, json, re
from pathlib import Path
from datetime import datetime

MEMORY_DIR = Path.home() / "{project_name}" / "memory"
CONV_DIR = MEMORY_DIR / "conversations"

def search_memories(query, max_results=5):
    """在全部记忆文件中搜索相关内容"""
    results = []
    keywords = _extract_keywords(query)
    
    # 搜索所有markdown文件
    for md_file in MEMORY_DIR.rglob("*.md"):
        if md_file.name.startswith("."):
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
            score = _relevance_score(content, keywords)
            if score > 0:
                results.append({
                    "file": str(md_file.relative_to(MEMORY_DIR)),
                    "score": score,
                    "snippet": _extract_snippet(content, keywords, 150)
                })
        except:
            pass
    
    # 按相关性排序
    results.sort(key=lambda r: r["score"], reverse=True)
    
    # 去重（相似snippet只保留最相关的）
    filtered = []
    seen = set()
    for r in results:
        key = r["snippet"][:50]
        if key not in seen:
            filtered.append(r)
            seen.add(key)
    
    return filtered[:max_results]

def _extract_keywords(text):
    """从查询中提取关键词"""
    # Simple: split + filter common words
    common = {"的", "了", "是", "我", "你", "他", "她", "它", "们", "这", "那", "在", "不", "和", "就", "都", "也", "要", "会", "有", "说", "看", "去", "来", "给", "让", "把", "被", "对", "从", "到", "上", "下", "中", "与", "或", "但", "而", "且", "吗", "呢", "吧", "啊", "哦", "嗯", "呀"}
    keywords = []
    for w in re.split(r'[\s,，。！？、；：（）()\[\]【】]+', text):
        w = w.strip().lower()
        if len(w) >= 2 and w not in common:
            keywords.append(w)
    return keywords

def _relevance_score(content, keywords):
    """计算文本与关键词的相关性"""
    if not keywords:
        return 0
    content_lower = content.lower()
    score = 0
    for kw in keywords:
        count = content_lower.count(kw.lower())
        if count > 0:
            score += min(count, 5)  # 最多5分
    return score

def _extract_snippet(content, keywords, max_len=150):
    """提取包含关键词的上下文片段"""
    content_lower = content.lower()
    best_pos = -1
    best_score = 0
    
    for kw in keywords:
        pos = content_lower.find(kw.lower())
        if pos >= 0:
            near_kw = sum(1 for k in keywords if k.lower() in content_lower[max(0,pos-50):pos+50])
            if near_kw > best_score:
                best_score = near_kw
                best_pos = pos
    
    if best_pos < 0:
        return content[:max_len] + "..."
    
    start = max(0, best_pos - max_len // 2)
    end = min(len(content), best_pos + max_len // 2)
    snippet = content[start:end].replace("\n", " ").strip()
    
    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet = snippet + "..."
    
    return snippet[:max_len]

def recall_context(user_message, max_results=3):
    """为当前消息召回相关上下文"""
    results = search_memories(user_message, max_results)
    
    if not results:
        return None
    
    context = "📝 相关记忆:\n"
    for r in results:
        context += f"  [{r[file]}] {r[snippet]}\n"
    
    return context

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if cmd == "search":
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        if not query:
            print("Usage: memory_recall.py search <关键词>")
            sys.exit(1)
        
        results = search_memories(query)
        for r in results:
            print(f"[{r[file]}] score={r[score]}")
            print(f"  {r[snippet]}")
            print()
    
    elif cmd == "recall":
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        if not query:
            print("Usage: memory_recall.py recall <user消息>")
            sys.exit(1)
        
        ctx = recall_context(query)
        if ctx:
            print(ctx)
        else:
            print("(no relevant memories)")
    
    else:
        print("Usage: memory_recall.py [search|recall] <query>")
