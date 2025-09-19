"""
Enhanced content summarization with multiple fallback strategies
"""
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import re
import json
import time
from googleapiclient.discovery import build

class EnhancedPodcastSummarizer:
    def __init__(self, api_key, model_name="anthropic/claude-3.5-sonnet", proxies=None, youtube_service=None):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.proxies = proxies
        self.youtube_service = youtube_service

    def extract_video_id(self, url):
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/v/([^&\n?#]+)',
            r'youtube\.com/watch\?.*v=([^&\n?#]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_video_details(self, video_id):
        """Get video details including title, description, duration"""
        if not self.youtube_service:
            return {}

        try:
            request = self.youtube_service.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()

            if response['items']:
                item = response['items'][0]
                return {
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel': item['snippet']['channelTitle'],
                    'duration': item['contentDetails']['duration'],
                    'view_count': item['statistics'].get('viewCount', 0)
                }
        except Exception as e:
            print(f"Error getting video details for {video_id}: {e}")

        return {}

    def get_transcript_with_fallback(self, video_id):
        """Get transcript with multiple fallback strategies"""

        # Strategy 1: Try multiple languages for auto-generated captions
        languages_to_try = ['en', 'en-US', 'en-GB', 'zh', 'zh-CN', 'zh-TW']

        for lang in languages_to_try:
            try:
                print(f"Trying transcript in language: {lang}")
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                text = ' '.join([item['text'] for item in transcript])
                if text and len(text) > 50:  # Ensure we got meaningful content
                    print(f"Successfully got transcript in {lang}: {len(text)} characters")
                    return text, 'transcript'
            except Exception as e:
                print(f"Failed to get transcript in {lang}: {e}")
                continue

        # Strategy 2: Try to get any available transcript
        try:
            print("Trying to get any available transcript...")
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # First try auto-generated
            for transcript in transcript_list:
                if transcript.is_generated:
                    try:
                        transcript_data = transcript.fetch()
                        text = ' '.join([item['text'] for item in transcript_data])
                        if text and len(text) > 50:
                            print(f"Got auto-generated transcript: {len(text)} characters")
                            return text, 'auto_transcript'
                    except Exception as e:
                        print(f"Failed to fetch auto transcript: {e}")
                        continue

            # Then try manual transcripts
            for transcript in transcript_list:
                if not transcript.is_generated:
                    try:
                        transcript_data = transcript.fetch()
                        text = ' '.join([item['text'] for item in transcript_data])
                        if text and len(text) > 50:
                            print(f"Got manual transcript: {len(text)} characters")
                            return text, 'manual_transcript'
                    except Exception as e:
                        print(f"Failed to fetch manual transcript: {e}")
                        continue

        except Exception as e:
            print(f"Failed to list transcripts for {video_id}: {e}")

        # Strategy 3: Use video description as fallback
        video_details = self.get_video_details(video_id)
        if video_details and video_details.get('description'):
            description = video_details['description']
            if len(description) > 100:  # Ensure meaningful description
                print(f"Using video description: {len(description)} characters")
                return description, 'description'

        print(f"No transcript or description available for {video_id}")
        return None, None

    def create_enhanced_prompt(self, content, title="", channel_name="", content_type='transcript'):
        """Create enhanced prompt based on content type"""

        content_type_prompts = {
            'transcript': "基于以下视频转录内容",
            'auto_transcript': "基于以下自动生成的视频字幕",
            'manual_transcript': "基于以下手动添加的视频字幕",
            'description': "基于以下视频描述信息"
        }

        content_instruction = content_type_prompts.get(content_type, "基于以下内容")

        return f"""
        请{content_instruction}，为这个科技/AI相关的视频提供中文摘要：

        标题: {title}
        频道: {channel_name}
        内容类型: {content_type}

        内容: {content[:8000]}

        请提供：
        1. 核心要点 (3-5个主要观点)
        2. 关键技术/概念
        3. 实用建议或结论
        4. 整体评价和推荐指数 (1-5星)

        注意：如果内容是视频描述而非完整转录，请基于可用信息提供合理的概述。
        请用简洁的中文回答，重点突出技术要点和实用价值。
        """

    def summarize_content(self, content, title="", channel_name="", content_type='transcript'):
        """Summarize content using OpenRouter API"""
        if not content:
            return None

        prompt = self.create_enhanced_prompt(content, title, channel_name, content_type)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=data,
                                   proxies=self.proxies, timeout=30)
            response.raise_for_status()

            result = response.json()
            return result['choices'][0]['message']['content']

        except Exception as e:
            print(f"Error summarizing content: {e}")
            return f"摘要生成失败: {str(e)}"

    def process_video(self, video_info, youtube_service=None):
        """Process a single video with enhanced fallback strategies"""
        video_id = video_info.get('id', {}).get('videoId')
        if not video_id:
            return None

        title = video_info.get('snippet', {}).get('title', '')
        channel_name = video_info.get('snippet', {}).get('channelTitle', '')

        print(f"Processing video: {title}")

        # Try to get content with fallback strategies
        content, content_type = self.get_transcript_with_fallback(video_id)

        if not content:
            return {
                'title': title,
                'channel': channel_name,
                'summary': '无法获取视频内容（无字幕且无描述信息）',
                'video_id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'content_type': 'none'
            }

        # Generate summary
        summary = self.summarize_content(content, title, channel_name, content_type)

        return {
            'title': title,
            'channel': channel_name,
            'summary': summary,
            'video_id': video_id,
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'content_type': content_type
        }