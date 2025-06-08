"""
YouTube.py3 - ヘルパー機能

クォータ確認、カテゴリ取得、言語・地域情報、ガイドカテゴリなどの機能を提供します。
"""

from .exceptions import YouTubeAPIError
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)


class HelperMixin:
    """ヘルパー機能を提供するMixin"""

    def check_quota_usage(self):
        """APIクォータの使用量を確認するヘルパーメソッド

        注意: 実際のクォータ使用量はGoogle Cloud Consoleで確認してください。
        このメソッドは簡単な動作確認のみ行います。

        Returns:
            bool: APIキーが有効かどうか
        """
        try:
            # 軽量なAPI呼び出しでキーの有効性をテスト
            request = self.youtube.videoCategories().list(
                part="snippet", regionCode="JP", maxResults=1
            )
            response = self._execute_request(request)
            logger.info("APIキーは有効です")
            return True
        except YouTubeAPIError as e:
            if e.status_code == 403:
                logger.error("APIキーが無効または制限されています")
                raise YouTubeAPIError(f"APIキーエラー: {e}")
            else:
                logger.error(f"API呼び出しエラー: {e}")
                raise

    def get_video_categories(self, region_code="JP"):
        """動画カテゴリ一覧を取得

        Args:
            region_code (str): 地域コード

        Returns:
            list: カテゴリ情報のリスト
        """
        request = self.youtube.videoCategories().list(
            part="snippet", regionCode=region_code
        )
        response = self._execute_request(request)
        return response["items"]

    def get_supported_languages(self):
        """サポートされている言語一覧を取得

        YouTube でサポートされている言語の一覧を取得します。

        Returns:
            list: 言語情報のリスト
        """
        request = self.youtube.i18nLanguages().list(part="snippet")
        response = self._execute_request(request)
        return response["items"]

    def get_supported_regions(self):
        """サポートされている地域一覧を取得

        YouTube でサポートされている地域の一覧を取得します。

        Returns:
            list: 地域情報のリスト
        """
        request = self.youtube.i18nRegions().list(part="snippet")
        response = self._execute_request(request)
        return response["items"]

    def get_guide_categories(self, region_code="JP"):
        """ガイドカテゴリを取得

        Args:
            region_code (str): 地域コード

        Returns:
            list: ガイドカテゴリのリスト
        """
        try:
            request = self.youtube.guideCategories().list(
                part="snippet", regionCode=region_code
            )
            response = request.execute()
            return response["items"]
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")