"""
YouTube.py3 - 動画関連機能

動画のアップロード、更新、削除、評価、サムネイル設定、字幕管理などの機能を提供します。
"""

from .exceptions import YouTubeAPIError
from googleapiclient.errors import HttpError


class VideoMixin:
    """動画関連の機能を提供するMixin"""

    def get_video_captions(self, video_id):
        """動画の字幕一覧を取得

        Args:
            video_id (str): YouTube動画のID

        Returns:
            list: 字幕情報のリスト
        """
        try:
            request = self.youtube.captions().list(part="snippet", videoId=video_id)
            response = request.execute()
            return response["items"]
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def download_caption(self, caption_id, format="srt"):
        """字幕をダウンロード

        Args:
            caption_id (str): 字幕ID
            format (str): ダウンロード形式 ('srt', 'vtt', 'ttml')

        Returns:
            str: 字幕テキスト
        """
        try:
            request = self.youtube.captions().download(id=caption_id, tfmt=format)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def upload_caption(self, video_id, language, name, caption_file):
        """字幕をアップロード

        Args:
            video_id (str): YouTube動画のID
            language (str): 言語コード（例: 'ja', 'en'）
            name (str): 字幕名
            caption_file: 字幕ファイル

        Returns:
            dict: アップロード結果
        """
        try:
            body = {
                "snippet": {"videoId": video_id, "language": language, "name": name}
            }

            request = self.youtube.captions().insert(
                part="snippet", body=body, media_body=caption_file
            )
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def update_caption(self, caption_id, name=None, caption_file=None):
        """字幕を更新

        Args:
            caption_id (str): 字幕ID
            name (str): 新しい字幕名（オプション）
            caption_file: 新しい字幕ファイル（オプション）

        Returns:
            dict: 更新結果
        """
        try:
            # まず現在の字幕情報を取得
            current_caption = (
                self.youtube.captions().list(part="snippet", id=caption_id).execute()
            )

            if not current_caption["items"]:
                raise YouTubeAPIError(f"字幕が見つかりません: {caption_id}")

            body = current_caption["items"][0]
            if name:
                body["snippet"]["name"] = name

            params = {"part": "snippet", "body": body}

            if caption_file:
                params["media_body"] = caption_file

            request = self.youtube.captions().update(**params)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def delete_caption(self, caption_id):
        """字幕を削除

        Args:
            caption_id (str): 字幕ID

        Returns:
            bool: 削除成功フラグ
        """
        try:
            request = self.youtube.captions().delete(id=caption_id)
            request.execute()
            return True
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def set_video_thumbnail(self, video_id, image_file):
        """動画のサムネイルを設定

        Args:
            video_id (str): 動画ID
            image_file: サムネイル画像ファイル

        Returns:
            dict: 設定結果
        """
        try:
            request = self.youtube.thumbnails().set(
                videoId=video_id, media_body=image_file
            )
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def upload_video(
        self,
        title,
        description,
        tags=None,
        category_id="22",
        privacy_status="private",
        video_file=None,
    ):
        """動画をアップロード

        Args:
            title (str): 動画タイトル
            description (str): 動画説明
            tags (list): タグのリスト
            category_id (str): カテゴリID
            privacy_status (str): プライバシー設定
            video_file: 動画ファイル

        Returns:
            dict: アップロード結果
        """
        try:
            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "categoryId": category_id,
                },
                "status": {"privacyStatus": privacy_status},
            }

            if tags:
                body["snippet"]["tags"] = tags

            params = {"part": "snippet,status", "body": body}

            if video_file:
                params["media_body"] = video_file

            request = self.youtube.videos().insert(**params)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def update_video(
        self, video_id, title=None, description=None, tags=None, category_id=None
    ):
        """動画情報を更新

        Args:
            video_id (str): 動画ID
            title (str): 新しいタイトル（オプション）
            description (str): 新しい説明（オプション）
            tags (list): 新しいタグ（オプション）
            category_id (str): 新しいカテゴリID（オプション）

        Returns:
            dict: 更新結果
        """
        try:
            # 現在の動画情報を取得
            current_video = self.get_video_info(video_id)

            body = {"id": video_id, "snippet": current_video["snippet"]}

            if title:
                body["snippet"]["title"] = title
            if description is not None:
                body["snippet"]["description"] = description
            if tags is not None:
                body["snippet"]["tags"] = tags
            if category_id:
                body["snippet"]["categoryId"] = category_id

            request = self.youtube.videos().update(part="snippet", body=body)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def rate_video(self, video_id, rating):
        """動画を評価

        Args:
            video_id (str): 動画ID
            rating (str): 評価 ('like', 'dislike', 'none')

        Returns:
            bool: 評価成功フラグ
        """
        try:
            request = self.youtube.videos().rate(id=video_id, rating=rating)
            request.execute()
            return True
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def get_video_rating(self, video_id):
        """動画の評価を取得

        Args:
            video_id (str): 動画ID

        Returns:
            dict: 評価情報
        """
        try:
            request = self.youtube.videos().getRating(id=video_id)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def report_video_abuse(self, video_id, reason_id, comments=""):
        """動画を報告

        Args:
            video_id (str): 動画ID
            reason_id (str): 報告理由ID
            comments (str): 追加コメント

        Returns:
            bool: 報告成功フラグ
        """
        try:
            body = {"videoId": video_id, "reasonId": reason_id, "comments": comments}

            request = self.youtube.videos().reportAbuse(body=body)
            request.execute()
            return True
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def delete_video(self, video_id):
        """動画を削除

        Args:
            video_id (str): 動画ID

        Returns:
            bool: 削除成功フラグ
        """
        try:
            request = self.youtube.videos().delete(id=video_id)
            request.execute()
            return True
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def get_video_info(self, video_id, include_statistics=True, include_content_details=True):
        """動画の詳細情報を取得
        
        Args:
            video_id (str): 動画ID
            include_statistics (bool): 統計情報を含めるか
            include_content_details (bool): コンテンツ詳細を含めるか
            
        Returns:
            dict: 動画の詳細情報
            {
                'id': str,
                'snippet': {...},
                'statistics': {
                    'viewCount': str,
                    'likeCount': str,
                    'commentCount': str,
                    'favoriteCount': str
                },
                'contentDetails': {
                    'duration': str,
                    'dimension': str,
                    'definition': str,
                    'caption': str
                }
            }
        """
        try:
            parts = ['snippet']
            if include_statistics:
                parts.append('statistics')
            if include_content_details:
                parts.append('contentDetails')
            
            response = self.service.videos().list(
                part=','.join(parts),
                id=video_id
            ).execute()
            
            if not response.get('items'):
                raise YouTubeAPIError(f"動画ID {video_id} が見つかりません")
            
            video_info = response['items'][0]
            
            # 統計情報の数値変換と追加処理
            if 'statistics' in video_info:
                stats = video_info['statistics']
                # 文字列を整数に変換（エラーハンドリング付き）
                for key in ['viewCount', 'likeCount', 'commentCount', 'favoriteCount']:
                    try:
                        if key in stats:
                            stats[f'{key}_int'] = int(stats[key])
                        else:
                            stats[key] = '0'
                            stats[f'{key}_int'] = 0
                    except (ValueError, TypeError):
                        stats[f'{key}_int'] = 0
                
                # 追加統計情報
                stats['engagement_ratio'] = self._calculate_engagement_ratio(stats)
            
            return video_info
            
        except Exception as e:
            raise YouTubeAPIError(f"動画情報の取得に失敗しました: {str(e)}")

    def _calculate_engagement_ratio(self, stats):
        """エンゲージメント率を計算
        
        Args:
            stats (dict): 統計情報
            
        Returns:
            float: エンゲージメント率
        """
        try:
            view_count = stats.get('viewCount_int', 0)
            like_count = stats.get('likeCount_int', 0)
            comment_count = stats.get('commentCount_int', 0)
            
            if view_count == 0:
                return 0.0
            
            engagement = (like_count + comment_count) / view_count
            return round(engagement * 100, 2)  # パーセンテージ
            
        except (TypeError, ZeroDivisionError):
            return 0.0

    def get_multiple_video_info(self, video_ids, include_statistics=True):
        """複数の動画情報を一括取得
        
        Args:
            video_ids (list): 動画IDのリスト
            include_statistics (bool): 統計情報を含めるか
            
        Returns:
            list: 動画情報のリスト
        """
        try:
            # YouTube APIは一度に50件まで処理可能
            batch_size = 50
            all_videos = []
            
            for i in range(0, len(video_ids), batch_size):
                batch_ids = video_ids[i:i + batch_size]
                
                parts = ['snippet']
                if include_statistics:
                    parts.append('statistics')
                    parts.append('contentDetails')
                
                response = self.service.videos().list(
                    part=','.join(parts),
                    id=','.join(batch_ids)
                ).execute()
                
                all_videos.extend(response.get('items', []))
            
            return all_videos
            
        except Exception as e:
            raise YouTubeAPIError(f"複数動画情報の取得に失敗しました: {str(e)}")