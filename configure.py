"""
配置助手脚本 - 帮助用户设置API密钥和邮箱配置
"""
import os
import shutil

def setup_env_file():
    """设置环境变量文件"""
    config_dir = 'config'
    env_template = os.path.join(config_dir, '.env.template')
    env_file = os.path.join(config_dir, '.env')

    if os.path.exists(env_file):
        print(f"⚠️  配置文件 {env_file} 已存在")
        choice = input("是否要重新配置？(y/N): ").lower()
        if choice != 'y':
            return False

    # Copy template to .env
    shutil.copy(env_template, env_file)
    print(f"✅ 已创建配置文件: {env_file}")

    print("\n" + "="*60)
    print("🔧 API密钥配置指南")
    print("="*60)

    # Gemini API Key setup
    print("\n1️⃣  Gemini API 密钥设置:")
    print("   🔗 访问: https://ai.google.dev/")
    print("   📝 点击 'Get API key' 获取免费的Gemini API密钥")
    gemini_key = input("   请输入你的Gemini API密钥: ").strip()

    # Email configuration
    print("\n2️⃣  邮箱配置:")
    print("   📧 推荐使用Gmail (其他邮箱需要修改SMTP设置)")
    email_username = input("   请输入发件人邮箱: ").strip()
    email_password = input("   请输入邮箱应用密码 (不是登录密码!): ").strip()
    email_to = input("   请输入收件人邮箱: ").strip()

    # Optional YouTube API
    print("\n3️⃣  YouTube API (可选, 直接回车跳过):")
    print("   🔗 如需YouTube订阅功能，需要在Google Cloud Console设置")
    youtube_key = input("   YouTube API Key (可选): ").strip()

    # Update .env file
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()

    if gemini_key:
        content = content.replace('your_gemini_api_key_here', gemini_key)
    if email_username:
        content = content.replace('your_email@gmail.com', email_username)
    if email_password:
        content = content.replace('your_app_password_here', email_password)
    if email_to:
        content = content.replace('recipient@gmail.com', email_to)
    if youtube_key:
        content = content.replace('your_youtube_api_key_here', youtube_key)

    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✅ 配置已保存到 {env_file}")
    return True

def show_gmail_setup_guide():
    """显示Gmail设置指南"""
    print("\n" + "="*60)
    print("📧 Gmail 应用密码设置指南")
    print("="*60)
    print("1. 登录你的Gmail账户")
    print("2. 前往: https://myaccount.google.com/security")
    print("3. 开启两步验证 (如果还没有开启)")
    print("4. 搜索 '应用专用密码' 或访问: https://myaccount.google.com/apppasswords")
    print("5. 选择应用类型为 '邮件'，设备类型为 '其他'")
    print("6. 输入应用名称 (如: YouTube Summarizer)")
    print("7. 复制生成的16位应用密码")
    print("8. 在上面的配置中输入这个16位密码，不是你的Gmail登录密码!")

def show_next_steps():
    """显示后续步骤"""
    print("\n" + "="*60)
    print("🚀 下一步操作")
    print("="*60)
    print("1. 测试运行:")
    print("   python src/main.py --once")
    print("\n2. 如果测试成功，启动定时任务:")
    print("   python src/main.py")
    print("\n3. 检查日志文件:")
    print("   查看 logs/ 目录下的日志文件")
    print("\n4. 查看生成的报告:")
    print("   查看 reports/ 目录下的PDF文件")

def main():
    print("YouTube Podcast Summarizer - Configuration Helper")
    print("=" * 60)

    if not os.path.exists('config'):
        print("❌ 配置目录不存在，请先运行: python setup.py")
        return

    # Setup environment file
    if setup_env_file():
        show_gmail_setup_guide()
        show_next_steps()

        print("\n" + "="*60)
        print("✨ 配置完成！现在可以开始使用了")
        print("="*60)
    else:
        print("⏹️  配置取消")

if __name__ == "__main__":
    main()