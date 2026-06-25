<div align="center">

# 🤖 AI Companion for WeChat

### Build your own AI companion on WeChat — with personality, memory, and emotions

[![GitHub Stars](https://img.shields.io/github/stars/Lonvin/xiaoluo?style=flat-square&color=yellow)](https://github.com/Lonvin/xiaoluo/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Node](https://img.shields.io/badge/Node-20+-green.svg)](https://nodejs.org)
[![Memory](https://img.shields.io/badge/Memory-%3C50MB-brightgreen)]()

</div>

---

## What is this?

A lightweight framework for building your own AI companion on WeChat. Give it a personality, a memory, and emotions — it chats like a real person, not a customer service bot.

Built on the official **WeChat iLink Bot API**. No unofficial protocols, no account reverse-engineering, no jailbreak risk.

> **This is a blank framework.** Run `python setup.py` → answer a few questions → your AI is born. Everything — name, species, gender, personality, speaking style — is up to you.

---

## ✨ Features

- **WeChat native** — cc-connect + iLink official API
- **Multi-model LLM** — DeepSeek / Claude / OpenAI / Qwen — you pick one
- **Customizable personality** — `setup.py` interactive wizard or edit `SOUL.md` directly
- **ChromaDB vector memory** — remembers conversations, auto-consolidates nightly
- **Emotion engine** — mood changes with conversation, drives reply style
- **Message pipeline** — enrichment, context injection, post-processing filter
- **Self-learning** — detects user corrections, learns from feedback
- **Cloud + local dual-mode** — MQTT-based routing, switch with one command
- **Security guardrails** — injection detection, API key audit

---

## Quick Start

### Prerequisites

- Ubuntu 22.04 (2 vCPU / 1.6GB RAM) or Windows 10+
- An LLM API key — [DeepSeek](https://platform.deepseek.com) (cheapest) or Claude / OpenAI / Qwen
- WeChat iLink Bot account — [ilinkai.weixin.qq.com](https://ilinkai.weixin.qq.com) (enterprise verification)

### 3 Steps

```bash
# 1. Clone
git clone https://github.com/Lonvin/xiaoluo.git
cd xiaoluo

# 2. Install
apt install -y nodejs python3 python3-pip
npm install -g cc-connect pm2

# 3. Initialize your AI
python3 setup.py
```

Follow the interactive wizard — name your AI, pick a species, choose a personality, define speaking style. Then:

```bash
# Configure WeChat bridge
cp configs/config.toml.template ~/.cc-connect/config.toml
# Edit: fill in iLink token, your WeChat ID, API key

# Start
pm2 start cc-connect -- --config ~/.cc-connect/config.toml
pm2 save && pm2 startup
```

Send a message to your bot — it replies. You're done.

---

## Project Structure

```
├── setup.py                      # Interactive initialization wizard
├── configs/
│   ├── SOUL.template.md          # Blank personality template
│   └── config.toml.template      # cc-connect config template
├── scripts/cloud/                # Multi-model LLM / TTS / image gen / security / memory
├── scripts/local/                # Windows local mode
├── guides/                       # Anti-AI voice, API options, quirks, MQTT
├── lessons/                      # Common fixes, token optimization
└── .gitignore                    # Memory files, configs, keys excluded
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| WeChat Bridge | [cc-connect](https://github.com/chenhg5/cc-connect) v1.3+ |
| AI Agent | Claude Code / Codex / any OpenAI-compatible CLI agent |
| LLM | DeepSeek V4 / Claude Sonnet / GPT-4o / Qwen |
| Memory | ChromaDB vector database + file-based facts |
| Process Manager | PM2 (cloud) / batch (Windows) |
| Python | 3.10+ |

---

## Roadmap

- [x] WeChat messaging (text + stickers + voice)
- [x] Multi-model LLM support
- [x] ChromaDB memory with auto-consolidation
- [x] Customizable personality system
- [x] Security guardrails
- [x] Self-learning from corrections
- [ ] Web dashboard
- [ ] Multi-user support
- [ ] Plugin system

---

## Security

1. **Never commit real configs** — `.gitignore` excludes `config.toml`, `SOUL.md`, `memory/*.md`
2. **Rotate API keys** every 3-6 months
3. **Use environment variables** for credentials
4. **Reset leaked iLink tokens** immediately at ilinkai.weixin.qq.com
5. **SSH key-only auth** — disable password login

---

## License

MIT — use it, modify it, share it.

---

<div align="center">

⭐ **Star this repo if it helped you build something!** ⭐

</div>
