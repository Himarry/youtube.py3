from .base import YouTubeAPIClient
from typing import Iterator, Dict, Any, Optional

class Videos:
    def __init__(self, client: YouTubeAPIClient):
        self.client = client

    def get_video(self, video_id: str):
        params = {
            'id': video_id,
            'part': 'snippet,contentDetails,statistics',
        }
        return self.client._request('videos', params)

    def get_videos_paginated(self, video_ids: list, max_results: int = 50, page_token: Optional[str] = None) -> Iterator[Dict[str, Any]]:
        """
        ページネーション対応: 複数動画IDで動画情報をイテレータで返す
        page_tokenで次ページ取得も可能
        """
        fetched = 0
        next_token = page_token
        ids = video_ids[:]
        while ids and fetched < max_results:
            batch = ids[:50]
            ids = ids[50:]
            params = {
                'id': ','.join(batch),
                'part': 'snippet,contentDetails,statistics',
                'maxResults': min(max_results - fetched, 50),
            }
            if next_token:
                params['pageToken'] = next_token
            resp = self.client._request('videos', params)
            for item in resp.get('items', []):
                yield item
                fetched += 1
                if fetched >= max_results:
                    return
            next_token = resp.get('nextPageToken')
            if not next_token or fetched >= max_results:
                break
