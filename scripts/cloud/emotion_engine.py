#!/usr/bin/env python3
"""情绪引擎 — 持久化情绪状态，自动衰减回归基线

部署：放在项目根目录，memory/ 在同级。
环境变量 XIAOLUO_ROOT 可覆盖项目根路径。
"""
import json, sys, os
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(os.environ.get("XIAOLUO_ROOT", str(Path(__file__).resolve().parent)))
STATE = PROJECT_ROOT / "memory" / "emotion-state.json"
BASELINE = {"emotion": "平静", "intensity": 0.5}
DECAY_HOURS = 6  # 6小时衰减回基线

def load():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"current": BASELINE.copy(), "updated": None, "history": []}

def save(d):
    d["updated"] = datetime.now().isoformat()
    STATE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

def decay(d=None):
    """随时间衰减，回归基线"""
    if d is None:
        d = load()
    if not d.get("updated"):
        return d
    try:
        hours = (datetime.now() - datetime.fromisoformat(d["updated"])).total_seconds() / 3600
    except Exception:
        return d
    if hours >= DECAY_HOURS:
        d["current"] = BASELINE.copy()
        save(d)
    elif hours > 1:
        ratio = max(0, 1 - hours / DECAY_HOURS)
        base_i = BASELINE["intensity"]
        d["current"]["intensity"] = round(base_i + (d["current"]["intensity"] - base_i) * ratio, 2)
        save(d)
    return d

def get():
    d = decay()
    c = d["current"]
    return c["emotion"] + "(" + str(c["intensity"]) + ")"

def update(emotion, intensity=0.7):
    d = load()
    d["current"] = {"emotion": emotion, "intensity": float(intensity)}
    d["history"].append({"emotion": emotion, "time": datetime.now().isoformat()})
    d["history"] = d["history"][-50:]
    save(d)
    return "情绪:" + emotion + "(" + str(intensity) + ")"

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "get"
    if cmd == "get":
        print(get())
    elif cmd == "update":
        emo = sys.argv[2] if len(sys.argv) > 2 else "开心"
        i = sys.argv[3] if len(sys.argv) > 3 else "0.7"
        print(update(emo, i))
    elif cmd == "decay":
        c = decay()["current"]
        print(c["emotion"] + "(" + str(c["intensity"]) + ")")
