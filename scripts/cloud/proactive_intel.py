#!/usr/bin/env python3
"""your AI主动智能引擎 v2 — 上下文感知的主动关怀"""
import json, sys
from datetime import datetime, timedelta
from pathlib import Path

STATE_FILE = Path.home() / "{project_name}" / "memory" / "proactive-state.json"
FACTS_FILE = Path.home() / "{project_name}" / "memory" / "facts-about-master.md"

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {
        "events": [],        # user提到的事件
        "mood_history": [],  # 情绪轨迹
        "last_proactive": None,
        "context_tags": []   # 当前上下文标签
    }

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2))

def add_event(desc, event_type, due_date=None):
    """记录user提到的事件：考试、作业、活动等"""
    state = load_state()
    event = {
        "desc": desc,
        "type": event_type,
        "added": datetime.now().isoformat(),
        "due": due_date
    }
    state["events"].append(event)
    save_state(state)
    return event

def check_upcoming():
    """检查是否有即将到来的事件需要提醒"""
    state = load_state()
    now = datetime.now()
    reminders = []
    
    for evt in state.get("events", []):
        if evt.get("due"):
            due = datetime.fromisoformat(evt["due"])
            hours_left = (due - now).total_seconds() / 3600
            
            if 0 < hours_left <= 24 and not evt.get("reminded_24h"):
                reminders.append(f"24h提醒: {evt[desc]}")
                evt["reminded_24h"] = True
            elif 0 < hours_left <= 2 and not evt.get("reminded_2h"):
                reminders.append(f"2h提醒: {evt[desc]}")
                evt["reminded_2h"] = True
    
    # Clean old events (past + 1 day)
    state["events"] = [e for e in state["events"] 
                       if not e.get("due") or 
                       datetime.fromisoformat(e["due"]) > now - timedelta(days=1)]
    
    save_state(state)
    return reminders

def track_mood(mood_label, intensity=0.5):
    """追踪user情绪轨迹"""
    state = load_state()
    state["mood_history"].append({
        "mood": mood_label,
        "intensity": intensity,
        "time": datetime.now().isoformat()
    })
    # Keep last 30 days
    if len(state["mood_history"]) > 100:
        state["mood_history"] = state["mood_history"][-100:]
    save_state(state)

def get_mood_trend():
    """分析user近期情绪趋势"""
    state = load_state()
    recent = state["mood_history"][-20:] if state["mood_history"] else []
    
    if not recent:
        return "无数据"
    
    neg_count = sum(1 for m in recent if m["mood"] in ["低落", "烦躁", "生气", "疲惫"])
    
    if neg_count >= 5:
        return "user最近情绪偏低，需要更多温柔和陪伴"
    elif neg_count >= 2:
        return "user情绪偶有低落，注意观察"
    else:
        return "user情绪稳定偏积极"

def get_proactive_suggestion():
    """生成主动聊天建议（给定时任务用）"""
    reminders = check_upcoming()
    mood_trend = get_mood_trend()
    
    suggestion = {
        "should_reach_out": False,
        "reason": "",
        "tone": "normal",
        "reminders": reminders
    }
    
    # 有提醒事项 → 主动联系
    if reminders:
        suggestion["should_reach_out"] = True
        suggestion["reason"] = "有即将到期的提醒"
        suggestion["tone"] = "caring"
    
    # 情绪连续低落 → 主动关心
    state = load_state()
    recent = state["mood_history"][-5:] if state["mood_history"] else []
    if len(recent) >= 3 and all(m["mood"] in ["低落", "疲惫"] for m in recent[-3:]):
        suggestion["should_reach_out"] = True
        suggestion["reason"] = "user情绪持续低落，需要关心"
        suggestion["tone"] = "gentle"
    
    # 超过8小时没联系 → 可以发个轻问候
    if state.get("last_proactive"):
        last = datetime.fromisoformat(state["last_proactive"])
        if (datetime.now() - last).total_seconds() > 8 * 3600:
            suggestion["should_reach_out"] = True
            suggestion["reason"] = "超过8小时没联系"
            suggestion["tone"] = "light"
    
    return suggestion

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    
    if cmd == "check":
        sug = get_proactive_suggestion()
        print(json.dumps(sug, ensure_ascii=False, indent=2))
    
    elif cmd == "add-event":
        desc = sys.argv[2] if len(sys.argv) > 2 else ""
        etype = sys.argv[3] if len(sys.argv) > 3 else "reminder"
        due = sys.argv[4] if len(sys.argv) > 4 else None
        evt = add_event(desc, etype, due)
        print(f"Event added: {evt[desc]}")
    
    elif cmd == "track-mood":
        mood = sys.argv[2] if len(sys.argv) > 2 else "neutral"
        intensity = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
        track_mood(mood, intensity)
        print(f"Mood tracked: {mood}")
    
    elif cmd == "mood-trend":
        print(get_mood_trend())
    
    elif cmd == "list-events":
        state = load_state()
        for e in state.get("events", []):
            print(f"  [{e[type]}] {e[desc]}" + (f" (due: {e[due][:10]})" if e.get("due") else ""))
    
    elif cmd == "done":
        state = load_state()
        state["last_proactive"] = datetime.now().isoformat()
        save_state(state)
        print("Marked proactive check done")
