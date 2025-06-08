"""
YouTube.py3 - OAuth認証管理モジュール

OAuth認証に関する機能を提供するモジュールです。
"""

import os
import pickle
import logging
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from .exceptions import YouTubeAPIError

logger = logging.getLogger(__name__)


class OAuthManager:
    """OAuth認証を管理するクラス"""
    
    # OAuth関連の定数
    OAUTH_SCOPES = {
        'readonly': 'https://www.googleapis.com/auth/youtube.readonly',
        'upload': 'https://www.googleapis.com/auth/youtube.upload', 
        'full': 'https://www.googleapis.com/auth/youtube',
        'force_ssl': 'https://www.googleapis.com/auth/youtube.force-ssl'
    }
    
    def __init__(self, oauth_config=None):
        """OAuth管理を初期化
        
        Args:
            oauth_config (dict): OAuth設定辞書
        """
        self.oauth_config = oauth_config or {}
        self.credentials = None
        
    def setup_oauth_credentials(self):
        """OAuth認証情報をセットアップ"""
        config = self.oauth_config
        client_secrets_file = config.get('client_secrets_file')
        token_file = config.get('token_file', 'token.pickle')
        scopes = self._resolve_scopes(config.get('scopes', ['readonly']))
        
        if not client_secrets_file:
            raise YouTubeAPIError("client_secrets_file が指定されていません")
        
        credentials = None
        
        # 既存のトークンファイルから認証情報を読み込み
        if os.path.exists(token_file):
            try:
                with open(token_file, 'rb') as token:
                    credentials = pickle.load(token)
            except Exception as e:
                logger.warning(f"トークンファイルの読み込みに失敗: {e}")
        
        # 認証情報が無効または存在しない場合は新規認証
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                except Exception as e:
                    logger.warning(f"トークンのリフレッシュに失敗: {e}")
                    credentials = None
            
            if not credentials:
                credentials = self._perform_oauth_flow(client_secrets_file, scopes)
            
            # トークンを保存
            try:
                with open(token_file, 'wb') as token:
                    pickle.dump(credentials, token)
            except Exception as e:
                logger.warning(f"トークンファイルの保存に失敗: {e}")
        
        self.credentials = credentials
        return credentials

    def _resolve_scopes(self, scope_names):
        """スコープ名を実際のスコープURLに変換"""
        resolved_scopes = []
        for scope_name in scope_names:
            if scope_name in self.OAUTH_SCOPES:
                resolved_scopes.append(self.OAUTH_SCOPES[scope_name])
            elif scope_name.startswith('https://'):
                resolved_scopes.append(scope_name)
            else:
                raise YouTubeAPIError(f"未知のスコープ: {scope_name}")
        return resolved_scopes

    def _perform_oauth_flow(self, client_secrets_file, scopes):
        """OAuth認証フローを実行"""
        config = self.oauth_config
        port = config.get('port', 8080)
        auto_open_browser = config.get('auto_open_browser', True)
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
            
            if auto_open_browser:
                credentials = flow.run_local_server(
                    port=port,
                    prompt='consent',
                    authorization_prompt_message='ブラウザでYouTube認証を完了してください...'
                )
            else:
                credentials = flow.run_console()
            
            return credentials
            
        except Exception as e:
            raise YouTubeAPIError(f"OAuth認証に失敗しました: {str(e)}")
    
    def is_authenticated(self):
        """OAuth認証済みかどうかをチェック"""
        return self.credentials is not None and self.credentials.valid
    
    def get_credentials(self):
        """認証情報を取得"""
        return self.credentials