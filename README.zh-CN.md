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
  <b>一个有记忆、有情绪、会主动关心你的微信 AI 伴侣框架。</b>
</p>

<p align="center">
  不是又一个客服机器人。一个真正有性格的 AI ——<br />
  能记住你们的对话、有自己的情绪、会主动找你聊天、<br />
  还会从你的反馈中不断学习成长。
</p>

> **重要提示**：基于微信官方 iLink Bot API 构建。无逆向工程，无非官方协议，无封号风险。仅供个人学习和实验。

---

## 🆕 v1.0

首个正式版 — 基于 cc-connect v1.3+

- **🧠 持久化记忆** — ChromaDB 向量数据库，夜间自动整理归档
- **😊 情绪引擎** — 情绪随对话变化，驱动回复风格和表情包选择
- **🎯 主动智能** — 事件追踪、情绪趋势、主动问候
- **📚 自学习** — 检测你的纠正，从反馈中学习
- **🎨 富媒体** — 表情包、语音消息、AI 画图、语音识别
- **🔒 安全防护** — 注入检测、危险命令拦截、密钥审计
- **☁️💻 云端+本地** — 服务器 24/7、电脑免费跑、双模切换

---

## ✨ 为什么选这个项目？

### 🧠 真正的长期记忆

不只是上下文窗口。向量化的持久记忆：

| 层级 | 名称 | 说明 |
|------|------|------|
| ChromaDB | 向量记忆 | 所有历史对话的语义搜索 |
| Facts | 事实库 | 提取的用户偏好、习惯、关键信息 |
| Working | 会话状态 | 当前情绪、对话索引、任务追踪 |
| Archive | 每日日志 | 完整对话记录，夜间自动整理 |

### 😊 有情绪的 AI

AI 的情绪会自然变化：

- **多种情绪态** — 开心、平静、撒娇、疲惫、焦虑
- **自动衰减** — 安静后逐渐回归基线
- **情绪传染** — 你的情绪会影响 AI
- **情绪驱动** — 不同情绪对应不同回复风格、表情包、语音语调

### 🎯 主动而非被动

一个会主动找你的 AI：

- **事件追踪** — 记住你提到的考试、作业、活动
- **情绪监测** — 你低落时主动关心
- **静默检测** — 长时间没联系时主动问候

### 📚 越用越聪明

自学习系统：

- **自动检测反馈** — 理解纠正、表扬、规则
- **规则晋升管道** — 观察 → 模式 → 规则 → 习惯
- **自动衰减** — 不用的规则逐渐淡出

---

## 🛠️ 技术栈

| 层级 | 技术 |
|-------|-----------|
| 微信桥接 | [cc-connect](https://github.com/chenhg5/cc-connect) v1.3+ |
| AI Agent | Claude Code / OpenAI 兼容 CLI Agent |
| LLM | DeepSeek V4 / Claude Sonnet / GPT-4o / Qwen |
| 记忆 | ChromaDB 向量库 + 文件式事实库 |
| 进程管理 | PM2（云端）/ batch（Windows）|
| Python | 3.10+ |

---

## 🚀 快速开始

### 1. 前置要求

- Ubuntu 22.04（2 vCPU / 1.6GB RAM）或 Windows 10+
- LLM API Key — [DeepSeek](https://platform.deepseek.com) 最便宜
- 微信 iLink Bot 账号 — [ilinkai.weixin.qq.com](https://ilinkai.weixin.qq.com)

### 2. 安装

```bash
git clone https://github.com/Lonvin/xiaoluo.git
cd xiaoluo
apt install -y nodejs python3 python3-pip
npm install -g cc-connect pm2
pip3 install -r requirements.txt
```

### 3. 初始化你的 AI

```bash
python3 setup.py
```

交互式向导 — 名字、物种、性别、性格、说话风格。或直接编辑 `configs/SOUL.template.md`。

### 4. 配置微信桥接

```bash
cp configs/config.toml.template ~/.cc-connect/config.toml
# 编辑：填入 iLink token、微信 ID、API key
```

### 5. 运行

```bash
pm2 start cc-connect -- --config ~/.cc-connect/config.toml
pm2 save && pm2 startup
```

发条消息 — AI 就回复了。

---

## 📚 文档

- [🏗️ 架构全景](ARCHITECTURE.md)
- [☁️ 云端部署](DEPLOY_CLOUD.md)
- [💻 本地部署](DEPLOY_LOCAL.md)
- [🎭 人格设计](guides/QUIRKS.md)
- [🔊 反AI味](guides/ANTI_AI_VOICE.md)
- [💰 API选项](guides/API_OPTIONS.md)
- [🐛 常见问题](lessons/PROBLEMS_AND_FIXES.md)

---

## 🗺️ 路线图

- [x] 微信消息
- [x] 多模型 LLM
- [x] ChromaDB 向量记忆
- [x] 情绪引擎
- [x] 定时任务
- [x] 安全防护
- [x] 自学习
- [ ] Web 面板
- [ ] 多用户
- [ ] 插件系统

---

## 贡献

个人学习项目。欢迎提 Issue 和 PR。

---

## 许可证

MIT — 随便用、随便改、随便分享。

---

<div align="center">

⭐ **有用就点个 Star！** ⭐

</div>
