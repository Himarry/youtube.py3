"""
YouTube.py3 - メインライブラリファイル

YouTube Data API v3を簡単に使用するためのPythonラッパーライブラリです。
複雑なAPIの詳細を隠蔽し、初心者でも使いやすいインターフェースを提供します。

【重要】APIキーについて：
このライブラリはYouTube Data APIを使用するため、各ユーザーが自分のAPIキーを取得する必要があります。
- ライブラリ自体にAPIキーは含まれていません
- 各ユーザーが個別にGoogle Cloud Consoleでプロジェクトを作成し、APIキーを取得します
- 使用量制限やセキュリティは各ユーザーのプロジェクトで管理されます
- ライブラリは単なる「便利なラッパー」であり、APIアクセス権限は含みません

"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
import json
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)


class YouTubeAPIError(Exception):
    """YouTube API関連のエラー例外クラス

    YouTube APIの呼び出し時に発生するエラーをラップし、
    より詳細なエラー情報を提供します。
    """

    def __init__(self, message, error_code=None, status_code=None, details=None):
        """YouTubeAPIErrorを初期化

        Args:
            message (str): エラーメッセージ
            error_code (str): APIエラーコード（オプション）
            status_code (int): HTTPステータスコード（オプション）
            details (dict): 詳細なエラー情報（オプション）
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}

    def __str__(self):
        """エラーの文字列表現を返す"""
        error_parts = [self.message]

        if self.error_code:
            error_parts.append(f"エラーコード: {self.error_code}")

        if self.status_code:
            error_parts.append(f"ステータスコード: {self.status_code}")

        return " | ".join(error_parts)

    def __repr__(self):
        """エラーの詳細な表現を返す"""
        return (
            f"YouTubeAPIError(message='{self.message}', "
            f"error_code='{self.error_code}', "
            f"status_code={self.status_code}, "
            f"details={self.details})"
        )

    def is_quota_exceeded(self):
        """クォータ超過エラーかどうかを判定

        Returns:
            bool: クォータ超過エラーの場合True
        """
        return self.status_code == 403 and (
            self.error_code == "quotaExceeded" or "quota" in self.message.lower()
        )

    def is_api_key_invalid(self):
        """APIキー無効エラーかどうかを判定

        Returns:
            bool: APIキー無効エラーの場合True
        """
        return self.status_code == 400 and (
            "api key" in self.message.lower() or "invalid" in self.message.lower()
        )

    def is_not_found(self):
        """リソースが見つからないエラーかどうかを判定

        Returns:
            bool: リソースが見つからない場合True
        """
        return (
            self.status_code == 404
            or "not found" in self.message.lower()
            or "見つかりません" in self.message
        )

    def is_forbidden(self):
        """アクセス権限エラーかどうかを判定

        Returns:
            bool: アクセス権限エラーの場合True
        """
        return self.status_code == 403

    def get_suggested_action(self):
        """エラーに対する推奨アクションを取得

        Returns:
            str: 推奨アクション
        """
        if self.is_quota_exceeded():
            return (
                "APIクォータが上限に達しています。"
                "しばらく待ってから再試行するか、Google Cloud Consoleで使用量を確認してください。"
            )
        elif self.is_api_key_invalid():
            return (
                "APIキーが無効です。"
                "Google Cloud ConsoleでAPIキーを確認し、YouTube Data API v3が有効になっているか確認してください。"
            )
        elif self.is_not_found():
            return (
                "指定されたリソース（動画、チャンネル、プレイリストなど）が見つかりません。"
                "IDが正しいか確認してください。"
            )
        elif self.is_forbidden():
            return (
                "アクセス権限がありません。"
                "APIキーの制限設定を確認するか、認証が必要な操作の場合はOAuth認証を使用してください。"
            )
        else:
            return "エラーの詳細を確認し、APIドキュメントを参照してください。"


class YouTubeAPI:
    """YouTube Data API v3の簡易ラッパークラス（OAuth対応版）

    【このライブラリの目的】
    YouTube Data API v3は非常に複雑で、初心者には使いにくいAPIです。
    このライブラリは以下の問題を解決します：

    1. 複雑なパラメータ設定を簡素化
    2. エラーハンドリングの統一
    3. ページネーション処理の自動化
    4. よく使う機能のワンライナー化
    5. 日本語での分かりやすいメソッド名と説明

    【APIキーについて】
    このライブラリを使用するには、各ユーザーが以下の手順でAPIキーを取得してください：

    1. Google Cloud Console（https://console.cloud.google.com/）にアクセス
    2. 新しいプロジェクトを作成（または既存プロジェクトを選択）
    3. YouTube Data API v3を有効化
    4. 認証情報ページでAPIキーを作成
    5. 必要に応じてAPIキーに制限を設定（推奨）

    使用例:
        import os
        from youtube_py3 import YouTubeAPI

        # 環境変数からAPIキーを取得（推奨）
        api_key = os.getenv('YOUTUBE_API_KEY')
        yt = YouTubeAPI(api_key)

        # チャンネル情報を取得
        channel = yt.get_channel_info("CHANNEL_ID")
        print(channel["snippet"]["title"])
    """

    # OAuth関連の定数
    OAUTH_SCOPES = {
        'readonly': 'https://www.googleapis.com/auth/youtube.readonly',
        'upload': 'https://www.googleapis.com/auth/youtube.upload', 
        'full': 'https://www.googleapis.com/auth/youtube',
        'force_ssl': 'https://www.googleapis.com/auth/youtube.force-ssl'
    }

    def __init__(self, api_key=None, oauth_credentials=None, oauth_config=None):
        """YouTube APIクライアントを初期化
        
        Args:
            api_key (str): YouTube Data API v3のAPIキー（読み取り専用操作用）
            oauth_credentials: OAuth認証情報オブジェクト
            oauth_config (dict): OAuth設定辞書
                {
                    'client_secrets_file': 'client_secrets.json',
                    'scopes': ['full'],  # または具体的なスコープ
                    'token_file': 'token.pickle',  # 認証トークン保存ファイル
                    'port': 8080,  # ローカルサーバーポート
                    'auto_open_browser': True  # ブラウザ自動起動
                }
        
        例:
            # APIキーのみ（読み取り専用）
            yt = YouTubeAPI(api_key="YOUR_API_KEY")
            
            # OAuth設定で初期化
            oauth_config = {
                'client_secrets_file': 'client_secrets.json',
                'scopes': ['full'],
                'token_file': 'youtube_token.pickle'
            }
            yt = YouTubeAPI(api_key="YOUR_API_KEY", oauth_config=oauth_config)
        """
        if not api_key and not oauth_credentials and not oauth_config:
            raise YouTubeAPIError("APIキーまたはOAuth設定が必要です")
        
        self._api_key = api_key
        self._oauth_credentials = oauth_credentials
        self._oauth_config = oauth_config or {}
        self._has_oauth = False
        
        try:
            # OAuth認証の処理
            if oauth_config:
                self._oauth_credentials = self._setup_oauth_credentials()
                self._has_oauth = True
            elif oauth_credentials:
                self._oauth_credentials = oauth_credentials
                self._has_oauth = True
            
            # YouTubeクライアントの構築
            if self._has_oauth:
                self.youtube = build("youtube", "v3", credentials=self._oauth_credentials)
            else:
                self.youtube = build("youtube", "v3", developerKey=api_key)
                
        except Exception as e:
            raise YouTubeAPIError(f"YouTube API の初期化に失敗しました: {str(e)}")

    def _setup_oauth_credentials(self):
        """OAuth認証情報をセットアップ"""
        config = self._oauth_config
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
        config = self._oauth_config
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

    def _require_oauth(self, operation_name="この操作"):
        """OAuth認証が必要な操作で呼び出すヘルパーメソッド"""
        if not self._has_oauth:
            raise YouTubeAPIError(
                f"{operation_name}にはOAuth認証が必要です。\n"
                "oauth_configパラメータでYouTubeAPIを初期化してください。"
            )

    # ======== 基本的な情報取得メソッド ========

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
            YouTubeAPIError: 動画が見つらない、またはAPI呼び出しに失敗した場合
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

    # ======== 検索メソッド ========

    def search_videos(self, query, max_results=5, order="relevance", channel_id=None):
        """動画を検索

        指定されたキーワードで動画を検索し、結果を取得します。

        Args:
            query (str): 検索キーワード
            max_results (int): 取得する最大結果数 (デフォルト: 5)
            order (str): ソート順序 (デフォルト: 'relevance')
            channel_id (str): 特定のチャンネル内で検索する場合のチャンネルID（オプション）

        Returns:
            list: 検索結果の辞書のリスト

        Raises:
            YouTubeAPIError: 検索に失敗した場合

        使用例:
            # 一般的な動画検索
            videos = yt.search_videos("Python プログラミング", max_results=10)
            
            # 特定のチャンネル内で検索
            videos = yt.search_videos(
                "機械学習", 
                max_results=20, 
                channel_id="UC_x5XG1OV2P6uZZ5FSM9Ttw"
            )
        """
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "order": order,
        }
        
        # チャンネルIDが指定された場合は追加
        if channel_id:
            params["channelId"] = channel_id
        
        request = self.youtube.search().list(**params)
        response = self._execute_request(request)
        return response["items"]

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

    # ======== リスト取得メソッド ========

    def get_playlist_videos(self, playlist_id, max_results=50):
        """プレイリストの動画一覧を取得

        Args:
            playlist_id (str): YouTubeプレイリストのID
            max_results (int): 取得する最大動画数 (デフォルト: 50)

        Returns:
            list: 動画情報の辞書のリスト

        Raises:
            YouTubeAPIError: プレイリストが見つからない、またはAPI呼び出しに失敗した場合
        """
        videos = []
        next_page_token = None

        while len(videos) < max_results:
            request = self.youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token,
            )
            response = self._execute_request(request)

            videos.extend(response["items"])

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return videos[:max_results]

    def get_comments(self, video_id, max_results=100):
        """動画のコメントを取得

        Args:
            video_id (str): YouTube動画のID
            max_results (int): 取得する最大コメント数 (デフォルト: 100)

        Returns:
            list: コメント情報の辞書のリスト

        Raises:
            YouTubeAPIError: コメントが無効化されている、またはAPI呼び出しに失敗した場合
        """
        comments = []
        next_page_token = None

        while len(comments) < max_results:
            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(100, max_results - len(comments)),
                pageToken=next_page_token,
                order="time",
            )
            
            try:
                response = self._execute_request(request)
            except YouTubeAPIError as e:
                if e.status_code == 403:
                    raise YouTubeAPIError("この動画のコメントは無効化されています")
                raise

            comments.extend(response["items"])

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return comments[:max_results]

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

    # ======== ページネーション対応メソッド ========

    def get_channel_videos_paginated(self, channel_id, max_results=None, order="date", page_token=None):
        """チャンネル動画を取得（ページネーション対応）
        
        Args:
            channel_id (str): チャンネルID
            max_results (int): 最大取得件数（Noneの場合は50件）
            order (str): ソート順序（'date', 'relevance', 'rating', 'title', 'viewCount'）
            page_token (str): ページトークン（次のページ用）
        
        Returns:
            dict: 検索結果とページ情報
                'items': 動画リスト
                'nextPageToken': 次のページトークン（存在する場合）
                'totalResults': 総件数（推定）
        
        Raises:
            YouTubeAPIError: API呼び出しに失敗した場合
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
        
        使用例:
            # 特定のチャンネル内でページネーション検索
            result = yt.search_videos_paginated(
                "Python", 
                max_results=25,
                channel_id="UC_x5XG1OV2P6uZZ5FSM9Ttw"
            )
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
        
        例:
            # チャンネルの全動画を取得
            all_videos = yt.paginate_all_results(yt.get_channel_videos_paginated, "CHANNEL_ID", max_total_results=500)
            
            # 検索結果を全件取得
            all_results = yt.paginate_all_results(yt.search_videos_paginated, "Python", max_total_results=1000)
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

    # ======== 簡略化メソッド（通常のリスト取得版） ========

    def get_channel_playlists(self, channel_id, max_results=50):
        """チャンネルのプレイリスト一覧を取得（簡略版）
        
        Args:
            channel_id (str): チャンネルID
            max_results (int): 最大取得件数
        
        Returns:
            list: プレイリスト一覧
        """
        return self.paginate_all_results(
            self.search_playlists_paginated,
            f"channel:{channel_id}",
            max_total_results=max_results
        )

    def search_all_videos(self, query, max_results=500, channel_id=None):
        """動画を全件検索（簡略版）
        
        Args:
            query (str): 検索キーワード
            max_results (int): 最大取得件数
            channel_id (str): 特定のチャンネル内で検索する場合のチャンネルID（オプション）
        
        Returns:
            list: 検索結果
        """
        return self.paginate_all_results(
            self.search_videos_paginated,
            query,
            max_total_results=max_results,
            channel_id=channel_id
        )

    def get_all_channel_videos(self, channel_id, max_results=500):
        """チャンネルの全動画を取得（簡略版）
        
        Args:
            channel_id (str): チャンネルID
            max_results (int): 最大取得件数
        
        Returns:
            list: 動画一覧
        """
        return self.paginate_all_results(
            self.get_channel_videos_paginated,
            channel_id,
            max_total_results=max_results
        )

    def get_all_playlist_videos(self, playlist_id, max_results=500):
        """プレイリストの全動画を取得（簡略版）
        
        Args:
            playlist_id (str): プレイリストID
            max_results (int): 最大取得件数
        
        Returns:
            list: 動画一覧
        """
        return self.paginate_all_results(
            self.get_playlist_videos_paginated,
            playlist_id,
            max_total_results=max_results
        )

    def get_all_comments(self, video_id, max_results=1000):
        """動画の全コメントを取得（簡略版）
        
        Args:
            video_id (str): 動画ID
            max_results (int): 最大取得件数
        
        Returns:
            list: コメント一覧
        """
        return self.paginate_all_results(
            self.get_comments_paginated,
            video_id,
            max_total_results=max_results
        )

    # ======== 統計情報取得メソッド ========

    def get_video_statistics_only(self, video_id):
        """動画の統計情報のみを取得

        指定された動画の統計情報（再生回数、いいね数など）のみを効率的に取得します。

        Args:
            video_id (str): YouTube動画のID

        Returns:
            dict: 統計情報

        Raises:
            YouTubeAPIError: 動画が見つらない、またはAPI呼び出しに失敗した場合
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

    # ======== ヘルパーメソッド ========

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

    # ======== 字幕（Captions）関連 ========

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

    # ======== チャンネルバナー関連 ========

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

    # ======== チャンネル更新関連 ========

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

    # ======== チャンネルセクション管理 ========

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

    # ======== コメント管理 ========

    def get_comment_details(self, comment_id):
        """コメント詳細を取得

        Args:
            comment_id (str): コメントID

        Returns:
            dict: コメント詳細情報
        """
        try:
            request = self.youtube.comments().list(part="snippet", id=comment_id)
            response = request.execute()

            if not response["items"]:
                raise YouTubeAPIError(f"コメントが見つかりません: {comment_id}")

            return response["items"][0]
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def post_comment_reply(self, parent_comment_id, text):
        """コメントに返信

        Args:
            parent_comment_id (str): 親コメントID
            text (str): 返信テキスト

        Returns:
            dict: 投稿結果
        """
        try:
            body = {"snippet": {"parentId": parent_comment_id, "textOriginal": text}}

            request = self.youtube.comments().insert(part="snippet", body=body)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def update_comment(self, comment_id, text):
        """コメントを更新

        Args:
            comment_id (str): コメントID
            text (str): 新しいテキスト

        Returns:
            dict: 更新結果
        """
        try:
            # 現在のコメント情報を取得
            current_comment = self.get_comment_details(comment_id)

            body = current_comment
            body["snippet"]["textOriginal"] = text

            request = self.youtube.comments().update(part="snippet", body=body)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def mark_comment_as_spam(self, comment_id):
        """コメントをスパムとしてマーク

        Args:
            comment_id (str): コメントID

        Returns:
            bool: 成功フラグ
        """
        try:
            request = self.youtube.comments().markAsSpam(id=comment_id)
            request.execute()
            return True
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def set_comment_moderation_status(self, comment_id, moderation_status):
        """コメントのモデレーション状態を設定

        Args:
            comment_id (str): コメントID
            moderation_status (str): モデレーション状態 ('published', 'heldForReview', 'likelySpam', 'rejected')

        Returns:
            bool: 成功フラグ
        """
        try:
            request = self.youtube.comments().setModerationStatus(
                id=comment_id, moderationStatus=moderation_status
            )
            request.execute()
            return True
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def delete_comment(self, comment_id):
        """コメントを削除

        Args:
            comment_id (str): コメントID

        Returns:
            bool: 削除成功フラグ
        """
        try:
            request = self.youtube.comments().delete(id=comment_id)
            request.execute()
            return True
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def post_comment_thread(self, video_id, text, channel_id=None):
        """新しいコメントスレッドを投稿

        Args:
            video_id (str): 動画ID（動画へのコメントの場合）
            text (str): コメントテキスト
            channel_id (str): チャンネルID（チャンネルへのコメントの場合）

        Returns:
            dict: 投稿結果
        """
        try:
            body = {"snippet": {"topLevelComment": {"snippet": {"textOriginal": text}}}}

            if video_id:
                body["snippet"]["videoId"] = video_id
            elif channel_id:
                body["snippet"]["channelId"] = channel_id
            else:
                raise YouTubeAPIError(
                    "video_id または channel_id のいずれかを指定してください"
                )

            request = self.youtube.commentThreads().insert(part="snippet", body=body)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    # ======== ガイドカテゴリ ========

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

    # ======== メンバーシップ関連 ========

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

    # ======== プレイリスト画像管理 ========

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

    # ======== プレイリスト管理 ========

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

    # ======== サムネイル管理 ========

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

    # ======== 動画管理（拡張） ========

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

    # ======== 透かし管理 ========

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

    # ======== サブスクリプション管理（拡張） ========

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

    # ======== 便利なヘルパーメソッド（簡略化） ========

    def get_basic_info(self, resource_id, resource_type="auto"):
        """リソースの基本情報を自動判別して取得
        
        Args:
            resource_id (str): YouTube ID（動画、チャンネル、プレイリスト）
            resource_type (str): リソースタイプ（'auto', 'video', 'channel', 'playlist'）
        
        Returns:
            dict: 基本情報
        
        例:
            # 自動判別
            info = yt.get_basic_info("dQw4w9WgXcQ")  # 動画として認識
            info = yt.get_basic_info("UC_x5XG1OV2P6uZZ5FSM9Ttw")  # チャンネルとして認識
        """
        if resource_type == "auto":
            # IDの長さと形式で自動判別
            if len(resource_id) == 11:
                resource_type = "video"
            elif len(resource_id) == 24 and resource_id.startswith("UC"):
                resource_type = "channel"
            elif len(resource_id) in [18, 24, 34]:
                resource_type = "playlist"
            else:
                raise YouTubeAPIError("リソースタイプを自動判別できませんでした")
        
        if resource_type == "video":
            return self.get_video_info(resource_id)
        elif resource_type == "channel":
            return self.get_channel_info(resource_id)
        elif resource_type == "playlist":
            return self.get_playlist_info(resource_id)
        else:
            raise YouTubeAPIError(f"未対応のリソースタイプ: {resource_type}")

    def quick_search(self, query, count=10, content_type="video"):
        """クイック検索（結果を簡潔に返す）
        
        Args:
            query (str): 検索キーワード
            count (int): 取得件数
            content_type (str): コンテンツタイプ（'video', 'channel', 'playlist', 'all'）
        
        Returns:
            list: 簡潔な検索結果
        
        例:
            results = yt.quick_search("Python プログラミング", count=5)
            for result in results:
                print(f"{result['title']} - {result['id']}")
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

    def get_stats_summary(self, resource_id, resource_type="auto"):
        """統計情報のサマリーを取得
        
        Args:
            resource_id (str): リソースID
            resource_type (str): リソースタイプ
        
        Returns:
            dict: 統計サマリー
        
        例:
            stats = yt.get_stats_summary("dQw4w9WgXcQ")
            print(f"再生回数: {stats['view_count']:,}")
        """
        if resource_type == "auto":
            if len(resource_id) == 11:
                resource_type = "video"
            elif len(resource_id) == 24 and resource_id.startswith("UC"):
                resource_type = "channel"
        
        if resource_type == "video":
            stats = self.get_video_statistics_only(resource_id)
            return {
                'view_count': int(stats.get('viewCount', 0)),
                'like_count': int(stats.get('likeCount', 0)),
                'comment_count': int(stats.get('commentCount', 0)),
                'type': 'video'
            }
        elif resource_type == "channel":
            stats = self.get_channel_statistics_only(resource_id)
            return {
                'subscriber_count': int(stats.get('subscriberCount', 0)),
                'video_count': int(stats.get('videoCount', 0)),
                'view_count': int(stats.get('viewCount', 0)),
                'type': 'channel'
            }
        else:
            raise YouTubeAPIError(f"統計情報は動画とチャンネルのみ対応: {resource_type}")

    def bulk_get_video_info(self, video_ids):
        """複数の動画情報を一括取得
        
        Args:
            video_ids (list): 動画IDのリスト（最大50件）
        
        Returns:
            list: 動画情報のリスト
        
        例:
            videos = yt.bulk_get_video_info(["dQw4w9WgXcQ", "jNQXAC9IVRw"])
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

    def get_trending_videos(self, region_code="JP", category_id=None, max_results=50):
        """トレンド動画を取得
        
        Args:
            region_code (str): 地域コード
            category_id (str): カテゴリID（オプション）
            max_results (int): 最大取得件数
        
        Returns:
            list: トレンド動画のリスト
        """
        params = {
            'part': 'snippet,statistics',
            'chart': 'mostPopular',
            'regionCode': region_code,
            'maxResults': max_results
        }
        
        if category_id:
            params['videoCategoryId'] = category_id
        
        request = self.youtube.videos().list(**params)
        response = self._execute_request(request)
        return response["items"]

    def get_channel_from_username(self, username):
        """ユーザー名からチャンネル情報を取得
        
        Args:
            username (str): YouTubeユーザー名
        
        Returns:
            dict: チャンネル情報
        """
        request = self.youtube.channels().list(
            part="snippet,statistics",
            forUsername=username
        )
        response = self._execute_request(request)
        
        if not response["items"]:
            raise YouTubeAPIError(f"ユーザーが見つかりません: {username}")
        
        return response["items"][0]

    def get_my_channel(self):
        """自分のチャンネル情報を取得（OAuth認証が必要）
        
        Returns:
            dict: 自分のチャンネル情報
        """
        request = self.youtube.channels().list(
            part="snippet,statistics",
            mine=True
        )
        response = self._execute_request(request)
        
        if not response["items"]:
                                             raise YouTubeAPIError("チャンネルが見つかりません（OAuth認証が必要です）")
        
        return response["items"][0]

    def extract_video_id_from_url(self, youtube_url):
        """YouTube URLから動画IDを抽出
        
        Args:
            youtube_url (str): YouTube URL
        
        Returns:
            str: 動画ID
        
        例:
            video_id = yt.extract_video_id_from_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        """
        import re
        
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, youtube_url)
            if match:
                return match.group(1)
        
        raise YouTubeAPIError(f"有効なYouTube URLではありません: {youtube_url}")

    def extract_playlist_id_from_url(self, youtube_url):
        """YouTube URLからプレイリストIDを抽出
        
        Args:
            youtube_url (str): YouTube URL
        
        Returns:
            str: プレイリストID
        """
        import re
        
        pattern = r'[?&]list=([a-zA-Z0-9_-]+)'
        match = re.search(pattern, youtube_url)
        
        if match:
            return match.group(1)
        
        raise YouTubeAPIError(f"プレイリストIDが見つかりません: {youtube_url}")

    def get_video_duration_seconds(self, video_id):
        """動画の長さを秒で取得
        
        Args:
            video_id (str): 動画ID
        
        Returns:
            int: 動画の長さ（秒）
        """
        import re
        
        request = self.youtube.videos().list(
            part="contentDetails",
            id=video_id
        )
        response = self._execute_request(request)
        
        if not response["items"]:
            raise YouTubeAPIError(f"動画が見つかりません: {video_id}")
        
        duration = response["items"][0]["contentDetails"]["duration"]
        
        # ISO 8601形式（PT4M13S）を秒に変換
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            return hours * 3600 + minutes * 60 + seconds
        
        return 0

    def format_view_count(self, view_count):
        """再生回数を読みやすい形式にフォーマット
        
        Args:
            view_count (int): 再生回数
        
        Returns:
            str: フォーマット済み文字列
        
        例:
            formatted = yt.format_view_count(1234567)  # "123.5万回"
        """
        view_count = int(view_count)
        
        if view_count >= 100000000:  # 1億以上
            return f"{view_count / 100000000:.1f}億回"
        elif view_count >= 10000:  # 1万以上
            return f"{view_count / 10000:.1f}万回"
        else:
            return f"{view_count:,}回"

    def format_subscriber_count(self, subscriber_count):
        """登録者数を読みやすい形式にフォーマット
        
        Args:
            subscriber_count (int): 登録者数
        
        Returns:
            str: フォーマット済み文字列
        """
        subscriber_count = int(subscriber_count)
        
        if subscriber_count >= 100000000:  # 1億以上
            return f"{subscriber_count / 100000000:.1f}億人"
        elif subscriber_count >= 10000:  # 1万以上
            return f"{subscriber_count / 10000:.1f}万人"
        else:
            return f"{subscriber_count:,}人"

    def search_and_get_details(self, query, max_results=10, include_stats=True):
        """検索して詳細情報も一緒に取得
        
        Args:
            query (str): 検索キーワード
            max_results (int): 最大結果数
            include_stats (bool): 統計情報を含めるか
        
        Returns:
            list: 詳細情報付きの検索結果
        
        例:
            results = yt.search_and_get_details("Python", max_results=5)
            for video in results:
                print(f"{video['title']} - {video['view_count']}回再生")
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

    def get_channel_upload_playlist(self, channel_id):
        """チャンネルのアップロードプレイリストIDを取得
        
        Args:
            channel_id (str): チャンネルID
        
        Returns:
            str: アップロードプレイリストID
        """
        request = self.youtube.channels().list(
            part="contentDetails",
            id=channel_id
        )
        response = self._execute_request(request)
        
        if not response["items"]:
            raise YouTubeAPIError(f"チャンネルが見つかりません: {channel_id}")
        
        uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        return uploads_playlist_id

    def get_latest_videos_from_channel(self, channel_id, max_results=10):
        """チャンネルの最新動画を効率的に取得
        
        Args:
            channel_id (str): チャンネルID
            max_results (int): 最大取得件数
        
        Returns:
            list: 最新動画のリスト
        """
        # アップロードプレイリストから取得（より効率的）
        uploads_playlist_id = self.get_channel_upload_playlist(channel_id)
        return self.get_playlist_videos(uploads_playlist_id, max_results=max_results)

    # ======== 動画分析・比較メソッド ========

    def compare_videos(self, video_ids, metrics=None):
        """複数の動画を比較分析
        
        Args:
            video_ids (list): 動画IDのリスト（最大50件）
            metrics (list): 比較する指標 ['views', 'likes', 'comments', 'duration']
        
        Returns:
            dict: 比較結果とランキング
        
        例:
            comparison = yt.compare_videos(["dQw4w9WgXcQ", "jNQXAC9IVRw"])
            print(f"最も再生された動画: {comparison['rankings']['views'][0]['title']}")
        """
        if not metrics:
            metrics = ['views', 'likes', 'comments', 'duration']
        
        videos = self.bulk_get_video_info(video_ids)
        
        comparison_data = []
        for video in videos:
            stats = video['statistics']
            snippet = video['snippet']
            
            video_data = {
                'id': video['id'],
                'title': snippet['title'],
                'channel': snippet['channelTitle'],
                'published': snippet['publishedAt'],
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0)),
                'duration': self.get_video_duration_seconds(video['id'])
            }
            comparison_data.append(video_data)
        
        # ランキング作成
        rankings = {}
        for metric in metrics:
            if metric == 'views':
                rankings['views'] = sorted(comparison_data, key=lambda x: x['views'], reverse=True)
            elif metric == 'likes':
                rankings['likes'] = sorted(comparison_data, key=lambda x: x['likes'], reverse=True)
            elif metric == 'comments':
                rankings['comments'] = sorted(comparison_data, key=lambda x: x['comments'], reverse=True)
            elif metric == 'duration':
                rankings['duration'] = sorted(comparison_data, key=lambda x: x['duration'], reverse=True)
        
        return {
            'videos': comparison_data,
            'rankings': rankings,
            'summary': {
                'total_views': sum(v['views'] for v in comparison_data),
                'average_likes': sum(v['likes'] for v in comparison_data) / len(comparison_data),
                'most_popular': max(comparison_data, key=lambda x: x['views'])
            }
        }

    def analyze_channel_performance(self, channel_id, days_back=30, max_videos=50):
        """チャンネルのパフォーマンス分析
        
        Args:
            channel_id (str): チャンネルID
            days_back (int): 分析対象期間（日数）
            max_videos (int): 分析する最大動画数
        
        Returns:
            dict: パフォーマンス分析結果
        """
        from datetime import datetime, timedelta
        
        # 指定期間内の動画を取得
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_videos = self.get_latest_videos_from_channel(channel_id, max_videos)
        
        # 動画IDを抽出して詳細情報を取得
        video_ids = [item['snippet']['resourceId']['videoId'] for item in recent_videos]
        detailed_videos = self.bulk_get_video_info(video_ids)
        
        # 期間内の動画のみフィルタリング
        period_videos = []
        for video in detailed_videos:
            pub_date = datetime.fromisoformat(video['snippet']['publishedAt'].replace('Z', '+00:00'))
            if pub_date >= cutoff_date.replace(tzinfo=pub_date.tzinfo):
                period_videos.append(video)
        
        if not period_videos:
            return {'error': f'過去{days_back}日間に投稿された動画が見つかりません'}
        
        # 統計計算
        total_views = sum(int(v['statistics'].get('viewCount', 0)) for v in period_videos)
        total_likes = sum(int(v['statistics'].get('likeCount', 0)) for v in period_videos)
        total_comments = sum(int(v['statistics'].get('commentCount', 0)) for v in period_videos)
        
        avg_views = total_views / len(period_videos)
        avg_likes = total_likes / len(period_videos)
        avg_comments = total_comments / len(period_videos)
        
        # トップパフォーマー
        top_video = max(period_videos, key=lambda x: int(x['statistics'].get('viewCount', 0)))
        
        return {
            'period': f'過去{days_back}日間',
            'video_count': len(period_videos),
            'totals': {
                'views': total_views,
                'likes': total_likes,
                'comments': total_comments
            },
            'averages': {
                'views_per_video': int(avg_views),
                'likes_per_video': int(avg_likes),
                'comments_per_video': int(avg_comments)
            },
            'top_performer': {
                'title': top_video['snippet']['title'],
                'views': int(top_video['statistics'].get('viewCount', 0)),
                'url': f"https://www.youtube.com/watch?v={top_video['id']}"
            },
            'engagement_rate': (total_likes + total_comments) / total_views * 100 if total_views > 0 else 0
        }

    # ======== データエクスポート機能 ========

    def export_search_results_to_csv(self, query, filename=None, max_results=100):
        """検索結果をCSVファイルにエクスポート
        
        Args:
            query (str): 検索キーワード
            filename (str): 出力ファイル名（Noneの場合は自動生成）
            max_results (int): 最大結果数
        
        Returns:
            str: 作成されたファイル名
        """
        import csv
        import os
        from datetime import datetime
        
        if not filename:
            safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"youtube_search_{safe_query}_{timestamp}.csv"
        
        # 検索実行
        results = self.search_and_get_details(query, max_results=max_results)
        
        # CSV出力
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['video_id', 'title', 'channel', 'published_at', 'duration_seconds', 
                         'view_count', 'like_count', 'comment_count', 'description', 'url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for video in results:
                writer.writerow({
                    'video_id': video['id']['videoId'],
                    'title': video['snippet']['title'],
                    'channel': video['snippet']['channelTitle'],
                    'published_at': video['snippet']['publishedAt'],
                    'duration_seconds': self.get_video_duration_seconds(video['id']['videoId']),
                    'view_count': video.get('view_count', 0),
                    'like_count': video.get('like_count', 0),
                    'comment_count': video.get('comment_count', 0),
                    'description': video['snippet']['description'][:500] + "..." if len(video['snippet']['description']) > 500 else video['snippet']['description'],
                    'url': f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                })
        
        return filename

    def export_channel_videos_to_json(self, channel_id, filename=None, max_videos=100):
        """チャンネルの動画情報をJSONファイルにエクスポート
        
        Args:
            channel_id (str): チャンネルID
            filename (str): 出力ファイル名
            max_videos (int): 最大動画数
        
        Returns:
            str: 作成されたファイル名
        """
        import json
        from datetime import datetime
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"channel_{channel_id}_{timestamp}.json"
        
        # チャンネル情報と動画を取得
        channel_info = self.get_channel_info(channel_id)
        videos = self.get_latest_videos_from_channel(channel_id, max_videos)
        
        # 動画の詳細情報を取得
        video_ids = [item['snippet']['resourceId']['videoId'] for item in videos]
        detailed_videos = self.bulk_get_video_info(video_ids)
        
        export_data = {
            'channel': {
                'id': channel_info['id'],
                'title': channel_info['snippet']['title'],
                'description': channel_info['snippet']['description'],
                'subscriber_count': int(channel_info['statistics'].get('subscriberCount', 0)),
                'video_count': int(channel_info['statistics'].get('videoCount', 0)),
                'view_count': int(channel_info['statistics'].get('viewCount', 0))
            },
            'videos': []
        }
        
        for video in detailed_videos:
            video_data = {
                'id': video['id'],
                'title': video['snippet']['title'],
                'description': video['snippet']['description'],
                'published_at': video['snippet']['publishedAt'],
                'duration_seconds': self.get_video_duration_seconds(video['id']),
                'statistics': {
                    'view_count': int(video['statistics'].get('viewCount', 0)),
                    'like_count': int(video['statistics'].get('likeCount', 0)),
                    'comment_count': int(video['statistics'].get('commentCount', 0))
                },
                'url': f"https://www.youtube.com/watch?v={video['id']}"
            }
            export_data['videos'].append(video_data)
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, ensure_ascii=False, indent=2)
        
        return filename

    # ======== 高度な検索・フィルタリング ========

    def search_videos_advanced(self, query, filters=None, sort_by='relevance'):
        """高度な動画検索（複数フィルター対応）
        
        Args:
            query (str): 検索キーワード
            filters (dict): フィルター条件
            sort_by (str): ソート順序
        
        Returns:
            list: フィルター済み検索結果
        
        例:
            filters = {
                'min_duration': 300,  # 5分以上
                'max_duration': 3600,  # 60分以下
                'min_views': 10000,   # 1万回以上再生
                'published_after': '2023-01-01',
                'channel_subscriber_min': 1000  # 登録者1000人以上のチャンネル
            }
            results = yt.search_videos_advanced("Python tutorial", filters=filters)
        """
        from datetime import datetime
        
        if not filters:
            filters = {}
        
        # 基本検索を実行（多めに取得してフィルタリング）
        raw_results = self.search_and_get_details(query, max_results=100)
        
        filtered_results = []
        
        for video in raw_results:
            # 長さフィルター
            duration = self.get_video_duration_seconds(video['id']['videoId'])
            if 'min_duration' in filters and duration < filters['min_duration']:
                continue
            if 'max_duration' in filters and duration > filters['max_duration']:
                continue
            
            # 再生回数フィルター
            views = video.get('view_count', 0)
            if 'min_views' in filters and views < filters['min_views']:
                continue
            if 'max_views' in filters and views > filters['max_views']:
                continue
            
            # いいね数フィルター
            likes = video.get('like_count', 0)
            if 'min_likes' in filters and likes < filters['min_likes']:
                continue
            
            # 投稿日フィルター
            if 'published_after' in filters:
                pub_date = datetime.fromisoformat(video['snippet']['publishedAt'].replace('Z', '+00:00'))
                filter_date = datetime.fromisoformat(filters['published_after']).replace(tzinfo=pub_date.tzinfo)
                if pub_date < filter_date:
                    continue
            
            # チャンネル登録者数フィルター
            if 'channel_subscriber_min' in filters:
                try:
                    channel_info = self.get_channel_info(video['snippet']['channelId'])
                    subscriber_count = int(channel_info['statistics'].get('subscriberCount', 0))
                    if subscriber_count < filters['channel_subscriber_min']:
                        continue
                except:
                    continue  # チャンネル情報取得失敗時はスキップ
            
            # 動画の長さを追加
            video['duration_seconds'] = duration
            video['duration_formatted'] = f"{duration//60}:{duration%60:02d}"
            
            filtered_results.append(video)
        
        # ソート
        if sort_by == 'views':
            filtered_results.sort(key=lambda x: x.get('view_count', 0), reverse=True)
        elif sort_by == 'likes':
            filtered_results.sort(key=lambda x: x.get('like_count', 0), reverse=True)
        elif sort_by == 'duration':
            filtered_results.sort(key=lambda x: x['duration_seconds'], reverse=True)
        elif sort_by == 'recent':
            filtered_results.sort(key=lambda x: x['snippet']['publishedAt'], reverse=True)
        
        return filtered_results

    # ======== バッチ処理・一括操作 ========

    def batch_analyze_channels(self, channel_ids, metrics=['subscribers', 'videos', 'views']):
        """複数チャンネルの一括分析
        
        Args:
            channel_ids (list): チャンネルIDのリスト
            metrics (list): 分析する指標
        
        Returns:
            dict: 分析結果とランキング
        """
        channels_data = self.bulk_get_channel_info(channel_ids)
        
        analysis = {
            'channels': [],
            'rankings': {},
            'summary': {}
        }
        
        for channel in channels_data:
            channel_analysis = {
                'id': channel['id'],
                'title': channel['snippet']['title'],
                'description': channel['snippet']['description'][:200] + "...",
                'subscribers': int(channel['statistics'].get('subscriberCount', 0)),
                'video_count': int(channel['statistics'].get('videoCount', 0)),
                'total_views': int(channel['statistics'].get('viewCount', 0)),
                'created_at': channel['snippet']['publishedAt']
            }
            analysis['channels'].append(channel_analysis)
        
        # ランキング作成
        if 'subscribers' in metrics:
            analysis['rankings']['subscribers'] = sorted(
                analysis['channels'], 
                key=lambda x: x['subscribers'], 
                reverse=True
            )
        
        if 'videos' in metrics:
            analysis['rankings']['videos'] = sorted(
                analysis['channels'], 
                key=lambda x: x['video_count'], 
                reverse=True
            )
        
        if 'views' in metrics:
            analysis['rankings']['views'] = sorted(
                analysis['channels'], 
                key=lambda x: x['total_views'], 
                reverse=True
            )
        
        # サマリー統計
        analysis['summary'] = {
            'total_channels': len(analysis['channels']),
            'total_subscribers': sum(c['subscribers'] for c in analysis['channels']),
            'total_videos': sum(c['video_count'] for c in analysis['channels']),
            'average_subscribers': sum(c['subscribers'] for c in analysis['channels']) / len(analysis['channels']),
            'top_channel': max(analysis['channels'], key=lambda x: x['subscribers'])
        }
        
        return analysis

    # ======== 通知・監視機能 ========

    def monitor_channel_for_new_videos(self, channel_id, last_video_id=None):
        """チャンネルの新しい動画をチェック
        
        Args:
            channel_id (str): 監視するチャンネルID
            last_video_id (str): 前回チェック時の最新動画ID
        
        Returns:
            dict: 新しい動画の情報
        """
        latest_videos = self.get_latest_videos_from_channel(channel_id, max_results=10)
        
        if not latest_videos:
            return {'new_videos': [], 'latest_video_id': None}
        
        current_latest_id = latest_videos[0]['snippet']['resourceId']['videoId']
        
        if not last_video_id or last_video_id == current_latest_id:
            return {'new_videos': [], 'latest_video_id': current_latest_id}
        
        # 新しい動画を特定
        new_videos = []
        for video in latest_videos:
            video_id = video['snippet']['resourceId']['videoId']
            if video_id == last_video_id:
                break
            new_videos.append(video)
        
        # 新しい動画の詳細情報を取得
        if new_videos:
            video_ids = [v['snippet']['resourceId']['videoId'] for v in new_videos]
            detailed_videos = self.bulk_get_video_info(video_ids)
            
            enhanced_videos = []
            for detail in detailed_videos:
                enhanced_videos.append({
                    'id': detail['id'],
                    'title': detail['snippet']['title'],
                    'published_at': detail['snippet']['publishedAt'],
                    'url': f"https://www.youtube.com/watch?v={detail['id']}",
                    'statistics': detail['statistics']
                })
        else:
            enhanced_videos = []
        
        return {
            'new_videos': enhanced_videos,
            'latest_video_id': current_latest_id,
            'count': len(enhanced_videos)
        }

    # ======== ユーティリティ機能 ========

    def generate_video_summary(self, video_id):
        """動画の包括的なサマリーを生成
        
        Args:
            video_id (str): 動画ID
        
        Returns:
            dict: 動画の包括的な情報
        """
        video = self.get_video_info(video_id)
        duration = self.get_video_duration_seconds(video_id)
        
        # エンゲージメント率計算
        views = int(video['statistics'].get('viewCount', 0))
        likes = int(video['statistics'].get('likeCount', 0))
        comments = int(video['statistics'].get('commentCount', 0))
        
        engagement_rate = ((likes + comments) / views * 100) if views > 0 else 0
        
        summary = {
            'basic_info': {
                'title': video['snippet']['title'],
                'channel': video['snippet']['channelTitle'],
                'published': video['snippet']['publishedAt'],
                'duration': f"{duration//60}:{duration%60:02d}",
                'duration_seconds': duration,
                'url': f"https://www.youtube.com/watch?v={video_id}"
            },
            'performance': {
                'views': views,
                'views_formatted': self.format_view_count(views),
                'likes': likes,
                'comments': comments,
                'engagement_rate': round(engagement_rate, 2)
            },
            'content': {
                'description_length': len(video['snippet']['description']),
                'description_preview': video['snippet']['description'][:200] + "..." if len(video['snippet']['description']) > 200 else video['snippet']['description'],
                'tags': video['snippet'].get('tags', []),
                'category_id': video['snippet'].get('categoryId')
            },
            'analysis': {
                'performance_score': self._calculate_performance_score(views, likes, comments, duration),
                'content_type': self._classify_video_length(duration),
                'engagement_level': self._classify_engagement(engagement_rate)
            }
        }
        
        return summary

    def _calculate_performance_score(self, views, likes, comments, duration):
        """動画のパフォーマンススコアを計算（0-100）"""
        # 簡単なスコア計算（実際にはもっと複雑な指標を使用可能）
        view_score = min(views / 100000 * 30, 30)  # 最大30点
        engagement_score = min((likes + comments) / views * 1000 * 40, 40) if views > 0 else 0  # 最大40点
        duration_score = 30 if 180 <= duration <= 600 else 15  # 3-10分で最大30点
        
        return min(view_score + engagement_score + duration_score, 100)

    def _classify_video_length(self, duration):
        """動画の長さで分類"""
        if duration < 60:
            return "ショート（60秒未満）"
        elif duration < 300:
            return "短編（5分未満）"
        elif duration < 1200:
            return "中編（20分未満）"
        else:
            return "長編（20分以上）"

    def _classify_engagement(self, engagement_rate):
        """エンゲージメント率で分類"""
        if engagement_rate >= 10:
            return "非常に高い"
        elif engagement_rate >= 5:
            return "高い"
        elif engagement_rate >= 2:
            return "普通"
        elif engagement_rate >= 1:
            return "低い"
        else:
            return "非常に低い"

    # ======== OAuth管理メソッド ========

    def setup_oauth_interactive(self, client_secrets_file, scopes=None, token_file=None):
        """対話的にOAuth認証をセットアップ
        
        Args:
            client_secrets_file (str): クライアントシークレットファイルのパス
            scopes (list): 必要なスコープ（デフォルト: ['readonly']）
            token_file (str): トークン保存ファイル（デフォルト: 'youtube_token.pickle'）
        
        Returns:
            bool: セットアップ成功フラグ
        
        例:
            yt = YouTubeAPI(api_key="YOUR_API_KEY")
            success = yt.setup_oauth_interactive(
                'client_secrets.json',
                scopes=['full'],
                token_file='my_token.pickle'
            )
        """
        if not scopes:
            scopes = ['readonly']
        
        if not token_file:
            token_file = 'youtube_token.pickle'
        
        try:
            resolved_scopes = self._resolve_scopes(scopes)
            
            # OAuth設定を更新
            self._oauth_config = {
                'client_secrets_file': client_secrets_file,
                'scopes': scopes,
                'token_file': token_file,
                'port': 8080,
                'auto_open_browser': True
            }
            
            # 認証実行
            self._oauth_credentials = self._setup_oauth_credentials()
            self._has_oauth = True
            
            # YouTubeクライアントを再構築
            self.youtube = build("youtube", "v3", credentials=self._oauth_credentials)
            
            return True
            
        except Exception as e:
            raise YouTubeAPIError(f"OAuth設定に失敗しました: {str(e)}")

    def get_oauth_authorization_url(self, client_secrets_file, scopes=None, state=None):
        """OAuth認証URLを取得（手動認証用）
        
        Args:
            client_secrets_file (str): クライアントシークレットファイル
            scopes (list): 必要なスコープ
            state (str): 状態パラメータ
        
        Returns:
            tuple: (認証URL, flowオブジェクト)
        
        例:
            auth_url, flow = yt.get_oauth_authorization_url('client_secrets.json', ['full'])
            print(f"このURLにアクセスしてください: {auth_url}")
        """
        if not scopes:
            scopes = ['readonly']
        
        resolved_scopes = self._resolve_scopes(scopes)
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, resolved_scopes)
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'  # アウトオブバンド
            
            auth_url, _ = flow.authorization_url(
                prompt='consent',
                state=state
            )
            
            return auth_url, flow
            
        except Exception as e:
            raise YouTubeAPIError(f"認証URL生成に失敗しました: {str(e)}")

    def complete_oauth_flow(self, flow, authorization_code, token_file=None):
        """OAuth認証フローを完了（手動認証用）
        
        Args:
            flow: get_oauth_authorization_urlで取得したflowオブジェクト
            authorization_code (str): ブラウザで取得した認証コード
            token_file (str): トークン保存ファイル
        
        Returns:
            bool: 認証完了フラグ
        
        例:
            auth_url, flow = yt.get_oauth_authorization_url('client_secrets.json')
            # ユーザーがブラウザで認証後、認証コードを取得
            code = input("認証コードを入力してください: ")
            yt.complete_oauth_flow(flow, code, 'my_token.pickle')
        """
        try:
            flow.fetch_token(code=authorization_code)
            credentials = flow.credentials
            
            # 認証情報を設定
            self._oauth_credentials = credentials
            self._has_oauth = True
            
            # YouTubeクライアントを再構築
            self.youtube = build("youtube", "v3", credentials=credentials)
            
            # トークンを保存
            if token_file:
                with open(token_file, 'wb') as token:
                    pickle.dump(credentials, token)
            
            return True
            
        except Exception as e:
            raise YouTubeAPIError(f"OAuth認証完了に失敗しました: {str(e)}")

    def refresh_oauth_token(self, token_file=None):
        """OAuth認証トークンをリフレッシュ
        
        Args:
            token_file (str): トークンファイル
        
        Returns:
            bool: リフレッシュ成功フラグ
        """
        if not self._has_oauth:
            raise YouTubeAPIError("OAuth認証が設定されていません")
        
        try:
            if self._oauth_credentials and self._oauth_credentials.refresh_token:
                self._oauth_credentials.refresh(Request())
                
                # トークンを保存
                if token_file or self._oauth_config.get('token_file'):
                    save_file = token_file or self._oauth_config['token_file']
                    with open(save_file, 'wb') as token:
                        pickle.dump(self._oauth_credentials, token)
                
                return True
            else:
                raise YouTubeAPIError("リフレッシュトークンが利用できません")
                
        except Exception as e:
            raise YouTubeAPIError(f"トークンリフレッシュに失敗しました: {str(e)}")

    def revoke_oauth_token(self, token_file=None):
        """OAuth認証トークンを無効化
        
        Args:
            token_file (str): 削除するトークンファイル
        
        Returns:
            bool: 無効化成功フラグ
        """
        if not self._has_oauth:
            return True
        
        try:
            # トークンを無効化
            if self._oauth_credentials:
                import requests
                requests.post(
                    'https://oauth2.googleapis.com/revoke',
                    params={'token': self._oauth_credentials.token},
                    headers={'content-type': 'application/x-www-form-urlencoded'}
                )
            
            # ローカルトークンファイルを削除
            if token_file or self._oauth_config.get('token_file'):
                file_to_delete = token_file or self._oauth_config['token_file']
                if os.path.exists(file_to_delete):
                    os.remove(file_to_delete)
            
            # OAuth設定をクリア
            self._oauth_credentials = None
            self._has_oauth = False
            
            # APIキーのみでクライアントを再構築
            if self._api_key:
                self.youtube = build("youtube", "v3", developerKey=self._api_key)
            
            return True
            
        except Exception as e:
            raise YouTubeAPIError(f"トークン無効化に失敗しました: {str(e)}")

    def get_oauth_info(self):
        """現在のOAuth認証情報を取得
        
        Returns:
            dict: OAuth認証情報
        """
        if not self._has_oauth:
            return {
                'authenticated': False,
                'scopes': [],
                'expires_at': None,
                'token_valid': False
            }
        
        return {
            'authenticated': True,
            'scopes': getattr(self._oauth_credentials, 'scopes', []),
            'expires_at': getattr(self._oauth_credentials, 'expiry', None),
            'token_valid': self._oauth_credentials.valid if self._oauth_credentials else False,
            'has_refresh_token': bool(getattr(self._oauth_credentials, 'refresh_token', None))
        }

    def check_oauth_scopes(self, required_scopes):
        """必要なスコープが許可されているかチェック
        
        Args:
            required_scopes (list): 必要なスコープリスト
        
        Returns:
            dict: スコープチェック結果
        """
        if not self._has_oauth:
            return {
                'has_all_scopes': False,
                'missing_scopes': required_scopes,
                'current_scopes': []
            }
        
        current_scopes = getattr(self._oauth_credentials, 'scopes', [])
        resolved_required = self._resolve_scopes(required_scopes)
        
        missing_scopes = [scope for scope in resolved_required if scope not in current_scopes]
        
        return {
            'has_all_scopes': len(missing_scopes) == 0,
            'missing_scopes': missing_scopes,
            'current_scopes': current_scopes
        }

    @classmethod
    def create_oauth_config_template(cls, output_file='oauth_config.json'):
        """OAuth設定テンプレートファイルを作成
        
        Args:
            output_file (str): 出力ファイル名
        
        Returns:
            str: 作成されたファイル名
        """
        import json
        
        template = {
            "client_secrets_file": "client_secrets.json",
            "scopes": ["readonly"],
            "token_file": "youtube_token.pickle",
            "port": 8080,
            "auto_open_browser": True,
            "_comment": {
                "scopes": "利用可能: readonly, upload, full, force_ssl",
                "client_secrets_file": "Google Cloud Consoleでダウンロードしたファイル",
                "token_file": "認証トークンの保存先",
                "port": "ローカルサーバーのポート番号",
                "auto_open_browser": "認証時にブラウザを自動で開くか"
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        return output_file

    # OAuth認証が必要なメソッドに認証チェックを追加
    def get_my_channel(self):
        """自分のチャンネル情報を取得（OAuth認証が必要）"""
        self._require_oauth("自分のチャンネル情報取得")
        
        request = self.youtube.channels().list(
            part="snippet,statistics",
            mine=True
        )
        response = self._execute_request(request)
        
        if not response["items"]:
            raise YouTubeAPIError("チャンネルが見つかりません")
        
        return response["items"][0]

    def upload_video(self, title, description, tags=None, category_id="22", privacy_status="private", video_file=None):
        """動画をアップロード（OAuth認証が必要）"""
        self._require_oauth("動画アップロード")
        
        # 必要なスコープをチェック
        scope_check = self.check_oauth_scopes(['upload'])
        if not scope_check['has_all_scopes']:
            raise YouTubeAPIError(
                f"動画アップロードには追加のスコープが必要です: {scope_check['missing_scopes']}"
            )
        
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
        except Exception as e:
            raise YouTubeAPIError(f"動画アップロードに失敗しました: {str(e)}")

    def create_playlist(self, title, description="", privacy_status="private"):
        """プレイリストを作成（OAuth認証が必要）"""
        self._require_oauth("プレイリスト作成")
        
        try:
            body = {
                "snippet": {"title": title, "description": description},
                "status": {"privacyStatus": privacy_status},
            }

            request = self.youtube.playlists().insert(part="snippet,status", body=body)
            response = request.execute()
            return response
        except Exception as e:
            raise YouTubeAPIError(f"プレイリスト作成に失敗しました: {str(e)}")

    def subscribe_to_channel(self, channel_id):
        """チャンネルをサブスクライブ（OAuth認証が必要）"""
        self._require_oauth("チャンネルサブスクライブ")
        
        try:
            body = {
                "snippet": {
                    "resourceId": {"kind": "youtube#channel", "channelId": channel_id}
                }
            }

            request = self.youtube.subscriptions().insert(part="snippet", body=body)
            response = request.execute()
            return response
        except Exception as e:
            raise YouTubeAPIError(f"サブスクライブに失敗しました: {str(e)}")

    def get_my_subscriptions(self, max_results=50):
        """自分のサブスクリプション一覧を取得（OAuth認証が必要）
        
        Args:
            max_results (int): 最大取得件数
        
        Returns:
            list: サブスクリプション一覧
        """
        self._require_oauth("サブスクリプション一覧取得")
        
        subscriptions = []
        next_page_token = None
        
        while len(subscriptions) < max_results:
            params = {
                'part': 'snippet',
                'mine': True,
                'maxResults': min(50, max_results - len(subscriptions))
            }
            
            if next_page_token:
                params['pageToken'] = next_page_token
            
            request = self.youtube.subscriptions().list(**params)
            response = self._execute_request(request)
            
            subscriptions.extend(response['items'])
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        
        return subscriptions[:max_results]

    def get_my_playlists(self, max_results=50):
        """自分のプレイリスト一覧を取得（OAuth認証が必要）
        
        Args:
            max_results (int): 最大取得件数
        
        Returns:
            list: プレイリスト一覧
        """
        self._require_oauth("プレイリスト一覧取得")
        
        playlists = []
        next_page_token = None
        
        while len(playlists) < max_results:
            params = {
                'part': 'snippet,status',
                'mine': True,
                'maxResults': min(50, max_results - len(playlists))
            }
            
            if next_page_token:
                params['pageToken'] = next_page_token
            
            request = self.youtube.playlists().list(**params)
            response = self._execute_request(request)
            
            playlists.extend(response['items'])
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        
        return playlists[:max_results]

    def get_my_videos(self, max_results=50):
        """自分がアップロードした動画一覧を取得（OAuth認証が必要）
        
        Args:
            max_results (int): 最大取得件数
        
        Returns:
            list: 動画一覧
        """
        self._require_oauth("アップロード動画一覧取得")
        
        # 自分のチャンネルのアップロードプレイリストIDを取得
        my_channel = self.get_my_channel()
        channel_id = my_channel['id']
        uploads_playlist_id = self.get_channel_upload_playlist(channel_id)
        
        # プレイリストから動画を取得
        return self.get_playlist_videos(uploads_playlist_id, max_results=max_results)

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

    def get_total_comments_excluding_channels(self, video_id, exclude_channels=None, max_comments=1000):
        """指定したチャンネルを除いた動画の総コメント数を取得"""
        if exclude_channels is None:
            exclude_channels = []
        
        try:
            # 動画のコメントを取得
            all_comments = self.get_all_comments(video_id, max_results=max_comments)
            
            if not all_comments:
                return {
                    'total_comments': 0,
                    'excluded_comments': 0,
                    'original_total': 0,
                    'exclude_channels': [],
                    'filtered_comments': []
                }
            
            # 除外チャンネルの情報を正規化
            exclude_channel_ids = set()
            exclude_channel_names = set()
            
            for channel in exclude_channels:
                if len(channel) == 24 and channel.startswith('UC'):
                    exclude_channel_ids.add(channel)
                else:
                    exclude_channel_names.add(channel.lower())
            
            # コメントをフィルタリング
            filtered_comments = []
            excluded_count = 0
            exclude_info = []
            
            for comment in all_comments:
                comment_snippet = comment['snippet']['topLevelComment']['snippet']
                author_channel_id = comment_snippet.get('authorChannelId', {}).get('value', '')
                author_name = comment_snippet.get('authorDisplayName', '')
                
                # 除外対象かチェック
                should_exclude = False
                exclude_reason = None
                
                if author_channel_id and author_channel_id in exclude_channel_ids:
                    should_exclude = True
                    exclude_reason = f"チャンネルID: {author_channel_id}"
                elif author_name.lower() in exclude_channel_names:
                    should_exclude = True
                    exclude_reason = f"チャンネル名: {author_name}"
                
                if should_exclude:
                    excluded_count += 1
                    exclude_info.append({
                        'channel_id': author_channel_id,
                        'channel_name': author_name,
                        'reason': exclude_reason,
                        'comment_id': comment['id']
                    })
                else:
                    filtered_comments.append(comment)
            
            # 除外されたチャンネルの統計
            excluded_channels_summary = {}
            for info in exclude_info:
                channel_key = info['channel_id'] if info['channel_id'] else info['channel_name']
                if channel_key not in excluded_channels_summary:
                    excluded_channels_summary[channel_key] = {
                        'channel_id': info['channel_id'],
                        'channel_name': info['channel_name'],
                        'excluded_count': 0
                    }
                excluded_channels_summary[channel_key]['excluded_count'] += 1
            
            return {
                'total_comments': len(filtered_comments),
                'excluded_comments': excluded_count,
                'original_total': len(all_comments),
                'exclude_channels': list(excluded_channels_summary.values()),
                'filtered_comments': filtered_comments,
                'filter_summary': {
                    'exclusion_rate': (excluded_count / len(all_comments) * 100) if all_comments else 0,
                    'most_excluded_channel': max(excluded_channels_summary.values(), 
                                               key=lambda x: x['excluded_count']) if excluded_channels_summary else None
                }
            }
            
        except YouTubeAPIError:
            raise
        except Exception as e:
            raise YouTubeAPIError(f"コメント集計処理でエラーが発生しました: {str(e)}")

    def get_comments_statistics_by_channel(self, video_id, max_comments=1000):
        """動画のコメントをチャンネル別に統計"""
        try:
            all_comments = self.get_all_comments(video_id, max_results=max_comments)
            
            if not all_comments:
                return {
                    'total_comments': 0,
                    'channel_stats': [],
                    'top_commenters': [],
                    'unique_channels': 0
                }
            
            # チャンネル別統計を集計
            channel_stats = {}
            
            for comment in all_comments:
                comment_snippet = comment['snippet']['topLevelComment']['snippet']
                author_channel_id = comment_snippet.get('authorChannelId', {}).get('value', 'unknown')
                author_name = comment_snippet.get('authorDisplayName', 'Unknown')
                
                channel_key = author_channel_id if author_channel_id != 'unknown' else author_name
                
                if channel_key not in channel_stats:
                    channel_stats[channel_key] = {
                        'channel_id': author_channel_id if author_channel_id != 'unknown' else None,
                        'channel_name': author_name,
                        'comment_count': 0,
                        'total_likes': 0,
                        'comments': []
                    }
                
                comment_likes = int(comment_snippet.get('likeCount', 0))
                channel_stats[channel_key]['comment_count'] += 1
                channel_stats[channel_key]['total_likes'] += comment_likes
                channel_stats[channel_key]['comments'].append({
                    'comment_id': comment['id'],
                    'text': comment_snippet['textDisplay'][:100] + "..." if len(comment_snippet['textDisplay']) > 100 else comment_snippet['textDisplay'],
                    'likes': comment_likes,
                    'published_at': comment_snippet['publishedAt']
                })
            
            # 統計をリストに変換してソート
            stats_list = list(channel_stats.values())
            stats_list.sort(key=lambda x: x['comment_count'], reverse=True)
            
            # 上位コメント投稿者（コメント数でソート）
            top_commenters = stats_list[:10]
            
            return {
                'total_comments': len(all_comments),
                'channel_stats': stats_list,
                'top_commenters': top_commenters,
                'unique_channels': len(channel_stats),
                'analysis': {
                    'average_comments_per_channel': len(all_comments) / len(channel_stats) if channel_stats else 0,
                    'most_active_commenter': stats_list[0] if stats_list else None,
                    'single_comment_channels': len([c for c in stats_list if c['comment_count'] == 1])
                }
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"コメント統計処理でエラーが発生しました: {str(e)}")

    def filter_comments_by_criteria(self, video_id, filters=None, max_comments=1000):
        """複数条件でコメントをフィルタリング"""
        from datetime import datetime
        
        if filters is None:
            filters = {}
        
        try:
            all_comments = self.get_all_comments(video_id, max_results=max_comments)
            
            if not all_comments:
                return {
                    'filtered_comments': [],
                    'total_filtered': 0,
                    'original_total': 0,
                    'filter_stats': {}
                }
            
            filtered_comments = []
            filter_stats = {
                'excluded_by_channel': 0,
                'excluded_by_likes': 0,
                'excluded_by_keywords': 0,
                'excluded_by_date': 0
            }
            
            # フィルター条件を準備
            exclude_channels = set(filters.get('exclude_channels', []))
            min_likes = filters.get('min_likes', 0)
            max_likes = filters.get('max_likes', float('inf'))
            include_keywords = [kw.lower() for kw in filters.get('keywords_include', [])]
            exclude_keywords = [kw.lower() for kw in filters.get('keywords_exclude', [])]
            
            date_after = None
            date_before = None
            if filters.get('date_after'):
                date_after = datetime.fromisoformat(filters['date_after'])
            if filters.get('date_before'):
                date_before = datetime.fromisoformat(filters['date_before'])
            
            for comment in all_comments:
                comment_snippet = comment['snippet']['topLevelComment']['snippet']
                should_include = True
                
                # チャンネル除外チェック
                author_channel_id = comment_snippet.get('authorChannelId', {}).get('value', '')
                author_name = comment_snippet.get('authorDisplayName', '')
                
                if (author_channel_id in exclude_channels or 
                    author_name in exclude_channels):
                    should_include = False
                    filter_stats['excluded_by_channel'] += 1
                    continue
                
                # いいね数チェック
                likes = int(comment_snippet.get('likeCount', 0))
                if likes < min_likes or likes > max_likes:
                    should_include = False
                    filter_stats['excluded_by_likes'] += 1
                    continue
                
                # キーワードチェック
                comment_text = comment_snippet['textDisplay'].lower()
                
                # 含むべきキーワードチェック
                if include_keywords and not any(kw in comment_text for kw in include_keywords):
                    should_include = False
                    filter_stats['excluded_by_keywords'] += 1
                    continue
                
                # 除外キーワードチェック
                if exclude_keywords and any(kw in comment_text for kw in exclude_keywords):
                    should_include = False
                    filter_stats['excluded_by_keywords'] += 1
                    continue
                
                # 日付チェック
                comment_date = datetime.fromisoformat(comment_snippet['publishedAt'].replace('Z', '+00:00'))
                
                if date_after and comment_date < date_after.replace(tzinfo=comment_date.tzinfo):
                    should_include = False
                    filter_stats['excluded_by_date'] += 1
                    continue
                
                if date_before and comment_date > date_before.replace(tzinfo=comment_date.tzinfo):
                    should_include = False
                    filter_stats['excluded_by_date'] += 1
                    continue
                
                if should_include:
                    filtered_comments.append(comment)
            
            return {
                'filtered_comments': filtered_comments,
                'total_filtered': len(filtered_comments),
                'original_total': len(all_comments),
                'filter_stats': filter_stats,
                'filtering_summary': {
                    'retention_rate': (len(filtered_comments) / len(all_comments) * 100) if all_comments else 0,
                    'total_excluded': sum(filter_stats.values()),
                    'applied_filters': list(filters.keys())
                }
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"コメントフィルタリング処理でエラーが発生しました: {str(e)}")
