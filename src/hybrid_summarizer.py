"""
Hybrid summarizer: Enhanced content fetching + Powerful AI analysis
"""
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import re
import json
import time

class HybridPodcastSummarizer:
    def __init__(self, api_key, model_name="anthropic/claude-3.5-sonnet", proxies=None, youtube_service=None):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.proxies = proxies
        self.youtube_service = youtube_service

    def get_video_details(self, video_id):
        """Get comprehensive video details from YouTube API"""
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
                    'view_count': item['statistics'].get('viewCount', 0),
                    'published_at': item['snippet']['publishedAt']
                }
        except Exception as e:
            print(f"Error getting video details: {e}")

        return {}

    def get_transcript_smart(self, video_id):
        """Smart transcript fetching with multiple strategies"""

        print(f"Attempting smart transcript fetch for {video_id}...")

        # Strategy 1: Try common languages in order of preference
        languages_priority = ['en', 'en-US', 'en-GB', 'en-CA', 'en-AU']

        for lang in languages_priority:
            try:
                print(f"  Trying language: {lang}")
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                text = ' '.join([item['text'] for item in transcript])

                if text and len(text) > 100:  # Meaningful content threshold
                    print(f"  SUCCESS: Got {len(text)} characters in {lang}")
                    return text, f'transcript_{lang}'

            except Exception as e:
                print(f"  Failed {lang}: {str(e)[:100]}...")
                continue

        # Strategy 2: Try any available transcript
        try:
            print("  Trying any available transcript...")
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # Prefer auto-generated as they're more complete
            for transcript in transcript_list:
                if transcript.is_generated:
                    try:
                        data = transcript.fetch()
                        text = ' '.join([item['text'] for item in data])
                        if len(text) > 100:
                            print(f"  SUCCESS: Auto-generated transcript, {len(text)} characters")
                            return text, 'auto_generated'
                    except:
                        continue

            # Then try manual transcripts
            for transcript in transcript_list:
                if not transcript.is_generated:
                    try:
                        data = transcript.fetch()
                        text = ' '.join([item['text'] for item in data])
                        if len(text) > 100:
                            print(f"  SUCCESS: Manual transcript, {len(text)} characters")
                            return text, 'manual'
                    except:
                        continue

        except Exception as e:
            print(f"  Failed to list transcripts: {str(e)[:100]}...")

        print("  No transcripts available")
        return None, None

    def get_content_with_fallbacks(self, video_id):
        """Get video content using multiple fallback strategies"""

        # Primary: Try transcript
        content, content_type = self.get_transcript_smart(video_id)
        if content:
            return content, content_type

        # Fallback: Use video description + details
        video_details = self.get_video_details(video_id)
        if video_details and video_details.get('description'):
            description = video_details['description']

            # Create enhanced description with metadata
            enhanced_content = f"""
Video Title: {video_details.get('title', '')}
Channel: {video_details.get('channel', '')}
Published: {video_details.get('published_at', '')}
Views: {video_details.get('view_count', '')}

Video Description:
{description}
            """.strip()

            if len(enhanced_content) > 200:
                print(f"  Using enhanced description: {len(enhanced_content)} characters")
                return enhanced_content, 'enhanced_description'

        return None, None

    def create_smart_prompt(self, content, title, channel_name, content_type):
        """Create intelligent prompt based on content type and quality"""

        content_instructions = {
            'transcript_en': "基于以下完整的英文视频转录内容",
            'auto_generated': "基于以下自动生成的视频字幕内容",
            'manual': "基于以下手动添加的视频字幕内容",
            'enhanced_description': "基于以下视频详细信息和描述"
        }

        instruction = content_instructions.get(content_type, "基于以下视频相关内容")

        return f"""
{instruction}，请为这个科技/AI播客视频提供专业的中文摘要分析：

标题: {title}
频道: {channel_name}
内容来源: {content_type}

内容:
{content[:10000]}  # 增加内容长度限制

请提供详细分析：
1. **核心观点** (3-5个主要论点，包含具体细节)
2. **关键技术/概念** (详细解释提到的技术术语)
3. **实用洞察** (可操作的建议和结论)
4. **行业影响** (对相关行业的潜在影响)
5. **推荐程度** (1-5星，附理由)

要求：
- 用简洁专业的中文表述
- 重点突出技术创新和商业价值
- 如果内容有限，请基于可用信息提供最佳分析
- 保持客观和准确性
        """

    def summarize_content(self, content, title, channel_name, content_type):
        """Generate summary using OpenRouter API"""
        if not content:
            return None

        prompt = self.create_smart_prompt(content, title, channel_name, content_type)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1500,  # 增加token限制获得更详细摘要
            "temperature": 0.7
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=data,
                                   proxies=self.proxies, timeout=45)
            response.raise_for_status()

            result = response.json()
            return result['choices'][0]['message']['content']

        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"摘要生成失败: {str(e)}"

    def process_video(self, video_info):
        """Process video with hybrid approach"""
        video_id = video_info.get('id', {}).get('videoId')
        if not video_id:
            return None

        title = video_info.get('snippet', {}).get('title', '')
        channel_name = video_info.get('snippet', {}).get('channelTitle', '')

        print(f"[HYBRID] Processing: {title}")

        # Get content using smart fallback strategies
        content, content_type = self.get_content_with_fallbacks(video_id)

        if not content:
            return {
                'title': title,
                'channel': channel_name,
                'summary': '无法获取视频内容（无字幕、无描述信息）',
                'video_id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'content_type': 'failed'
            }

        # Generate enhanced summary
        summary = self.summarize_content(content, title, channel_name, content_type)

        return {
            'title': title,
            'channel': channel_name,
            'summary': summary,
            'video_id': video_id,
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'content_type': content_type
        }