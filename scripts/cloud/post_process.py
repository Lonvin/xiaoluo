import re
import random
import time

def sillytavern_style_process(text):
    """
    酒馆核心技术：输出后暴力矫正
    不管模型输出什么，最后都改成人话
    """

    # ========== 1. 删除所有AI话术 ==========
    bad_words = [
        '好的', '当然', '没问题', '请问', '建议', '综上所述',
        '首先', '其次', '最后', '作为AI', '根据我的', '很高兴',
        '收到', '没问题', '当然可以', '帮你', '为你'
    ]
    for word in bad_words:
        text = text.replace(word, '')

    # ========== 2. 删除所有标点符号 ==========
    text = re.sub(r'[，。？！、；：""''（）【】]', '', text)

    # ========== 3. 5%概率直接丢弃（模拟打了又删） ==========
    if random.random() < 0.05:
        return []  # 什么都不发

    # ========== 4. 超过12字强行拆分，分多条发 ==========
    messages = []
    if len(text) > 12:
        # 从中间切开
        mid = len(text) // 2
        # 找最近的空格切开
        while mid < len(text) and text[mid] != ' ' and mid - len(text) < 5:
            mid += 1
        messages.append(text[:mid].strip())
        messages.append(text[mid:].strip())
    else:
        messages.append(text.strip())

    # ========== 5. 12%概率随机打错字 ==========
    if random.random() < 0.12:
        typos = {'呢': '捏', '了': '啦', '哈': '害', '怎': '咋', '的': '滴', '我': '窝'}
        for i, msg in enumerate(messages):
            for old, new in typos.items():
                if old in msg and random.random() < 0.3:
                    messages[i] = msg.replace(old, new, 1)
                    break

    # ========== 6. 15%概率结尾加哈哈 ==========
    if random.random() < 0.15 and messages:
        messages[-1] += ' 哈哈'

    # ========== 7. 过滤空消息 ==========
    messages = [m for m in messages if m.strip()]

    return messages


def get_send_delays(messages):
    """每条消息之间的发送延迟（真人打字速度）"""
    delays = []
    for msg in messages:
        delay = max(0.5, min(len(msg) * 0.15, 3))
        delay += random.uniform(-0.2, 0.4)
        delays.append(max(0.3, delay))
    return delays
