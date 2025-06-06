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
    """YouTube Data API v3の簡易ラッパークラス

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

    def __init__(self, api_key):
        """YouTube APIクライアントを初期化

        【重要】各ユーザーが個別に取得したAPIキーを使用してください。
        このライブラリ自体はAPIキーを提供しません。

        Args:
            api_key (str): YouTube Data API v3のAPIキー
                         Google Cloud Consoleから個別に取得してください

        Raises:
            YouTubeAPIError: APIキーが空またはAPI初期化に失敗した場合

        例:
            # 環境変数を使用する方法（推奨）
            import os
            api_key = os.getenv('YOUTUBE_API_KEY')
            yt = YouTubeAPI(api_key)

            # 設定ファイルを使用する方法
            import json
            with open('config.json') as f:
                config = json.load(f)
            yt = YouTubeAPI(config['youtube_api_key'])
        """
        if not api_key:
            raise YouTubeAPIError(
                "APIキーが必要です。Google Cloud Consoleで個別に取得してください。\n"
                "詳細: https://developers.google.com/youtube/v3/getting-started"
            )

        try:
            # YouTube Data API v3クライアントを構築
            self.youtube = build("youtube", "v3", developerKey=api_key)
            self._api_key = api_key  # デバッグ用（ログには出力しない）
        except Exception as e:
            raise YouTubeAPIError(
                f"YouTube API の初期化に失敗しました: {str(e)}\n"
                "APIキーが正しいか確認してください。"
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
            raise YouTubeAPIError(f"予期しないエラー: {e}")

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

    def search_videos(self, query, max_results=5, order="relevance"):
        """動画を検索

        指定されたキーワードで動画を検索し、結果を取得します。

        Args:
            query (str): 検索キーワード
            max_results (int): 取得する最大結果数 (デフォルト: 5)
            order (str): ソート順序 (デフォルト: 'relevance')

        Returns:
            list: 検索結果の辞書のリスト

        Raises:
            YouTubeAPIError: 検索に失敗した場合
        """
        request = self.youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=max_results,
            order=order,
        )
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

    def search_videos_paginated(self, query, max_results=None, order="relevance", page_token=None, **filters):
        """動画検索（ページネーション対応）
        
        Args:
            query (str): 検索キーワード
            max_results (int): 最大取得件数（Noneの場合は50件）
            order (str): ソート順序
            page_token (str): ページトークン
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
