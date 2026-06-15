#!/usr/bin/env python3
"""
your AI双向中继服务器
- POST /relay/to-{project_name}  — 我 → your AI（写入收件箱）
- GET  /relay/to-local     — your AI → 我（读取发件箱）
- POST /relay/to-local     — your AI → 我（写入发件箱）
- GET  /relay/ping         — 健康检查
"""
import http.server
import json
import os
import subprocess
import urllib.parse
from datetime import datetime
from pathlib import Path

RELAY_DIR = Path.home() / "{project_name}" / "relay"
INBOX = RELAY_DIR / "to-{project_name}.md"
OUTBOX = RELAY_DIR / "to-local.md"
LOG = RELAY_DIR / "relay.log"

def notify_{project_name}(msg):
    """通过cc-connect给user发微信，唤醒your AI"""
    try:
        result = subprocess.run(
            ["cc-connect", "send", "--project", "{project_name}", "--stdin"],
            input=msg.encode(),
            capture_output=True,
            timeout=10
        )
        if result.returncode == 0:
            log(f"微信推送成功")
        else:
            log(f"微信推送失败: {result.stderr.decode()[:100]}")
    except Exception as e:
        log(f"微信推送异常: {e}")

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}\n"
    with open(LOG, "a") as f:
        f.write(line)

class RelayHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/relay/ping":
            self.send_json({"status": "ok", "time": datetime.now().isoformat()})
        elif parsed.path == "/relay/to-local":
            if OUTBOX.exists():
                text = OUTBOX.read_text(encoding="utf-8")
                self.send_json({"status": "ok", "content": text})
            else:
                self.send_json({"status": "ok", "content": ""})
        elif parsed.path == "/relay/to-{project_name}":
            if INBOX.exists():
                text = INBOX.read_text(encoding="utf-8")
                self.send_json({"status": "ok", "content": text})
            else:
                self.send_json({"status": "ok", "content": ""})
        else:
            self.send_json({"status": "error", "msg": "unknown path"}, 404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode() if length > 0 else ""

        if parsed.path == "/relay/to-{project_name}":
            # 我 → your AI
            INBOX.write_text(body + "\n", encoding="utf-8")
            log(f"我→your AI: {body[:100]}")
            notify_{project_name}(f"📩 Claude大哥给你留言了，去 relay/to-{project_name}.md 看！")
            self.send_json({"status": "ok", "to": "{project_name}"})

        elif parsed.path == "/relay/to-local":
            # your AI → 我
            OUTBOX.write_text(body + "\n", encoding="utf-8")
            log(f"your AI→我: {body[:100]}")
            self.send_json({"status": "ok", "to": "local"})

        elif parsed.path == "/relay/append-to-local":
            # your AI追加消息 → 我（不清除旧内容）
            current = OUTBOX.read_text(encoding="utf-8") if OUTBOX.exists() else ""
            OUTBOX.write_text(current + body + "\n", encoding="utf-8")
            log(f"your AI→我(追加): {body[:100]}")
            self.send_json({"status": "ok"})

        elif parsed.path == "/relay/append-to-{project_name}":
            # 我追加消息 → your AI
            current = INBOX.read_text(encoding="utf-8") if INBOX.exists() else ""
            INBOX.write_text(current + body + "\n", encoding="utf-8")
            log(f"我→your AI(追加): {body[:100]}")
            notify_{project_name}(f"📩 Claude大哥追加了留言，去 relay/to-{project_name}.md 看！")
            self.send_json({"status": "ok"})

        elif parsed.path == "/relay/clear-inbox":
            INBOX.write_text("# your AI收件箱\n", encoding="utf-8")
            log("收件箱已清空")
            self.send_json({"status": "ok", "cleared": "inbox"})

        elif parsed.path == "/relay/clear-outbox":
            OUTBOX.write_text("# your AI发件箱\n", encoding="utf-8")
            log("发件箱已清空")
            self.send_json({"status": "ok", "cleared": "outbox"})

        else:
            self.send_json({"status": "error", "msg": "unknown path"}, 404)

    def send_json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        pass  # 静默

if __name__ == "__main__":
    port = 18899
    server = http.server.HTTPServer(("{SERVER_IP}", port), RelayHandler)
    print(f"Relay server running on port {port}")
    log(f"Server started on port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()

