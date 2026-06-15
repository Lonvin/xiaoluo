# 我们踩过的坑

按时间顺序记录从零到一部署你的AI的全部问题与解决方案。

---

## 1. cc-connect 配置

**问题：** TOML 格式报错 `parse config: expected value but found "xx" instead`

**原因：** TOML 对字符串格式要求严格。`language = zh` 不会被解析为字符串，必须加引号 `language = "zh"`。system_prompt 中包含换行符 `\n` 也会导致解析失败。

**解决：** system_prompt 写成单行，不加换行符。所有字符串值加双引号。

---

## 2. 后台进程频繁崩溃

**问题：** Cloud claude-bot 频繁停止响应，pm2 显示重启几十次。

**原因：** 
- bot.sh 只读取 task.md 第一行（`head -1`），丢失了详细指令
- 并发修改 task.md 导致 md5 hash 没变但内容变了
- 没有日志，无法排查

**解决：**
- `head -1` → `tail -n +2 | head -c 2000`（读全部内容）
- 双重检测：md5 hash AND 内容比对
- 加 bot.log 日志记录每次触发

---

## 3. LibreOffice 转 PPT 踩坑

**问题：** 需要把 .ppt 转 .pptx 修复手机显示乱码，服务器没有 LibreOffice。

**解决过程：**
1. `apt install libreoffice` → 需要 sudo 密码，没有
2. `apt download libreoffice-impress` → 下载 .deb 但不安装
3. `dpkg-deb -x *.deb ~/lo/` → 手动解压提取可执行文件
4. `~/lo/opt/libreoffice*/program/soffice --headless --convert-to pptx` → 启动报 "Could not find platform independent libraries" → 这是个无害警告，转换实际成功了
5. 中文文件名在 git 里乱码 → 放弃 git checkout，直接用 Python zipfile 解压

**教训：** 没有 sudo 的服务器上装大型软件可以先下载 .deb 包手动解压。找个有空余空间的目录（`/tmp` 或 `~`）。

---

## 4. DeepSeek 余额监控

**问题：** 需要在余额低时自动告警，并优化 token 使用。

**解决：**
- Python 脚本调用 `https://api.deepseek.com/user/balance`
- 三级阈值：🟡10元 🔴5元 🚨2元
- cron 每6小时检查一次
- 余额低时自动启用省钱策略（关 thinking、精简回复）
- Windows GBK 编码问题：加 `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")`

---

## 5. 表情包从 0 到 575 张

**初版问题：** 用 Pillow 生成文字色块图片——用户原话"只有一个框，里面只有孤零零的文字，很难算是表情"

**解决：**
- 从 [ChineseBQB](https://github.com/zhaoolee/ChineseBQB) 下载真实中文网络表情包
- 仓库里是 .zip 文件，不能用 `git checkout`（中文文件名乱码）
- 用 Python zipfile 逐个解压
- 创建 `pick.py` 选择器：输入情绪词 → 匹配文件名 → 返回路径
- 最终：575张（291 GIF + 252 JPG + 9 PNG），分8个类别

---

## 6. 反AI味改造

**问题：** AI 回复有明显的机器味——"好的！""收到！""根据我的分析""综上所述""如有需要请随时找我"

**解决：**
- 创建 `anti-ai-voice.md` 禁词清单（融合 humanizer 29 种模式 + stop-slop 6 条自检）
- system_prompt 直接内置核心规则：禁止"好的/当然/没问题/请问/建议您/高兴/收到/综上所述"
- SOUL.md 加对话示例（❌ vs ✅ 对比）
- 关键认知：不是"让 AI 更像人"，是"禁止 AI 做那些人类不会做的事"

---

## 7. 人格深度

**迭代过程：**
1. v1：空泛描述 "温柔可爱"
2. v2：加情绪体系、场景模式
3. v3：参考 [aaronjmars/soul.md](https://github.com/aaronjmars/soul.md) 重写——加世界观、矛盾、品味、触发点、背景故事
4. v4：对标 aaronjmars 本人的 SOUL.md 密度，Voice 部分覆盖句法结构、消息结构、标点符号学、17种情绪节奏模式、话题切换、6种消息回应模式、6种互动模式、28种禁词

**核心认知：** 好的 SOUL.md 是"读完能预测这个人遇到新话题会说什么"——不是描述，是观点。说"我喜欢猫"不是观点，说"我觉得朋友圈三天可见的人都有秘密"才是。

---

## 8. Token 优化

**问题：** 后台 cron 每次醒来都完整读一遍 SOUL.md + AGENTS.md，浪费大量 token。

**解决：**
- 所有后台 cron 加 `LIGHT MODE: skip SOUL.md/AGENTS.md` 前缀
- 主动检查从每小时 → 取消（只在早安晚安窗口联系用户）
- 必读文件瘦身：AGENTS.md 8.5KB→7KB, stickers-guide 6.4KB→846B, anti-ai-voice 4.4KB→980B
- 完整版指南保留为按需读取的参考文件

**效果：** 日省约 60,000 tokens（~0.5 CNY/天）

---

## 9. 淘宝/京东购物

**失败路径：**
- 淘宝：云端无头浏览器 → 北京数据中心 IP → 秒封
- 京东社交媒体渠道：API 403，权限不够
- 京东网站渠道：需要 ICP 备案（几周起步）

**可行路径：**
- 京东联盟 API（社交媒体渠道可转链接，搜索需要网站渠道）
- WebSearch 搜商品 + 手动购买（不用 API，0 成本）
- 本地 Chrome CDP（OpenClaw 同款方案）：通过 `--remote-debugging-port=9222` 连真实浏览器

---

## 10. 消息多线程（未解决）

**问题：** 用户连续发多条消息，你的AI只回第一条。

**根因：** cc-connect 单线程架构——串行处理消息队列，Claude Code 处理消息1时消息2在排队。

**尝试过的方案：**
- Claude Code wrapper 缓冲合并 → 有时间竞争问题
- HTTP 代理拦截 → cc-connect 用持久连接，不是 webhook
- 自写 gateway 替代 cc-connect → 工作量大，未完成

**当前缓解措施：** AGENTS.md 加多消息处理规则——你的AI启动时检查是否有多条未读消息，一次性回应。

---

## 11. 中文字体在 Linux 上

**问题：** 生成图片时中文显示为方块。

**解决：**
```bash
apt download fonts-wqy-microhei
dpkg-deb -x fonts-wqy-microhei*.deb /tmp/font_extract/
# 字体文件在 /tmp/font_extract/usr/share/fonts/truetype/wqy/
```

---

## 12. Clash 代理

**问题：** 服务器在国内，无法访问 GitHub raw、Google 等。

**解决：**
- 安装 Mihomo (Clash Meta) v1.19.3
- HTTP 代理 127.0.0.1:7890
- pm2 托管运行
- `~/.bashrc` 配环境变量 `export http_proxy=http://127.0.0.1:7890`

---

## 核心教训

1. **先跑起来再优化。** 第一版只是一个能回微信的 Claude Code，够了。
2. **文件即配置。** 所有状态都是 Markdown/JSON，不用数据库，可以 git 版本控制。
3. **测试驱动的灵魂。** aaronjmars 的"弱模型校准"方法——拿便宜模型跑你的 SOUL，跑偏了就说明人格不够锋利。
4. **Token 是钱。** 每个 cron 每次读 SOUL.md 都是成本。LIGHT MODE 省了 >50% 后台 token。
5. **反爬是真实存在的。** 不要幻想云端无头浏览器能绕过淘宝京东的检测。
