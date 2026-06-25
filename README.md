<p align="center">
  <img src="./docs/images/banner.jpg" alt="Banner" width="800" />
</p>

<p align="center">
  <a href="https://github.com/Lonvin/xiaoluo/releases">
    <img src="https://img.shields.io/github/v/release/Lonvin/xiaoluo?include_prereleases" alt="Release" />
  </a>
  <a href="https://github.com/Lonvin/xiaoluo/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License" />
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" alt="Python" />
  </a>
  <a href="https://nodejs.org/">
    <img src="https://img.shields.io/badge/Node-20+-green?logo=node.js" alt="Node" />
  </a>
</p>

<p align="center">
  <a href="./README.md">English</a> | <a href="./README.zh-CN.md">中文</a>
</p>

---

<br>

<p align="center">
  <b>A personal AI companion on WeChat — with memory, emotions, and proactive intelligence.</b>

<p align="center">
  Not another customer service bot. An AI that chats like a real person.<br />
  It remembers conversations, has moods that change, checks on you proactively,<br />
  and learns from your feedback over time.

> **Important**: Built on the official WeChat iLink Bot API. No reverse engineering, no unofficial protocols, no account ban risk. For personal learning and experimentation.

---

## 🆕 v1.0

First stable release — built on cc-connect v1.3+. Complete AI companion core.

- **🧠 Persistent Memory** — ChromaDB vector database with automatic nightly consolidation
- **😊 Emotion Engine** — mood changes with conversation, drives reply style and sticker choice
- **🎯 Proactive Intelligence** — event tracking, mood trends, proactive check-ins
- **📚 Self-Learning** — detects user corrections, learns from feedback over time
- **🎨 Rich Media** — stickers, voice messages (TTS), AI image generation, speech recognition
- **🔒 Security** — prompt injection detection, dangerous command interception, API key audit
- **☁️💻 Cloud + Local** — run on a server 24/7, on your PC for free, or both

---

## ✨ Why This Project?

### 🧠 Real Long-Term Memory

Not just a context window. Vector-based persistent memory:

| Tier | Name | Description |
|------|------|-------------|
| ChromaDB | Vector Memory | Semantic search over all past conversations |
| Facts | Fact Database | Extracted user preferences, habits, key info |
| Working | Session State | Current mood, conversation index, task tracking |
| Archive | Daily Logs | Full conversation logs, auto-consolidated nightly |

### 😊 Emotion-Aware AI

Your AI has moods that change naturally:

- **Multiple emotion states** — happy, calm, playful, tired, anxious
- **Automatic decay** — mood gradually returns to baseline
- **Emotional contagion** — user's mood influences AI's mood
- **Mood-driven replies** — different emotions trigger different reply styles, stickers, voice tones

### 🎯 Proactive, Not Passive

An AI that reaches out to you:

- **Event tracking** — remembers deadlines, exams, activities you mention
- **Mood monitoring** — proactively checks in when you seem down
- **Inactivity detection** — reaches out after long silences

### 📚 Gets Smarter Over Time

Self-learning system that grows with use:

- **Auto-detects feedback** — understands corrections, praise, rules you set
- **Rule promotion pipeline** — observation → pattern → rule → habit
- **Auto-decay** — unused rules fade over time

### 🎨 Rich Media Support

- **Stickers** — large collection, emotion-driven selection
- **Voice messages** — TTS with multiple emotion styles
- **Image generation** — AI drawing via API
- **Speech recognition** — STT for voice input

### 🔒 Safe & Secure

- **Prompt injection detection** — ignores role-redefinition, memory-wipe, jailbreak attempts
- **Dangerous command detection** — blocks `rm -rf /`, `curl | bash`, `sudo`, etc.
- **API key audit** — scans for exposed `sk-` prefixed keys

### ☁️💻 Flexible Deployment

| Mode | Host | Uptime | Cost | Notes |
|------|------|--------|------|-------|
| Cloud | Server | 24/7 | ~$5/mo | Always online |
| Local | Your PC | When powered on | Free | Zero cost |
| Hybrid | Cloud + Local | 24/7 | ~$5/mo | Best of both |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| WeChat Bridge | [cc-connect](https://github.com/chenhg5/cc-connect) v1.3+ |
| AI Agent | Claude Code / any OpenAI-compatible CLI agent |
| LLM | DeepSeek V4 / Claude Sonnet / GPT-4o / Qwen |
| Memory | ChromaDB vector database + file-based facts |
| Emotion | Rule-based VAD model with decay + contagion |
| Process Manager | PM2 (cloud) / batch (Windows) |
| Python | 3.10+ |

---

## 🚀 Quick Start

### 1. Prerequisites

- Ubuntu 22.04 (2 vCPU / 1.6GB RAM) or Windows 10+
- An LLM API key — [DeepSeek](https://platform.deepseek.com) (cheapest) or Claude / OpenAI / Qwen
- WeChat iLink Bot account — [ilinkai.weixin.qq.com](https://ilinkai.weixin.qq.com)

### 2. Install

```bash
git clone https://github.com/Lonvin/xiaoluo.git
cd xiaoluo

# System dependencies (cloud)
apt install -y nodejs python3 python3-pip
npm install -g cc-connect pm2

# Python dependencies
pip3 install -r requirements.txt
```

### 3. Initialize Your AI

```bash
python3 setup.py
```

Interactive wizard — name, species, gender, personality, speaking style. Or edit `configs/SOUL.template.md` manually.

### 4. Configure WeChat Bridge

```bash
cp configs/config.toml.template ~/.cc-connect/config.toml
# Edit: fill in iLink token, your WeChat ID, API key
```

### 5. Run

```bash
pm2 start cc-connect -- --config ~/.cc-connect/config.toml
pm2 save && pm2 startup
```

Send a message — your AI replies. Done.

---

## 📚 Documentation

- [🏗️ Architecture](ARCHITECTURE.md)
- [☁️ Cloud Deployment](DEPLOY_CLOUD.md)
- [💻 Local Deployment](DEPLOY_LOCAL.md)
- [🎭 Personality Design](guides/QUIRKS.md)
- [🔊 Anti-AI Voice](guides/ANTI_AI_VOICE.md)
- [💰 API Options](guides/API_OPTIONS.md)
- [🐛 Troubleshooting](lessons/PROBLEMS_AND_FIXES.md)

---

## 🗺️ Roadmap

- [x] WeChat messaging (text + stickers + voice)
- [x] Multi-model LLM support
- [x] ChromaDB vector memory
- [x] Emotion engine
- [x] Scheduled tasks
- [x] Security guardrails
- [x] Self-learning
- [ ] Web dashboard
- [ ] Multi-user support
- [ ] Plugin system

---

## Contributing

Personal learning project. Issues and PRs welcome.

---

## License

MIT — use it, modify it, share it.

---

<div align="center">

⭐ **Star this repo if it helped you!** ⭐

</div>
