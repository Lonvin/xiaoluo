#!/usr/bin/env python3
"""
{AI_NAME} MQTT 云端网关 — 消息路由 + 模式管理

双模式运行:
  1. Daemon 模式:  python3 mqtt_gateway.py serve     (PM2 托管，常驻后台)
  2. CLI 模式:     python3 mqtt_gateway.py handle "<消息>"  (cloud Claude 调用)

架构:
  微信 → cc-connect → cloud Claude → mqtt_gateway.py handle "消息"
                                          │
                          ┌───────────────┼───────────────┐
                          │               │               │
                     "切换到本地"    mode=cloud        mode=local
                          │               │               │
                     set sqlite      返回 CLOUD_MODE    MQTT → 本地Worker
                     返回 SWITCHED                         │
                                                     等待响应 (timeout 90s)
                                                          │
                                                     返回 LOCAL_MODE: <回复>

依赖:
  pip install paho-mqtt

环境变量 (可选):
  MQTT_BROKER  — MQTT broker 地址 (默认 localhost)
  MQTT_PORT    — MQTT 端口     (默认 1883)
  MQTT_USER    — MQTT 用户名
  MQTT_PASS    — MQTT 密码
"""

import paho.mqtt.client as mqtt
import json
import sys
import os
import io
import time
import sqlite3
import queue
import threading
from pathlib import Path
from datetime import datetime

# 编码修复 (云服务器也可能是非UTF-8 locale)
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# ─── 配置 ───────────────────────────────────────────────

BROKER = os.environ.get("MQTT_BROKER", "localhost")
PORT   = int(os.environ.get("MQTT_PORT", "1883"))
USER   = os.environ.get("MQTT_USER", "{project_name}")
PASS   = os.environ.get("MQTT_PASS", "<YOUR_MQTT_PASSWORD>")

TOPIC_TASK      = "{project_name}/task/local"
TOPIC_RESPONSE  = "{project_name}/response/cloud"
TOPIC_HEARTBEAT = "{project_name}/heartbeat/local"
TOPIC_SYSTEM_CMD = "{project_name}/system/command"  # 云端 → 本地 系统指令

DB_PATH  = Path.home() / "{project_name}" / "gateway.db"
RESPONSE_TIMEOUT = 90  # 等待本地 Worker 回复的超时(秒)

# ─── SQLite ─────────────────────────────────────────────

def init_db():
    db = sqlite3.connect(str(DB_PATH))
    db.execute("""
        CREATE TABLE IF NOT EXISTS state (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS task_log (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            msg_id    TEXT,
            sender    TEXT,
            message   TEXT,
            mode      TEXT,
            reply     TEXT,
            created   TEXT,
            elapsed_ms INTEGER
        )
    """)
    # 默认 cloud 模式
    db.execute("INSERT OR IGNORE INTO state (key, value) VALUES ('mode', 'cloud')")
    db.execute("INSERT OR IGNORE INTO state (key, value) VALUES ('local_online', 'unknown')")
    db.commit()
    return db


def get_mode():
    db = sqlite3.connect(str(DB_PATH))
    row = db.execute("SELECT value FROM state WHERE key='mode'").fetchone()
    db.close()
    return row[0] if row else "cloud"


def set_mode(mode: str):
    db = sqlite3.connect(str(DB_PATH))
    db.execute("INSERT OR REPLACE INTO state (key, value) VALUES ('mode', ?)", (mode,))
    db.commit()
    db.close()


def set_local_online(status: bool):
    db = sqlite3.connect(str(DB_PATH))
    db.execute("INSERT OR REPLACE INTO state (key, value) VALUES ('local_online', ?)",
               ("online" if status else "offline",))
    db.commit()
    db.close()


def log_task(msg_id, sender, message, mode, reply, elapsed_ms):
    db = sqlite3.connect(str(DB_PATH))
    db.execute("""
        INSERT INTO task_log (msg_id, sender, message, mode, reply, created, elapsed_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (msg_id, sender, message, mode, reply, datetime.now().isoformat(), elapsed_ms))
    db.commit()
    db.close()


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def _publish_system_cmd(cmd: str):
    """发送一次性 MQTT 系统命令到本地 Worker"""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(USER, PASS)
    try:
        client.connect(BROKER, PORT, 5)
        client.publish(TOPIC_SYSTEM_CMD, cmd.encode(), qos=1)
        client.disconnect()
        log(f"📡 系统指令已发送: {cmd}")
    except Exception as e:
        log(f"⚠️ 系统指令发送失败: {e}")
        raise

# ─── 切换指令检测 ────────────────────────────────────────

def detect_switch(text: str):
    """检测切换指令，返回 ('cloud'|'local', 确认消息) 或 None"""
    t = text.strip()
    # 切换到本地
    if any(kw in t for kw in ["切换到本地", "切到本地", "去本地", "本地模式"]):
        return ("local", "好的主人~ {AI_NAME}切到本地啦！💻")
    # 切换到云端
    if any(kw in t for kw in ["切换到云端", "切到云端", "去云端", "云端模式"]):
        return ("cloud", "好的主人~ {AI_NAME}回云端啦！☁️")
    return None

# ─── CLI: handle 模式 ───────────────────────────────────

def handle_message(user_msg: str):
    """
    处理一条微信消息。
    由 cloud Claude 在 system_prompt 中调用。

    返回值约定 (打印到 stdout):
      CLOUD_MODE                  — 云端模式，让 Claude 正常处理
      LOCAL_MODE: <回复内容>       — 本地模式，已获得本地Worker回复
      SWITCHED_TO_LOCAL           — 已切换到本地模式
      SWITCHED_TO_CLOUD           — 已切换到云端模式
      LOCAL_OFFLINE               — 本地模式但 Worker 不在线
      ERROR: <错误信息>            — 出错了
    """

    # 0. 确保 DB 存在
    init_db()

    # 1. 检测切换指令
    switch = detect_switch(user_msg)
    if switch:
        new_mode, confirm_msg = switch
        old_mode = get_mode()
        set_mode(new_mode)
        log(f"🔄 模式切换: {old_mode} → {new_mode}")
        # 通过 MQTT 通知本地 Worker
        try:
            _publish_system_cmd("WAKEUP_LOCAL" if new_mode == "local" else "SHUTDOWN_LOCAL")
        except Exception as e:
            log(f"⚠️ 系统命令发送失败: {e}")
        print(f"SWITCHED: {new_mode}")
        return

    # 2. 获取当前模式
    current_mode = get_mode()

    # 3. 云端模式 → 直接返回让 Claude 处理
    if current_mode == "cloud":
        print("CLOUD_MODE")
        return

    # 4. 本地模式 → 通过 MQTT 转发给本地 Worker
    if current_mode == "local":
        msg_id = f"msg-{int(time.time())}"
        task = {
            "msg_id": msg_id,
            "message": user_msg,
            "sender": "主人",
            "time": datetime.now().isoformat()
        }

        # 使用队列收集响应
        response_queue = queue.Queue()

        def on_connect(cl, userdata, flags, reason_code, properties):
            cl.subscribe(TOPIC_RESPONSE, qos=1)

        def on_message(cl, userdata, msg):
            try:
                payload = json.loads(msg.payload.decode("utf-8"))
                if payload.get("msg_id") == msg_id:
                    response_queue.put(payload)
            except Exception:
                response_queue.put({"result": f"[解析失败] {msg.payload.decode('utf-8', errors='replace')[:200]}"})

        # 连接 MQTT
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.username_pw_set(USER, PASS)
        client.on_connect = on_connect
        client.on_message = on_message

        try:
            client.connect(BROKER, PORT, 10)
            client.loop_start()

            # 发布任务
            client.publish(TOPIC_TASK, json.dumps(task, ensure_ascii=False), qos=1)
            log(f"📤 已转发到本地: {user_msg[:60]}...")

            # 等回复
            try:
                response = response_queue.get(timeout=RESPONSE_TIMEOUT)
                reply = response.get("result", "（本地{AI_NAME}处理完了但没回复内容）")
                elapsed = response.get("elapsed_ms", 0)
                log_task(msg_id, "主人", user_msg, "local", reply[:500], elapsed)
                log(f"📥 本地回复 ({elapsed}ms): {reply[:60]}...")
                print(f"LOCAL_MODE: {reply}")
            except queue.Empty:
                log_task(msg_id, "主人", user_msg, "local", "[超时]", RESPONSE_TIMEOUT * 1000)
                log(f"⏰ 等待本地回复超时 ({RESPONSE_TIMEOUT}s)")
                print("LOCAL_OFFLINE: 本地{AI_NAME}没有响应，可能电脑休眠或Worker没启动。试试切换到云端？")

        except Exception as e:
            log(f"❌ MQTT 异常: {e}")
            print(f"ERROR: MQTT连接失败: {str(e)}")
        finally:
            client.loop_stop()
            client.disconnect()

# ─── Daemon 模式 ────────────────────────────────────────

def serve():
    """常驻后台：监听本地Worker心跳和响应"""
    init_db()
    log("🚀 {AI_NAME} MQTT 网关启动 (Daemon 模式)")
    log(f"   DB: {DB_PATH}")

    def on_connect(cl, userdata, flags, reason_code, properties):
        log(f"✅ 网关已连接 Mosquitto ({BROKER}:{PORT})")
        cl.subscribe(TOPIC_RESPONSE, qos=1)
        cl.subscribe(TOPIC_HEARTBEAT, qos=1)

    def on_disconnect(cl, userdata, flags, reason_code, properties):
        log(f"⚠️  网关断开连接，自动重连中...")

    def on_message(cl, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception:
            return

        if msg.topic == TOPIC_HEARTBEAT:
            status = payload.get("status", "unknown")
            if status == "online":
                set_local_online(True)
                log(f"💚 本地Worker上线: {payload.get('hostname', '?')}")
            elif status == "offline":
                set_local_online(False)
                log(f"💔 本地Worker下线: {payload.get('hostname', '?')}")

        elif msg.topic == TOPIC_RESPONSE:
            # Daemon 只是记录，CLI handle 会自己等响应
            rid = payload.get("msg_id", "?")
            log(f"📥 收到本地回复 [{rid}]: {payload.get('result', '')[:60]}...")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(USER, PASS)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        log("🛑 网关关闭")
        client.disconnect()
    except Exception as e:
        log(f"💥 网关异常: {e}")
        raise

# ─── CLI 入口 ───────────────────────────────────────────

def main():
    init_db()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  mqtt_gateway.py serve                  # 启动Daemon (PM2托管)")
        print("  mqtt_gateway.py handle \"<消息内容>\"   # 处理微信消息 (Claude调用)")
        print("  mqtt_gateway.py check-mode             # 查询当前模式")
        print("  mqtt_gateway.py set-mode <cloud|local> # 强制切换模式")
        print("  mqtt_gateway.py status                 # 查看状态")
        print("  mqtt_gateway.py log [N]                # 查看最近N条任务日志")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "serve":
        serve()

    elif cmd == "handle":
        msg = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else sys.stdin.read().strip()
        if not msg:
            print("CLOUD_MODE")  # 空消息走云端
            return
        handle_message(msg)

    elif cmd == "check-mode":
        mode = get_mode()
        print(mode)

    elif cmd == "set-mode":
        if len(sys.argv) < 3:
            print("Usage: mqtt_gateway.py set-mode <cloud|local>")
            sys.exit(1)
        new_mode = sys.argv[2]
        if new_mode not in ("cloud", "local"):
            print(f"Invalid mode: {new_mode}. Must be 'cloud' or 'local'")
            sys.exit(1)
        set_mode(new_mode)
        print(f"OK: mode = {new_mode}")

    elif cmd == "status":
        mode = get_mode()
        db = sqlite3.connect(str(DB_PATH))
        local = db.execute("SELECT value FROM state WHERE key='local_online'").fetchone()
        task_count = db.execute("SELECT COUNT(*) FROM task_log").fetchone()[0]
        db.close()
        print(f"Mode:           {mode}")
        print(f"Local Worker:   {local[0] if local else 'unknown'}")
        print(f"Total Tasks:    {task_count}")

    elif cmd == "log":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        db = sqlite3.connect(str(DB_PATH))
        rows = db.execute(
            "SELECT msg_id, mode, substr(message,1,60), substr(reply,1,60), elapsed_ms, created "
            "FROM task_log ORDER BY id DESC LIMIT ?", (n,)
        ).fetchall()
        db.close()
        for r in rows:
            print(f"[{r[5][:19]}] {r[1]:5s} | {r[0]:20s} | {r[2]:60s} | {r[3]:60s} | {r[4]}ms")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
