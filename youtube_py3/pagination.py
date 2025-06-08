"""
YouTube.py3 - ページネーション機能モジュール

YouTube APIのページネーション処理を提供するモジュールです。
"""

from .exceptions import YouTubeAPIError


class PaginationMixin:
    """ページネーション機能を提供するミックスインクラス"""
    
    def get_channel_videos_paginated(self, channel_id, max_results=None, order="date", page_token=None):
        """チャンネル動画を取得（ページネーション対応）
        
        Args:
            channel_id (str): チャンネルID
            max_results (int): 最大取得件数（Noneの場合は50件）
            order (str): ソート順序（'date', 'relevance', 'rating', 'title', 'viewCount'）
            page_token (str): ページトークン（次のページ用）
        
        Returns:
            dict: 検索結果とページ情報
        """
        if max_results is None:
            max_results = 50
        
        max_results = min(max_results, 50)
        
        params = {
            'part': 'snippet',
            'channelId': channel_id,
            'type': 'video',
            'maxResults': max_results,
            'order': order
        }
        
        if page_token:
            params['pageToken'] = page_token
        
        request = self.youtube.search().list(**params)
        response = self._execute_request(request)
        
        return {
            'items': response.get('items', []),
            'nextPageToken': response.get('nextPageToken'),
            'totalResults': response.get('pageInfo', {}).get('totalResults', 0),
            'resultsPerPage': response.get('pageInfo', {}).get('resultsPerPage', 0)
        }

    def search_videos_paginated(self, query, max_results=None, order="relevance", page_token=None, channel_id=None, **filters):
        """動画検索（ページネーション対応）
        
        Args:
            query (str): 検索キーワード
            max_results (int): 最大取得件数（Noneの場合は50件）
            order (str): ソート順序
            page_token (str): ページトークン
            channel_id (str): 特定のチャンネル内で検索する場合のチャンネルID（オプション）
            **filters: 追加フィルター
        
        Returns:
            dict: 検索結果とページ情報
        """
        if max_results is None:
            max_results = 50
        
        max_results = min(max_results, 50)
        
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': max_results,
            'order': order,
            **filters
        }
        
        # チャンネルIDが指定された場合は追加
        if channel_id:
            params['channelId'] = channel_id
        
        if page_token:
            params['pageToken'] = page_token
        
        request = self.youtube.search().list(**params)
        response = self._execute_request(request)
        
        return {
            'items': response.get('items', []),
            'nextPageToken': response.get('nextPageToken'),
            'totalResults': response.get('pageInfo', {}).get('totalResults', 0),
            'resultsPerPage': response.get('pageInfo', {}).get('resultsPerPage', 0)
        }

    def get_playlist_videos_paginated(self, playlist_id, max_results=None, page_token=None):
        """プレイリスト動画を取得（ページネーション対応）
        
        Args:
            playlist_id (str): プレイリストID
            max_results (int): 最大取得件数
            page_token (str): ページトークン
        
        Returns:
            dict: 検索結果とページ情報
        """
        if max_results is None:
            max_results = 50
        
        max_results = min(max_results, 50)
        
        params = {
            'part': 'snippet',
            'playlistId': playlist_id,
            'maxResults': max_results
        }
        
        if page_token:
            params['pageToken'] = page_token
        
        request = self.youtube.playlistItems().list(**params)
        response = self._execute_request(request)
        
        return {
            'items': response.get('items', []),
            'nextPageToken': response.get('nextPageToken'),
            'totalResults': response.get('pageInfo', {}).get('totalResults', 0),
            'resultsPerPage': response.get('pageInfo', {}).get('resultsPerPage', 0)
        }

    def get_comments_paginated(self, video_id, max_results=None, order="time", page_token=None):
        """コメントを取得（ページネーション対応）
        
        Args:
            video_id (str): 動画ID
            max_results (int): 最大取得件数
            order (str): ソート順序（'time', 'relevance'）
            page_token (str): ページトークン
        
        Returns:
            dict: 検索結果とページ情報
        """
        if max_results is None:
            max_results = 100
        
        max_results = min(max_results, 100)
        
        params = {
            'part': 'snippet',
            'videoId': video_id,
            'maxResults': max_results,
            'order': order
        }
        
        if page_token:
            params['pageToken'] = page_token
        
        request = self.youtube.commentThreads().list(**params)
        
        try:
            response = self._execute_request(request)
        except YouTubeAPIError as e:
            if e.status_code == 403:
                raise YouTubeAPIError("この動画のコメントは無効化されています")
            raise
        
        return {
            'items': response.get('items', []),
            'nextPageToken': response.get('nextPageToken'),
            'totalResults': response.get('pageInfo', {}).get('totalResults', 0),
            'resultsPerPage': response.get('pageInfo', {}).get('resultsPerPage', 0)
        }

    def paginate_all_results(self, paginated_func, *args, max_total_results=None, **kwargs):
        """ページネーション対応関数で全件取得するヘルパー
        
        Args:
            paginated_func: ページネーション対応関数
            *args: 関数の引数
            max_total_results (int): 最大総取得件数
            **kwargs: 関数のキーワード引数
        
        Returns:
            list: 全ての結果
        """
        all_items = []
        next_page_token = None
        
        while True:
            # 残り取得可能件数を計算
            if max_total_results:
                remaining = max_total_results - len(all_items)
                if remaining <= 0:
                    break
                
                # 今回のリクエストで取得する件数（最大50件）
                current_max = min(50, remaining)
                kwargs['max_results'] = current_max
            
            # ページネーション関数を実行
            kwargs['page_token'] = next_page_token
            result = paginated_func(*args, **kwargs)
            
            # 結果を追加
            items = result.get('items', [])
            if not items:
                break
            
            all_items.extend(items)
            
            # 次のページトークンを取得
            next_page_token = result.get('nextPageToken')
            if not next_page_token:
                break
        return all_items