import re

# 酒馆式世界书：关键词触发 → 人格注入
WORLD_BOOK = [
    {
        'keywords': r'熬夜|三点|四点|五点|没睡',
        'personality': '（示例）催主人睡觉，语气由SOUL.md决定不要客气。'
    },
    {
        'keywords': r'bug|报错|debug|卡死|写代码|编译',
        'personality': '（示例）主人在写代码，可以关心或调侃，风格见SOUL.md不用安慰。'
    },
    {
        'keywords': r'吃饭|饿|外卖|火锅|奶茶',
        'personality': '关心主人的饮食健康。可以啰嗦一点。'
    },
    {
        'keywords': r'游戏|赢了|输了|上分|掉分',
        'personality': '开启兄弟模式。可以说666，可以说菜狗，可以互怼。'
    },
]


def inject_personality(user_message, system_prompt):
    """
    根据用户消息关键词，动态注入人格
    这就是酒馆比向量检索聪明的地方
    """
    extra_personality = []

    for entry in WORLD_BOOK:
        if re.search(entry['keywords'], user_message, re.IGNORECASE):
            extra_personality.append(entry['personality'])

    if extra_personality:
        return system_prompt + '\n\n【当前场景注入】\n' + '\n'.join(extra_personality)

    return system_prompt

