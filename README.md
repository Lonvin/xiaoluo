<div align="center">

# 🤖 WeChat AI Chatbot

A personal AI companion on WeChat — built for learning and experimentation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Node](https://img.shields.io/badge/Node-20+-green.svg)](https://nodejs.org)

</div>

---

## Project Overview

This is a personal learning project for building an AI companion on WeChat. It uses the official WeChat iLink Bot API — no unofficial protocols, no account reverse-engineering.

The goal: an AI that chats like a real person — with personality, emotions, and memory. Not a customer service bot.

> **Important**: This project is for personal learning and experimentation only. All functionality complies with WeChat's Terms of Service and iLink API guidelines.

---

## Features

- WeChat native messaging via cc-connect + iLink official API
- Multi-model LLM support (DeepSeek / Claude / OpenAI / Qwen — choose one)
- 4-tier persistent memory with auto-compression
- VAD 3D emotion engine — mood changes with conversation
- Sticker/emoji system — emotion-driven
- Voice messages + image generation
- Proactive intelligence (event tracking, mood trends)
- Shopping search (JD Union affiliate API)
- Security guardrails (injection detection)
- Self-learning from user corrections
- Scheduled tasks (daily greetings, memory consolidation)
- Cloud + local dual-mode (optional MQTT routing)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| WeChat Bridge | [cc-connect](https://github.com/chenhg5/cc-connect) v1.3+ |
| AI Agent | [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (or any OpenAI-compatible CLI agent) |
| LLM | DeepSeek V4 / Claude Sonnet / GPT-4o / Qwen — you pick |
| Memory | 4-tier file-based (SOUL → core → working → session) |
| Process Manager | PM2 (cloud) / startup batch (local) |
| Message Queue | Mosquitto MQTT (optional, for cloud/local routing) |
| Python | 3.10+ (auxiliary scripts) |

---

## Quick Start

### 1. Prerequisites

- A cloud server (Ubuntu 22.04, 2 vCPU / 1.6GB RAM) or Windows 10+ PC
- DeepSeek API Key (or Claude/OpenAI/Qwen) — [platform.deepseek.com](https://platform.deepseek.com)
- WeChat iLink Bot account — [ilinkai.weixin.qq.com](https://ilinkai.weixin.qq.com) (requires enterprise verification)

### 2. Install

```bash
# Clone
git clone https://github.com/cybercaller/ai-companion.git
cd {project_name}

# Install system dependencies (cloud)
apt install -y nodejs python3 python3-pip
npm install -g cc-connect pm2 @anthropic-ai/claude-code
```

### 3. Configure

```bash
# Copy and edit config template
cp configs/config.toml.template ~/.cc-connect/config.toml
# Edit: fill in your iLink bot token, WeChat ID, API keys

# Create your AI's soul
cp configs/SOUL.template.md SOUL.md
# Edit: fill in your AI's name, identity, personality
```

### 4. Run

```bash
# Start cc-connect (cloud)
pm2 start cc-connect --name my-ai -- --config ~/.cc-connect/config.toml
pm2 save && pm2 startup

# Or start locally (Windows)
cc-connect --config %USERPROFILE%\.cc-connect\config.toml
```

### 5. Test

Send a WeChat message to your bot. It should reply.

---

## Security Checklist

**Do this before anything else:**

1. **Never commit real configs** — `.gitignore` already excludes `config.toml`, `SOUL.md`, `memory/*.md`. Verify: `git status` shows no untracked personal files.
2. **Rotate API keys regularly** — DeepSeek, SiliconFlow, JD Union keys should be changed every 3-6 months.
3. **Use environment variables** — See `.env.example` for the preferred way to store credentials.
4. **WeChat bot token** — If your token leaks, reset it immediately at ilinkai.weixin.qq.com. Anyone with your token can impersonate your bot.
5. **Server SSH** — Disable password login, use key-only auth. Change default SSH port.
6. **Cloud security group** — Only open ports 22, 80, 443. Keep MQTT (1883) internal or use SSH tunnel.

---

## Project Structure

```
├── README.md
├── DEPLOY_CLOUD.md              # Cloud deployment guide
├── DEPLOY_LOCAL.md              # Windows local deployment guide
├── configs/
│   ├── SOUL.template.md         # Personality template — CUSTOMIZE THIS
│   └── config.toml.template     # cc-connect config template
├── scripts/
│   ├── cloud/                   # Cloud-side Python scripts
│   │   ├── correction_learner.py
│   │   ├── image_gen.py
│   │   ├── voice_msg.py
│   │   ├── memory_recall.py
│   │   ├── knowledge_graph.py
│   │   ├── proactive_intel.py
│   │   ├── security_guard.py
│   │   └── relay_server.py
│   └── local/                   # Local-side scripts
│       ├── deepseek_monitor.py
│       └── start-chrome-for-debug.bat
├── guides/
│   ├── ANTI_AI_VOICE.md         # How to make AI sound human
│   ├── API_OPTIONS.md           # All LLM/TTS/STT/image API options
│   ├── QUIRKS.md                # Personality quirk design
│   ├── SERVER_AND_DOMAIN.md     # Server & domain for beginners
│   └── DOMAIN_AND_MQTT.md       # Advanced MQTT cloud/local routing
├── lessons/
│   ├── PROBLEMS_AND_FIXES.md    # Common issues
│   └── TOKEN_OPTIMIZATION.md    # How to save on API costs
├── memory/
│   └── TEMPLATES.md             # Memory file templates
└── .gitignore
```

---

## Roadmap

- [x] WeChat messaging (text + stickers + voice)
- [x] Multi-model LLM support
- [x] 4-tier memory system
- [x] Emotion engine (VAD 3D)
- [x] Scheduled tasks (greetings, memory consolidation)
- [x] Security guardrails
- [x] Self-learning from corrections
- [ ] Web dashboard for monitoring
- [ ] Multi-user support
- [ ] Plugin system

---

## Contributing

This is a personal learning project. Issues and PRs are welcome for discussion and learning. If you have ideas or find bugs, feel free to open an issue.

---

## License

MIT — use it, modify it, share it. Attribution appreciated but not required.

---

## Contact

- GitHub: [@cybercaller](https://github.com/cybercaller)
- Issues: [github.com/cybercaller/ai-companion/issues](https://github.com/cybercaller/ai-companion/issues)

---

<div align="center">

⭐ **If this project helped you, a Star would mean a lot!** ⭐

</div>
