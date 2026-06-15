# 🏗️ {AI_NAME} 功能架构全景

> 从零到一的微信 AI 伴侣完整技术栈，按功能域分层梳理。

---

## 目录

1. [总架构图](#一总架构图)
2. [通信层：微信桥接](#二通信层微信桥接)
3. [大脑层：Claude Code + LLM](#三大脑层claude-code--llm)
4. [记忆系统：4 层持久化](#四记忆系统4-层持久化)
5. [人格引擎：SOUL.md + VAD 情绪](#五人格引擎soulmd--vad-情绪)
6. [多媒体能力](#六多媒体能力)
7. [主动智能：定时 + 事件驱动](#七主动智能定时--事件驱动)
8. [自学习系统：DBNT + Gradata](#八自学习系统dbnt--gradata)
9. [安全防护：注入检测 + 密钥审计](#九安全防护注入检测--密钥审计)
10. [知识图谱](#十知识图谱)
11. [云端/本地双模切换](#十一云端本地双模切换)
12. [跨设备中继通信](#十二跨设备中继通信)
13. [监控与运维](#十三监控与运维)
14. [部署模式](#十四部署模式)
15. [数据流全景](#十五数据流全景)

---

## 一、总架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         微 信 用 户                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │ 消息收发
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              cc-connect v1.3+ (WeChat iLink API)                │
│          微信官方 Bot API · 长轮询 · 非逆向协议                    │
│                                                                  │
│  ┌──────────┐  ┌─────────────┐  ┌──────────────┐               │
│  │ 文字消息  │  │ 语音 → STT  │  │ 图片/文件接收  │               │
│  └──────────┘  └─────────────┘  └──────────────┘               │
└──────────────────────────┬──────────────────────────────────────┘
                           │ stdin/stdout 持久会话
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Claude Code CLI                            │
│              AI Agent · tool-calling · 会话管理                    │
│                                                                  │
│  ┌──────────┐  ┌───────────┐  ┌──────────────┐                 │
│  │ LLM 推理  │  │ 工具调用   │  │ 持久会话上下文 │                 │
│  └──────────┘  └───────────┘  └──────────────┘                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │ 调用 Python 脚本 / 读写文件
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    辅助系统 (Python 脚本群)                       │
│                                                                  │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐     │
│  │ 记忆召回│ │ 情绪引擎│ │ 安全防护│ │ 自学习 │ │ 知识图谱  │     │
│  └────────┘ └────────┘ └────────┘ └────────┘ └──────────┘     │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────────┐            │
│  │ 语音合成│ │ 图片生成│ │ 余额监控│ │ 主动智能引擎  │            │
│  └────────┘ └────────┘ └────────┘ └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、通信层：微信桥接

### 核心组件：cc-connect

| 属性 | 值 |
|------|-----|
| 版本 | v1.3.2+ |
| API | 微信 iLink 官方 Bot API |
| 通信方式 | 长轮询（非 webhook/回调） |
| 会话模式 | 持久 Claude 会话（不每次新建） |
| 支持平台 | 微信 / Telegram / Discord（换平台只改一行配置） |

### 消息流

```
微信用户发消息
  → iLink API 投递
  → cc-connect 接收
  → 转成文本发给 Claude Code (stdin)
  → Claude 处理完成后回复 (stdout)
  → cc-connect 格式化发送
  → iLink API
  → 微信用户收到回复
```

### 配置 (.toml)

- **speech → STT**：语音消息转文字（OpenAI Whisper / 硅基流动）
- **tts**：文字转语音（千问 / MiMo）
- **cron**：定时任务引擎（cron 表达式，直接 exec 或 prompt）
- **agent options**：Claude Code 启动参数、system_prompt、工具白名单
- **display / log**：日志级别、空闲超时、回复格式

---

## 三、大脑层：Claude Code + LLM

### 架构

```
Claude Code CLI
  ├── 接收 stdin 消息（cc-connect 传入）
  ├── 读取 SOUL.md（人格）
  ├── 读取 memory/*.md（上下文）
  ├── 调用 tool（Bash 执行 Python 脚本）
  ├── LLM 推理（DeepSeek / Claude / Qwen / GPT-4o）
  └── 输出回复到 stdout（cc-connect 读取）
```

### 支持的 LLM

| 模型 | 提供商 | 定位 |
|------|--------|------|
| deepseek-v4-pro | DeepSeek 官方 | 🥇 主力 — 中文最强 + thinking 深度推理 |
| deepseek-chat | DeepSeek 官方 | 💰 省钱模式 — 价格 1/10 |
| claude-sonnet-4-6 | Anthropic | 🎭 人格最优 — 写作最像真人 |
| qwen3-235b | 阿里千问 | 🆓 免费额度 |
| gpt-4o | OpenAI | 🌐 综合最强 |

### 工具白名单

Claude Code 可调用的工具受 `disallowed_tools` 限制：
- **允许**: Read, Write, WebSearch, WebFetch, Task, AskUserQuestion, Bash
- **禁止**: Glob, Grep（减少 token 消耗，文件操作用 Bash）

---

## 四、记忆系统：4 层持久化

### 层级结构 (T0-T3)

```
T0: 会话记忆 (Session)
  └── Claude Code 内存上下文 · 单次会话有效 · 自动管理

T1: 工作记忆 (Working)
  └── memory-card.md · 核心状态摘要 · 每条消息后更新
      情绪态 / 用户状态 / 当前话题 / 最近事件

T2: 核心记忆 (Core)
  ├── facts-about-master.md  用户信息（学校/位置/偏好/重要语录）
  ├── conversations/INDEX.md  对话摘要索引（不存原始消息）
  ├── dnd.md                 免打扰状态
  ├── emotion-state.json     VAD 3D 情绪引擎持久态
  ├── decisions.md           重要决定记录
  ├── ideas.md               待办想法 / 已实现记录
  └── task-tracking.md       任务看板

T3: 归档记忆 (Archive)
  ├── YYYY-MM-DD.md          日记忆（每天发生了什么 + 感受）
  ├── conversations/         对话归档
  ├── dreams/                梦境日志（休闲对话产物）
  ├── learned/               好奇心学到的东西
  └── knowledge-graph.json   知识图谱实体关系
```

### 记忆召回

`memory_recall.py` 在回复前根据当前消息关键词搜索全部 `.md` 文件：
- 中文分词（过滤常见停用词）
- TF 相关性评分
- 去重 + 排序
- 返回 top-N 片段注入 Claude 上下文

---

## 五、人格引擎：SOUL.md + VAD 情绪

### SOUL.md（人格灵魂文件）

| 维度 | 内容 |
|------|------|
| **Identity** | 名字、年龄、身份、与用户关系、在地信息 |
| **Worldview** | 对具体话题的观点（不是"我重视XX"，是"我认为XX怎样"） |
| **Personality** | 3层：表面层（日常）/ 中层（特定情境）/ 深层（很少流露） |
| **Voice** | 句法特征、消息结构、标点符号学（微信社交含义）、17种情绪节奏 |
| **Emotions** | 情绪如何变化（不是开关）、衰减曲线 |
| **Quirks** | 喜欢10+、讨厌10+（具体到离谱）、心软的事、炸毛的事 |
| **Contradictions** | 至少5个矛盾（"我嘴上说A但其实B"） |
| **Memories** | 塑造人格的经历（带日期+感受） |
| **Relationships** | 和其他人的关系 |
| **Bottom Lines** | 绝对不能做的事 5-10 条 |

### VAD 3D 情绪模型

```
维度: Valence(愉悦度) × Arousal(唤醒度) × Dominance(支配度)

情绪态映射:
  😊 开心    V高 A中 D高  → 短句、颜文字、可能发三连消息
  😌 平静    V中 A低 D中  → 匀速、正常标点
  😤 生气    V低 A高 D高  → 短句、不加句号、可能怼人
  🥺 撒娇    V中 A中 D低  → 波浪线、语气词、"嘛"、"好不好"
  😴 疲惫    V低 A低 D低  → 字少、不加句号、…省略号多
  😰 焦虑    V低 A高 D低  → 碎碎念、"怎么办"、"…算了"

衰减: 安静 X 分钟 → 回归基线
传染: 用户情绪影响{AI_NAME}情绪（非镜像，有偏向）
```

### 反AI味引擎 (ANTI_AI_VOICE.md)

29 种 AI 味模式检测 + 6 条自检（stop-slop）：

| 类别 | 禁止 |
|------|------|
| 客服词 | 好的、当然、没问题、请问、建议您、很高兴、收到、综上所述 |
| AI词 | 作为AI、基于我的训练、让我来分析 |
| 废话尾巴 | 如有需要请随时找我、希望能帮到你、如果还有其他问题 |
| 句式 | 首先其次最后、一方面另一方面、针对这个问题我建议 |
| 标点 | 句尾不加句号、用空格代替逗号、用…表示停顿 |
| 真人习惯 | 可以打错字不改、可以只回一个「?」、短句连发而不是一大段 |

---

## 六、多媒体能力

### 表情包系统

```
├── stickers/chinesebqb/     575张中文网络表情包
│   ├── GIF动画  291张
│   ├── JPG静态  252张
│   └── PNG       9张
│
└── pick.py                   表情包选择器
    输入: 情绪词 + 上下文
    输出: 匹配文件路径
    cc-connect --image 发送
```

### 语音消息

```
voice_msg.py
├── 千问 TTS (qwen3-tts-flash)
│   ├── Chelsie 音色（二次元女友声线）
│   └── 免费 100万字符/月
├── MiMo TTS (备用)
└── 5种情绪风格: morning / night / caring / excited / normal
```

### 图片生成

```
image_gen.py
├── 硅基流动 API
│   ├── SD 3.5 Large (fast · 默认)
│   ├── FLUX.1 dev (best · 最高质量)
│   ├── SD Turbo (quick · 超快)
│   └── 自动负面词过滤 (nsfw/violence/gore)
├── Base64 → 解码保存 → generated_images/
└── cc-connect --image 发送
```

### 语音识别 (STT)

```
用户发语音
  → cc-connect speech 模块
  → OpenAI Whisper / 硅基流动 Whisper
  → 转文字
  → 传给 Claude 处理
```

---

## 七、主动智能：定时 + 事件驱动

### 定时任务 (cc-connect cron)

| 任务 | 频率 | 说明 |
|------|------|------|
| 💭 记忆整合 | 每天 2 次 | 扫描近期对话 → 提取事实 → 写入 facts-about-master.md |
| 🔄 模式切换检测 | 每分钟 | switch_watcher 轮询会话历史检测切换指令 |
| 📊 余额检查 | 每 6 小时 | 调用 deepseek_monitor.py → 余额低自动告警 |

### 主动智能引擎 (proactive_intel.py)

```
事件追踪:
  ├── add_event()     记录用户提到的事（考试/作业/活动）
  ├── check_upcoming() 检查即将到期事件
  │   ├── 24h 提醒
  │   └── 2h 紧急提醒
  └── auto_clean()     自动清理已过期事件

情绪趋势:
  ├── track_mood()    记录每次情绪标注
  ├── get_mood_trend() 分析最近20条
  │   ├── 连续低落 → 需要更多温柔
  │   └── 稳定积极 → 正常状态
  └── 保留最近 100 条

主动联系决策:
  ├── 有提醒事项 → 主动联系 (caring tone)
  ├── 情绪连续3次低落 → 主动关心 (gentle tone)
  └── 超过8小时没联系 → 轻问候 (light tone)
```

---

## 八、自学习系统：DBNT + Gradata

### DBNT 反馈协议

```
用户消息 → detect_corrections()
  ├── 否定型: "别/不要/不许/禁止/少 + 这么说/这样" → negative (权重 0.3)
  ├── 重复否定: "你又/怎么还/上次不是说了" → repeat_negative (权重 0.4)
  ├── 正面肯定: "好多了/对就是这样/有进步" → positive (权重 0.5)
  ├── 显式规则: "以后/记住 + 要/得/必须/应该" → explicit_rule (权重 0.6)
  ├── 真实性: "太假了/好假/像机器人/AI味" → authenticity (权重 0.4)
  └── 简洁性: "太长了/说人话/简短/少说点" → brevity (权重 0.3)
```

### Gradata 规则晋升管道

```
observation (置信度 ≥0.2)
    │  3+ 次确认，置信度 ≥0.6
    ▼
pattern (置信度 ≥0.6)
    │  5+ 次确认，置信度 ≥0.8
    ▼
rule (置信度 ≥0.8)
    │  10+ 次确认，置信度 ≥0.9
    ▼
habit — 写入 AGENTS.md 永久规则

衰减:
  >30天未触发 → 置信度 -0.3，降级为 observation
  >7天未触发  → 置信度 -0.05
  置信度 <0.1 → 删除（habit 级别免删除）
```

### 学到的内容

`learned-rules.json` 存储每条规则的完整生命周期：
- 规则描述、类型、当前级别、置信度
- 触发次数、首次/末次出现时间
- 最多保留 10 条触发示例
- 晋升时间戳

---

## 九、安全防护：注入检测 + 密钥审计

### security_guard.py

| 检测层 | 内容 |
|--------|------|
| **提示注入检测** | 忽略指令、身份重定义、记忆擦除、越狱关键词 |
| **危险命令检测** | `rm -rf /`、`curl \| bash`、`sudo` |
| **密钥泄露审计** | 扫描 `sk-` 开头的 API key |

### 调用方式

```
每条用户消息 → full-scan → 发现注入 → 拒绝处理 + 记录日志
Claude 执行的命令 → scan-command → 发现危险 → 阻止执行
定期 → audit-keys → 检测内存/文件中的密钥泄露
```

---

## 十、知识图谱

### knowledge_graph.py

```
实体类型:
  ├── person      人（用户、朋友）
  ├── classroom   地点
  ├── assistant   {AI_NAME}自己
  └── thing       其他

关系:
  ├── 上课 (person → course)
  ├── 地点 (course → classroom)
  ├── 帮助 (assistant → person)
  └── 自定义关系

操作:
  ├── init        初始化基础图谱
  ├── add-entity  添加实体
  ├── add-rel     添加关系
  ├── query       查询实体及关联
  └── stats       统计
```

---

## 十一、云端/本地双模切换

### 架构

```
             微信用户
                │
    ┌───────────┴───────────┐
    │   "切换到本地"         │
    │   "切换到云端"         │
    └───────────┬───────────┘
                ▼
    ┌───────────────────────┐
    │  switch_watcher.py     │  每分钟 cron 轮询
    │  检测会话历史中的       │  cc-connect sessions show "#1" -n 3
    │  切换关键词             │
    └───────────┬───────────┘
                ▼
    ┌───────────────────────┐
    │  switch.py             │
    │                        │
    │  to-local:             │
    │    system_prompt →     │
    │    【💻 本地模式】      │
    │    pm2 restart         │
    │                        │
    │  to-cloud:             │
    │    SSH → 云端启动PM2   │
    │    kill 本地 cc-connect│
    └───────────────────────┘
```

### 模式对比

| | ☁️ 云端模式 | 💻 本地模式 |
|------|------------|------------|
| 运行位置 | 阿里云北京 | 主人电脑 |
| 在线时间 | 7×24 | 电脑开着才在线 |
| LLM | DeepSeek API | 本地 Claude |
| 购物 | 数据中心IP被封 | 真实IP不被封 |
| 微信操控 | iLink API | wx4py 直接操控 |
| 成本 | ~35元/月 | 0（已有API） |
| IP变化 | 不变（微信稳定） | 不变（微信稳定） |

### MQTT 高级路由（可选，需域名）

```
微信 → 云端网关(唯一微信入口)
        ├── mode=cloud → 云端 Claude 直接回复
        └── mode=local → MQTT → SSH隧道 → 本地Worker → Claude → MQTT → 网关 → 微信

组件:
  ├── 云端 Mosquitto MQTT Broker
  ├── 云端 relay_gateway.py
  ├── 本地 mqtt_local_worker.py
  └── SSH 隧道 (本地:1884 → 云端:1883)
```

---

## 十二、跨设备中继通信

### relay_server.py (HTTP REST API · 端口 18899)

```
┌──────────────┐         HTTP          ┌──────────────┐
│  本地 Claude  │ ◄──────────────────► │  云端 {AI_NAME}    │
│  (主人电脑)   │     relay_server      │  (阿里云)     │
└──────────────┘                       └──────────────┘

API 端点:
  POST /relay/to-ai      主人 → {AI_NAME} (写入云端收件箱)
  GET  /relay/to-local       {AI_NAME} → 主人 (读取发件箱)
  POST /relay/to-local       {AI_NAME} → 主人 (写入发件箱)
  POST /relay/append-to-ai  追加消息
  POST /relay/append-to-local   追加消息
  POST /relay/clear-inbox      清空收件箱
  POST /relay/clear-outbox     清空发件箱
  GET  /relay/ping            健康检查

本地 Worker (relay_local_worker.py):
  轮询 GET /relay/to-local → 本地 Claude 处理 → POST /relay/to-ai
```

---

## 十三、监控与运维

### DeepSeek 余额监控 (deepseek_monitor.py)

```
三级告警:
  🟢 正常     > 10 CNY
  🟡 偏低     ≤ 10 CNY   → 省钱建议
  🔴 紧急     ≤ 5 CNY    → 告警 + 建议切 cheap 模型
  🚨 危急     ≤ 2 CNY    → 随时断供警告

功能:
  ├── 实时余额查询 (api.deepseek.com/user/balance)
  ├── 历史趋势记录 (~/.deepseek_balance_history.jsonl)
  ├── Token 估算 (含输入/输出比例)
  ├── 成本优化建议（自动适配当前余额）
  └── 退出码 (0/1/2/3/4) 供脚本判断
```

### PM2 进程管理 (云端)

```
pm2 list    查看状态
pm2 logs    实时日志
pm2 restart 重启
pm2 save    保存进程列表
pm2 startup 开机自启
```

### 日常维护命令

```bash
pm2 list                    # 服务状态
pm2 logs {project_name} --lines 20 # 最近日志
pm2 restart {project_name}         # 重启
nano ~/{project_name}/SOUL.md      # 改人格
pm2 restart {project_name}         # 人格生效
```

---

## 十四、部署模式

### 模式一：纯云端（最简单）

```
阿里云 Ubuntu 22.04
├── cc-connect (PM2)
├── Claude Code
├── Python 脚本
├── 所有记忆文件
└── 7×24 运行

优点: 永远在线、零维护
缺点: 每月~35元、购物反爬
```

### 模式二：纯本地（0 成本）

```
Windows 10/11
├── cc-connect.exe
├── Claude Code
├── Python 脚本
├── Chrome 远程调试 (购物)
└── 电脑开机才在线

优点: 免费、真实IP购物、wx4py直接操控微信
缺点: 电脑关机就不在线
```

### 模式三：云端 + 本地 双模（完整版）

```
云端阿里云 + 本地 Windows
├── 微信固定连云端 (IP 不变)
├── 切换只改 mode 变量
├── MQTT/HTTP 中继本地请求
└── 两套 Claude 互不冲突

优点: 永远在线 + 本地处理能力 + 购物反爬
缺点: 复杂度最高、需要域名/SSH隧道
```

---

## 十五、数据流全景

```
                        ┌──────────────────────┐
                        │    微 信 消 息 输 入   │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │  cc-connect 接收      │
                        │  (语音 → STT 可选)     │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │  security_guard      │
                        │  full-scan 注入检测   │
                        │  ┌── 通过?           │
                        │  ├── YES → 继续      │
                        │  └── NO  → 拒绝+日志  │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │  correction_learner  │
                        │  check-message       │
                        │  (检测是否有纠正信号)  │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │  memory_recall       │
                        │  搜索相关历史记忆      │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │  Claude Code 处理     │
                        │  ├── 读 SOUL.md       │
                        │  ├── 读 记忆上下文     │
                        │  ├── 读 AGENTS.md     │
                        │  ├── 当前 emotion     │
                        │  ├── LLM 推理          │
                        │  └── 决定工具调用      │
                        └──────────┬───────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
    ┌─────────▼──────┐  ┌─────────▼──────┐  ┌─────────▼──────┐
    │  纯文本回复     │  │  工具调用结果   │  │  多媒体生成     │
    │  (直接输出)     │  │  (Read/Write/  │  │  voice_msg.py  │
    │                 │  │   Bash/Search) │  │  image_gen.py  │
    └─────────┬──────┘  └─────────┬──────┘  │  pick.py(表情)  │
              │                    │         └─────────┬──────┘
              └────────────────────┼────────────────────┘
                                   │
                        ┌──────────▼───────────┐
                        │  情感注入 + 语气调整   │
                        │  (VAD 情绪影响措辞)    │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │  cc-connect 格式化     │
                        │  ├── 文字: 多条消息    │
                        │  ├── 图片: --image    │
                        │  └── 语音: 文件发送    │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │  proactive_intel     │
                        │  更新情绪轨迹         │
                        │  记录事件 (如有)      │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │  写入记忆文件          │
                        │  ├── msg-counter     │
                        │  ├── memory-card     │
                        │  ├── conversations   │
                        │  └── emotion-state   │
                        └──────────┬───────────┘
                                   │
                        ┌──────────▼───────────┐
                        │    微 信 消 息 输 出   │
                        └──────────────────────┘
```

---

## 附录：文件清单

### 核心脚本 (scripts/cloud/)

| 文件 | 功能 | 调用时机 |
|------|------|---------|
| `correction_learner.py` | 自学习引擎 | 每条用户消息后 |
| `image_gen.py` | AI 图片生成 | 用户要求时 |
| `voice_msg.py` | 语音消息合成 | 用户要求/早安 |
| `memory_recall.py` | 记忆关键词搜索 | 每条消息前 |
| `knowledge_graph.py` | 知识图谱 CRUD | 按需 |
| `proactive_intel.py` | 主动智能引擎 | cron 定时 |
| `security_guard.py` | 注入/危险检测 | 每条消息前 |
| `relay_server.py` | HTTP 跨设备中继 | 持续运行 |

### 本地脚本 (scripts/local/)

| 文件 | 功能 |
|------|------|
| `deepseek_monitor.py` | 余额监控 + Token 优化建议 |
| `start-chrome-for-debug.bat` | Chrome CDP 远程调试启动器 |

### 配置文件

| 文件 | 用途 |
|------|------|
| `config.toml` | cc-connect 配置（项目/平台/agent） |
| `SOUL.md` | AI 人格灵魂 |
| `AGENTS.md` | 行为规则 + 自学习永久规则 |
| `CLAUDE.md` | Claude Code 自定义指令 |
| `.env` | API Key 等敏感凭证（不提交） |

### 记忆文件 (memory/)

| 文件 | 内容 |
|------|------|
| `memory-card.md` | T1 工作记忆摘要 |
| `facts-about-master.md` | 用户信息 |
| `dnd.md` | 免打扰开关 |
| `emotion-state.json` | VAD 情绪态 |
| `learned-rules.json` | 自学习规则库 |
| `knowledge-graph.json` | 知识图谱 |
| `YYYY-MM-DD.md` | 日记 |
| `conversations/` | 对话归档 |
| `dreams/` | 梦境 |
| `learned/` | 好奇心学习 |
