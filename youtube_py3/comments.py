from .base import YouTubeAPIClient
from typing import List, Dict, Any, Optional, Iterator

class Comments:
    def __init__(self, client: YouTubeAPIClient):
        self.client = client

    def get_viewer_comments(self, video_id: str, channel_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        指定動画のコメントから、
        ・チャンネル運営者のコメントを除外
        ・トップレベルのみ
        ・返信がないコメントのみ
        を取得
        """
        comments = []
        page_token = None
        while True:
            params = {
                'part': 'snippet',
                'videoId': video_id,
                'maxResults': min(max_results, 100),
                'textFormat': 'plainText',
                'order': 'relevance',
            }
            if page_token:
                params['pageToken'] = page_token
            resp = self.client._request('commentThreads', params)
            for item in resp.get('items', []):
                snippet = item['snippet']['topLevelComment']['snippet']
                # 運営者（動画投稿者）のコメントを除外
                if snippet.get('authorChannelId', {}).get('value') == channel_id:
                    continue
                # 返信がないコメントのみ
                if item['snippet'].get('totalReplyCount', 0) > 0:
                    continue
                comments.append(item)
                if len(comments) >= max_results:
                    return comments
            page_token = resp.get('nextPageToken')
            if not page_token:
                break
        return comments

    def get_viewer_comments_paginated(self, video_id: str, channel_id: str, max_results: int = 100, page_token: Optional[str] = None) -> Iterator[Dict[str, Any]]:
        """
        ページネーション対応: 指定動画の視聴者コメント（運営者除外・トップレベル・返信なし）をイテレータで返す
        page_tokenで次ページ取得も可能
        """
        fetched = 0
        next_token = page_token
        while True:
            params = {
                'part': 'snippet',
                'videoId': video_id,
                'maxResults': min(max_results - fetched, 100),
                'textFormat': 'plainText',
                'order': 'relevance',
            }
            if next_token:
                params['pageToken'] = next_token
            resp = self.client._request('commentThreads', params)
            for item in resp.get('items', []):
                snippet = item['snippet']['topLevelComment']['snippet']
                if snippet.get('authorChannelId', {}).get('value') == channel_id:
                    continue
                if item['snippet'].get('totalReplyCount', 0) > 0:
                    continue
                yield item
                fetched += 1
                if fetched >= max_results:
                    return
            next_token = resp.get('nextPageToken')
            if not next_token or fetched >= max_results:
                break
