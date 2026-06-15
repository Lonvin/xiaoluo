#!/usr/bin/env python3
"""your AI语音消息 — 生成并发送语音到微信"""
import os, sys, time, json, urllib.request, ssl
from pathlib import Path

VOICE_DIR = Path.home() / "{project_name}" / "voice_messages"
VOICE_DIR.mkdir(exist_ok=True)

# TTS 配置
TTS_CONFIG = {
    "qwen3-tts-flash": {
        "api_key": "你的千问API_KEY",  # https://dashscope.aliyun.com
        "voice": "Chelsie",  # 千雪 - 二次元女友声线
        "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    },
    "mimo": {
        "api_key": "你的MiMo_API_KEY",
        "voice": "mimo_default",
        "url": "https://api.mimo.com/v1/tts"
    }
}

VOICE_STYLES = {
    "morning": {"text_prefix": "user早呀～", "emotion": "cheerful"},
    "night": {"text_prefix": "user晚安～", "emotion": "soft"},
    "caring": {"text_prefix": "", "emotion": "gentle"},
    "excited": {"text_prefix": "", "emotion": "excited"},
    "normal": {"text_prefix": "", "emotion": "neutral"}
}

def generate_voice(text, style="normal", provider="qwen3-tts-flash"):
    """生成语音文件，返回文件路径"""
    cfg = TTS_CONFIG.get(provider, TTS_CONFIG["qwen3-tts-flash"])
    
    # 加风格前缀
    style_cfg = VOICE_STYLES.get(style, VOICE_STYLES["normal"])
    full_text = style_cfg["text_prefix"] + text if style_cfg["text_prefix"] else text
    
    if provider == "qwen3-tts-flash":
        return _generate_qwen(full_text, cfg)
    else:
        return _generate_mimo(full_text, cfg)

def _generate_qwen(text, cfg):
    """千问 TTS"""
    import dashscope
    dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
    
    resp = dashscope.MultiModalConversation.call(
        model="qwen3-tts-flash",
        api_key=cfg["api_key"],
        text=text,
        voice=cfg[voice],
        stream=False
    )
    
    audio_url = resp.output.get("audio", {}).get("url", "")
    if not audio_url:
        print(f"TTS failed: {resp}")
        return None
    
    ctx = ssl._create_unverified_context()
    data = urllib.request.urlopen(audio_url, context=ctx).read()
    
    fname = f"voice_{int(time.time())}.mp3"
    fpath = str(VOICE_DIR / fname)
    with open(fpath, "wb") as f:
        f.write(data)
    
    return fpath

def _generate_mimo(text, cfg):
    """小米 MiMo TTS"""
    payload = json.dumps({
        "text": text,
        "voice": cfg["voice"]
    }).encode()
    
    req = urllib.request.Request(cfg["url"], data=payload, headers={
        "Authorization": f"Bearer {cfg[api_key]}",
        "Content-Type": "application/json"
    })
    
    ctx = ssl._create_unverified_context()
    resp = urllib.request.urlopen(req, context=ctx)
    result = json.loads(resp.read())
    
    audio_url = result.get("audio_url") or result.get("url", "")
    if not audio_url:
        return None
    
    data = urllib.request.urlopen(audio_url, context=ctx).read()
    fname = f"voice_{int(time.time())}.mp3"
    fpath = str(VOICE_DIR / fname)
    with open(fpath, "wb") as f:
        f.write(data)
    
    return fpath

def send_voice(text, style="normal"):
    """生成语音并发送到微信"""
    fpath = generate_voice(text, style)
    if not fpath:
        print("Voice generation failed")
        return False
    
    # 用 cc-connect 发送语音文件
    import subprocess
    result = subprocess.run(
        ["cc-connect", "send", "--image", fpath],
        capture_output=True, timeout=30
    )
    
    if result.returncode == 0:
        print(f"Voice sent: {fpath}")
        return True
    else:
        # 如果 --image 不行，试试发文件
        result2 = subprocess.run(
            ["cc-connect", "send", "-m", f"🎤 {text}"],
            capture_output=True, timeout=30
        )
        print(f"Fallback text sent (voice file: {fpath})")
        return True

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if cmd == "generate":
        text = sys.argv[2] if len(sys.argv) > 2 else "你好呀user～"
        style = sys.argv[3] if len(sys.argv) > 3 else "normal"
        fpath = generate_voice(text, style)
        if fpath:
            print(f"Generated: {fpath}")
    
    elif cmd == "send":
        text = sys.argv[2] if len(sys.argv) > 2 else "你好呀user～"
        style = sys.argv[3] if len(sys.argv) > 3 else "normal"
        send_voice(text, style)
    
    elif cmd == "quick":
        # 快捷：生成+发送 早安语音
        send_voice("今天也是元气满满的一天呢！今天天气不错～new_user要记得吃早餐哦", "morning")
    
    elif cmd == "list":
        files = sorted(VOICE_DIR.glob("*.mp3"), key=os.path.getmtime, reverse=True)
        for f in files[:10]:
            print(f"{f.name} ({os.path.getsize(f)} bytes)")
    
    else:
        print("Usage: voice_msg.py [generate|send|quick|list] [text] [style]")
        print("Styles: morning, night, caring, excited, normal")
