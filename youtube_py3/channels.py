from .base import YouTubeAPIClient
from typing import Iterator, Dict, Any, Optional

class Channels:
    def __init__(self, client: YouTubeAPIClient):
        self.client = client

    def get_channel(self, channel_id: str):
        params = {
            'id': channel_id,
            'part': 'snippet,statistics',
        }
        return self.client._request('channels', params)

    def get_channel_paginated(self, for_username: Optional[str] = None, max_results: int = 50, page_token: Optional[str] = None) -> Iterator[Dict[str, Any]]:
        """
        ページネーション対応: チャンネル情報をイテレータで返す
        for_username指定でユーザー名検索も可能
        page_tokenで次ページ取得も可能
        """
        fetched = 0
        next_token = page_token
        while True:
            params = {
                'part': 'snippet,statistics',
                'maxResults': min(max_results - fetched, 50),
            }
            if for_username:
                params['forUsername'] = for_username
            if next_token:
                params['pageToken'] = next_token
            resp = self.client._request('channels', params)
            for item in resp.get('items', []):
                yield item
                fetched += 1
                if fetched >= max_results:
                    return
            next_token = resp.get('nextPageToken')
            if not next_token or fetched >= max_results:
                break

    def search_channels(self, query: str, max_results: int = 5):
        """
        チャンネル名で検索し、チャンネル情報リストを返す
        """
        params = {
            'q': query,
            'part': 'snippet',
            'type': 'channel',
            'maxResults': max_results,
        }
        return self.client._request('search', params)

    def get_latest_video_id(self, channel_id: str) -> Optional[str]:
        """
        指定チャンネルの最新動画IDを取得
        """
        params = {
            'part': 'snippet',
            'channelId': channel_id,
            'order': 'date',
            'type': 'video',
            'maxResults': 1,
        }
        resp = self.client._request('search', params)
        items = resp.get('items', [])
        if items:
            return items[0]['id']['videoId']
        return None
