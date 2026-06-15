import chromadb
import json
import os
import time
import uuid
import urllib.request
from datetime import datetime, timedelta

# 设置代理
if "http_proxy" not in os.environ:
    os.environ["http_proxy"] = "http://{SERVER_IP}:7890"
    os.environ["https_proxy"] = "http://{SERVER_IP}:7890"

# LLM调用工具
def call_llm_simple(prompt):
    """调用硅基流动的Qwen模型做简单判断"""
    data = json.dumps({
        "model": "Qwen/Qwen3-8B-Instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }).encode()
    req = urllib.request.Request(
        "https://api.siliconflow.cn/v1/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {YOUR_API_KEY}"
        }
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        return result["choices"][0]["message"]["content"]
    except:
        return ""


class ActiveMemoryEngine:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="/root/{project_name}/vector_db")
        self.collection = self.client.get_or_create_collection("{project_name}_long_term")
        self.facts_file = "/root/{project_name}/memory/facts.json"

        # 权重配置
        self.WEIGHT_IMPORTANT = 15
        self.WEIGHT_NORMAL = 5
        self.WEIGHT_DECAY = 1
        self.FORGET_THRESHOLD = 3

    # ========== 旧接口兼容 ==========
    def add_episode(self, text, topic="chat"):
        doc_id = f"mem_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.collection.add(
            documents=[text],
            metadatas=[{
                "tags": topic,
                "weight": self.WEIGHT_NORMAL,
                "created_at": time.time(),
                "last_mentioned": time.time(),
                "times_mentioned": 1
            }],
            ids=[doc_id]
        )

    def recall_episodes(self, query, top_k=3):
        if self.collection.count() == 0:
            return ""
        # 按权重排序召回
        results = self.collection.query(query_texts=[query], n_results=top_k * 2)
        if not results["documents"][0]:
            return ""
        scored = []
        for idx, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][idx]
            dist = results["distances"][0][idx] if results["distances"] else 0
            score = meta["weight"] * (1 - dist)
            scored.append((score, doc))
        scored.sort(reverse=True)
        top = [doc for _, doc in scored[:top_k]]
        return "\n".join(top)

    def update_fact(self, key, value):
        with open(self.facts_file, "r", encoding="utf-8") as f:
            facts = json.load(f)
        facts[key] = value
        with open(self.facts_file, "w", encoding="utf-8") as f:
            json.dump(facts, f, ensure_ascii=False, indent=2)

    # ========== 主动编码（每轮对话后调用） ==========
    def encode_after_chat(self, user_msg, bot_reply):
        """判断要不要记、记什么"""
        judge_prompt = f"""
判断以下对话是否值得存入长期记忆，只输出JSON。

主人说：{user_msg}
{AI_NAME}说：{bot_reply}

输出格式：
{{
    "worth_remember": true/false,
    "memory_text": "一句话提炼记忆内容",
    "tags": ["标签1", "标签2"],
    "importance": 1-10
}}

规则：
- 主人的喜好、习惯、事实、重要约定 → 值得记
- 纯闲聊废话、表情、语气词 → 不值得记
- 主人说"别记这个" → 不值得记
"""
        result = call_llm_simple(judge_prompt)
        try:
            data = json.loads(result)
        except:
            return False

        if not data.get("worth_remember", False):
            return False

        base_weight = data.get("importance", 5)
        if any(k in user_msg for k in ["我", "我喜欢", "我讨厌", "记住", "不许忘"]):
            base_weight += 5

        mem_id = str(uuid.uuid4())
        self.collection.add(
            ids=[mem_id],
            documents=[data["memory_text"]],
            metadatas=[{
                "tags": ",".join(data.get("tags", [])),
                "weight": base_weight,
                "created_at": time.time(),
                "last_mentioned": time.time(),
                "times_mentioned": 1
            }]
        )
        return True

    # ========== 睡眠巩固 ==========
    def sleep_consolidate(self):
        """每日整理：衰减、遗忘、总结"""
        all_docs = self.collection.get(include=["documents", "metadatas"])
        if not all_docs["ids"]:
            return {"kept": 0, "forgotten": 0, "new_today": 0}

        now = time.time()
        update_ids = []
        update_metas = []
        delete_ids = []

        for idx, mem_id in enumerate(all_docs["ids"]):
            meta = all_docs["metadatas"][idx]
            days_old = (now - meta["created_at"]) / 86400
            decay = int(days_old / 7) * self.WEIGHT_DECAY
            new_weight = max(meta["weight"] - decay, 0)

            if new_weight < self.FORGET_THRESHOLD:
                delete_ids.append(mem_id)
                continue

            meta["weight"] = new_weight
            update_ids.append(mem_id)
            update_metas.append(meta)

        if delete_ids:
            self.collection.delete(ids=delete_ids)
        if update_ids:
            self.collection.update(ids=update_ids, metadatas=update_metas)

        # 生成今日总结
        today_start = datetime.now().replace(hour=0, minute=0, second=0).timestamp()
        today_memories = [
            doc for idx, doc in enumerate(all_docs["documents"])
            if all_docs["metadatas"][idx]["created_at"] >= today_start
        ]

        if today_memories:
            summary_text = "\n".join(today_memories)
            summary_prompt = f"""
用{AI_NAME}的语气写一段今天的记忆总结，100字以内。
就像睡前复盘一样，温柔一点。

今天新增的记忆：
{summary_text}
"""
            daily_summary = call_llm_simple(summary_prompt)
            if daily_summary:
                self.collection.add(
                    ids=[f"summary_{int(now)}"],
                    documents=[daily_summary],
                    metadatas=[{
                        "tags": "每日总结",
                        "weight": 10,
                        "created_at": now,
                        "last_mentioned": now,
                        "times_mentioned": 1
                    }]
                )

        return {
            "kept": len(update_ids),
            "forgotten": len(delete_ids),
            "new_today": len(today_memories)
        }

    # ========== 手动加分 ==========
    def boost_memory(self, keyword, points=20):
        """主人说记住了 给指定记忆加分"""
        results = self.collection.query(query_texts=[keyword], n_results=5)
        if not results["ids"][0]:
            return False
        for idx, mem_id in enumerate(results["ids"][0]):
            meta = results["metadatas"][0][idx]
            meta["weight"] += points
            meta["times_mentioned"] += 1
            meta["last_mentioned"] = time.time()
            self.collection.update(ids=[mem_id], metadatas=[meta])
        return True


memory_engine = ActiveMemoryEngine()
