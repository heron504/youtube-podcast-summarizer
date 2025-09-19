# 快速开始指南

## 🚀 方案A：演示模式（推荐新手）

无需YouTube API，使用示例数据快速测试系统：

### 1. 获取OpenRouter API密钥
- 访问 https://openrouter.ai/
- 注册并创建API密钥

### 2. 获取QQ邮箱授权码
- QQ邮箱网页版 → 设置 → 账户
- 开启IMAP/SMTP服务
- 获取授权码（16位）

### 3. 编辑配置
编辑 `config/.env` 文件：
```
OPENROUTER_API_KEY=sk-or-v1-xxxxx（你的密钥）
EMAIL_USERNAME=your@qq.com
EMAIL_PASSWORD=abcdefghijklmnop（QQ授权码）
EMAIL_TO=recipient@qq.com
```

### 4. 运行演示
```bash
python demo_without_youtube.py
```

## 🎯 方案B：完整功能（需要YouTube API）

如果你想要获取真实的YouTube订阅：

### 1. Google Cloud Console设置
- 创建项目
- 启用YouTube Data API v3
- 创建OAuth 2.0客户端ID（桌面应用）
- 下载credentials.json文件

### 2. 配置文件
在config/.env中添加：
```
YOUTUBE_API_KEY=（OAuth不需要这个，留空）
```

### 3. 运行完整系统
```bash
python src/main.py --once
```

## 💡 建议流程

1. **先运行方案A**确认系统工作正常
2. **再配置YouTube API**获取真实订阅数据
3. **最后部署到GitHub Actions**实现自动化

这样可以逐步验证每个功能是否正常。