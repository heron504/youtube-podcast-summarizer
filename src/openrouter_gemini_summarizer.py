"""
OpenRouter Gemini 2.0 Pro summarizer for direct YouTube URL processing
"""
import requests
import re
import json

class OpenRouterGeminiSummarizer:
    def __init__(self, api_key, proxies=None):
        self.api_key = api_key
        self.model_name = "google/gemini-2.5-pro"  # Gemini 2.5 Pro on OpenRouter
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

    def summarize_youtube_video(self, video_url, title="", channel_name=""):
        """Use OpenRouter Gemini 2.0 Pro to directly analyze YouTube video"""

        prompt = f"""
请观看这个YouTube视频，制作一份详细完整的内容纪要：

视频链接: {video_url}
标题: {title}
频道: {channel_name}

要求：
1. 制作详细的内容纪要，不要只是要点总结
2. 完整记录视频中的重要信息、观点、论述过程
3. 包含具体的细节、数据、案例和引用
4. 保持视频内容的逻辑结构和论述顺序
5. 使用简体中文，可以使用Markdown格式来组织内容
6. 内容要充实详细，不要删减重要信息

请制作一份详尽的内容纪要，让读者通过纪要就能了解视频的完整内容：
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
            "max_tokens": 4000,
            "temperature": 0.7
        }

        try:
            print(f"Using OpenRouter Gemini 2.5 Pro to analyze: {video_url}")
            response = requests.post(self.base_url, headers=headers, json=data,
                                   proxies=self.proxies, timeout=60)
            response.raise_for_status()

            result = response.json()
            return result['choices'][0]['message']['content']

        except Exception as e:
            print(f"Error with OpenRouter Gemini: {e}")
            return f"视频分析失败: {str(e)}"

    def process_video(self, video_info):
        """Process a single video using OpenRouter Gemini 2.0 Pro"""
        video_id = video_info.get('id', {}).get('videoId')
        if not video_id:
            return None

        title = video_info.get('snippet', {}).get('title', '')
        channel_name = video_info.get('snippet', {}).get('channelTitle', '')
        video_url = f'https://www.youtube.com/watch?v={video_id}'

        print(f"Processing video with OpenRouter Gemini: {title}")

        # Let OpenRouter Gemini 2.0 Pro directly analyze the YouTube video
        summary = self.summarize_youtube_video(video_url, title, channel_name)

        return {
            'title': title,
            'channel': channel_name,
            'summary': summary,
            'video_id': video_id,
            'url': video_url,
            'content_type': 'openrouter_gemini_direct'
        }