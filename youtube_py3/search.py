"""
YouTube.py3 - 検索機能モジュール

YouTube APIの検索機能を提供するモジュールです。
"""

from .exceptions import YouTubeAPIError


class SearchMixin:
    """検索機能を提供するミックスインクラス"""
    
    def search_videos(self, query, max_results=50, channel_id=None, order="relevance", 
                     published_after=None, published_before=None, region_code=None):
        """動画検索機能（拡張版）
        
        Args:
            query (str): 検索キーワード
            max_results (int): 最大取得件数
            channel_id (str): 特定チャンネル内で検索する場合のチャンネルID
            order (str): ソート順序 ("relevance", "date", "rating", "viewCount", "title")
            published_after (str): この日時以降の動画のみ（RFC 3339形式）
            published_before (str): この日時以前の動画のみ（RFC 3339形式）
            region_code (str): 地域コード（ISO 3166-1 alpha-2）
            
        Returns:
            list: 検索結果の動画リスト
        """
        try:
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': min(max_results, 50),
                'order': order
            }
            
            # オプションパラメータを追加
            if channel_id:
                params['channelId'] = channel_id
            if published_after:
                params['publishedAfter'] = published_after
            if published_before:
                params['publishedBefore'] = published_before
            if region_code:
                params['regionCode'] = region_code
            
            response = self.service.search().list(**params).execute()
            
            # 統計情報も含めて動画情報を拡張
            video_ids = [item['id']['videoId'] for item in response.get('items', [])]
            if video_ids:
                # バッチで動画の詳細情報を取得
                videos_detail = self.service.videos().list(
                    part='statistics,contentDetails',
                    id=','.join(video_ids)
                ).execute()
                
                # 統計情報をマージ
                stats_dict = {item['id']: item for item in videos_detail.get('items', [])}
                
                for item in response.get('items', []):
                    video_id = item['id']['videoId']
                    if video_id in stats_dict:
                        item['statistics'] = stats_dict[video_id].get('statistics', {})
                        item['contentDetails'] = stats_dict[video_id].get('contentDetails', {})
            
            return response.get('items', [])
            
        except Exception as e:
            raise YouTubeAPIError(f"動画検索に失敗しました: {str(e)}")

    def search_channels(self, query, max_results=5, order="relevance"):
        """チャンネルを検索

        Args:
            query (str): 検索キーワード
            max_results (int): 取得する最大結果数
            order (str): ソート順序

        Returns:
            list: 検索結果のリスト
        """
        request = self.youtube.search().list(
            part="snippet",
            q=query,
            type="channel",
            maxResults=max_results,
            order=order,
        )
        response = self._execute_request(request)
        return response["items"]

    def search_playlists(self, query, max_results=5, order="relevance"):
        """プレイリストを検索

        Args:
            query (str): 検索キーワード
            max_results (int): 取得する最大結果数
            order (str): ソート順序

        Returns:
            list: 検索結果のリスト
        """
        request = self.youtube.search().list(
            part="snippet",
            q=query,
            type="playlist",
            maxResults=max_results,
            order=order,
        )
        response = self._execute_request(request)
        return response["items"]

    def search_and_get_details(self, query, max_results=10, include_stats=True):
        """検索して詳細情報も一緒に取得
        
        Args:
            query (str): 検索キーワード
            max_results (int): 最大結果数
            include_stats (bool): 統計情報を含めるか
        
        Returns:
            list: 詳細情報付きの検索結果
        """
        # まず検索を実行
        search_results = self.search_videos(query, max_results=max_results)
        
        # 動画IDを抽出
        video_ids = [item['id']['videoId'] for item in search_results]
        
        if not include_stats:
            return search_results
        
        # 統計情報を一括取得
        detailed_videos = self.bulk_get_video_info(video_ids)
        
        # 検索結果と統計情報をマージ
        enhanced_results = []
        for search_item, detail_item in zip(search_results, detailed_videos):
            enhanced_item = search_item.copy()
            enhanced_item['statistics'] = detail_item['statistics']
            enhanced_item['view_count'] = int(detail_item['statistics'].get('viewCount', 0))
            enhanced_item['like_count'] = int(detail_item['statistics'].get('likeCount', 0))
            enhanced_item['comment_count'] = int(detail_item['statistics'].get('commentCount', 0))
            enhanced_results.append(enhanced_item)
        
        return enhanced_results

    def quick_search(self, query, count=10, content_type="video"):
        """クイック検索（結果を簡潔に返す）
        
        Args:
            query (str): 検索キーワード
            count (int): 取得件数
            content_type (str): コンテンツタイプ（'video', 'channel', 'playlist', 'all'）
        
        Returns:
            list: 簡潔な検索結果
        """
        if content_type == "all":
            # 全タイプを検索
            videos = self.search_videos(query, max_results=count//3 + 1)
            channels = self.search_channels(query, max_results=count//3 + 1)
            playlists = self.search_playlists(query, max_results=count//3 + 1)
            
            results = []
            for item in videos + channels + playlists:
                results.append({
                    'id': item['id'].get('videoId') or item['id'].get('channelId') or item['id'].get('playlistId'),
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'][:100] + "..." if len(item['snippet']['description']) > 100 else item['snippet']['description'],
                    'type': item['id']['kind'].split('#')[1],
                    'thumbnail': item['snippet']['thumbnails']['default']['url']
                })
            return results[:count]
        else:
            # 指定タイプのみ検索
            if content_type == "video":
                items = self.search_videos(query, max_results=count)
            elif content_type == "channel":
                items = self.search_channels(query, max_results=count)
            elif content_type == "playlist":
                items = self.search_playlists(query, max_results=count)
            else:
                raise YouTubeAPIError(f"未対応のコンテンツタイプ: {content_type}")
            
            results = []
            for item in items:
                results.append({
                    'id': item['id'].get('videoId') or item['id'].get('channelId') or item['id'].get('playlistId'),
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'][:100] + "..." if len(item['snippet']['description']) > 100 else item['snippet']['description'],
                    'type': content_type,
                    'thumbnail': item['snippet']['thumbnails']['default']['url']
                })
            return results

    def search_channel_videos(self, channel_id, max_results=50, order="date", 
                             published_after=None, published_before=None):
        """特定チャンネルの動画を検索（拡張版）
        
        Args:
            channel_id (str): チャンネルID
            max_results (int): 最大取得件数
            order (str): ソート順序 ("date", "relevance", "rating", "viewCount", "title")
            published_after (str): この日時以降の動画のみ
            published_before (str): この日時以前の動画のみ
            
        Returns:
            list: チャンネルの動画リスト
        """
        return self.search_videos(
            query="",
            max_results=max_results,
            channel_id=channel_id,
            order=order,
            published_after=published_after,
            published_before=published_before
        )

    def search_videos_filtered(self, query="", max_results=50, channel_id=None, 
                              duration="any", upload_date="any", video_type="any",
                              order="relevance", definition="any", caption="any"):
        """フィルター付き動画検索
        
        Args:
            query (str): 検索キーワード
            max_results (int): 最大取得件数
            channel_id (str): 特定チャンネル内で検索
            duration (str): 再生時間フィルター ("any", "short", "medium", "long")
            upload_date (str): アップロード日フィルター ("any", "hour", "today", "week", "month", "year")
            video_type (str): 動画タイプ ("any", "episode", "movie")
            order (str): ソート順序
            definition (str): 画質 ("any", "high", "standard")
            caption (str): 字幕 ("any", "closedCaption")
            
        Returns:
            list: フィルター済み検索結果
        """
        try:
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': min(max_results, 50),
                'order': order
            }
            
            # フィルター適用
            if channel_id:
                params['channelId'] = channel_id
            if duration != "any":
                params['videoDuration'] = duration
            if upload_date != "any":
                params['publishedAfter'] = self._get_upload_date_filter(upload_date)
            if video_type != "any":
                params['videoType'] = video_type
            if definition != "any":
                params['videoDefinition'] = definition
            if caption != "any":
                params['videoCaption'] = caption
            
            response = self.service.search().list(**params).execute()
            
            # 統計情報を追加
            video_ids = [item['id']['videoId'] for item in response.get('items', [])]
            if video_ids:
                return self._enrich_videos_with_stats(response.get('items', []), video_ids)
            
            return response.get('items', [])
            
        except Exception as e:
            raise YouTubeAPIError(f"フィルター付き検索に失敗しました: {str(e)}")

    def get_trending_videos(self, region_code="JP", category_id=None, max_results=50):
        """トレンド動画を取得
        
        Args:
            region_code (str): 地域コード (例: "JP", "US", "GB")
            category_id (str): カテゴリID (オプション)
            max_results (int): 最大取得件数
            
        Returns:
            list: トレンド動画リスト
        """
        try:
            params = {
                'part': 'snippet,statistics,contentDetails',
                'chart': 'mostPopular',
                'regionCode': region_code,
                'maxResults': min(max_results, 50)
            }
            
            if category_id:
                params['videoCategoryId'] = category_id
            
            response = self.service.videos().list(**params).execute()
            return response.get('items', [])
            
        except Exception as e:
            raise YouTubeAPIError(f"トレンド動画取得に失敗しました: {str(e)}")

    def search_youtube_shorts(self, query="", max_results=50, order="relevance"):
        """YouTube Shortsのみを検索
        
        Args:
            query (str): 検索キーワード
            max_results (int): 最大取得件数
            order (str): ソート順序
            
        Returns:
            list: YouTube Shortsのリスト
        """
        # Shortsは60秒以下の縦動画として検索
        videos = self.search_videos_filtered(
            query=query,
            max_results=max_results * 2,  # フィルタリング後に減る可能性があるため多めに取得
            duration="short",
            order=order
        )
        
        # 追加フィルタ: アスペクト比や再生時間でShortsを特定
        shorts = []
        for video in videos:
            duration = video.get('contentDetails', {}).get('duration', '')
            if self._is_youtube_shorts(duration):
                shorts.append(video)
                if len(shorts) >= max_results:
                    break
        
        return shorts

    def _get_upload_date_filter(self, upload_date):
        """アップロード日フィルターを日時に変換"""
        from datetime import datetime, timedelta
        import pytz
        
        now = datetime.now(pytz.UTC)
        
        if upload_date == "hour":
            return (now - timedelta(hours=1)).isoformat()
        elif upload_date == "today":
            return (now - timedelta(days=1)).isoformat()
        elif upload_date == "week":
            return (now - timedelta(weeks=1)).isoformat()
        elif upload_date == "month":
            return (now - timedelta(days=30)).isoformat()
        elif upload_date == "year":
            return (now - timedelta(days=365)).isoformat()
        
        return None

    def _enrich_videos_with_stats(self, videos, video_ids):
        """動画に統計情報を追加"""
        try:
            stats_response = self.service.videos().list(
                part='statistics,contentDetails',
                id=','.join(video_ids)
            ).execute()
            
            stats_dict = {item['id']: item for item in stats_response.get('items', [])}
            
            for video in videos:
                video_id = video['id']['videoId']
                if video_id in stats_dict:
                    video['statistics'] = stats_dict[video_id].get('statistics', {})
                    video['contentDetails'] = stats_dict[video_id].get('contentDetails', {})
            
            return videos
            
        except Exception:
            return videos  # エラー時は統計情報なしで返す

    def _is_youtube_shorts(self, duration):
        """YouTube Shortsかどうかを判定"""
        if not duration:
            return False
        
        # ISO 8601形式の再生時間を秒に変換
        import re
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return False
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds <= 60  # 60秒以下はShorts