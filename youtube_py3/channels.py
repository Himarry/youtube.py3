"""
YouTube.py3 - チャンネル関連機能

チャンネル情報の取得、更新、バナー管理、セクション管理などの機能を提供します。
"""

from .exceptions import YouTubeAPIError
from googleapiclient.errors import HttpError


class ChannelMixin:
    """チャンネル関連の機能を提供するMixin"""

    def get_channel_videos(self, channel_id, max_results=50, order="date"):
        """チャンネルの動画を取得

        Args:
            channel_id (str): チャンネルID
            max_results (int): 取得する最大動画数
            order (str): ソート順序

        Returns:
            list: 動画のリスト
        """
        videos = []
        next_page_token = None

        while len(videos) < max_results:
            request = self.youtube.search().list(
                part="snippet",
                channelId=channel_id,
                type="video",
                maxResults=min(50, max_results - len(videos)),
                order=order,
                pageToken=next_page_token,
            )
            response = self._execute_request(request)

            videos.extend(response["items"])

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return videos[:max_results]

    def upload_channel_banner(self, image_file):
        """チャンネルバナーをアップロード

        Args:
            image_file: 画像ファイル

        Returns:
            dict: アップロード結果（URLを含む）
        """
        try:
            request = self.youtube.channelBanners().insert(media_body=image_file)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def update_channel(self, channel_id, title=None, description=None, keywords=None):
        """チャンネル情報を更新

        Args:
            channel_id (str): チャンネルID
            title (str): 新しいタイトル（オプション）
            description (str): 新しい説明（オプション）
            keywords (str): 新しいキーワード（オプション）

        Returns:
            dict: 更新結果
        """
        try:
            # 現在のチャンネル情報を取得
            current_channel = self.get_channel_info(channel_id)

            body = {"id": channel_id, "snippet": current_channel["snippet"]}

            if title:
                body["snippet"]["title"] = title
            if description:
                body["snippet"]["description"] = description
            if keywords:
                body["snippet"]["keywords"] = keywords

            request = self.youtube.channels().update(part="snippet", body=body)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def create_channel_section(self, channel_id, section_type, title, position=0):
        """チャンネルセクションを作成

        Args:
            channel_id (str): チャンネルID
            section_type (str): セクションタイプ
            title (str): セクションタイトル
            position (int): 表示位置

        Returns:
            dict: 作成結果
        """
        try:
            body = {
                "snippet": {
                    "type": section_type,
                    "title": title,
                    "position": position,
                    "channelId": channel_id,
                }
            }

            request = self.youtube.channelSections().insert(part="snippet", body=body)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def update_channel_section(self, section_id, title=None, position=None):
        """チャンネルセクションを更新

        Args:
            section_id (str): セクションID
            title (str): 新しいタイトル（オプション）
            position (int): 新しい位置（オプション）

        Returns:
            dict: 更新結果
        """
        try:
            # 現在のセクション情報を取得
            current_sections = (
                self.youtube.channelSections()
                .list(part="snippet", id=section_id)
                .execute()
            )

            if not current_sections["items"]:
                raise YouTubeAPIError(f"セクションが見つかりません: {section_id}")

            body = current_sections["items"][0]

            if title:
                body["snippet"]["title"] = title
            if position is not None:
                body["snippet"]["position"] = position

            request = self.youtube.channelSections().update(part="snippet", body=body)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def delete_channel_section(self, section_id):
        """チャンネルセクションを削除

        Args:
            section_id (str): セクションID

        Returns:
            bool: 削除成功フラグ
        """
        try:
            request = self.youtube.channelSections().delete(id=section_id)
            request.execute()
            return True
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def get_channel_members(self, max_results=50):
        """チャンネルメンバーを取得

        Args:
            max_results (int): 取得する最大メンバー数

        Returns:
            list: メンバー情報のリスト
        """
        try:
            request = self.youtube.members().list(
                part="snippet", maxResults=max_results
            )
            response = request.execute()
            return response["items"]
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def get_membership_levels(self):
        """メンバーシップレベルを取得

        Returns:
            list: メンバーシップレベルのリスト
        """
        try:
            request = self.youtube.membershipsLevels().list(part="snippet")
            response = request.execute()
            return response["items"]
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def set_watermark(
        self, channel_id, image_file, timing_type="offsetFromStart", offset_ms=15000
    ):
        """チャンネルに透かしを設定

        Args:
            channel_id (str): チャンネルID
            image_file: 透かし画像ファイル
            timing_type (str): タイミングタイプ
            offset_ms (int): オフセット（ミリ秒）

        Returns:
            dict: 設定結果
        """
        try:
            body = {"timing": {"type": timing_type, "offsetMs": offset_ms}}

            request = self.youtube.watermarks().set(
                channelId=channel_id, body=body, media_body=image_file
            )
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def unset_watermark(self, channel_id):
        """チャンネルの透かしを削除

        Args:
            channel_id (str): チャンネルID

        Returns:
            bool: 削除成功フラグ
        """
        try:
            request = self.youtube.watermarks().unset(channelId=channel_id)
            request.execute()
            return True
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def subscribe_to_channel(self, channel_id):
        """チャンネルをサブスクライブ

        Args:
            channel_id (str): サブスクライブするチャンネルID

        Returns:
            dict: サブスクライブ結果
        """
        try:
            body = {
                "snippet": {
                    "resourceId": {"kind": "youtube#channel", "channelId": channel_id}
                }
            }

            request = self.youtube.subscriptions().insert(part="snippet", body=body)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def unsubscribe_from_channel(self, subscription_id):
        """チャンネルのサブスクライブを解除

        Args:
            subscription_id (str): サブスクリプションID

        Returns:
            bool: 解除成功フラグ
        """
        try:
            request = self.youtube.subscriptions().delete(id=subscription_id)
            request.execute()
            return True
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def get_channel_info_simple(self, channel_identifier, include_statistics=True):
        """チャンネル情報を簡単に取得（ID、ユーザー名、URL対応）

        Args:
            channel_identifier (str): チャンネルID、ユーザー名、またはURL
            include_statistics (bool): 統計情報を含めるか

        Returns:
            dict: チャンネル情報
            {
                'id': str,
                'title': str,
                'description': str,
                'thumbnail_url': str,
                'subscriber_count': int,
                'video_count': int,
                'view_count': int,
                'created_at': str,
                'country': str,
                'custom_url': str
            }
        """
        try:
            # URLまたはIDの正規化
            if channel_identifier.startswith("http"):
                channel_id = self._extract_channel_id_from_url(channel_identifier)
            elif channel_identifier.startswith("@"):
                # ハンドル名の場合
                channel_id = self._get_channel_id_by_handle(channel_identifier)
            elif channel_identifier.startswith("UC") and len(channel_identifier) == 24:
                # チャンネルID
                channel_id = channel_identifier
            else:
                # ユーザー名
                channel_id = self._get_channel_id_by_username(channel_identifier)

            # チャンネル情報取得
            parts = ["snippet"]
            if include_statistics:
                parts.append("statistics")

            response = self.service.channels().list(
                part=",".join(parts), id=channel_id
            ).execute()

            if not response.get("items"):
                raise YouTubeAPIError(f"チャンネルが見つかりません: {channel_identifier}")

            channel = response["items"][0]
            snippet = channel["snippet"]
            statistics = channel.get("statistics", {})

            # 簡略化された情報を返す
            return {
                "id": channel["id"],
                "title": snippet["title"],
                "description": snippet.get("description", ""),
                "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "subscriber_count": int(statistics.get("subscriberCount", 0)),
                "video_count": int(statistics.get("videoCount", 0)),
                "view_count": int(statistics.get("viewCount", 0)),
                "created_at": snippet.get("publishedAt", ""),
                "country": snippet.get("country", ""),
                "custom_url": snippet.get("customUrl", ""),
                "raw_data": channel,  # 元データも保持
            }

        except Exception as e:
            raise YouTubeAPIError(f"チャンネル情報取得に失敗しました: {str(e)}")

    def _extract_channel_id_from_url(self, url):
        """URLからチャンネルIDを抽出"""
        import re

        patterns = [
            r"youtube\.com/channel/([a-zA-Z0-9_-]+)",
            r"youtube\.com/c/([a-zA-Z0-9_-]+)",
            r"youtube\.com/user/([a-zA-Z0-9_-]+)",
            r"youtube\.com/@([a-zA-Z0-9_-]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                identifier = match.group(1)
                if identifier.startswith("UC") and len(identifier) == 24:
                    return identifier
                else:
                    return self._get_channel_id_by_username(identifier)

        raise YouTubeAPIError(f"URLからチャンネルIDを抽出できませんでした: {url}")

    def _get_channel_id_by_username(self, username):
        """ユーザー名からチャンネルIDを取得"""
        try:
            response = self.service.channels().list(
                part="id", forUsername=username
            ).execute()

            if response.get("items"):
                return response["items"][0]["id"]
            else:
                # ハンドル名として試行
                return self._get_channel_id_by_handle(f"@{username}")

        except Exception:
            raise YouTubeAPIError(f"ユーザー名からチャンネルIDを取得できませんでした: {username}")

    def _get_channel_id_by_handle(self, handle):
        """ハンドル名からチャンネルIDを取得"""
        try:
            # 検索APIを使用してハンドルからチャンネルを検索
            response = self.service.search().list(
                part="snippet", q=handle, type="channel", maxResults=1
            ).execute()

            if response.get("items"):
                return response["items"][0]["snippet"]["channelId"]
            else:
                raise YouTubeAPIError(f"ハンドル名からチャンネルが見つかりません: {handle}")

        except Exception as e:
            raise YouTubeAPIError(f"ハンドル名からチャンネルIDを取得できませんでした: {str(e)}")

    def get_channel_videos_advanced(
        self, channel_id, max_results=50, order="date", video_type="any", duration="any", after_date=None
    ):
        """チャンネルの動画を高度な条件で取得

        Args:
            channel_id (str): チャンネルID
            max_results (int): 最大取得件数
            order (str): ソート順序 ("date", "rating", "relevance", "title", "viewCount")
            video_type (str): 動画タイプ ("any", "episode", "movie")
            duration (str): 再生時間 ("any", "long", "medium", "short")
            after_date (str): この日付以降の動画のみ (YYYY-MM-DD)

        Returns:
            list: 動画リスト（統計情報付き）
        """
        try:
            params = {
                "part": "snippet",
                "channelId": channel_id,
                "type": "video",
                "order": order,
                "maxResults": min(max_results, 50),
            }

            if video_type != "any":
                params["videoType"] = video_type
            if duration != "any":
                params["videoDuration"] = duration
            if after_date:
                params["publishedAfter"] = f"{after_date}T00:00:00Z"

            response = self.service.search().list(**params).execute()

            # 統計情報を追加取得
            video_ids = [item["id"]["videoId"] for item in response.get("items", [])]
            if video_ids:
                stats_response = self.service.videos().list(
                    part="statistics,contentDetails", id=",".join(video_ids)
                ).execute()

                stats_dict = {item["id"]: item for item in stats_response.get("items", [])}

                for item in response.get("items", []):
                    video_id = item["id"]["videoId"]
                    if video_id in stats_dict:
                        item["statistics"] = stats_dict[video_id].get("statistics", {})
                        item["contentDetails"] = stats_dict[video_id].get("contentDetails", {})

            return response.get("items", [])

        except Exception as e:
            raise YouTubeAPIError(f"チャンネル動画の高度取得に失敗しました: {str(e)}")