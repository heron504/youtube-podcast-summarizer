"""
部署和调度方案选择器
"""
import os
import sys

def show_deployment_options():
    """显示不同的部署选择"""
    print("=" * 60)
    print("🚀 YouTube Podcast Summarizer - 部署选择")
    print("=" * 60)

    options = {
        "1": {
            "name": "本地运行 (需要电脑开机)",
            "pros": ["设置简单", "免费", "数据在本地"],
            "cons": ["需要电脑一直开着", "不稳定"],
            "suitable": "适合：测试使用，偶尔运行"
        },
        "2": {
            "name": "GitHub Actions (推荐)",
            "pros": ["完全免费", "云端运行", "稳定可靠", "自动备份"],
            "cons": ["需要学习GitHub", "有运行时间限制"],
            "suitable": "适合：日常使用，自动化"
        },
        "3": {
            "name": "云服务器 (VPS)",
            "pros": ["24小时运行", "完全控制", "性能稳定"],
            "cons": ["需要付费", "需要服务器管理知识"],
            "suitable": "适合：专业使用，高频率需求"
        },
        "4": {
            "name": "树莓派/小主机",
            "pros": ["一次投资", "本地控制", "低功耗"],
            "cons": ["需要硬件投资", "需要技术知识"],
            "suitable": "适合：技术爱好者，家庭使用"
        }
    }

    for key, option in options.items():
        print(f"\n{key}. {option['name']}")
        print(f"   优点: {', '.join(option['pros'])}")
        print(f"   缺点: {', '.join(option['cons'])}")
        print(f"   {option['suitable']}")

    return options

def create_github_actions_workflow():
    """创建GitHub Actions工作流文件"""
    workflow_content = """name: Daily YouTube Podcast Summary

on:
  schedule:
    # 每天北京时间早上8点运行 (UTC 00:00)
    - cron: '0 0 * * *'
  workflow_dispatch:  # 允许手动触发

jobs:
  generate-summary:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run podcast summarizer
      env:
        OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
        OPENROUTER_MODEL: ${{ secrets.OPENROUTER_MODEL }}
        EMAIL_USERNAME: ${{ secrets.EMAIL_USERNAME }}
        EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
        EMAIL_TO: ${{ secrets.EMAIL_TO }}
        EMAIL_SMTP_SERVER: ${{ secrets.EMAIL_SMTP_SERVER }}
        EMAIL_SMTP_PORT: ${{ secrets.EMAIL_SMTP_PORT }}
      run: |
        python src/main.py --once

    - name: Upload logs
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: logs
        path: logs/

    - name: Upload reports
      uses: actions/upload-artifact@v4
      if: success()
      with:
        name: reports
        path: reports/
"""

    # 创建.github/workflows目录
    os.makedirs('.github/workflows', exist_ok=True)

    workflow_path = '.github/workflows/daily-summary.yml'
    with open(workflow_path, 'w', encoding='utf-8') as f:
        f.write(workflow_content)

    print(f"✅ GitHub Actions工作流已创建: {workflow_path}")
    return workflow_path

def create_windows_task_scheduler():
    """创建Windows定时任务脚本"""
    bat_content = f"""@echo off
cd /d "{os.getcwd()}"
python src/main.py --once
"""

    with open('run_daily_summary.bat', 'w', encoding='gbk') as f:
        f.write(bat_content)

    print("✅ Windows批处理脚本已创建: run_daily_summary.bat")
    print("请手动在Windows任务计划程序中创建任务：")
    print("1. 打开'任务计划程序'")
    print("2. 创建基本任务")
    print("3. 设置每日触发")
    print(f"4. 操作选择: {os.path.abspath('run_daily_summary.bat')}")

def create_linux_cron():
    """创建Linux cron任务"""
    cron_content = f"""# 每天早上8点运行YouTube摘要
0 8 * * * cd {os.getcwd()} && python src/main.py --once >> logs/cron.log 2>&1
"""

    with open('crontab_entry.txt', 'w') as f:
        f.write(cron_content)

    print("✅ Cron任务配置已创建: crontab_entry.txt")
    print("在Linux系统中执行以下命令添加定时任务：")
    print("crontab -e")
    print("然后将crontab_entry.txt的内容添加到文件末尾")

def show_github_actions_setup():
    """显示GitHub Actions设置指南"""
    print("\n" + "=" * 60)
    print("📋 GitHub Actions 设置指南")
    print("=" * 60)
    print("1. 将代码推送到GitHub仓库")
    print("2. 在GitHub仓库设置中添加Secrets:")
    print("   - OPENROUTER_API_KEY: 你的OpenRouter API密钥")
    print("   - OPENROUTER_MODEL: anthropic/claude-3.5-sonnet")
    print("   - EMAIL_USERNAME: 你的QQ邮箱")
    print("   - EMAIL_PASSWORD: QQ邮箱授权码")
    print("   - EMAIL_TO: 接收邮件的邮箱")
    print("   - EMAIL_SMTP_SERVER: smtp.qq.com")
    print("   - EMAIL_SMTP_PORT: 587")
    print("3. 工作流将每天自动运行")
    print("4. 可在Actions页面查看运行状态和日志")

def main():
    print("选择部署方案:")
    options = show_deployment_options()

    print("\n" + "=" * 60)
    choice = input("请选择部署方案 (1-4): ").strip()

    if choice == "1":
        print("\n本地运行设置:")
        print("直接运行: python src/main.py")
        print("定时运行需要电脑保持开机状态")

    elif choice == "2":
        print("\n正在创建GitHub Actions配置...")
        create_github_actions_workflow()
        show_github_actions_setup()

    elif choice == "3":
        print("\n云服务器部署建议:")
        print("1. 购买VPS (推荐: 腾讯云, 阿里云)")
        print("2. 安装Python环境")
        print("3. 上传代码并安装依赖")
        print("4. 使用cron设置定时任务")
        create_linux_cron()

    elif choice == "4":
        print("\n树莓派部署建议:")
        print("1. 安装Raspberry Pi OS")
        print("2. 安装Python和依赖")
        print("3. 设置开机自启和定时任务")
        create_linux_cron()

    else:
        print("无效选择")
        return

    print("\n" + "=" * 60)
    print("✨ 部署方案配置完成！")

if __name__ == "__main__":
    main()