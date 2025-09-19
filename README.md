# YouTube Podcast Summarizer

自动化YouTube播客摘要生成器，每日获取订阅的YouTube视频，使用AI生成中文摘要，并通过邮件发送PDF报告。

## 功能特点

- 🔄 **自动化运行**：每天北京时间8点自动运行
- 📺 **YouTube集成**：获取最近24小时内的订阅视频
- 🤖 **AI摘要**：使用OpenRouter API生成300-500字的中文摘要
- 📄 **PDF报告**：格式化生成带有视频链接的PDF报告
- 📧 **邮件发送**：自动发送到指定邮箱
- ☁️ **云端运行**：通过GitHub Actions实现云端自动化

## 部署到GitHub Actions

### 1. Fork或创建仓库

将此仓库fork到你的GitHub账号，或创建新仓库并上传代码。

### 2. 配置Secrets

在GitHub仓库的 Settings > Secrets and variables > Actions 中添加以下secrets：

**必需配置：**
- `OPENROUTER_API_KEY` - OpenRouter API密钥
- `EMAIL_USERNAME` - QQ邮箱用户名
- `EMAIL_PASSWORD` - QQ邮箱授权码
- `EMAIL_TO` - 接收报告的邮箱地址

**可选配置：**
- `YOUTUBE_API_KEY` - YouTube Data API密钥（推荐配置）
- `YOUTUBE_CREDENTIALS_JSON` - YouTube OAuth2凭据JSON（如需要）

### 3. 启用GitHub Actions

1. 进入仓库的 Actions 标签页
2. 点击 "I understand my workflows, go ahead and enable them"
3. 工作流将每天北京时间上午8点自动运行

### 4. 手动测试运行

可以在Actions页面点击"Daily YouTube Podcast Summary"工作流，然后点击"Run workflow"进行手动测试。

## API密钥获取

### OpenRouter API
1. 访问 [OpenRouter](https://openrouter.ai/)
2. 注册账号并获取API密钥
3. 确保账户有足够余额

### YouTube Data API (可选)
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目并启用YouTube Data API v3
3. 创建API密钥

### QQ邮箱配置
1. 登录QQ邮箱
2. 设置 > 账户 > POP3/IMAP/SMTP服务
3. 开启SMTP服务并获取授权码

## 本地开发

### 环境要求
- Python 3.11+
- 依赖包见 `requirements.txt`

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置文件
创建 `config/.env` 文件：
```env
# OpenRouter API
OPENROUTER_API_KEY=your_openrouter_key

# YouTube API (可选)
YOUTUBE_API_KEY=your_youtube_key
YOUTUBE_CREDENTIALS_FILE=config/youtube_credentials.json

# QQ邮箱配置
EMAIL_SMTP_SERVER=smtp.qq.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_qq_email
EMAIL_PASSWORD=your_qq_auth_code
EMAIL_TO=recipient@email.com

# 代理配置 (如需要)
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890

# 其他配置
MAX_CHANNELS_TO_PROCESS=50
MAX_VIDEOS_PER_CHANNEL=5
DAYS_BACK_TO_FETCH=1
PDF_OUTPUT_DIR=reports
DEBUG=false
```

### 运行
```bash
# 单次运行
python src/main.py --once

# 启动调度器
python src/main.py
```

## 项目结构

```
youtube_podcast_summarizer/
├── src/
│   ├── main.py              # 主程序
│   ├── config_manager.py    # 配置管理
│   ├── youtube_client.py    # YouTube API客户端
│   ├── fixed_summarizer.py  # AI摘要生成器
│   ├── fixed_pdf_generator.py # PDF报告生成器
│   └── email_sender.py      # 邮件发送器
├── config/
│   └── .env                 # 环境变量配置
├── .github/workflows/
│   └── daily_summary.yml    # GitHub Actions工作流
├── requirements.txt         # Python依赖
└── README.md               # 说明文档
```

## 输出格式

生成的PDF报告包含：
- 📅 报告日期和视频数量统计
- 📺 每个视频的标题（加粗）和中文翻译
- 🏷️ 频道名称和视频链接
- 📝 300-500字的中文摘要（1.5倍行距）

## 故障排除

### 常见问题
1. **YouTube API配额超限**：正常现象，系统会在配额重置后恢复
2. **邮件发送失败**：检查QQ邮箱SMTP设置和授权码
3. **PDF生成失败**：检查系统字体支持
4. **OpenRouter API错误**：检查API密钥和余额

### 查看日志
GitHub Actions运行后可以下载日志文件查看详细信息。

## 许可证

MIT License
