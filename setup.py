"""
Setup script for YouTube Podcast Summarizer
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config_manager import ConfigManager

def create_directory_structure():
    """Create necessary directories"""
    directories = ['config', 'logs', 'reports']

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Created directory: {directory}")

def setup_configuration():
    """Setup configuration files"""
    config_manager = ConfigManager()

    # Create environment template
    config_manager.create_env_template()

    # Create initial settings file
    config_manager.save_settings()

    print("\nConfiguration setup completed!")
    print(f"Please edit the configuration files in the 'config' directory:")
    print(f"1. Copy .env.template to .env and fill in your API keys")
    print(f"2. Optionally modify settings.json for custom preferences")

def create_readme():
    """Create README file with setup instructions"""
    readme_content = """# YouTube Podcast Summarizer

自动化工具，每日拉取YouTube订阅更新，使用Gemini AI生成中文摘要并邮件发送PDF报告。

## 功能特性

- 🎯 自动获取YouTube订阅频道的最新视频
- 🤖 使用Google Gemini AI生成中文内容摘要
- 📄 生成美观的PDF报告
- 📧 自动邮件发送报告
- ⏰ 每日自动执行

## 安装设置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

复制 `config/.env.template` 为 `config/.env` 并填入以下信息：

- `GEMINI_API_KEY`: Google Gemini API密钥
- `EMAIL_USERNAME`: 发件人邮箱
- `EMAIL_PASSWORD`: 邮箱应用密码
- `EMAIL_TO`: 收件人邮箱

### 3. YouTube API设置（可选）

如需YouTube API功能，请：
1. 在Google Cloud Console创建项目
2. 启用YouTube Data API v3
3. 下载credentials.json到项目根目录
4. 首次运行时会提示OAuth认证

### 4. 运行程序

测试运行（执行一次）：
```bash
python src/main.py --once
```

启动定时任务：
```bash
python src/main.py
```

## 配置说明

### 邮箱配置

#### Gmail设置
- SMTP服务器: smtp.gmail.com
- 端口: 587
- 需要开启两步验证并生成应用专用密码

#### Outlook设置
- SMTP服务器: smtp-mail.outlook.com
- 端口: 587

### 程序配置

编辑 `config/settings.json`：

```json
{
  "max_videos_per_channel": 3,      // 每个频道最多处理视频数
  "max_channels_to_process": 20,    // 最多处理频道数
  "schedule_time": "08:00",         // 每日执行时间
  "pdf_output_dir": "reports",      // PDF输出目录
  "log_level": "INFO"               // 日志级别
}
```

## 目录结构

```
youtube_podcast_summarizer/
├── src/                    # 源代码
│   ├── main.py            # 主程序
│   ├── youtube_client.py  # YouTube API客户端
│   ├── summarizer.py      # 内容摘要器
│   ├── report_generator.py # PDF报告生成器
│   ├── email_sender.py    # 邮件发送器
│   └── config_manager.py  # 配置管理器
├── config/                # 配置文件
├── logs/                  # 日志文件
├── reports/               # 生成的PDF报告
└── requirements.txt       # Python依赖
```

## 注意事项

1. 首次运行需要YouTube OAuth认证
2. Gemini API有调用频率限制，注意配额使用
3. 邮箱需要开启SMTP服务并使用应用密码
4. PDF生成需要中文字体支持

## 故障排除

- 如遇到YouTube API配额不足，可降低处理频道数和视频数
- 邮件发送失败请检查SMTP设置和应用密码
- PDF中文显示异常请检查系统中文字体安装

## 许可证

MIT License
"""

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("Created README.md")

def main():
    print("YouTube Podcast Summarizer - 设置向导")
    print("=" * 50)

    # Create directory structure
    print("\n1. 创建目录结构...")
    create_directory_structure()

    # Setup configuration
    print("\n2. 设置配置文件...")
    setup_configuration()

    # Create README
    print("\n3. 创建说明文档...")
    create_readme()

    print("\n" + "=" * 50)
    print("设置完成! 请按照以下步骤继续：")
    print("\n1. 安装依赖包:")
    print("   pip install -r requirements.txt")
    print("\n2. 配置API密钥:")
    print("   编辑 config/.env 文件，填入你的API密钥和邮箱信息")
    print("\n3. 测试运行:")
    print("   python src/main.py --once")
    print("\n4. 启动定时任务:")
    print("   python src/main.py")

if __name__ == "__main__":
    main()