"""
Configuration management for the application
"""
import os
from dotenv import load_dotenv
import json

class ConfigManager:
    def __init__(self, config_dir='config'):
        self.config_dir = config_dir
        self.env_file = os.path.join(config_dir, '.env')
        self.settings_file = os.path.join(config_dir, 'settings.json')

        # Load environment variables
        load_dotenv(self.env_file)

        # Load settings
        self.settings = self.load_settings()

    def load_settings(self):
        """Load application settings"""
        default_settings = {
            'max_videos_per_channel': 3,
            'max_channels_to_process': 20,
            'days_back_to_fetch': 1,  # 获取最近几天的视频，默认1天
            'schedule_time': '08:00',
            'pdf_output_dir': 'reports',
            'log_level': 'INFO'
        }

        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # Merge with defaults
                    default_settings.update(settings)
            except Exception as e:
                print(f"Error loading settings: {e}")

        return default_settings

    def save_settings(self):
        """Save current settings to file"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            print(f"Settings saved to {self.settings_file}")
        except Exception as e:
            print(f"Error saving settings: {e}")

    def create_env_template(self):
        """Create environment template file"""
        template = """# YouTube API配置
YOUTUBE_API_KEY=your_youtube_api_key_here
YOUTUBE_CREDENTIALS_FILE=credentials.json

# Gemini API配置
GEMINI_API_KEY=your_gemini_api_key_here

# 邮箱配置
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
EMAIL_TO=recipient@gmail.com
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587

# 可选配置
DEBUG=False
"""

        env_path = os.path.join(self.config_dir, '.env.template')
        os.makedirs(self.config_dir, exist_ok=True)

        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(template)

        print(f"Environment template created at {env_path}")

    # YouTube API settings
    @property
    def youtube_api_key(self):
        return os.getenv('YOUTUBE_API_KEY')

    @property
    def youtube_credentials_file(self):
        return os.getenv('YOUTUBE_CREDENTIALS_FILE', 'credentials.json')

    # OpenRouter API settings
    @property
    def openrouter_api_key(self):
        return os.getenv('OPENROUTER_API_KEY')

    @property
    def openrouter_model(self):
        return os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')

    # Email settings
    @property
    def email_username(self):
        return os.getenv('EMAIL_USERNAME')

    @property
    def email_password(self):
        return os.getenv('EMAIL_PASSWORD')

    @property
    def email_to(self):
        return os.getenv('EMAIL_TO')

    @property
    def email_smtp_server(self):
        return os.getenv('EMAIL_SMTP_SERVER', 'smtp.qq.com')

    @property
    def email_smtp_port(self):
        return int(os.getenv('EMAIL_SMTP_PORT', 587))

    # Application settings
    @property
    def max_videos_per_channel(self):
        return self.settings.get('max_videos_per_channel', 3)

    @property
    def max_channels_to_process(self):
        return self.settings.get('max_channels_to_process', 20)

    @property
    def days_back_to_fetch(self):
        return self.settings.get('days_back_to_fetch', 1)

    @property
    def schedule_time(self):
        return self.settings.get('schedule_time', '08:00')

    @property
    def pdf_output_dir(self):
        return self.settings.get('pdf_output_dir', 'reports')

    @property
    def is_debug(self):
        return os.getenv('DEBUG', 'False').lower() == 'true'

    # Proxy settings
    @property
    def http_proxy(self):
        return os.getenv('HTTP_PROXY')

    @property
    def https_proxy(self):
        return os.getenv('HTTPS_PROXY')

    def get_proxy_dict(self):
        """Get proxy configuration as dict"""
        proxies = {}
        if self.http_proxy:
            proxies['http'] = self.http_proxy
        if self.https_proxy:
            proxies['https'] = self.https_proxy
        return proxies if proxies else None

    def validate_config(self):
        """Validate configuration completeness"""
        required_vars = [
            'OPENROUTER_API_KEY',
            'EMAIL_USERNAME',
            'EMAIL_PASSWORD',
            'EMAIL_TO'
        ]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            print("Missing required environment variables:")
            for var in missing_vars:
                print(f"  - {var}")
            return False

        return True