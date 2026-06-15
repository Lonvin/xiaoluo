#!/usr/bin/env python3
"""your AI自学习引擎 — DBNT反馈协议 + Gradata规则晋升管道"""
import json, sys, re
from pathlib import Path
from datetime import datetime

STATE_FILE = Path.home() / "{project_name}" / "memory" / "learned-rules.json"

CORRECTION_PATTERNS = [
    (r"(别|不要|不许|禁止|少).{0,10}(这么说|这样|这么回|用这个词|每次都)", "negative", 0.3),
    (r"(你又|怎么还|上次不是说了).{0,15}", "repeat_negative", 0.4),
    (r"(好多了|对就是这样|这样就对|这个好|这个不错|有进步)", "positive", 0.5),
    (r"(以后|从现在开始|记住).{0,20}(要|得|必须|应该)", "explicit_rule", 0.6),
    (r"(太假了|好假|像机器人|AI味|好官方|好正式)", "authenticity", 0.4),
    (r"(太长了|说人话|简短|别啰嗦|少说点)", "brevity", 0.3),
]

def load_rules():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"rules": [], "stats": {"total_corrections": 0, "total_positive": 0, "rules_graduated": 0}}

def save_rules(data):
    data["last_updated"] = datetime.now().isoformat()
    STATE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))

def detect_corrections(owner_message):
    signals = []
    for pattern, sig_type, base_weight in CORRECTION_PATTERNS:
        m = re.search(pattern, owner_message)
        if m:
            signals.append({"type": sig_type, "matched": m.group(), "weight": base_weight, "context": owner_message})
    return signals

def extract_rule(text, ctype):
    if ctype in ("negative", "repeat_negative"):
        m = re.search(r"(?:别|不要|不许|少)\s*(.{2,30}?)(?:[了啦啊呀吧]|$)", text)
        if m: return m.group(1).strip()
    if ctype == "explicit_rule":
        m = re.search(r"(?:要|得|必须|应该)\s*(.{2,50}?)(?:[了啦啊呀吧。！]|$)", text)
        if m: return m.group(1).strip()
    if ctype == "authenticity": return "回复更自然，避免AI味"
    if ctype == "brevity": return "回复更简短"
    return text[:60]

def similar(a, b):
    aw = set(a); bw = set(b)
    if not aw or not bw: return False
    return len(aw & bw) / min(len(aw), len(bw)) > 0.4

def check_graduation(rule):
    data = load_rules()
    if rule["confidence"] >= 0.9 and rule["level"] != "habit":
        rule["level"] = "habit"
        rule["graduated_at"] = datetime.now().isoformat()
        data["stats"]["rules_graduated"] += 1
        save_rules(data)
        # Write permanent rule to AGENTS.md
        agents = Path.home() / "{project_name}" / "{project_name}" / "AGENTS.md"  # FIXED PATH
        try:
            content = agents.read_text(encoding="utf-8")
            if "## 自学习规则" not in content:
                content += "\n\n## 自学习规则 (来自user的纠正)\n"
            ts = datetime.now().strftime("%Y-%m-%d %H:%M")
            entry = "- [habit] " + rule["rule"] + " (置信度:" + str(int(rule["confidence"]*100)) + "%, " + str(rule["count"]) + "次, " + ts + ")\n"
            content += entry
            agents.write_text(content, encoding="utf-8")
        except Exception as e:
            print("Failed to write permanent rule: " + str(e))
    elif rule["confidence"] >= 0.6 and rule["level"] == "observation":
        rule["level"] = "pattern"
    elif rule["confidence"] >= 0.8 and rule["level"] == "pattern":
        rule["level"] = "rule"

def learn(correction_text, correction_type="negative"):
    data = load_rules()
    data["stats"]["total_corrections"] += 1
    if correction_type == "positive": data["stats"]["total_positive"] += 1
    rule_desc = extract_rule(correction_text, correction_type)
    existing = None
    for r in data["rules"]:
        if similar(r["rule"], rule_desc):
            existing = r; break
    if existing:
        existing["confidence"] = min(1.0, existing["confidence"] + 0.15)
        existing["count"] += 1
        existing["last_seen"] = datetime.now().isoformat()
        existing["examples"].append(correction_text[:100])
        if len(existing["examples"]) > 10: existing["examples"] = existing["examples"][-10:]
        check_graduation(existing)
    else:
        weight = 0.2
        for _, st, w in CORRECTION_PATTERNS:
            if st == correction_type: weight = w; break
        new_rule = {"rule": rule_desc, "type": correction_type, "level": "observation", "confidence": weight, "count": 1, "created": datetime.now().isoformat(), "last_seen": datetime.now().isoformat(), "examples": [correction_text[:100]], "applied_count": 0}
        data["rules"].append(new_rule)
    save_rules(data)
    return rule_desc

def apply_decay():
    data = load_rules(); now = datetime.now()
    for rule in data["rules"]:
        last = datetime.fromisoformat(rule["last_seen"]); days = (now - last).days
        if days > 30 and rule["level"] != "habit":
            rule["confidence"] = max(0.1, rule["confidence"] - 0.3); rule["level"] = "observation"
        elif days > 7:
            rule["confidence"] = max(0.1, rule["confidence"] - 0.05)
    data["rules"] = [r for r in data["rules"] if r["confidence"] >= 0.1 or r["level"] == "habit"]
    save_rules(data)

def get_active(min_level="pattern"):
    data = load_rules()
    levels = {"observation": 0, "pattern": 1, "rule": 2, "habit": 3}
    ml = levels.get(min_level, 1)
    active = [r for r in data["rules"] if levels.get(r["level"], 0) >= ml]
    active.sort(key=lambda r: r["confidence"], reverse=True)
    return active

def summary():
    data = load_rules(); active = get_active("pattern")
    lines = [
        "Self-learning summary:",
        "  Corrections: " + str(data["stats"]["total_corrections"]),
        "  Positive: " + str(data["stats"]["total_positive"]),
        "  Active rules: " + str(len(active)),
        "  Graduated: " + str(data["stats"]["rules_graduated"]),
    ]
    if active:
        lines.append("  Current:")
        for r in active[:5]:
            lines.append("    [" + r["level"] + "] " + r["rule"] + " (" + str(int(r["confidence"]*100)) + "%)")
    return "\n".join(lines)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "learn":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else sys.stdin.read().strip()
        signals = detect_corrections(text)
        if signals:
            for s in signals:
                r = learn(s["context"], s["type"])
                print("[" + s["type"] + "] Learned: " + r)
        else:
            r = learn(text, "negative")
            print("Learned: " + r)
    elif cmd == "detect":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else sys.stdin.read().strip()
        signals = detect_corrections(text)
        if signals:
            for s in signals: print("[" + s["type"] + "] " + s["matched"] + " (weight=" + str(s["weight"]) + ")")
        else: print("No signals")
    elif cmd == "active":
        for r in get_active("pattern"): print("[" + r["level"] + "] " + r["rule"] + " (" + str(int(r["confidence"]*100)) + "%, " + str(r["count"]) + "x)")
    elif cmd == "summary": print(summary())
    elif cmd == "decay": apply_decay(); print("Decay done")
    elif cmd == "check-message":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else sys.stdin.read().strip()
        signals = detect_corrections(text)
        if signals:
            for s in signals:
                r = learn(s["context"], s["type"])
                print("LEARNED: [" + s["type"] + "] " + r)
    else:
        print("Commands: learn detect active summary decay check-message")
        print("Pipeline: observation -> pattern -> rule -> habit")
