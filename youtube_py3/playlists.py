"""
YouTube.py3 - プレイリスト関連機能

プレイリストの作成、更新、削除、動画の追加・削除、画像管理などの機能を提供します。
"""

from .exceptions import YouTubeAPIError
from googleapiclient.errors import HttpError


class PlaylistMixin:
    """プレイリスト関連の機能を提供するMixin"""

    def get_playlist_images(self, playlist_id):
        """プレイリスト画像を取得

        Args:
            playlist_id (str): プレイリストID

        Returns:
            list: プレイリスト画像のリスト
        """
        try:
            request = self.youtube.playlistImages().list(
                part="snippet", parent=playlist_id
            )
            response = request.execute()
            return response["items"]
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def upload_playlist_image(self, playlist_id, image_file):
        """プレイリスト画像をアップロード

        Args:
            playlist_id (str): プレイリストID
            image_file: 画像ファイル

        Returns:
            dict: アップロード結果
        """
        try:
            request = self.youtube.playlistImages().insert(
                onBehalfOfContentOwner=playlist_id, media_body=image_file
            )
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def create_playlist(self, title, description="", privacy_status="private"):
        """プレイリストを作成

        Args:
            title (str): プレイリストタイトル
            description (str): プレイリスト説明
            privacy_status (str): プライバシー設定 ('private', 'public', 'unlisted')

        Returns:
            dict: 作成されたプレイリスト情報
        """
        try:
            body = {
                "snippet": {"title": title, "description": description},
                "status": {"privacyStatus": privacy_status},
            }

            request = self.youtube.playlists().insert(part="snippet,status", body=body)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def update_playlist(
        self, playlist_id, title=None, description=None, privacy_status=None
    ):
        """プレイリストを更新

        Args:
            playlist_id (str): プレイリストID
            title (str): 新しいタイトル（オプション）
            description (str): 新しい説明（オプション）
            privacy_status (str): 新しいプライバシー設定（オプション）

        Returns:
            dict: 更新結果
        """
        try:
            # 現在のプレイリスト情報を取得
            current_playlist = self.get_playlist_info(playlist_id)

            body = {
                "id": playlist_id,
                "snippet": current_playlist["snippet"],
                "status": current_playlist.get("status", {}),
            }

            if title:
                body["snippet"]["title"] = title
            if description is not None:
                body["snippet"]["description"] = description
            if privacy_status:
                body["status"]["privacyStatus"] = privacy_status

            request = self.youtube.playlists().update(part="snippet,status", body=body)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def delete_playlist(self, playlist_id):
        """プレイリストを削除

        Args:
            playlist_id (str): プレイリストID

        Returns:
            bool: 削除成功フラグ
        """
        try:
            request = self.youtube.playlists().delete(id=playlist_id)
            request.execute()
            return True
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def add_video_to_playlist(self, playlist_id, video_id, position=None):
        """プレイリストに動画を追加

        Args:
            playlist_id (str): プレイリストID
            video_id (str): 動画ID
            position (int): 挿入位置（オプション）

        Returns:
            dict: 追加結果
        """
        try:
            body = {
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": video_id},
                }
            }

            if position is not None:
                body["snippet"]["position"] = position

            request = self.youtube.playlistItems().insert(part="snippet", body=body)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def remove_video_from_playlist(self, playlist_item_id):
        """プレイリストから動画を削除

        Args:
            playlist_item_id (str): プレイリストアイテムID

        Returns:
            bool: 削除成功フラグ
        """
        try:
            request = self.youtube.playlistItems().delete(id=playlist_item_id)
            request.execute()
            return True
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def update_playlist_item_position(self, playlist_item_id, new_position):
        """プレイリスト内動画の位置を更新

        Args:
            playlist_item_id (str): プレイリストアイテムID
            new_position (int): 新しい位置

        Returns:
            dict: 更新結果
        """
        try:
            # 現在のプレイリストアイテム情報を取得
            current_item = (
                self.youtube.playlistItems()
                .list(part="snippet", id=playlist_item_id)
                .execute()
            )

            if not current_item["items"]:
                raise YouTubeAPIError(
                    f"プレイリストアイテムが見つかりません: {playlist_item_id}"
                )

            body = current_item["items"][0]
            body["snippet"]["position"] = new_position

            request = self.youtube.playlistItems().update(part="snippet", body=body)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def get_playlist_videos_complete(self, playlist_id, include_unavailable=True):
        """プレイリストの全動画を取得（削除済み動画も含む）

        Args:
            playlist_id (str): プレイリストID
            include_unavailable (bool): 利用不可動画も含めるか

        Returns:
            dict: プレイリスト情報と動画リスト
            {
                'playlist_info': {...},
                'available_videos': [...],
                'unavailable_videos': [...],
                'total_count': int,
                'available_count': int,
                'unavailable_count': int
            }
        """
        try:
            # プレイリスト情報取得
            playlist_response = self.service.playlists().list(
                part="snippet,contentDetails", id=playlist_id
            ).execute()

            if not playlist_response.get("items"):
                raise YouTubeAPIError(f"プレイリストが見つかりません: {playlist_id}")

            playlist_info = playlist_response["items"][0]

            # プレイリストアイテム取得
            all_items = []
            next_page_token = None

            while True:
                params = {
                    "part": "snippet,contentDetails",
                    "playlistId": playlist_id,
                    "maxResults": 50,
                }

                if next_page_token:
                    params["pageToken"] = next_page_token

                response = self.service.playlistItems().list(**params).execute()
                all_items.extend(response.get("items", []))

                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break

            # 利用可能/不可能動画を分離
            available_videos = []
            unavailable_videos = []

            for item in all_items:
                video_id = item["snippet"]["resourceId"]["videoId"]

                # 動画の存在確認
                try:
                    video_response = self.service.videos().list(
                        part="snippet,statistics", id=video_id
                    ).execute()

                    if video_response.get("items"):
                        # 利用可能
                        video_data = video_response["items"][0]
                        video_data["playlist_position"] = item["snippet"]["position"]
                        available_videos.append(video_data)
                    else:
                        # 削除済みまたは非公開
                        if include_unavailable:
                            unavailable_data = {
                                "video_id": video_id,
                                "title": item["snippet"].get("title", "Deleted video"),
                                "playlist_position": item["snippet"]["position"],
                                "status": "unavailable",
                            }
                            unavailable_videos.append(unavailable_data)

                except Exception:
                    if include_unavailable:
                        unavailable_data = {
                            "video_id": video_id,
                            "title": item["snippet"].get("title", "Private video"),
                            "playlist_position": item["snippet"]["position"],
                            "status": "private_or_deleted",
                        }
                        unavailable_videos.append(unavailable_data)

            return {
                "playlist_info": playlist_info,
                "available_videos": available_videos,
                "unavailable_videos": unavailable_videos,
                "total_count": len(all_items),
                "available_count": len(available_videos),
                "unavailable_count": len(unavailable_videos),
            }

        except Exception as e:
            raise YouTubeAPIError(f"プレイリスト完全取得に失敗しました: {str(e)}")

    def create_playlist_from_search(
        self, title, description, search_query, max_videos=50, privacy_status="private"
    ):
        """検索結果からプレイリストを自動作成

        Args:
            title (str): プレイリストタイトル
            description (str): プレイリスト説明
            search_query (str): 検索クエリ
            max_videos (int): 最大動画数
            privacy_status (str): プライバシー設定 ('private', 'public', 'unlisted')

        Returns:
            dict: 作成されたプレイリスト情報
        """
        if not self.service:
            raise YouTubeAPIError("OAuth認証が必要です")

        try:
            # プレイリスト作成
            playlist_response = self.service.playlists().insert(
                part="snippet,status",
                body={
                    "snippet": {"title": title, "description": description},
                    "status": {"privacyStatus": privacy_status},
                },
            ).execute()

            playlist_id = playlist_response["id"]

            # 検索して動画を追加
            search_response = self.service.search().list(
                part="id",
                q=search_query,
                type="video",
                maxResults=max_videos,
                order="relevance",
            ).execute()

            added_videos = []
            for item in search_response.get("items", []):
                video_id = item["id"]["videoId"]

                try:
                    self.service.playlistItems().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "playlistId": playlist_id,
                                "resourceId": {"kind": "youtube#video", "videoId": video_id},
                            }
                        },
                    ).execute()
                    added_videos.append(video_id)

                except Exception:
                    continue  # スキップして続行

            return {
                "playlist_id": playlist_id,
                "playlist_info": playlist_response,
                "added_videos": added_videos,
                "added_count": len(added_videos),
            }

        except Exception as e:
            raise YouTubeAPIError(f"プレイリスト自動作成に失敗しました: {str(e)}")

    def merge_playlists(
        self, target_playlist_id, source_playlist_ids, remove_duplicates=True
    ):
        """複数のプレイリストをマージ

        Args:
            target_playlist_id (str): マージ先プレイリストID
            source_playlist_ids (list): マージ元プレイリストIDのリスト
            remove_duplicates (bool): 重複動画を除去するか

        Returns:
            dict: マージ結果
        """
        if not self.service:
            raise YouTubeAPIError("OAuth認証が必要です")

        try:
            all_video_ids = set() if remove_duplicates else []
            merged_count = 0
            skipped_count = 0

            for source_id in source_playlist_ids:
                # ソースプレイリストの動画取得
                source_videos = self.get_playlist_videos_complete(source_id)

                for video in source_videos["available_videos"]:
                    video_id = video["id"]

                    # 重複チェック
                    if remove_duplicates:
                        if video_id in all_video_ids:
                            skipped_count += 1
                            continue
                        all_video_ids.add(video_id)

                    # ターゲットプレイリストに追加
                    try:
                        self.service.playlistItems().insert(
                            part="snippet",
                            body={
                                "snippet": {
                                    "playlistId": target_playlist_id,
                                    "resourceId": {"kind": "youtube#video", "videoId": video_id},
                                }
                            },
                        ).execute()
                        merged_count += 1

                    except Exception:
                        skipped_count += 1
                        continue

            return {
                "target_playlist_id": target_playlist_id,
                "merged_count": merged_count,
                "skipped_count": skipped_count,
                "total_processed": merged_count + skipped_count,
            }

        except Exception as e:
            raise YouTubeAPIError(f"プレイリストマージに失敗しました: {str(e)}")