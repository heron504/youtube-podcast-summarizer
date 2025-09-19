# GitHub Actions 部署指南

## 📋 设置步骤

### 1. 将代码推送到GitHub

```bash
# 在项目目录中执行
git init
git add .
git commit -m "Initial commit: YouTube Podcast Summarizer"

# 在GitHub创建新仓库，然后执行
git branch -M main
git remote add origin https://github.com/你的用户名/youtube_podcast_summarizer.git
git push -u origin main
```

### 2. 在GitHub仓库中设置Secrets

进入你的GitHub仓库 → Settings → Secrets and variables → Actions

添加以下Repository secrets：

| Secret Name | Value | 说明 |
|------------|--------|------|
| `OPENROUTER_API_KEY` | 你的OpenRouter API密钥 | 从 https://openrouter.ai/ 获取 |
| `OPENROUTER_MODEL` | `anthropic/claude-3.5-sonnet` | 使用的AI模型 |
| `EMAIL_USERNAME` | 你的QQ邮箱地址 | 如：example@qq.com |
| `EMAIL_PASSWORD` | QQ邮箱授权码 | 不是登录密码！ |
| `EMAIL_TO` | 接收报告的邮箱 | 可以是任何邮箱 |
| `EMAIL_SMTP_SERVER` | `smtp.qq.com` | QQ邮箱SMTP服务器 |
| `EMAIL_SMTP_PORT` | `587` | SMTP端口 |

### 3. 获取QQ邮箱授权码

1. 登录QQ邮箱网页版
2. 设置 → 账户
3. 找到"POP3/IMAP/SMTP服务"
4. 开启"IMAP/SMTP服务"
5. 获取授权码（不是QQ密码！）
6. 将授权码填入 `EMAIL_PASSWORD`

### 4. 获取OpenRouter API密钥

1. 访问 https://openrouter.ai/
2. 注册并登录
3. 在API Keys页面创建新密钥
4. 复制密钥到 `OPENROUTER_API_KEY`

### 5. 测试运行

- 推送代码后，转到Actions页面
- 点击"Daily YouTube Podcast Summary"
- 点击"Run workflow" 手动测试运行
- 检查运行日志确保无错误

### 6. 定时运行

- 工作流将每天北京时间早上8点自动运行
- 可在Actions页面查看运行历史
- 如果失败，检查Secrets设置和日志

## 🔧 自定义设置

### 修改运行时间

编辑 `.github/workflows/daily-summary.yml`:

```yaml
schedule:
  # 修改这里的时间 (UTC时间)
  - cron: '0 0 * * *'  # 北京时间8点 = UTC 0点
```

### 修改AI模型

在GitHub Secrets中修改 `OPENROUTER_MODEL`:
- `anthropic/claude-3.5-sonnet` (推荐)
- `openai/gpt-4-turbo`
- `google/gemini-pro`
- 等其他支持的模型

## 💰 费用说明

- **GitHub Actions**: 每月2000分钟免费额度，足够日常使用
- **OpenRouter API**: 按使用量付费，每日摘要约$0.01-0.05
- **QQ邮箱**: 完全免费

## 🐛 故障排除

### 常见错误

1. **API密钥错误**: 检查Secrets设置
2. **邮件发送失败**: 确认QQ邮箱授权码正确
3. **权限错误**: 确保仓库是public或有正确的权限

### 查看日志

- Actions页面 → 选择运行记录 → 查看详细日志
- 下载Artifacts中的logs文件

## 📧 测试邮件发送

可以本地运行一次测试：

```bash
# 确保已填写config/.env文件
python src/main.py --once
```

成功后再推送到GitHub运行自动化任务。