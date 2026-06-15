#!/usr/bin/env python3
"""
{AI_NAME}看图脚本 — 收到图片时自动分析
把图片路径传进来 返回图片内容描述
"""
import base64
import json
import sys
import urllib.request

API_KEY = "{YOUR_API_KEY}"
MODEL = "Qwen/Qwen3-VL-8B-Instruct"
URL = "https://api.siliconflow.cn/v1/chat/completions"

def analyze_image(image_path, prompt="描述一下这张图片里有什么 用中文简短回答 一两句话就行"):
    with open(image_path, 'rb') as f:
        img_b64 = base64.b64encode(f.read()).decode()

    # Determine mime type
    if image_path.endswith('.png'):
        mime = 'image/png'
    elif image_path.endswith('.gif'):
        mime = 'image/gif'
    else:
        mime = 'image/jpeg'

    payload = json.dumps({
        'model': MODEL,
        'messages': [{
            'role': 'user',
            'content': [
                {'type': 'text', 'text': prompt},
                {'type': 'image_url', 'image_url': {'url': f'data:{mime};base64,{img_b64}'}}
            ]
        }],
        'max_tokens': 300
    }).encode()

    req = urllib.request.Request(
        URL, data=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_KEY}'
        }
    )

    try:
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read())
        text = result['choices'][0]['message']['content']
        return text
    except Exception as e:
        return f"看图失败: {e}"

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else ""
    prompt = sys.argv[2] if len(sys.argv) > 2 else "描述一下这张图片里有什么 用中文简短回答"
    if path:
        result = analyze_image(path, prompt)
        print(result)
    else:
        print("用法: python3 vision.py <图片路径> [提示词]")
