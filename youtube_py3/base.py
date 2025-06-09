import requests
from .exceptions import (
    YouTubeAPIError, YouTubeAuthError, YouTubeQuotaExceededError, YouTubeNotFoundError,
    YouTubeInvalidRequestError, YouTubeRateLimitError,
    YouTubeCommentError, YouTubeVideoError, YouTubeChannelError, YouTubePlaylistError, YouTubeSearchError
)

class YouTubeAPIClient:
    BASE_URL = "https://www.googleapis.com/youtube/v3/"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _request(self, endpoint: str, params: dict):
        params['key'] = self.api_key
        url = self.BASE_URL + endpoint
        response = requests.get(url, params=params)
        if response.status_code == 401:
            raise YouTubeAuthError(f"Auth Error: {response.text}")
        if response.status_code == 403:
            if 'quota' in response.text.lower():
                raise YouTubeQuotaExceededError(f"Quota Exceeded: {response.text}")
            if 'rateLimit' in response.text or 'rate limit' in response.text:
                raise YouTubeRateLimitError(f"Rate Limit: {response.text}")
            raise YouTubeAPIError(f"Forbidden: {response.text}")
        if response.status_code == 404:
            raise YouTubeNotFoundError(f"Not Found: {response.text}")
        if response.status_code == 400:
            raise YouTubeInvalidRequestError(f"Invalid Request: {response.text}")
        if response.status_code != 200:
            raise YouTubeAPIError(f"API Error: {response.status_code} {response.text}")
        data = response.json()
        # 機能別例外の例示（APIレスポンスのerror.reasonで判定）
        if 'error' in data:
            reason = data['error'].get('errors', [{}])[0].get('reason', '')
            if reason == 'commentsDisabled':
                raise YouTubeCommentError(f"Comments Disabled: {data['error']}")
            if reason == 'videoNotFound':
                raise YouTubeVideoError(f"Video Not Found: {data['error']}")
            if reason == 'channelNotFound':
                raise YouTubeChannelError(f"Channel Not Found: {data['error']}")
            if reason == 'playlistNotFound':
                raise YouTubePlaylistError(f"Playlist Not Found: {data['error']}")
            if reason == 'searchNotAllowed':
                raise YouTubeSearchError(f"Search Not Allowed: {data['error']}")
            raise YouTubeAPIError(f"API Error: {data['error']}")
        return data
