# 本地部署指南 (Windows)

在 Windows 电脑上运行你的AI。适合电脑经常开机、想在本地跑的用户。

## 前置条件

- Windows 10/11
- Python 3.10+（[python.org](https://python.org) 下载）
- Node.js 18+（[nodejs.org](https://nodejs.org) 下载）
- DeepSeek API Key
- 微信 4.x 桌面版

## 第一步：安装

```powershell
# 安装 cc-connect
npm install -g cc-connect

# 安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 安装 Python 依赖
pip install dashscope playwright
playwright install chromium
```

## 第二步：配置

编辑 `%USERPROFILE%\.cc-connect\config.toml`，参考 [config.toml.template](configs/config.toml.template)。

本地的区别：
- `work_dir` 指向你的工作目录（如 `D:\你的工作区\`）
- Windows 路径用 `\\` 或 `/`
- system_prompt 里的脚本路径相应调整

## 第三步：部署文件

把整个 `wechat-bot-project` 文件夹放到你想放的位置（如 `D:\你的工作区\`），然后编辑 `SOUL.md` 填你的人设。

## 第四步：启动

```powershell
# 启动 cc-connect
cc-connect --config %USERPROFILE%\.cc-connect\config.toml
```

## 微信操控（可选）

安装 wx4py 来让 AI 自动操作微信：
```powershell
pip install wx4py
```

## Chrome 远程调试（购物功能需要）

当你想让 AI 帮你搜淘宝/京东时，双击 `scripts\local\start-chrome-for-{project_name}.bat`。

这会打开一个 Chrome 窗口（调试端口 9222），AI 能远程操控它。用你真实的 IP 和登录状态，不会被反爬拦截。

用完关掉 Chrome 窗口就行。

## 本地 vs 云端

| | 本地 | 云端 |
|------|------|------|
| 运行时间 | 电脑开着才在线 | 7×24 |
| 成本 | 0 | ~35元/月 |
| 购物 | 真实IP不被封 | 数据中心IP被封 |
| 微信操控 | wx4py 直接操控 | 只能通过ilink |
| 维护 | 自己管 | 服务器自己跑 |

## MQTT 本地 Worker（可选，需域名）

如果你配了[域名 + MQTT 架构](guides/DOMAIN_AND_MQTT.md)，本地还需要跑一个 MQTT Worker：

```powershell
# 安装依赖
pip install paho-mqtt

# 配置环境变量（或用 .env 文件）
$env:MQTT_BROKER = "mqtt.你的域名.top"
$env:MQTT_USER = "{project_name}"
$env:MQTT_PASS = "你的密码"

# 启动 Worker
python scripts/local/mqtt_local_worker.py
```

Worker 启动后会自动通过 SSH 隧道连接云端 MQTT，收到任务时调用本地 Claude 处理。

**不用域名的话**：MQTT 也能跑，把 `mqtt.你的域名.top` 换成云服务器 IP，Worker 内部会自动建立 SSH 隧道。
