"""
YouTube.py3 - 情報取得モジュール

YouTube API の基本的な情報取得機能を提供するモジュールです。
"""

from .base import YouTubeAPIBase
from .exceptions import YouTubeAPIError


class InfoRetrievalMixin:
    """情報取得機能を提供するミックスインクラス"""
    
    def get_channel_info(self, channel_id):
        """チャンネル情報を取得

        指定されたチャンネルIDから、チャンネルの基本情報と統計情報を取得します。

        Args:
            channel_id (str): YouTubeチャンネルのID

        Returns:
            dict: チャンネル情報の辞書

        Raises:
            YouTubeAPIError: チャンネルが見つからない、またはAPI呼び出しに失敗した場合
        """
        request = self.youtube.channels().list(
            part="snippet,statistics", id=channel_id
        )
        response = self._execute_request(request)

        if not response["items"]:
            raise YouTubeAPIError(
                f"チャンネルが見つかりません: {channel_id}",
                error_code="channelNotFound",
                status_code=404,
            )

        return response["items"][0]

    def get_video_info(self, video_id):
        """動画情報を取得

        指定された動画IDから、動画の詳細情報と統計情報を取得します。

        Args:
            video_id (str): YouTube動画のID

        Returns:
            dict: 動画情報の辞書

        Raises:
            YouTubeAPIError: 動画が見つからない、またはAPI呼び出しに失敗した場合
        """
        request = self.youtube.videos().list(
            part="snippet,statistics", id=video_id
        )
        response = self._execute_request(request)

        if not response["items"]:
            raise YouTubeAPIError(f"動画が見つかりません: {video_id}")

        return response["items"][0]

    def get_playlist_info(self, playlist_id):
        """プレイリスト情報を取得

        Args:
            playlist_id (str): プレイリストID

        Returns:
            dict: プレイリスト情報
        """
        request = self.youtube.playlists().list(
            part="snippet,contentDetails,status", id=playlist_id
        )
        response = self._execute_request(request)

        if not response["items"]:
            raise YouTubeAPIError(f"プレイリストが見つかりません: {playlist_id}")

        return response["items"][0]

    def get_video_statistics_only(self, video_id):
        """動画の統計情報のみを取得

        指定された動画の統計情報（再生回数、いいね数など）のみを効率的に取得します。

        Args:
            video_id (str): YouTube動画のID

        Returns:
            dict: 統計情報

        Raises:
            YouTubeAPIError: 動画が見つからない、またはAPI呼び出しに失敗した場合
        """
        request = self.youtube.videos().list(part="statistics", id=video_id)
        response = self._execute_request(request)

        if not response["items"]:
            raise YouTubeAPIError(f"動画が見つかりません: {video_id}")

        return response["items"][0]["statistics"]

    def get_channel_statistics_only(self, channel_id):
        """チャンネルの統計情報のみを取得

        指定されたチャンネルの統計情報（登録者数、動画数など）のみを効率的に取得します。

        Args:
            channel_id (str): YouTubeチャンネルのID

        Returns:
            dict: 統計情報

        Raises:
            YouTubeAPIError: チャンネルが見つからない、またはAPI呼び出しに失敗した場合
        """
        request = self.youtube.channels().list(part="statistics", id=channel_id)
        response = self._execute_request(request)

        if not response["items"]:
            raise YouTubeAPIError(f"チャンネルが見つかりません: {channel_id}")

        return response["items"][0]["statistics"]

    def bulk_get_video_info(self, video_ids):
        """複数の動画情報を一括取得
        
        Args:
            video_ids (list): 動画IDのリスト（最大50件）
        
        Returns:
            list: 動画情報のリスト
        """
        if len(video_ids) > 50:
            raise YouTubeAPIError("一度に取得できる動画は最大50件です")
        
        video_ids_str = ",".join(video_ids)
        request = self.youtube.videos().list(
            part="snippet,statistics",
            id=video_ids_str
        )
        response = self._execute_request(request)
        return response["items"]

    def bulk_get_channel_info(self, channel_ids):
        """複数のチャンネル情報を一括取得
        
        Args:
            channel_ids (list): チャンネルIDのリスト（最大50件）
        
        Returns:
            list: チャンネル情報のリスト
        """
        if len(channel_ids) > 50:
            raise YouTubeAPIError("一度に取得できるチャンネルは最大50件です")
        
        channel_ids_str = ",".join(channel_ids)
        request = self.youtube.channels().list(
            part="snippet,statistics",
            id=channel_ids_str
        )
        response = self._execute_request(request)
        return response["items"]