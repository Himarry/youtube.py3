from .base import YouTubeAPIClient
from typing import Iterator, Dict, Any, Optional

class Search:
    def __init__(self, client: YouTubeAPIClient):
        self.client = client

    def search_videos(self, query: str, max_results: int = 5):
        params = {
            'q': query,
            'part': 'snippet',
            'type': 'video',
            'maxResults': max_results,
        }
        return self.client._request('search', params)

    def search_videos_paginated(self, query: str, max_results: int = 50, page_token: Optional[str] = None) -> Iterator[Dict[str, Any]]:
        """
        ページネーション対応: 検索結果をイテレータで返す
        page_tokenで次ページ取得も可能
        """
        fetched = 0
        next_token = page_token
        while True:
            params = {
                'q': query,
                'part': 'snippet',
                'type': 'video',
                'maxResults': min(max_results - fetched, 50),
            }
            if next_token:
                params['pageToken'] = next_token
            resp = self.client._request('search', params)
            for item in resp.get('items', []):
                yield item
                fetched += 1
                if fetched >= max_results:
                    return
            next_token = resp.get('nextPageToken')
            if not next_token or fetched >= max_results:
                break
