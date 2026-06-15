# 域名 + MQTT 高级架构指南

如果你有一个域名（比如 `your-domain.top`），可以解锁云端/本地无缝切换，零风控风险。

---

## 为什么要域名

不用域名也能跑——直接用云服务器 IP。但加上域名后：

- **MQTT 路由**：`mqtt.你的域名.top` → 本地 AI 通过域名连接云服务器消息队列
- **代码不写死 IP**：换服务器只改 DNS，不改代码
- **Web 控制台**：可以部署一个 Admin Dashboard
- **短链接购物**：`go.你的域名.top/商品` 代替淘宝口令
- **SSL 证书**：Cloudflare 免费提供，隐藏服务器真实 IP

---

## 架构对比

### 无域名（基础版）

```
微信 → 云服务器IP → cc-connect → Claude Code
```

一切都在云端跑。本地电脑只用来 SSH 管理。

### 有域名（进阶版）

```
微信 → 云端网关(唯一微信入口)
         ├── mode=cloud → 云端 Claude 直接回复
         └── mode=local → MQTT → 本地 Worker → Claude → MQTT → 网关 → 微信

mqtt.your-domain.top          ← MQTT 消息队列
admin.your-domain.top (可选)  ← Web 控制台
go.your-domain.top (可选)     ← 购物短链接
```

**关键优势：** 切换"云端/本地"只改变一个变量值。微信端永远只看到云端固定 IP，不需要重新登录，完美规避异地登录风控。

---

## 实施步骤

### 第一步：配置 DNS

在域名后台（阿里云万网/Cloudflare 等）添加 A 记录：

| 主机记录 | 类型 | 值 |
|---------|------|-----|
| `@` | A | 你的云服务器 IP |
| `mqtt` | A | 你的云服务器 IP |

等 2-5 分钟生效。测试：`ping mqtt.你的域名.top`

### 第二步：云服务器装 Mosquitto

```bash
apt install -y mosquitto mosquitto-clients
```

配置密码：
```bash
mosquitto_passwd -c /etc/mosquitto/passwd {project_name}
# 输入你的密码
```

创建配置文件 `/etc/mosquitto/conf.d/{project_name}.conf`：
```
listener 1883 0.0.0.0
allow_anonymous false
password_file /etc/mosquitto/passwd
```

重启：`systemctl restart mosquitto`

### 第三步：部署云端网关

把 `scripts/cloud/relay_gateway.py` 部署到云服务器，用 PM2 管理：

```bash
pm2 start relay_gateway.py --name gateway --interpreter python3
pm2 save
```

### 第四步：配置本地 Worker

在 Windows 本地机器上，把 `scripts/local/mqtt_local_worker.py` 配置好。

创建 `.env` 文件：
```
MQTT_BROKER=mqtt.你的域名.top
MQTT_PORT=1883
MQTT_USER={project_name}
MQTT_PASS=你的密码
```

依赖安装：`pip install paho-mqtt`

### 第五步：启动本地 Worker

```powershell
python mqtt_local_worker.py
```

建议加到 Windows 开机启动。

---

## 切换流程

在微信上发消息给 你的AI：

- **"切换到本地"** → 云端网关转发到 MQTT → 本地 Worker 用 Claude 处理 → 返回微信
- **"切换到云端"** → 云端 Claude 直接处理

切换是软切换——只是改一个 mode 变量。云端 cc-connect 从不停止，IP 永远不变。

---

## 无域名版

如果不想买域名，直接用 IP 也能跑 MQTT：

1. 所有 `mqtt.你的域名.top` 改成 `你的服务器IP`（你的云服务器 IP）
2. 本地 Worker 需要 SSH 隧道连接 MQTT（因为阿里云安全组可能拦截外部 MQTT 流量）

SSH 隧道命令：
```bash
ssh -f -N -L 1884:localhost:1883 -i ~/.ssh/cloud_user {project_name}@你的IP
```

然后 Worker 连 `127.0.0.1:1884` 即可。

---

## 安全建议

1. **套 Cloudflare**：免费 CDN + SSL，隐藏服务器真实 IP
2. **MQTT 用密码**：不用匿名访问
3. **1883 端口**：可以不开在公网，用 SSH 隧道更安全
4. **API Key 放 .env**：不要提交到 GitHub

---

## 费用

| 项目 | 费用 |
|------|------|
| 域名 | 6-19 元/年 |
| Cloudflare | 免费 |
| Mosquitto | 免费开源 |
| 云服务器 | 跟基础部署共用，不额外加钱 |
