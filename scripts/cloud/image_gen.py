#!/usr/bin/env python3
"""your AI图片生成 — 用硅基流动/千问生成图片发给user"""
import os, sys, json, time, base64, urllib.request, ssl
from pathlib import Path

IMG_DIR = Path.home() / "{project_name}" / "generated_images"
IMG_DIR.mkdir(exist_ok=True)

# 硅基流动 (SiliconFlow) — 免费额度，多种模型
SILICON_KEY = "你的硅基流动API_KEY"  # https://siliconflow.cn
SILICON_URL = "https://api.siliconflow.cn/v1/image/generations"

MODELS = {
    "fast": "stabilityai/stable-diffusion-3-5-large",     # 快+好
    "best": "black-forest-labs/FLUX.1-dev",                # 质量最高
    "anime": "stabilityai/stable-diffusion-3-5-large",     # 二次元风格
    "quick": "stabilityai/sd-turbo",                       # 超快
}

def generate_image(prompt, model="fast", size="1024x1024"):
    """生成图片，返回文件路径"""
    payload = json.dumps({
        "model": MODELS.get(model, MODELS["fast"]),
        "prompt": prompt,
        "num_images": 1,
        "image_size": size,
        "negative_prompt": "nsfw, nude, violence, gore, ugly, bad quality, blurry"
    }).encode()
    
    req = urllib.request.Request(SILICON_URL, data=payload, headers={
        "Authorization": f"Bearer {SILICON_KEY}",
        "Content-Type": "application/json"
    })
    
    try:
        ctx = ssl._create_unverified_context()
        resp = urllib.request.urlopen(req, context=ctx, timeout=120)
        result = json.loads(resp.read())
        
        # 硅基返回 base64 图片
        images = result.get("images", [])
        if not images:
            # 尝试从 data 字段获取
            data = result.get("data", [])
            if data:
                b64 = data[0].get("b64_json") or data[0].get("url", "")
            else:
                print(f"Unexpected response: {json.dumps(result, ensure_ascii=False)[:300]}")
                return None
        else:
            b64 = images[0].get("b64_json") or images[0].get("url", "")
        
        if not b64:
            print("No image data in response")
            return None
        
        # 如果是URL就下载，如果是base64就解码
        if b64.startswith("http"):
            img_data = urllib.request.urlopen(b64, context=ctx).read()
        else:
            img_data = base64.b64decode(b64)
        
        fname = f"img_{int(time.time())}.png"
        fpath = str(IMG_DIR / fname)
        with open(fpath, "wb") as f:
            f.write(img_data)
        
        return fpath
    
    except urllib.error.HTTPError as e:
        print(f"Image API HTTP {e.code}: {e.read().decode()[:200]}")
        return None
    except Exception as e:
        print(f"Image generation failed: {e}")
        return None

def generate_and_send(prompt, model="fast"):
    """生成图片并发送到微信"""
    fpath = generate_image(prompt, model)
    if not fpath:
        return False
    
    import subprocess
    result = subprocess.run(
        ["cc-connect", "send", "-m", f"user看这个～ {prompt[:50]}", "--image", fpath],
        capture_output=True, timeout=30
    )
    
    if result.returncode == 0:
        print(f"Image sent: {fpath}")
        return True
    else:
        # 只发图
        result2 = subprocess.run(
            ["cc-connect", "send", "--image", fpath],
            capture_output=True, timeout=30
        )
        print(f"Image sent (image only): {fpath}")
        return True

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if cmd == "generate":
        prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "一只可爱的卡通小猫"
        model = "fast"
        fpath = generate_image(prompt, model)
        if fpath:
            print(f"Generated: {fpath}")
    
    elif cmd == "send":
        prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "一只可爱的卡通小猫"
        generate_and_send(prompt)
    
    elif cmd == "list":
        files = sorted(IMG_DIR.glob("*.png"), key=os.path.getmtime, reverse=True)
        for f in files[:10]:
            print(f"{f.name} ({os.path.getsize(f)} bytes)")
    
    else:
        print("Usage: image_gen.py [generate|send|list] [prompt]")
        print("Models: fast, best, anime, quick")
