"""
Gemini-based summarizer that can directly process YouTube URLs
"""
import google.generativeai as genai
import re

class GeminiYoutubeSummarizer:
    def __init__(self, api_key, model_name="gemini-pro"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

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
        """Directly summarize YouTube video using Gemini's built-in capability"""

        prompt = f"""
        请分析这个YouTube视频并提供中文摘要：

        视频链接: {video_url}
        标题: {title}
        频道: {channel_name}

        请提供：
        1. 核心要点 (3-5个主要观点)
        2. 关键技术/概念
        3. 实用建议或结论
        4. 整体评价和推荐指数 (1-5星)

        请用简洁的中文回答，重点突出技术要点和实用价值。
        注意：这是一个科技/AI相关的播客或技术分享视频。
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error analyzing video {video_url}: {e}")
            return f"视频分析失败: {str(e)}"

    def process_video(self, video_info):
        """Process a single video using Gemini's YouTube capability"""
        video_id = video_info.get('id', {}).get('videoId')
        if not video_id:
            return None

        title = video_info.get('snippet', {}).get('title', '')
        channel_name = video_info.get('snippet', {}).get('channelTitle', '')
        video_url = f'https://www.youtube.com/watch?v={video_id}'

        print(f"Processing video with Gemini: {title}")

        # Let Gemini directly analyze the YouTube video
        summary = self.summarize_youtube_video(video_url, title, channel_name)

        return {
            'title': title,
            'channel': channel_name,
            'summary': summary,
            'video_id': video_id,
            'url': video_url,
            'content_type': 'gemini_direct'
        }