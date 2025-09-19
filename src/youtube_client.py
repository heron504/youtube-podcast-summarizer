"""
YouTube API client for fetching subscription videos
"""
import os
import httplib2
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

class YouTubeClient:
    SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

    def __init__(self, credentials_file=None, proxy_info=None):
        self.service = None
        self.credentials_file = credentials_file or 'credentials.json'
        self.proxy_info = proxy_info

    def authenticate(self):
        """Authenticate with YouTube API"""
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        # Build service - proxy is handled by system environment
        self.service = build('youtube', 'v3', credentials=creds)

    def get_subscriptions(self, max_results=50):
        """Get user's subscriptions"""
        if not self.service:
            raise Exception("Not authenticated. Call authenticate() first.")

        request = self.service.subscriptions().list(
            part="snippet",
            mine=True,
            maxResults=max_results
        )
        return request.execute()

    def get_channel_latest_videos(self, channel_id, max_results=5, days_back=1):
        """Get latest videos from a specific channel within the last N days"""
        if not self.service:
            raise Exception("Not authenticated. Call authenticate() first.")

        # Calculate the published after timestamp (N days ago)
        published_after = datetime.now() - timedelta(days=days_back)
        published_after_iso = published_after.isoformat() + 'Z'

        request = self.service.search().list(
            part="snippet",
            channelId=channel_id,
            type="video",
            order="date",
            maxResults=max_results,
            publishedAfter=published_after_iso
        )
        return request.execute()