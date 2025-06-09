from .base import YouTubeAPIClient
from typing import Iterator, Dict, Any, Optional

class Playlists:
    def __init__(self, client: YouTubeAPIClient):
        self.client = client

    def get_playlist(self, playlist_id: str):
        params = {
            'id': playlist_id,
            'part': 'snippet,contentDetails',
        }
        return self.client._request('playlists', params)

    def get_playlists_paginated(self, channel_id: str, max_results: int = 50, page_token: Optional[str] = None) -> Iterator[Dict[str, Any]]:
        """
        ページネーション対応: チャンネルのプレイリスト一覧をイテレータで返す
        page_tokenで次ページ取得も可能
        """
        fetched = 0
        next_token = page_token
        while True:
            params = {
                'channelId': channel_id,
                'part': 'snippet,contentDetails',
                'maxResults': min(max_results - fetched, 50),
            }
            if next_token:
                params['pageToken'] = next_token
            resp = self.client._request('playlists', params)
            for item in resp.get('items', []):
                yield item
                fetched += 1
                if fetched >= max_results:
                    return
            next_token = resp.get('nextPageToken')
            if not next_token or fetched >= max_results:
                break
