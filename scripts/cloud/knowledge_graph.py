#!/usr/bin/env python3
"""your AI知识图谱"""
import json, sys
from pathlib import Path
from datetime import datetime

KG_FILE = Path.home() / "{project_name}" / "memory" / "knowledge-graph.json"

def load():
    if KG_FILE.exists():
        return json.loads(KG_FILE.read_text())
    return {"entities": {}, "relations": [], "last_updated": None}

def save(kg):
    kg["last_updated"] = datetime.now().isoformat()
    KG_FILE.write_text(json.dumps(kg, ensure_ascii=False, indent=2))

def add_entity(name, etype, props=None):
    kg = load()
    if name not in kg["entities"]:
        kg["entities"][name] = {"type": etype, "props": props or {}, "added": datetime.now().isoformat()}
    elif props:
        kg["entities"][name]["props"].update(props)
    save(kg)
    return "OK: " + name

def add_relation(src, rel, dst):
    kg = load()
    for e, t in [(src, "thing"), (dst, "thing")]:
        if e not in kg["entities"]:
            kg["entities"][e] = {"type": t, "props": {}, "added": datetime.now().isoformat()}
    kg["relations"].append({"src": src, "rel": rel, "dst": dst, "added": datetime.now().isoformat()})
    save(kg)
    return src + " --" + rel + "--> " + dst

def query(name):
    kg = load()
    if name not in kg["entities"]:
        return "Unknown: " + name
    e = kg["entities"][name]
    lines = [name + " (" + e["type"] + ")"]
    for k, v in e["props"].items():
        lines.append("  " + k + ": " + str(v))
    rels = [r for r in kg["relations"] if r["src"] == name or r["dst"] == name]
    if rels:
        lines.append("  关联:")
        for r in rels:
            if r["src"] == name:
                lines.append("    -> " + r["rel"] + " -> " + r["dst"])
            else:
                lines.append("    <- " + r["rel"] + " <- " + r["src"])
    return "\n".join(lines)

def init_master():
    kg = load()
    # user
    add_entity("user", "person", {"location": "你的城市", "school": "你的学校"})
    # 课程 — 改成你自己的
    courses = [
        ("课程名1", "教室号", "周一8:00"),
        ("课程名2", "教室号", "周一10:15"),
        ("课程名3", "教室号", "周二8:00"),
        ("课程名4", "教室号", "周三14:00"),
    ]
    for cname, room, tslot in courses:
        add_entity(cname, "course", {"room": room, "time": tslot})
        add_relation("user", "上课", cname)
        if room != "待通知":
            add_entity(room, "classroom", {})
            add_relation(cname, "地点", room)
    # your AI
    add_entity("your AI", "assistant", {"age": 22, "style": "温柔可爱"})
    add_relation("your AI", "帮助", "user")
    print("KG: " + str(len(kg["entities"])) + " entities, " + str(len(kg["relations"])) + " relations")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "init":
        init_master()
    elif cmd == "add-entity":
        add_entity(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "thing")
    elif cmd == "add-rel":
        add_relation(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "query":
        print(query(sys.argv[2] if len(sys.argv) > 2 else "user"))
    elif cmd == "stats":
        kg = load()
        print("Entities: " + str(len(kg["entities"])) + "  Relations: " + str(len(kg["relations"])))
    else:
        print("Commands: init add-entity add-rel query stats")
