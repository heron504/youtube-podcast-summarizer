"""
Main application for YouTube Podcast Summarizer
"""
import os
import sys
import logging
from datetime import datetime
import schedule
import time
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_manager import ConfigManager
from youtube_client import YouTubeClient
from fixed_summarizer import FixedSummarizer
from fixed_pdf_generator import FixedPDFGenerator
from email_sender import EmailSender

class YouTubePodcastSummarizer:
    def __init__(self):
        self.config = ConfigManager()
        self.youtube_client = None
        self.summarizer = None
        self.report_generator = None
        self.email_sender = None

        # Setup logging
        self.setup_logging()

        # Initialize components
        self.initialize_components()

    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"podcast_summarizer_{datetime.now().strftime('%Y%m%d')}.log"

        logging.basicConfig(
            level=logging.INFO if not self.config.is_debug else logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def initialize_components(self):
        """Initialize all components"""
        try:
            # Set proxy environment variables for Google APIs
            if self.config.http_proxy:
                os.environ['HTTP_PROXY'] = self.config.http_proxy
                os.environ['HTTPS_PROXY'] = self.config.https_proxy or self.config.http_proxy
                self.logger.info(f"Proxy configured: {self.config.http_proxy}")

            # Validate configuration
            if not self.config.validate_config():
                self.logger.error("Configuration validation failed")
                return False

            # Initialize YouTube client (optional)
            if self.config.youtube_api_key:
                self.youtube_client = YouTubeClient(self.config.youtube_credentials_file)
                self.logger.info("YouTube client initialized")
            else:
                self.youtube_client = None
                self.logger.info("YouTube API not configured - will use alternative methods")

            # Initialize fixed summarizer with proper content generation
            if self.config.openrouter_api_key:
                proxies = self.config.get_proxy_dict()
                self.summarizer = FixedSummarizer(
                    self.config.openrouter_api_key,
                    proxies=proxies,
                    max_workers=5
                )
            else:
                self.logger.error("OpenRouter API key not found")
                return False

            # Initialize fixed PDF generator
            self.report_generator = FixedPDFGenerator()

            # Initialize email sender
            self.email_sender = EmailSender(
                self.config.email_smtp_server,
                self.config.email_smtp_port,
                self.config.email_username,
                self.config.email_password
            )

            self.logger.info("All components initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            return False

    def process_daily_summaries(self):
        """Main processing function"""
        try:
            self.logger.info("Starting daily summary processing...")

            # Authenticate with YouTube
            self.logger.info("Authenticating with YouTube API...")
            self.youtube_client.authenticate()

            # Get subscriptions
            self.logger.info("Fetching subscriptions...")
            subscriptions = self.youtube_client.get_subscriptions(
                max_results=self.config.max_channels_to_process
            )

            if not subscriptions.get('items'):
                self.logger.warning("No subscriptions found")
                return

            # 收集所有需要处理的视频
            all_videos = []
            processed_channels = 0

            for subscription in subscriptions['items']:
                try:
                    channel_id = subscription['snippet']['resourceId']['channelId']
                    channel_title = subscription['snippet']['title']

                    self.logger.info(f"Fetching videos from channel: {channel_title}")

                    # Get latest videos from this channel (within specified days)
                    videos = self.youtube_client.get_channel_latest_videos(
                        channel_id,
                        max_results=self.config.max_videos_per_channel,
                        days_back=self.config.days_back_to_fetch
                    )

                    for video in videos.get('items', []):
                        all_videos.append(video)

                    processed_channels += 1

                except Exception as e:
                    self.logger.error(f"Error processing channel {channel_title}: {e}")
                    continue

            # 并行处理所有视频
            if all_videos:
                self.logger.info(f"开始并行处理 {len(all_videos)} 个视频...")
                summaries = self.summarizer.process_videos_parallel(all_videos)
            else:
                summaries = []

            if summaries:
                self.logger.info(f"Generated {len(summaries)} summaries from {processed_channels} channels")

                # Generate PDF report
                output_dir = Path(self.config.pdf_output_dir)
                output_dir.mkdir(exist_ok=True)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pdf_path = output_dir / f"podcast_summary_{timestamp}.pdf"

                self.logger.info("Generating PDF report...")
                generated_pdf = self.report_generator.generate_report(summaries, str(pdf_path))

                if generated_pdf:
                    # Send email
                    self.logger.info("Sending email...")
                    success = self.email_sender.send_report(
                        self.config.email_to,
                        generated_pdf
                    )

                    if success:
                        self.logger.info("Daily summary completed successfully!")
                    else:
                        self.logger.error("Failed to send email")
                else:
                    self.logger.error("Failed to generate PDF report")
            else:
                self.logger.warning("No summaries generated")

        except Exception as e:
            self.logger.error(f"Error in daily processing: {e}")

    def setup_scheduler(self):
        """Setup daily scheduler"""
        schedule.every().day.at(self.config.schedule_time).do(self.process_daily_summaries)
        self.logger.info(f"Scheduler setup: will run daily at {self.config.schedule_time}")

    def run_scheduler(self):
        """Run the scheduler continuously"""
        self.logger.info("Starting scheduler...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def run_once(self):
        """Run processing once (for testing)"""
        self.process_daily_summaries()

def main():
    app = YouTubePodcastSummarizer()

    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Run once for testing
        app.run_once()
    else:
        # Setup and run scheduler
        app.setup_scheduler()
        app.run_scheduler()

if __name__ == "__main__":
    main()