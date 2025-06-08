"""
YouTube.py3 - 基本設定とヘルパー関数

YouTubeAPIの基本設定とユーティリティ関数を提供するモジュールです。
"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
import json
import re
from datetime import datetime

from .exceptions import YouTubeAPIError
from .oauth_manager import OAuthManager

logger = logging.getLogger(__name__)


class YouTubeAPIBase:
    """YouTube API の基本機能を提供するベースクラス"""
    
    def __init__(self, api_key=None, oauth_credentials=None, oauth_config=None):
        """YouTube APIクライアントを初期化
        
        Args:
            api_key (str): YouTube Data API v3のAPIキー（読み取り専用操作用）
            oauth_credentials: OAuth認証情報オブジェクト
            oauth_config (dict): OAuth設定辞書
        """
        if not api_key and not oauth_credentials and not oauth_config:
            raise YouTubeAPIError("APIキーまたはOAuth設定が必要です")
        
        self._api_key = api_key
        self._oauth_manager = None
        self._has_oauth = False
        
        try:
            # OAuth認証の処理
            if oauth_config:
                self._oauth_manager = OAuthManager(oauth_config)
                oauth_credentials = self._oauth_manager.setup_oauth_credentials()
                self._has_oauth = True
            elif oauth_credentials:
                self._oauth_manager = OAuthManager()
                self._oauth_manager.credentials = oauth_credentials
                self._has_oauth = True
            
            # YouTubeクライアントの構築
            if self._has_oauth and oauth_credentials:
                self.youtube = build("youtube", "v3", credentials=oauth_credentials)
            else:
                self.youtube = build("youtube", "v3", developerKey=api_key)
                
        except Exception as e:
            raise YouTubeAPIError(f"YouTube API の初期化に失敗しました: {str(e)}")

    def _require_oauth(self, operation_name="この操作"):
        """OAuth認証が必要な操作で呼び出すヘルパーメソッド"""
        if not self._has_oauth:
            raise YouTubeAPIError(
                f"{operation_name}にはOAuth認証が必要です。\n"
                "oauth_configパラメータでYouTubeAPIを初期化してください。"
            )

    def _handle_http_error(self, e):
        """HTTPエラーを適切なYouTubeAPIErrorに変換"""
        error_details = {}
        status_code = e.resp.status if hasattr(e, 'resp') else None
        
        try:
            error_details = json.loads(e.content.decode())
        except:
            pass

        error_code = error_details.get("error", {}).get("code")
        
        raise YouTubeAPIError(
            f"API エラー: {e}",
            error_code=error_code,
            status_code=status_code,
            details=error_details,
        )

    def _execute_request(self, request):
        """APIリクエストを実行し、エラーハンドリングを行う"""
        try:
            return request.execute()
        except HttpError as e:
            self._handle_http_error(e)
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {str(e)}")