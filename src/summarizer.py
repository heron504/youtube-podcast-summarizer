"""
Content summarization using OpenRouter API
"""
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import re
import json

class PodcastSummarizer:
    def __init__(self, api_key, model_name="anthropic/claude-3.5-sonnet", proxies=None):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.proxies = proxies

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

    def get_transcript(self, video_id):
        """Get transcript for a YouTube video"""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'zh'])
            text = ' '.join([item['text'] for item in transcript])
            return text
        except Exception as e:
            print(f"Error getting transcript for {video_id}: {e}")
            return None

    def summarize_content(self, text, title="", channel_name=""):
        """Summarize podcast content using OpenRouter API"""
        if not text:
            return None

        prompt = f"""
        Please provide a comprehensive summary of this podcast/video in Chinese:

        Title: {title}
        Channel: {channel_name}

        Content: {text[:8000]}  # Limit content to avoid token limits

        Please provide:
        1. 核心要点 (3-5个主要观点)
        2. 关键技术/概念
        3. 实用建议或结论
        4. 整体评价和推荐指数 (1-5星)

        请用简洁的中文回答，重点突出技术要点和实用价值。
        """

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

    def process_video(self, video_info):
        """Process a single video: get transcript and summarize"""
        video_id = video_info.get('id', {}).get('videoId')
        if not video_id:
            return None

        title = video_info.get('snippet', {}).get('title', '')
        channel_name = video_info.get('snippet', {}).get('channelTitle', '')

        transcript = self.get_transcript(video_id)
        if not transcript:
            return {
                'title': title,
                'channel': channel_name,
                'summary': '无法获取视频转录内容',
                'video_id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}'
            }

        summary = self.summarize_content(transcript, title, channel_name)

        return {
            'title': title,
            'channel': channel_name,
            'summary': summary,
            'video_id': video_id,
            'url': f'https://www.youtube.com/watch?v={video_id}'
        }