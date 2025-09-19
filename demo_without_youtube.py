"""
Demo version without YouTube API - using sample videos
"""
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_demo_videos():
    """Create sample video data for demo"""
    return [
        {
            "id": {"videoId": "dQw4w9WgXcQ"},
            "snippet": {
                "title": "AI在2024年的最新发展趋势",
                "channelTitle": "Tech Review频道",
                "description": "讨论人工智能在2024年的发展趋势，包括大语言模型、机器学习和自动化技术的最新进展。"
            }
        },
        {
            "id": {"videoId": "jNQXAC9IVRw"},
            "snippet": {
                "title": "深度学习入门指南",
                "channelTitle": "AI教育频道",
                "description": "为初学者介绍深度学习的基本概念，包括神经网络、反向传播和梯度下降算法。"
            }
        },
        {
            "id": {"videoId": "9bZkp7q19f0"},
            "snippet": {
                "title": "区块链技术的实际应用案例",
                "channelTitle": "科技前沿",
                "description": "探讨区块链技术在金融、供应链和数字身份验证中的实际应用案例。"
            }
        }
    ]

def demo_run():
    """Run demo without YouTube API"""
    print("YouTube Podcast Summarizer - Demo Mode")
    print("=" * 50)

    try:
        from config_manager import ConfigManager
        from summarizer import PodcastSummarizer
        from report_generator import ReportGenerator
        from email_sender import EmailSender

        # Load configuration
        config = ConfigManager()

        # Check OpenRouter API key
        if not config.openrouter_api_key or config.openrouter_api_key == 'your_openrouter_api_key_here':
            print("ERROR: Please configure OpenRouter API key in config/.env")
            return False

        print("1. Initializing components...")

        # Initialize summarizer
        summarizer = PodcastSummarizer(config.openrouter_api_key, config.openrouter_model)
        print("   - OpenRouter summarizer: OK")

        # Initialize report generator
        report_generator = ReportGenerator()
        print("   - PDF report generator: OK")

        # Initialize email sender
        email_sender = EmailSender(
            config.email_smtp_server,
            config.email_smtp_port,
            config.email_username,
            config.email_password
        )
        print("   - Email sender: OK")

        print("\n2. Processing demo videos...")
        demo_videos = create_demo_videos()
        summaries = []

        for i, video in enumerate(demo_videos, 1):
            print(f"   Processing video {i}/{len(demo_videos)}...")

            # Create mock transcript for demo
            mock_transcript = f"""
            This is a demo transcript for the video '{video['snippet']['title']}'
            from channel '{video['snippet']['channelTitle']}'.
            {video['snippet']['description']}

            In this video, we discuss the latest developments in technology,
            including artificial intelligence, machine learning, and their applications
            in various industries. The content covers both theoretical concepts
            and practical implementations.
            """

            # Generate summary using real API
            summary = summarizer.summarize_content(
                mock_transcript,
                video['snippet']['title'],
                video['snippet']['channelTitle']
            )

            if summary:
                summaries.append({
                    'title': video['snippet']['title'],
                    'channel': video['snippet']['channelTitle'],
                    'summary': summary,
                    'video_id': video['id']['videoId'],
                    'url': f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                })
                print(f"   [OK] Summary generated for: {video['snippet']['title']}")
            else:
                print(f"   [FAIL] Failed to generate summary for: {video['snippet']['title']}")

        if summaries:
            print(f"\n3. Generated {len(summaries)} summaries")

            # Generate PDF report
            print("4. Generating PDF report...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = f"reports/demo_report_{timestamp}.pdf"

            os.makedirs("reports", exist_ok=True)
            generated_pdf = report_generator.generate_report(summaries, pdf_path)

            if generated_pdf:
                print(f"   [OK] PDF report created: {generated_pdf}")

                # Send email
                if config.email_username and config.email_username != 'your_qq_email@qq.com':
                    print("5. Sending email...")
                    success = email_sender.send_report(
                        config.email_to,
                        generated_pdf,
                        f"AI科技播客每日摘要 - 演示版 ({datetime.now().strftime('%Y-%m-%d')})"
                    )

                    if success:
                        print("   [OK] Email sent successfully!")
                    else:
                        print("   [FAIL] Email sending failed")
                else:
                    print("5. Email not configured - skipping email step")
                    print(f"   You can find the report at: {os.path.abspath(generated_pdf)}")

                print("\n" + "=" * 50)
                print("[SUCCESS] Demo completed successfully!")
                print("This demo shows how the system works with sample data.")
                print("Configure YouTube API to get real subscription videos.")

                return True
            else:
                print("   [FAIL] PDF generation failed")
        else:
            print("ERROR: No summaries generated")

        return False

    except Exception as e:
        print(f"ERROR: Demo failed - {e}")
        return False

if __name__ == "__main__":
    demo_run()