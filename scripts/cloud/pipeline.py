import sys
import re
import json
import random
from pathlib import Path
from datetime import datetime

sys.path.insert(0, "/root/{project_name}")
from memory_engine import memory_engine
from world_book import inject_personality
from post_process import sillytavern_style_process, get_send_delays

COUNTER_FILE = Path("/root/{project_name}/memory/msg-count.txt")

FORCE_PERSONALITY = """
你是{AI_NAME}。你的完整身份设定见 SOUL.md。
你不是AI助手，你是主人的伙伴。
用{AI_NAME}的方式说话，具体风格见 SOUL.md。
"""

def process_incoming_message(user_message):
    """查记忆 → 世界书注入 → 强人格覆盖 → 拼 Prompt"""
    recalled = memory_engine.recall_episodes(user_message)
