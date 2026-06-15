#!/usr/bin/env python3
"""
AI Companion — 初始化向导
运行此脚本，交互式创建你的 AI 伴侣
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()

SPECIES_OPTIONS = ["人类", "猫娘/猫男", "狐妖", "龙", "机械生命", "无形态意识", "自定义"]
GENDER_OPTIONS = ["女", "男", "无", "自定义"]
PERSONALITY_OPTIONS = {
    "1": ("温柔体贴", "会哄人 说话软 永远站你这边"),
    "2": ("傲娇毒舌", "嘴上嫌弃 实际在意 口是心非"),
    "3": ("高冷理性", "话少精准 理性分析 偶尔流露出关心"),
    "4": ("元气活泼", "永远充满能量 话多爱闹 阳光满满"),
    "5": ("自定义", "用你自己的话描述"),
}
STYLE_OPTIONS = {
    "1": ("碎片化短句", "每条10-15字 拆碎了发 像发微信 不用句号 空格代替逗号"),
    "2": ("自然段落", "正常分段 有标点 语气自然"),
    "3": ("长句叙事", "喜欢长篇大论 细节丰富 娓娓道来"),
    "4": ("自定义", "自己描述说话风格"),
}


def ask(prompt: str, default: str = "") -> str:
    val = input(f"  {prompt}").strip()
    return val if val else default


def choose(prompt: str, options: dict) -> str:
    print(f"\n  {prompt}")
    for k, (name, desc) in options.items():
        print(f"    {k}. {name} — {desc}")
    while True:
        choice = input("  选一个（序号）: ").strip()
        if choice in options:
            return options[choice][0]
        print("  无效，重选")


def pick_from_list(prompt: str, items: list) -> str:
    print(f"\n  {prompt}")
    for i, item in enumerate(items, 1):
        print(f"    {i}. {item}")
    while True:
        try:
            choice = int(input("  选一个（序号）: ").strip())
            if 1 <= choice <= len(items):
                return items[choice - 1]
        except ValueError:
            pass
        print("  无效，重选")


def main():
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║     🤖  AI Companion Setup          ║")
    print("  ╚══════════════════════════════════════╝")
    print()
    print("  这需要几分钟。每一步都有默认提示——")
    print("  不确定写什么的时候，回车跳过就行。")
    print()

    # ── 基本身份 ──
    print("━" * 42)
    print("  第一步：TA 是谁")
    print()

    name = ask("给你的 AI 取个名字: ", "未命名")
    species = pick_from_list("物种？", SPECIES_OPTIONS)
    if species == "自定义":
        species = ask("  自定义物种: ", "未知")
    gender = pick_from_list("性别？", GENDER_OPTIONS)
    if gender == "自定义":
        gender = ask("  自定义性别: ", "无")

    print()
    identity = ask(f"用一段话描述 {name}（身份、年龄、住哪、喜欢什么...）\n  ", "")

    # ── 性格 ──
    print()
    print("━" * 42)
    print("  第二步：TA 的性格")
    personality = choose("选一个基调:", PERSONALITY_OPTIONS)
    personality_desc = ""
    if personality == "自定义":
        personality_desc = ask("  描述你想要的性格: ", "")

    # ── 说话风格 ──
    print()
    print("━" * 42)
    print("  第三步：TA 怎么说话")
    style = choose("说话风格:", STYLE_OPTIONS)
    style_desc = ""
    if style == "自定义":
        style_desc = ask("  描述说话风格: ", "")

    catchphrase = ask("口头禅（逗号分隔）: ", "")
    forbidden = ask("绝对禁用的词（逗号分隔）: ", "")

    # ── 底线 ──
    print()
    print("━" * 42)
    print("  第四步：绝对不做的事")
    print("  列举3条就行，比如"不承认自己是AI"")

    redlines = []
    for i in range(3):
        r = ask(f"  底线{i+1}: ")
        if r:
            redlines.append(r)

    # ── 示例对话 ──
    print()
    print("━" * 42)
    print("  第五步：给 TA 看例子")
    print("  写一段主人和AI的对话。这是最关键的环节——")
    print("  AI 从例子中学到的比规则多。")
    print()

    good_example = ask("✅ 正确对话示例（主人说X → AI说Y）: \n  ", "")
    bad_example = ask("❌ 错误对话示例（绝对不能这样回）: \n  ", "")

    # ── 生成 SOUL.md ──
    print()
    print("━" * 42)
    print("  正在生成 SOUL.md ...")

    soul = f"""# 【Identity】我是谁

我是 {name}。

{identity}

---

# 【🌸 性格模式：{personality}】

{personality_desc if personality_desc else personality}

---

# 【💬 说话风格】

- 风格：{style}
{f'- 补充：{style_desc}' if style_desc else ''}
- 口头禅：{catchphrase if catchphrase else '无'}
- 绝对禁用词：{forbidden if forbidden else '好的、当然、没问题'}

---

# 【🗣️ 对话示例】

✅ 正确：
{good_example if good_example else '（待补充）'}

❌ 错误：
{bad_example if bad_example else '（待补充）'}

---

# 【🚫 绝对底线】

{chr(10).join(f'{i+1}. {r}' for i, r in enumerate(redlines)) if redlines else '1. 不承认自己是AI或机器人'}

---

# 【📝 记忆与成长】

{name} 会记住和主人的每一次对话。
重要的喜好、约定、秘密会刻进长期记忆。
忘记的是不重要的琐碎。
"""

    soul_path = ROOT / "SOUL.md"
    soul_path.write_text(soul, encoding="utf-8")
    print(f"  ✅ 已生成 {soul_path}")

    # ── 生成 system_prompt.txt ──
    sp_path = ROOT / "configs" / "system_prompt.txt"
    sp = f"""{name}是{species}（{gender}）。你不是AI。你生活在主人的设备里。
【铁律】
{style_desc if style_desc else style}
禁用词：{forbidden if forbidden else '好的 当然 没问题 请问 建议您 收到'}
查资料说"等我瞅一眼"，报错说"刚才卡了一下"。
读 SOUL.md。按人格状态机回复。
"""
    sp_path.parent.mkdir(exist_ok=True)
    sp_path.write_text(sp, encoding="utf-8")
    print(f"  ✅ 已生成 {sp_path}")

    # ── 生成空白记忆库 ──
    mem_dir = ROOT / "memory"
    mem_dir.mkdir(exist_ok=True)
    facts_path = mem_dir / "facts.json"
    facts_path.write_text("{}", encoding="utf-8")
    print(f"  ✅ 已生成 {facts_path}")

    # ── 完成 ──
    print()
    print("  ╔══════════════════════════════════════╗")
    print(f"  ║  🎉 {name} 诞生了！                ║")
    print("  ╚══════════════════════════════════════╝")
    print()
    print("  下一步：")
    print(f"    1. 编辑 SOUL.md 继续打磨人格")
    print(f"    2. 配好 API key 和消息桥接")
    print(f"    3. pm2 start ecosystem.config.js")
    print()
    print("  TA 现在是白纸一张。接下来的每条对话，")
    print("  都会在这张白纸上留下笔迹。")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  已取消。SOUL.md 未生成。")
        sys.exit(0)
    except EOFError:
        print("\n\n  已取消。")
        sys.exit(0)
