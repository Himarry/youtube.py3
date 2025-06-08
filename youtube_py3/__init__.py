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
from typing import Optional, Dict, Any, List

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

# 新機能モジュール
from .realtime import RealtimeMixin
from .advanced_analytics import AdvancedAnalyticsMixin
from .automation import AutomationMixin
from .media_processing import MediaProcessingMixin
from .integration import IntegrationMixin

# バージョン情報
__version__ = "4.2.0"
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
    
    # === 新機能Mixin（v5.0.0で追加） ===
    'RealtimeMixin',
    'AdvancedAnalyticsMixin', 
    'AutomationMixin',
    'MediaProcessingMixin',
    'IntegrationMixin',
    
    # === 新機能便利関数 ===
    'setup_realtime_monitoring',
    'create_automated_workflow',
    'process_video_content',
    'sync_to_social_media',
    'generate_trend_report',
    
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

# ===============================
# 新機能の便利な関数（v5.0.0で追加）
# ===============================

def setup_realtime_monitoring(channel_id: str, events: list = None, 
                             callback=None, api_key: Optional[str] = None):
    """リアルタイム監視を簡単にセットアップ
    
    Args:
        channel_id (str): 監視するチャンネルID
        events (list): 監視するイベント（デフォルト: ['new_videos', 'live_chat']）
        callback (callable): イベント発生時のコールバック
        api_key (str, optional): APIキー
        
    Returns:
        dict: 監視設定結果
        
    Example:
        >>> import youtube_py3
        >>> def on_new_video(event_data):
        ...     print(f"新動画: {event_data['title']}")
        >>> youtube_py3.setup_realtime_monitoring("CHANNEL_ID", callback=on_new_video)
    """
    if events is None:
        events = ['new_videos', 'subscriber_changes']
    
    yt = create_client(api_key=api_key)
    return yt.monitor_channel_activity(channel_id, callback=callback)

def create_automated_workflow(workflow_config: Dict[str, Any], 
                            api_key: Optional[str] = None):
    """自動化ワークフローを作成
    
    Args:
        workflow_config (dict): ワークフロー設定
        api_key (str, optional): APIキー
        
    Returns:
        dict: ワークフロー作成結果
        
    Example:
        >>> import youtube_py3
        >>> workflow = {
        ...     'type': 'scheduled_upload',
        ...     'video_path': 'video.mp4',
        ...     'metadata': {'title': 'My Video', 'description': 'Description'},
        ...     'publish_time': '2024-01-01T12:00:00'
        ... }
        >>> youtube_py3.create_automated_workflow(workflow)
    """
    yt = create_client(api_key=api_key)
    
    if workflow_config['type'] == 'scheduled_upload':
        return yt.schedule_video_upload(
            workflow_config['video_path'],
            workflow_config['metadata'], 
            workflow_config['publish_time']
        )
    elif workflow_config['type'] == 'comment_moderation':
        return yt.auto_moderate_comments(
            workflow_config['channel_id'],
            workflow_config['rules']
        )
    else:
        raise YouTubeAPIError(f"未対応のワークフロータイプ: {workflow_config['type']}")

def process_video_content(video_path: str, processing_options: Dict[str, Any], 
                        api_key: Optional[str] = None):
    """動画コンテンツを自動処理
    
    Args:
        video_path (str): 動画ファイルパス
        processing_options (dict): 処理オプション
        api_key (str, optional): APIキー
        
    Returns:
        dict: 処理結果
        
    Example:
        >>> import youtube_py3
        >>> options = {
        ...     'extract_thumbnails': [10, 30, 60],  # 10秒、30秒、60秒地点
        ...     'generate_highlights': 120,  # 2分のハイライト
        ...     'transcribe_audio': 'ja'
        ... }
        >>> results = youtube_py3.process_video_content('video.mp4', options)
    """
    yt = create_client(api_key=api_key)
    results = {}
    
    if 'extract_thumbnails' in processing_options:
        results['thumbnails'] = yt.extract_video_thumbnails(
            video_path, processing_options['extract_thumbnails']
        )
    
    if 'generate_highlights' in processing_options:
        results['highlights'] = yt.generate_video_highlights(
            video_path, processing_options['generate_highlights']
        )
    
    if 'transcribe_audio' in processing_options:
        results['transcription'] = yt.transcribe_video_audio(
            video_path, processing_options['transcribe_audio']
        )
    
    if 'generate_subtitles' in processing_options:
        results['subtitles'] = yt.generate_video_subtitles(
            video_path, processing_options['generate_subtitles']
        )
    
    return results

def sync_to_social_media(video_id: str, platforms: List[str], 
                        api_key: Optional[str] = None):
    """動画を他のSNSプラットフォームに同期
    
    Args:
        video_id (str): YouTube動画ID
        platforms (list): 同期先プラットフォーム
        api_key (str, optional): APIキー
        
    Returns:
        dict: 同期結果
        
    Example:
        >>> import youtube_py3
        >>> youtube_py3.sync_to_social_media("VIDEO_ID", ["twitter", "facebook"])
    """
    yt = create_client(api_key=api_key)
    
    # 動画情報取得
    video_info = yt.get_video_info(video_id)
    content_data = {
        'title': video_info['snippet']['title'],
        'description': video_info['snippet']['description'],
        'url': f"https://www.youtube.com/watch?v={video_id}",
        'thumbnail': video_info['snippet']['thumbnails']['high']['url']
    }
    
    return yt.sync_with_social_media(platforms, video_id, content_data)

def generate_trend_report(category: Optional[str] = None, region: str = 'JP', 
                         api_key: Optional[str] = None):
    """トレンド分析レポートを生成
    
    Args:
        category (str, optional): カテゴリID
        region (str): 地域コード
        api_key (str, optional): APIキー
        
    Returns:
        dict: トレンド分析結果
        
    Example:
        >>> import youtube_py3
        >>> report = youtube_py3.generate_trend_report(category="10", region="JP")
        >>> print(f"平均視聴回数: {report['view_statistics']['average_views']}")
    """
    yt = create_client(api_key=api_key)
    return yt.generate_trending_analysis(category, region)

# ===============================
# 更新された情報表示関数
# ===============================

def info():
    """ライブラリの情報を表示"""
    print(f"""
YouTube.py3 - YouTube Data API v3 Python Wrapper Library
========================================================
Version: {__version__}
Author: {__author__}
License: {__license__}
URL: {__url__}

Description:
{__description__}

🎯 主な機能:
• 基本機能: 動画・チャンネル・プレイリスト管理
• リアルタイム: ライブチャット監視、チャンネル監視
• AI分析: トレンド分析、競合分析、パフォーマンス予測
• 自動化: スケジュール投稿、コメント自動モデレーション
• メディア処理: サムネイル抽出、ハイライト生成、文字起こし
• 統合連携: SNS連携、Google Ads、ストリーミング配信

📊 総メソッド数: 321個
📅 最新バージョン: v{__version__}

Quick Start:
    import youtube_py3
    yt = youtube_py3.create_client(api_key="YOUR_API_KEY")
    
    # 基本検索
    videos = yt.search_videos("Python tutorial", max_results=5)
    
    # リアルタイム監視
    youtube_py3.setup_realtime_monitoring("CHANNEL_ID")
    
    # トレンド分析
    report = youtube_py3.generate_trend_report()
    
    # 動画処理
    results = youtube_py3.process_video_content("video.mp4", {{
        'extract_thumbnails': [10, 30, 60],
        'generate_highlights': 120
    }})

For more information, visit: {__url__}
""")

# ===============================
# バージョン互換性チェック
# ===============================

def check_compatibility():
    """ライブラリの互換性をチェック"""
    import sys
    
    # Python バージョンチェック
    if sys.version_info < (3, 8):
        print("⚠️  警告: Python 3.8以上が推奨されます")
    
    # 必要なパッケージのチェック
    required_packages = [
        'google-api-python-client',
        'google-auth',
        'google-auth-oauthlib',
        'opencv-python',
        'pillow',
        'requests',
        'schedule'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️  不足しているパッケージ: {', '.join(missing_packages)}")
        print("以下のコマンドでインストールしてください:")
        print(f"pip install {' '.join(missing_packages)}")
    else:
        print("✅ すべての依存関係が正常にインストールされています")

# 起動時チェック（開発モード時のみ）
if os.getenv('YOUTUBE_PY3_DEBUG'):
    print(f"YouTube.py3 v{__version__} loaded successfully")
    check_compatibility()
