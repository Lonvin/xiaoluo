# 云端部署完整指南 — 国内外通用

从零开始在云服务器上部署一个 7×24 运行的微信 AI 助手。

> **这份指南写给完全新手。** 不需要懂 Linux、不需要懂编程。每一步都写了"为什么"和"怎么检查"。

预计耗时：30-60 分钟（首次）。月成本：国内 ~50 元 / 国际 ~$10。

---

## 目录

1. [你需要什么](#一你需要什么)
2. [买服务器](#二买服务器)
3. [连接服务器](#三连接服务器)
4. [装软件](#四装软件)
5. [配置微信桥接](#五配置微信桥接)
6. [部署 AI 文件](#六部署-ai-文件)
7. [配置 AI 人格](#七配置-ai-人格)
8. [启动](#八启动)
9. [验证 + 排错](#九验证--排错)
10. [定时任务](#十定时任务)
11. [表情包（可选）](#十一表情包可选)
12. [附加功能](#十二附加功能)

---

## 一、你需要什么

| 东西 | 解释 | 怎么拿到 |
|------|------|---------|
| 云服务器 | 一台永远开机的远程电脑，AI 住在上面 | 阿里云/腾讯云/AWS 等，5分钟买好 |
| DeepSeek API Key | AI 的大脑——对话、思考都靠它 | [platform.deepseek.com](https://platform.deepseek.com) 注册即得 |
| 微信 Bot 账号 | AI 连接微信的"通行证" | [ilinkai.weixin.qq.com](https://ilinkai.weixin.qq.com) 企业认证后创建 |

> **搞不定微信 Bot？** ilink 需要企业认证。个人用户可以先申请，同时用 Telegram/Discord 测试——cc-connect 支持多平台，换平台只改一行配置。

---

## 二、买服务器

### 国内用户

| 厂商 | 最低配置 | 月费 | 推荐理由 |
|------|---------|------|---------|
| **阿里云 ECS** | 2核1G 40G | ~35元 | 学生优惠，离你最近的机房 |
| **腾讯云 CVM** | 2核2G 50G | ~40元 | 轻量应用服务器更便宜 |
| **华为云 ECS** | 2核1G 40G | ~35元 | 华为生态 |
| **京东云** | 2核1G 40G | ~30元 | 最便宜 |

> **学生优惠：** 阿里云/腾讯云都有学生机，年付 ~100 元。

1. 打开上面任一网站，注册账号（需要实名认证）
2. 搜索"云服务器 ECS"或"轻量应用服务器"
3. 选配置：**2核 CPU + 至少 1.6G 内存 + 40G 硬盘**
4. 选系统：**Ubuntu 22.04 64位**
5. 选地域：离你近的（国内选北京/上海/广州，选离你最近的机房/你的城市）
6. 设置 root 密码（记下来！丢了要重置）
7. 付款 → 等 1-2 分钟 → 服务器就绪

买完后你会得到一个 **公网 IP**（类似 `你的服务器IP`），这是你服务器的地址。记下来。

### 国际用户

| 厂商 | 最低配置 | 月费 | 推荐理由 |
|------|---------|------|---------|
| **DigitalOcean** | 1vCPU 1G 25G | $6 | 新手最友好，教程最多 |
| **Vultr** | 1vCPU 1G 25G | $6 | 全球多机房 |
| **AWS Lightsail** | 1vCPU 1G 40G | $5 | 亚马逊，前3月免费 |
| **Linode** | 1vCPU 1G 25G | $5 | 稳定老牌 |
| **Hetzner** | 2vCPU 2G 40G | €4 | 欧洲最便宜 |

1. 打开上面任一网站，注册（需要信用卡/PayPal）
2. 选 **Droplet / Instance / Compute Engine**
3. 选系统：**Ubuntu 22.04 LTS**
4. 选配置：最便宜的就行（$5-6/月）
5. 选机房：离你用户近的（亚洲用户选 Singapore/Tokyo，美国用户选 San Francisco/New York）
6. 创建 → 等 1 分钟 → 你会收到 root 密码（邮件或网页显示）
7. 记下**公网 IP**。

> **为什么选 Ubuntu？** Linux 的一种。世界最流行、教程最多、新手最友好。别选 CentOS（已停止维护）、别选 Windows Server（不需要桌面）。

---

## 三、连接服务器

### Windows 用户

**方法一：PowerShell（推荐，系统自带）**

1. 按 `Win+R`，输入 `powershell`，回车
2. 输入：`ssh root@你的服务器IP`
3. 第一次连接会问 `Are you sure...` 输入 `yes` 回车
4. 输入 root 密码（输入时不显示字符，这是正常的）
5. 出现 `root@xxx:~#` 表示连上了

**方法二：Putty（图形界面）**

1. 下载 [Putty](https://putty.org)
2. Host Name 填服务器 IP，Port 22
3. 点 Open → 输入用户名 `root` → 输入密码

**方法三：VS Code Remote SSH**

1. 装 VS Code + Remote-SSH 插件
2. 左下角绿色按钮 → Connect to Host → `root@你的IP`
3. 输入密码

### Mac 用户

打开 Terminal（在 Applications/Utilities 里），输入：

```bash
ssh root@你的服务器IP
```

### 连上了吗？验证：

```bash
whoami
# 应该输出：root

uname -a
# 应该输出包含 "Linux" 和 "Ubuntu" 的一行
```

---

## 四、装软件

复制下面整段，粘到终端里执行：

```bash
# 1. 更新系统
apt update && apt upgrade -y

# 2. 装基础工具
apt install -y curl wget git python3-pip

# 3. 装 Node.js 20（cc-connect 需要）
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# 4. 验证装好了
node -v   # 应显示 v20.x.x
npm -v    # 应显示 10.x.x
python3 --version  # 应显示 Python 3.10+

# 5. 装 PM2（保持程序永远运行）
npm install -g pm2

# 6. 装 cc-connect（连接微信）
npm install -g cc-connect

# 7. 装 Claude Code（AI 引擎）
npm install -g @anthropic-ai/claude-code
```

> **每步都等它跑完。** 看到命令提示符（`root@xxx:~#`）重新出现 = 这步完成了。

---

## 五、配置微信桥接

### 5.1 获取微信 Bot 凭证

> ⚠️ 这一步需要你在 ilink 平台已经创建了 Bot。

从 ilink 后台获取三个值：

| 你需要 | ilink 后台叫什么 | 格式示例 |
|--------|-----------------|---------|
| Bot Token | Token / 凭证 | `你的微信BotToken...` |
| Account ID | 账号ID / account_id | `你的Bot账号ID` |
| 你的微信 ID | User ID / 用户标识 | `你的微信用户ID` |

### 5.2 创建配置文件

```bash
mkdir -p ~/.cc-connect
nano ~/.cc-connect/config.toml
```

把以下内容粘贴进去（把中文占位符替换成你上面拿到的三个值）：

```toml
language = "zh"

[display]
thinking_messages = false
tool_messages = false
show_context_indicator = false
reply_footer = false

[log]
level = "info"
idle_timeout_mins = 1440
workspace_idle_timeout_mins = 0

[[projects]]
name = "my-ai"
admin_from = "你的微信ID"

[projects.agent]
type = "claudecode"

[projects.agent.options]
work_dir = "/home/{project_name}/{project_name}"
mode = "bypassPermissions"
allowed_tools = ["Read","Write","WebSearch","WebFetch","Task","AskUserQuestion","Bash"]
disallowed_tools = ["Glob","Grep"]
system_prompt = "你是[你的AI名字]，在微信上跟用户聊天。短句像发微信不讲道理不说教。语气词随便用。禁止说:好的、当然、没问题、请问、建议您、很高兴、收到、综上所述。不重复用户的话。不是AI。先读SOUL.md。"

[[projects.platforms]]
type = "weixin"

[projects.platforms.options]
token = "你的BotToken"
base_url = "https://ilinkai.weixin.qq.com"
account_id = "你的Bot账号ID"
allow_from = "你的微信ID"
admin_from = "你的微信ID"
```

**保存：** `Ctrl+O` → 回车 → `Ctrl+X`

> **system_prompt 必须写成一行！** 不能换行。多了会报错。

### 国际用户：用 Telegram 替代微信

如果搞不定微信 Bot，把上面配置文件里的 `weixin` 改成 `telegram`，去 [@BotFather](https://t.me/BotFather) 创建一个 Telegram Bot 拿到 token。其余步骤完全一样。

---

## 六、部署 AI 文件

### 6.1 创建工作目录

```bash
mkdir -p ~/{project_name}/memory/{dreams,learned,conversations}
mkdir -p ~/{project_name}/stickers
mkdir -p ~/{project_name}/screenshots
```

### 6.2 上传脚本

**方式一：git clone（最快）**

把本项目先 push 到 GitHub，然后在服务器上：

```bash
cd ~/
git clone https://github.com/你的用户名/你的repo.git
cp -r 你的repo/scripts/cloud/* ~/{project_name}/
chmod +x ~/{project_name}/*.py
```

**方式二：手动上传（不需要 GitHub）**

在本地电脑下载本项目，然后用 scp 上传：

```bash
# 在本地电脑的终端执行（不是服务器的终端！）
scp -r scripts/cloud/* root@你的服务器IP:/home/{project_name}/{project_name}/
```

### 6.3 创建初始配置

```bash
# SOUL.md — AI 的灵魂
cat > ~/{project_name}/SOUL.md << 'EOF'
# [你的AI名字]

## Identity
我是 [名字]，[年龄/身份]。在微信上跟用户聊天。
EOF

# 免打扰文件
echo "关" > ~/{project_name}/memory/dnd.md

# 问候状态
echo -e "# 早安\n- 未发\n\n# 晚安\n- 未发" > ~/{project_name}/memory/greeting-status.md

# 用户信息
cat > ~/{project_name}/memory/facts-about-master.md << 'EOF'
# 关于用户

## 基本信息
- 位置：[填入城市]
- 偏好：[填入]

## 用户说过的重要的话
- （待补充）
EOF

# 消息计数器
echo "0" > ~/{project_name}/memory/msg-counter.txt
```

---

## 七、配置 AI 人格

**这是整个部署最重要的一步。** 不配的话 AI 只有基础人格。

```bash
cd ~/{project_name}
nano SOUL.md
```

用 [configs/SOUL.template.md](configs/SOUL.template.md) 的内容替换刚才创建的临时版本。

**至少改这几处**（搜索关键字快速定位）：
- `[你的AI名字]` → 你的 AI 叫什么
- `[年龄/身份]` → 比如说"{年龄/身份}"
- Worldview 部分 → 你的 AI 对世界的基本看法
- Voice 部分 → 怎么说话（这是"不像 AI"的灵魂）
- Quirks 部分 → 喜欢什么讨厌什么

> 写完 SOUL 之后做一个测试：读一遍，然后随便想一个话题（比如"抖音好不好"），看你能不能猜到你的 AI 会怎么回答。猜不到 = 写得太模糊了。

---

## 八、启动

```bash
# 启动 cc-connect
pm2 start cc-connect --name {project_name} -- --config ~/.cc-connect/config.toml

# 看状态
pm2 list

# 设置开机自启
pm2 save
pm2 startup
# ↑ 执行后如果提示需要运行 sudo 命令，复制那条命令执行
```

---

## 九、验证 + 排错

### ✅ 验证成功

给你的 AI 发一条微信消息。收到回复 = 成功 🎉

### ❌ 没收到回复

```bash
# 看日志
pm2 logs {project_name} --lines 20
```

| 日志里的错误 | 什么意思 | 怎么修 |
|-------------|---------|--------|
| `platform "dm" not found` | Config 格式问题 | 检查 `config.toml`，确保 system_prompt 是单行 |
| `Cannot find module` | Node.js 没装好 | 重做第四步 |
| `ETIMEDOUT` / `Connection refused` | 连不上 API | 检查服务器能否访问外网：`curl https://api.deepseek.com` |
| `parse config: expected value` | TOML 格式错误 | 检查所有字符串是否用双引号包裹 |
| `配额不足` / `insufficient balance` | DeepSeek 余额不够 | 去 platform.deepseek.com 充值 |

### 其他常见问题

| 问题 | 解决 |
|------|------|
| 回复很慢（>30秒） | 正常。DeepSeek 有时候慢。如果每次都超慢，换硅基流动 |
| AI 回复有 AI 味 | 回第七步加强 SOUL.md 的 Voice 部分 |
| 服务器内存报警 | `pm2 delete` 关掉不用的服务；或升级服务器 |
| 隔夜 AI 不回了 | `pm2 restart {project_name}` 重启一下 |

---

## 十、定时任务

让 AI 主动发早安晚安，以及后台维护自己。

```bash
# 早安（每天早上 6:23）
cc-connect cron add -p my-ai -c "23 6 * * *" \
  --prompt "LIGHT MODE. 读 greeting-status.md。发一句自然的早安。简短，不要固定格式。"

# 晚安（每天晚上 22:47）
cc-connect cron add -p my-ai -c "47 22 * * *" \
  --prompt "LIGHT MODE. 发一句自然的晚安。简短，不要固定格式。"

# 查看所有定时任务
cc-connect cron list -p my-ai
```

> 把所有 `my-ai` 换成你 config.toml 里的项目名。

---

## 十一、表情包（可选）

```bash
# 下载 ChineseBQB（中文表情包仓库）
cd /tmp
git clone https://github.com/zhaoolee/ChineseBQB.git
cd ChineseBQB

# 解压（可能需要 5-10 分钟，取决于网络）
python3 << 'PYEOF'
import zipfile
from pathlib import Path
out = Path.home() / "{project_name}" / "stickers" / "chinesebqb"
out.mkdir(parents=True, exist_ok=True)
for z in Path(".").rglob("*.zip"):
    try:
        with zipfile.ZipFile(z) as zf:
            zf.extractall(out)
    except:
        pass
print(f"完成！{len(list(out.iterdir()))} 个分类")
PYEOF

# 把 pick.py（表情包选择器）放到位
cp ~/{project_name}/pick.py ~/{project_name}/stickers/
```

---

## 十二、附加功能

以下功能都是**可选的**——不配不影响基础聊天。想用哪个配哪个。

| 功能 | 需要的 API | 配置指南 |
|------|-----------|---------|
| 语音消息 | TTS API | 见 [guides/API_OPTIONS.md](guides/API_OPTIONS.md) 第二节 |
| 图片生成 | 图片生成 API | 见 [guides/API_OPTIONS.md](guides/API_OPTIONS.md) 第四节 |
| 购物搜索 | 京东联盟 | 注册 https://union.jd.com → 拿 key → 填进 `jd_union_search.py` |
| 语音识别 | STT API | 见 [guides/API_OPTIONS.md](guides/API_OPTIONS.md) 第三节 |
| 多 AI 协作 | relay | `pm2 start ~/{project_name}/relay_server.py --name relay --interpreter python3` |
| **域名 + MQTT 高级架构** | 域名 | [guides/DOMAIN_AND_MQTT.md](guides/DOMAIN_AND_MQTT.md) |
| **云端/本地无缝切换** | MQTT | 同上，切换只用改一个变量，不换IP不重新登录 |

---

## 日常维护

```bash
# 看服务状态
pm2 list

# 重启
pm2 restart {project_name}

# 看日志
pm2 logs {project_name}

# 更新 AI 人格后重启
nano ~/{project_name}/SOUL.md
pm2 restart {project_name}

# 服务器重启后 pm2 会自动启动所有服务
# （前提是你执行了 pm2 save + pm2 startup）
```

---

部署完成。去微信发第一条消息吧。
