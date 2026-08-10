<p align="center">
  <b>xiaoluo — a personal AI companion on WeChat</b>
</p>

<p align="center">
  Chats like a real person. Remembers conversations. Has moods.<br />
  Built on WeChat iLink Bot API + cc-connect. No reverse engineering.
</p>

---

## ⚠️ 项目现状

**这是一个从个人服务器中提取的代码子集，不是开箱即用的完整项目。**

| | 实际情况 |
|------|------|
| 核心聊天 | ✅ 能跑：微信收发 + DeepSeek/Claude + 记忆 + 情绪 |
| 早安晚安 | ✅ 定时触发，配合 reminder_daemon.py |
| TTS 语音 | ✅ cc-connect 自带 qwen3-tts，不依赖本项目代码 |
| 安全防护 | ✅ security_guard.py 可用 |
| 自学习 | ✅ correction_learner.py 可用 |
| 一键部署 | ❌ setup.py 有语法错误，init 向导跑不起来 |
| 图片识别 | ❌ vision.py 缺失 |
| 图片生成 | ❌ image_gen.py 缺失 |
| 语音生成 | ❌ voice_msg.py 有 bug（变量未定义） |
| 表情包 | ❌ pick.py / stickers-guide.md 缺失 |
| 消息计数 | ❌ msg_counter.py 缺失 |
| 云本切换 | ❌ mqtt_local_worker.py 等 3 个文件缺失 |
| 模式切换 | ❌ switch.py / switch_watcher.py 缺失 |
| 购物功能 | ❌ jd_union_search.py 缺失 |
| DeepSeek 监控 | ❌ deepseek_monitor.py 缺失 |
| 依赖文件 | ❌ requirements.txt 是空的 |
| 开源许可证 | ❌ LICENSE 文件缺失 |
| 占位符 | ❌ `{project_name}` `{YOUR_API_KEY}` 散落多个脚本，无自动替换 |

**约 40% 的文档化功能在当前仓库中无法工作。**

---

## 实际能用的部分

### 记忆引擎 (`memory_engine.py`)
ChromaDB 向量库 + 事实文件。逻辑完整。

### 情绪引擎 (`emotion_engine.py`)
VAD 情绪状态持久化 + 自动衰减 + 情绪感染。逻辑完整。

### 安全防护 (`security_guard.py`)
注入检测 + 危险命令拦截 + API Key 审计。逻辑完整。

### 知识图谱 (`knowledge_graph.py`)
实体关系图。逻辑完整。

### 自学习 (`correction_learner.py`)
读取纠正 → 存规则 JSON → 自动应用。逻辑完整。

### 主动智能 (`proactive_intel.py`)
事件追踪 + 即将到来事件提醒。逻辑完整。

### 定时守护 (`reminder_daemon.py`)
早安/晚安/记忆整理。可独立运行。

### 世界书 (`world_book.py`)
根据上下文注入人格设定。逻辑完整。

---

## 技术栈

| 层 | 技术 |
|------|------|
| 微信桥接 | [cc-connect](https://github.com/chenhg5/cc-connect) |
| AI Agent | Claude Code CLI（或任意 OpenAI 兼容 CLI） |
| 模型 | DeepSeek V4（推荐）/ Claude / GPT / Qwen |
| 记忆 | ChromaDB 向量数据库 |
| 情绪 | 规则型 VAD 模型 |
| 进程管理 | PM2 |

---

## 部署说明

**这个仓库不能直接 clone 就跑**。如果你真想部署：

1. 先装 cc-connect 并配通微信（这是大部分工作）
2. 确认 Claude Code CLI 能正常对话
3. 逐个调试本项目脚本——修复语法错误、填占位符、补依赖
4. 只部署你需要的模块，不需要的不装

详细步骤参考 `DEPLOY_CLOUD.md`（但注意：文档描述的是理想系统，不是仓库现状）。

---

## 文档

- [🏗️ ARCHITECTURE](ARCHITECTURE.md)
- [☁️ DEPLOY_CLOUD](DEPLOY_CLOUD.md)
- [💻 DEPLOY_LOCAL](DEPLOY_LOCAL.md)

---

## License

MIT

---

## 致谢

- [cc-connect](https://github.com/chenhg5/cc-connect) — 个人微信 AI 桥接
- [ChromaDB](https://www.trychroma.com/) — 向量数据库
