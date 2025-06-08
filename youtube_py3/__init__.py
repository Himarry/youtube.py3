"""
YouTube.py3 - YouTube Data API v3 Python Wrapper Library

YouTube Data API v3を簡単に使用するためのPythonラッパーライブラリです。
複雑なAPIの詳細を隠蔽し、初心者でも使いやすいインターフェースを提供します。

主な機能:
- 動画情報の取得
- チャンネル情報の取得  
- プレイリスト管理
- コメント取得・投稿
- 検索機能
- OAuth認証対応
- ページネーション自動処理
- エラーハンドリング

使用例:
    import youtube_py3
    
    # 簡単な使用方法
    yt = youtube_py3.create_client(api_key="YOUR_API_KEY")
    videos = yt.search_videos("Python", max_results=5)
    
    # 高度な使用方法
    from youtube_py3 import YouTubeAPI
    yt = YouTubeAPI(api_key="YOUR_API_KEY")
    channel = yt.get_channel_info("CHANNEL_ID")
"""

import os
import logging
from typing import Optional, Dict, Any

# メインクラスとコンポーネント
from .youtube_py3 import YouTubeAPI
from .exceptions import YouTubeAPIError

# 管理クラス
from .oauth_manager import OAuthManager
from .config_manager import ConfigManager

# ユーティリティ
from .utils import YouTubeUtils

# Mixinクラス（高度なユーザー向け）
from .base import YouTubeAPIBase
from .info_retrieval import InfoRetrievalMixin
from .search import SearchMixin
from .pagination import PaginationMixin
from .comments import CommentsMixin
from .playlists import PlaylistMixin
from .channels import ChannelMixin
from .videos import VideoMixin
from .helpers import HelperMixin

# 新しいMixinクラス（高度なユーザー向け）
from .analytics import AnalyticsMixin
from .monitoring import MonitoringMixin
from .content_optimization import ContentOptimizationMixin
from .sentiment_analysis import SentimentAnalysisMixin
from .data_export import DataExportMixin

# バージョン情報
__version__ = "3.2.0"
__author__ = "Himarry"
__email__ = " "  # 追加
__license__ = "MIT"
__description__ = "YouTube Data API v3の簡単で使いやすいPythonラッパーライブラリ"
__url__ = "https://github.com/chihalu/youtube-py3"

# 公開するクラス・関数
__all__ = [
    # === メインインターフェース ===
    'YouTubeAPI',
    'create_client',
    'quick_search',
    'extract_video_id',
    'extract_channel_id',
    'get_my_comments_on_channel',
    'get_comments_without_author',
    'analyze_channel_performance',
    'monitor_uploads',
    'export_channel_data',
    
    # === 例外クラス ===
    'YouTubeAPIError',
    
    # === 管理クラス ===
    'OAuthManager',
    'ConfigManager',
    
    # === ユーティリティ ===
    'YouTubeUtils',
    
    # === 高度なユーザー向け（Mixin） ===
    'YouTubeAPIBase',
    'InfoRetrievalMixin',
    'SearchMixin', 
    'PaginationMixin',
    'CommentsMixin',
    'PlaylistMixin',
    'ChannelMixin',
    'VideoMixin',
    'HelperMixin',
    'AnalyticsMixin',
    'MonitoringMixin',
    'ContentOptimizationMixin',
    'SentimentAnalysisMixin',
    'DataExportMixin',
    
    # === メタデータ ===
    '__version__',
    '__author__',
    '__email__',
    '__license__',
    '__description__',
    '__url__'
]

# ===============================
# 便利な関数（初心者向け）
# ===============================

def create_client(api_key: Optional[str] = None, 
                 oauth_config: Optional[Dict[str, Any]] = None,
                 auto_setup: bool = True) -> YouTubeAPI:
    """YouTubeAPIクライアントを簡単に作成するヘルパー関数
    
    Args:
        api_key (str, optional): APIキー（環境変数YOUTUBE_API_KEYからも取得可能）
        oauth_config (dict, optional): OAuth設定
        auto_setup (bool): 自動セットアップを行うか
        
    Returns:
        YouTubeAPI: 初期化されたクライアント
        
    Example:
        >>> import youtube_py3
        >>> yt = youtube_py3.create_client(api_key="YOUR_API_KEY")
        >>> videos = yt.search_videos("Python", max_results=5)
        
        >>> # 環境変数から自動取得
        >>> yt = youtube_py3.create_client()  # YOUTUBE_API_KEY環境変数を使用
    """
    # 環境変数からAPIキーを取得
    if api_key is None:
        api_key = os.getenv('YOUTUBE_API_KEY')
        
    if auto_setup and api_key is None and oauth_config is None:
        raise YouTubeAPIError(
            "APIキーまたはOAuth設定が必要です。\n"
            "環境変数 YOUTUBE_API_KEY を設定するか、api_key引数を指定してください。"
        )
    
    return YouTubeAPI(api_key=api_key, oauth_config=oauth_config)

def quick_search(query: str, max_results: int = 10, api_key: Optional[str] = None):
    """動画を素早く検索するワンライナー関数
    
    Args:
        query (str): 検索クエリ
        max_results (int): 取得する結果数（デフォルト: 10）
        api_key (str, optional): APIキー
        
    Returns:
        list: 検索結果のリスト
        
    Example:
        >>> import youtube_py3
        >>> videos = youtube_py3.quick_search("Python tutorial", max_results=5)
        >>> for video in videos:
        ...     print(video['snippet']['title'])
    """
    yt = create_client(api_key=api_key)
    return yt.search_videos(query, max_results=max_results)

def extract_video_id(url: str) -> str:
    """URLから動画IDを抽出するヘルパー関数
    
    Args:
        url (str): YouTube URL
        
    Returns:
        str: 動画ID
        
    Example:
        >>> import youtube_py3
        >>> video_id = youtube_py3.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        >>> print(video_id)  # dQw4w9WgXcQ
    """
    return YouTubeUtils.extract_video_id(url)

def extract_channel_id(url: str) -> str:
    """URLからチャンネルIDを抽出するヘルパー関数
    
    Args:
        url (str): YouTube URL
        
    Returns:
        str: チャンネルID
    """
    return YouTubeUtils.extract_channel_id(url)

def extract_playlist_id(url: str) -> str:
    """URLからプレイリストIDを抽出するヘルパー関数
    
    Args:
        url (str): YouTube URL
        
    Returns:
        str: プレイリストID
    """
    return YouTubeUtils.extract_playlist_id(url)

def get_my_comments_on_channel(channel_id: str, api_key: Optional[str] = None, oauth_config: Optional[Dict[str, Any]] = None):
    """指定チャンネルの動画で自分のコメントを取得するワンライナー関数
    
    Args:
        channel_id (str): 対象チャンネルのID
        api_key (str, optional): APIキー
        oauth_config (dict, optional): OAuth設定（必須）
        
    Returns:
        list: 自分のコメント一覧
        
    Example:
        >>> import youtube_py3
        >>> oauth_config = {'client_secrets_file': 'client_secrets.json', 'scopes': ['full']}
        >>> my_comments = youtube_py3.get_my_comments_on_channel("UC_CHANNEL_ID", oauth_config=oauth_config)
    """
    if oauth_config is None:
        raise YouTubeAPIError("この機能にはOAuth認証が必要です。oauth_configを指定してください。")
    
    yt = create_client(api_key=api_key, oauth_config=oauth_config)
    return yt.get_all_my_comments_on_channel(channel_id)

def get_comments_without_author(video_id: str, api_key: Optional[str] = None):
    """投稿主のコメントを除外して動画のコメントを取得するワンライナー関数
    
    Args:
        video_id (str): 動画ID
        api_key (str, optional): APIキー
        
    Returns:
        list: コメント一覧（投稿主のコメントを除外）
        
    Example:
        >>> import youtube_py3
        >>> comments = youtube_py3.get_comments_without_author("VIDEO_ID")
        >>> for comment in comments:
        ...     print(comment['snippet']['topLevelComment']['snippet']['textDisplay'])
    """
    yt = create_client(api_key=api_key)
    return yt.get_all_comments_excluding_author(video_id)

def analyze_channel_performance(channel_id: str, api_key: Optional[str] = None, days: int = 30):
    """チャンネルパフォーマンス分析のワンライナー関数
    
    Args:
        channel_id (str): チャンネルID
        api_key (str, optional): APIキー
        days (int): 分析期間
        
    Returns:
        dict: パフォーマンス分析結果
    """
    yt = create_client(api_key=api_key)
    return yt.analyze_channel_performance(channel_id, days)

def monitor_uploads(channel_id: str, api_key: Optional[str] = None, callback=None):
    """新規アップロード監視のワンライナー関数
    
    Args:
        channel_id (str): 監視するチャンネルID
        api_key (str, optional): APIキー
        callback (callable): コールバック関数
        
    Returns:
        dict: 監視設定結果
    """
    yt = create_client(api_key=api_key)
    return yt.monitor_new_uploads(channel_id, callback)

def export_channel_data(channel_id: str, output_dir: str = "exports", 
                       api_key: Optional[str] = None, formats=None):
    """チャンネルデータエクスポートのワンライナー関数
    
    Args:
        channel_id (str): チャンネルID
        output_dir (str): 出力ディレクトリ
        api_key (str, optional): APIキー
        formats (list): エクスポート形式
        
    Returns:
        dict: エクスポート結果
    """
    if formats is None:
        formats = ['csv', 'json']
    
    yt = create_client(api_key=api_key)
    return yt.export_comprehensive_report(channel_id, output_dir)

# ===============================
# 設定とロギング
# ===============================

def setup_logging(level: str = "WARNING", 
                 format: Optional[str] = None,
                 file: Optional[str] = None):
    """ライブラリのログ設定を行う
    
    Args:
        level (str): ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        format (str, optional): ログフォーマット
        file (str, optional): ログファイルパス
    """
    logger = logging.getLogger('youtube_py3')
    
    # レベル設定
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    logger.setLevel(numeric_level)
    
    # フォーマット設定
    if format is None:
        format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format)
    
    # ハンドラー設定
    if file:
        handler = logging.FileHandler(file)
    else:
        handler = logging.StreamHandler()
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def get_version() -> str:
    """ライブラリのバージョンを取得
    
    Returns:
        str: バージョン文字列
    """
    return __version__

def info():
    """ライブラリの情報を表示"""
    print(f"""
YouTube.py3 - YouTube Data API v3 Python Wrapper
================================================
Version: {__version__}
Author: {__author__}
License: {__license__}
URL: {__url__}

Description:
{__description__}

Quick Start:
    import youtube_py3
    yt = youtube_py3.create_client(api_key="YOUR_API_KEY")
    videos = yt.search_videos("Python tutorial", max_results=5)
    
For more information, visit: {__url__}
""")

# ===============================
# 初期化時の設定
# ===============================

# デフォルトのログ設定
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.WARNING)

if not _logger.handlers:
    _handler = logging.StreamHandler()
    _formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    _handler.setFormatter(_formatter)
    _logger.addHandler(_handler)

# グローバル設定マネージャー
_config_manager = ConfigManager()

def get_config() -> ConfigManager:
    """グローバル設定マネージャーを取得
    
    Returns:
        ConfigManager: 設定マネージャー
    """
    return _config_manager

# ライブラリ読み込み時のメッセージ（開発時のみ）
if os.getenv('YOUTUBE_PY3_DEBUG'):
    print(f"YouTube.py3 v{__version__} loaded successfully")
