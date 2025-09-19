"""
Parallel OpenRouter Gemini Summarizer with concurrent API calls
"""
import requests
import json
import concurrent.futures
import time
from typing import List, Dict, Any
import logging

class ParallelOpenRouterGeminiSummarizer:
    def __init__(self, api_key: str, proxies: Dict = None, max_workers: int = 5):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model_name = "google/gemini-2.5-pro"
        self.proxies = proxies
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)

    def _make_api_call(self, video_info: Dict) -> Dict:
        """Make a single API call for one video"""
        video_id = video_info.get('id', {}).get('videoId', '')
        title = video_info.get('snippet', {}).get('title', 'Unknown')
        channel = video_info.get('snippet', {}).get('channelTitle', 'Unknown')

        self.logger.info(f"Processing video: {title}")

        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # 详细摘要提示词 - 确保有足够内容
        prompt = f"""请详细观看这个YouTube视频并用中文写一个完整摘要：{video_url}

要求：
1. 写2段话的摘要，每段150-250字，总共300-500字
2. 第一段详细概括视频的主题、背景和核心观点
3. 第二段深入阐述重要细节、具体数据、实例或结论
4. 必须涵盖视频的主要论点和关键信息
5. 用简体中文写作，保持信息量丰富
6. 确保内容完整，不要过分简化

请直接输出2个详细段落，不需要标题。"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,  # 调整到2000确保获得足够详细的内容
            "temperature": 0.1
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                proxies=self.proxies,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()

            summary_content = result['choices'][0]['message']['content']

            return {
                'title': title,
                'channel': channel,
                'summary': summary_content,
                'video_id': video_id,
                'url': video_url,
                'content_type': 'openrouter_gemini_parallel',
                'success': True
            }

        except Exception as e:
            self.logger.error(f"Error processing video {title}: {e}")
            return {
                'title': title,
                'channel': channel,
                'summary': f"处理失败: {str(e)}",
                'video_id': video_id,
                'url': video_url,
                'content_type': 'openrouter_gemini_parallel',
                'success': False
            }

    def process_videos_parallel(self, videos: List[Dict]) -> List[Dict]:
        """Process multiple videos in parallel"""
        self.logger.info(f"开始并行处理 {len(videos)} 个视频，使用 {self.max_workers} 个并发线程")

        start_time = time.time()
        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_video = {
                executor.submit(self._make_api_call, video): video
                for video in videos
            }

            # 收集结果
            for future in concurrent.futures.as_completed(future_to_video):
                try:
                    result = future.result()
                    if result['success']:
                        results.append(result)
                        self.logger.info(f"✓ 完成: {result['title']} ({len(result['summary'])} 字符)")
                    else:
                        self.logger.error(f"✗ 失败: {result['title']}")
                except Exception as e:
                    video = future_to_video[future]
                    self.logger.error(f"线程异常: {video.get('snippet', {}).get('title', 'Unknown')}: {e}")

        end_time = time.time()
        self.logger.info(f"并行处理完成! 总耗时: {end_time - start_time:.1f}秒, 成功: {len(results)}/{len(videos)}")

        return results

    def process_video(self, video_info: Dict) -> Dict:
        """Single video processing (for backward compatibility)"""
        return self._make_api_call(video_info)