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

from .base import YouTubeAPIBase
from .info_retrieval import InfoRetrievalMixin
from .search import SearchMixin
from .pagination import PaginationMixin
from .exceptions import YouTubeAPIError
from .comments import CommentsMixin
from .playlists import PlaylistMixin
from .channels import ChannelMixin
from .videos import VideoMixin
from .helpers import HelperMixin
from .sentiment_analysis import SentimentAnalysisMixin
from .monitoring import MonitoringMixin
from .content_optimization import ContentOptimizationMixin
from .data_export import DataExportMixin
from datetime import datetime

class YouTubeAPI(YouTubeAPIBase, InfoRetrievalMixin, SearchMixin, PaginationMixin, 
                 CommentsMixin, PlaylistMixin, ChannelMixin, VideoMixin, HelperMixin):
    """YouTube Data API v3の簡易ラッパークラス（OAuth対応版）

    【このライブラリの目的】
    YouTube Data API v3は非常に複雑で、初心者には使いにくいAPIです。
    このライブラリは以下の問題を解決します：

    1. 複雑なパラメータ設定を簡素化
    2. エラーハンドリングの統一
    3. ページネーション処理の自動化
    4. よく使う機能のワンライナー化
    5. 日本語での分かりやすいメソッド名と説明

    【継承構造】
    このクラスは以下のMixinクラスから機能を継承しています：
    - YouTubeAPIBase: 基本API機能
    - InfoRetrievalMixin: 情報取得機能
    - SearchMixin: 検索機能
    - PaginationMixin: ページネーション機能
    - CommentsMixin: コメント管理機能
    - PlaylistMixin: プレイリスト管理機能
    - ChannelMixin: チャンネル管理機能
    - VideoMixin: 動画管理機能
    - HelperMixin: ヘルパー機能

    【APIキーについて】
    このライブラリを使用するには、各ユーザーが以下の手順でAPIキーを取得してください：

    1. Google Cloud Console（https://console.cloud.google.com/）にアクセス
    2. 新しいプロジェクトを作成（または既存プロジェクトを選択）
    3. YouTube Data API v3を有効化
    4. 認証情報ページでAPIキーを作成
    5. 必要に応じてAPIキーに制限を設定（推奨）

    【OAuth機能について】
    書き込み操作（動画アップロード、プレイリスト作成など）にはOAuth認証が必要です。
    """

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
        super().__init__(api_key, oauth_credentials, oauth_config)

    # ======== 簡略化メソッド（通常のリスト取得版） ========
    # これらのメソッドは paginate_all_results() を使用して
    # 複雑なページネーション処理を自動化し、簡単にデータを取得できます

    def get_channel_playlists(self, channel_id, max_results=50):
        """チャンネルのプレイリスト一覧を取得（簡略版）
        
        PaginationMixin.paginate_all_results() を使用して
        SearchMixin.search_playlists_paginated() の結果を全件取得します。
        
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
        
        PaginationMixin.paginate_all_results() を使用して
        SearchMixin.search_videos_paginated() の結果を全件取得します。
        
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
        
        PaginationMixin.paginate_all_results() を使用して
        SearchMixin.get_channel_videos_paginated() の結果を全件取得します。
        
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
        
        PaginationMixin.paginate_all_results() を使用して
        PlaylistMixin.get_playlist_videos_paginated() の結果を全件取得します。
        
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
        
        PaginationMixin.paginate_all_results() を使用して
        CommentsMixin.get_comments_paginated() の結果を全件取得します。
        
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

    def get_all_my_comments_on_channel(self, channel_id, max_results=500):
        """指定チャンネルの動画で自分のコメントを全て取得（簡略版）
        
        OAuth認証が必要です。指定したチャンネルの動画から、
        認証ユーザー（自分）のコメントのみを取得します。
        
        Args:
            channel_id (str): 対象チャンネルのID
            max_results (int): 最大取得件数
            
        Returns:
            list: 自分のコメント一覧
            
        Example:
            >>> # OAuth設定でクライアント初期化
            >>> oauth_config = {'client_secrets_file': 'client_secrets.json', 'scopes': ['full']}
            >>> yt = YouTubeAPI(api_key="YOUR_API_KEY", oauth_config=oauth_config)
            >>> my_comments = yt.get_all_my_comments_on_channel("UC_CHANNEL_ID")
            >>> for comment in my_comments:
            ...     print(f"動画ID: {comment['video_id']}")
            ...     print(f"コメント: {comment['comment_text']}")
        """
        return self.paginate_all_results(
            self.get_my_comments_on_channel_paginated,
            channel_id,
            max_total_results=max_results
        )

    def get_all_comments_excluding_author(self, video_id, max_results=1000):
        """動画の全コメントを投稿主のコメントを除外して取得（簡略版）
        
        投稿主（動画アップロード者）のコメントを除外して、
        他のユーザーのコメントのみを取得します。
        
        Args:
            video_id (str): 動画ID
            max_results (int): 最大取得件数
            
        Returns:
            list: コメント一覧（投稿主のコメントを除外）
            
        Example:
            >>> yt = YouTubeAPI(api_key="YOUR_API_KEY")
            >>> comments = yt.get_all_comments_excluding_author("VIDEO_ID")
            >>> for comment in comments:
            ...     print(comment['snippet']['topLevelComment']['snippet']['textDisplay'])
        """
        return self.paginate_all_results(
            self.get_comments_excluding_author_paginated,
            video_id,
            max_total_results=max_results
        )

    def get_video_comments(self, video_id, max_results=100, include_replies=True):
        """動画のコメント一覧を取得（便利メソッド）
        
        Args:
            video_id (str): 動画ID
            max_results (int): 最大取得件数
            include_replies (bool): 返信コメントも含めるか
            
        Returns:
            dict: コメント情報と統計
        """
        return CommentsMixin.get_video_comments(self, video_id, max_results, include_replies)

    def search_videos_advanced(self, query="", max_results=50, channel_id=None, 
                              order="relevance", published_after=None):
        """高度な動画検索（便利メソッド）
        
        Args:
            query (str): 検索キーワード
            max_results (int): 最大取得件数
            channel_id (str): 特定チャンネル内で検索
            order (str): ソート順序
            published_after (str): この日時以降の動画のみ
            
        Returns:
            list: 検索結果
        """
        return SearchMixin.search_videos(
            self, query, max_results, channel_id, order, published_after
        )

    def analyze_video(self, video_id):
        """動画の総合分析（統計＋コメント分析）
        
        Args:
            video_id (str): 動画ID
            
        Returns:
            dict: 総合分析結果
        """
        try:
            # 動画情報取得
            video_info = self.get_video_info(video_id)
            
            # コメント分析
            comment_analysis = self.separate_author_comments(video_id, max_results=200)
            
            # 総合分析結果
            analysis = {
                'video_info': video_info,
                'comment_analysis': comment_analysis,
                'summary': {
                    'title': video_info.get('snippet', {}).get('title', 'Unknown'),
                    'channel_title': video_info.get('snippet', {}).get('channelTitle', 'Unknown'),
                    'view_count': video_info.get('statistics', {}).get('viewCount_int', 0),
                    'like_count': video_info.get('statistics', {}).get('likeCount_int', 0),
                    'comment_count': video_info.get('statistics', {}).get('commentCount_int', 0),
                    'engagement_ratio': video_info.get('statistics', {}).get('engagement_ratio', 0),
                    'author_comment_ratio': comment_analysis['statistics']['author_comment_ratio'],
                    'analyzed_comments': comment_analysis['statistics']['total_comments']
                }
            }
            
            return analysis
            
        except Exception as e:
            return {
                'error': f"動画分析に失敗しました: {str(e)}",
                'video_id': video_id
            }

    def get_channel_simple(self, channel_identifier):
        """チャンネル情報を簡単に取得（便利メソッド）
        
        Args:
            channel_identifier (str): チャンネルID、ユーザー名、またはURL
            
        Returns:
            dict: 簡略化されたチャンネル情報
        """
        return self.get_channel_info_simple(channel_identifier)

    def search_videos_filtered(self, query="", max_results=50, **filters):
        """フィルター付き動画検索（便利メソッド）
        
        Args:
            query (str): 検索キーワード
            max_results (int): 最大取得件数
            **filters: 検索フィルター
            
        Returns:
            list: フィルター済み検索結果
        """
        return SearchMixin.search_videos_filtered(self, query, max_results, **filters)

    def get_trending_videos(self, region_code="JP", max_results=50):
        """トレンド動画を取得（便利メソッド）
        
        Args:
            region_code (str): 地域コード
            max_results (int): 最大取得件数
            
        Returns:
            list: トレンド動画リスト
        """
        return SearchMixin.get_trending_videos(self, region_code, max_results=max_results)

    def search_youtube_shorts(self, query="", max_results=50):
        """YouTube Shortsを検索（便利メソッド）
        
        Args:
            query (str): 検索キーワード
            max_results (int): 最大取得件数
            
        Returns:
            list: YouTube Shortsのリスト
        """
        return SearchMixin.search_youtube_shorts(self, query, max_results)

    def get_multiple_video_info_batch(self, video_ids, batch_size=50):
        """複数動画の情報をバッチ処理で効率的に取得
        
        Args:
            video_ids (list): 動画IDのリスト
            batch_size (int): バッチサイズ
            
        Returns:
            list: 動画情報のリスト
        """
        from .utils import YouTubeUtils
        
        all_videos = []
        for batch in YouTubeUtils.batch_process(video_ids, batch_size):
            batch_videos = self.get_multiple_video_info(batch)
            all_videos.extend(batch_videos)
        
        return all_videos

    def export_channel_report(self, channel_id, filename, format="csv"):
        """チャンネルレポートをエクスポート
        
        Args:
            channel_id (str): チャンネルID
            filename (str): 出力ファイル名
            format (str): 出力形式 ("csv", "json")
        """
        from .utils import YouTubeUtils
        from datetime import datetime
        
        # チャンネル情報取得
        channel_info = self.get_channel_simple(channel_id)
        
        # 動画一覧取得
        videos = self.get_all_channel_videos(channel_id, max_results=200)
        
        # レポートデータ作成
        report_data = []
        for video in videos:
            video_data = {
                'video_id': video['id']['videoId'],
                'title': video['snippet']['title'],
                'published_at': video['snippet']['publishedAt'],
                'view_count': video.get('statistics', {}).get('viewCount', 0),
                'like_count': video.get('statistics', {}).get('likeCount', 0),
                'comment_count': video.get('statistics', {}).get('commentCount', 0),
                'duration': video.get('contentDetails', {}).get('duration', ''),
                'engagement_rate': YouTubeUtils.calculate_engagement_rate(
                    video.get('statistics', {})
                )
            }
            report_data.append(video_data)
        
        # エクスポート
        if format == "csv":
            YouTubeUtils.export_to_csv(report_data, filename)
        elif format == "json":
            export_data = {
                'channel_info': channel_info,
                'videos': report_data,
                'generated_at': datetime.now().isoformat()
            }
            YouTubeUtils.export_to_json(export_data, filename)
    
    def analyze_comment_sentiment(self, video_id, max_comments=200):
        """コメント感情分析（便利メソッド）
        
        Args:
            video_id (str): 動画ID
            max_comments (int): 分析するコメント数
            
        Returns:
            dict: 感情分析結果
        """
        return SentimentAnalysisMixin.analyze_comment_sentiment(self, video_id, max_comments)

    def detect_trending_keywords(self, region_code="JP"):
        """トレンドキーワード検出（便利メソッド）
        
        Args:
            region_code (str): 地域コード
            
        Returns:
            dict: トレンドキーワード分析結果
        """
        return MonitoringMixin.detect_trending_keywords(self, region_code)

    def optimize_upload_time(self, channel_id, days=30):
        """最適アップロード時間分析（便利メソッド）
        
        Args:
            channel_id (str): チャンネルID
            days (int): 分析期間
            
        Returns:
            dict: 最適時間分析結果
        """
        return ContentOptimizationMixin.analyze_optimal_upload_time(self, channel_id, days)

    def export_comprehensive_report(self, channel_id, output_dir="reports"):
        """包括的レポートエクスポート（便利メソッド）
        
        Args:
            channel_id (str): チャンネルID
            output_dir (str): 出力ディレクトリ
            
        Returns:
            dict: エクスポート結果
        """
        return DataExportMixin.export_channel_report(
            self, channel_id, output_dir, formats=['csv', 'json', 'html']
        )

    def monitor_new_uploads(self, channel_id, callback=None):
        """新規アップロード監視開始（便利メソッド）
        
        Args:
            channel_id (str): 監視するチャンネルID
            callback (callable): コールバック関数
            
        Returns:
            dict: 監視設定結果
        """
        return MonitoringMixin.monitor_channel_uploads(self, channel_id, callback)

    def create_content_strategy(self, channel_id):
        """コンテンツ戦略提案（統合メソッド）
        
        Args:
            channel_id (str): チャンネルID
            
        Returns:
            dict: 戦略提案結果
        """
        try:
            # 各種分析実行
            performance = self.analyze_channel_performance(channel_id, days=90)
            upload_timing = self.optimize_upload_time(channel_id)
            trending = self.detect_trending_keywords()
            content_ideas = self.generate_content_ideas(channel_id, 
                                                       trending.get('trending_keywords', [])[:5])
            
            # 統合戦略作成
            strategy = {
                'channel_id': channel_id,
                'analysis_date': datetime.now().isoformat(),
                'performance_insights': performance,
                'optimal_timing': upload_timing,
                'trending_opportunities': trending,
                'content_suggestions': content_ideas,
                'strategic_recommendations': self._generate_strategic_recommendations(
                    performance, upload_timing, trending, content_ideas
                )
            }
            
            return strategy
            
        except Exception as e:
            raise YouTubeAPIError(f"コンテンツ戦略作成に失敗しました: {str(e)}")

    def _generate_strategic_recommendations(self, performance, timing, trending, content_ideas):
        """戦略的推奨事項生成"""
        recommendations = []
        
        # パフォーマンス分析から
        growth_rate = performance.get('growth_insights', {}).get('view_growth_rate', 0)
        if growth_rate > 10:
            recommendations.append("成長トレンドが良好です。現在の戦略を継続してください。")
        elif growth_rate < -10:
            recommendations.append("成長が鈍化しています。コンテンツ戦略の見直しが必要です。")
        
        # タイミング分析から
        optimal_hour = timing.get('recommendations', {}).get('optimal_hour')
        if optimal_hour:
            recommendations.append(f"最適投稿時間: {optimal_hour}")
        
        # トレンド分析から
        top_keywords = trending.get('trending_keywords', [])[:3]
        if top_keywords:
            keywords_str = ', '.join([kw[0] for kw in top_keywords])
            recommendations.append(f"注目キーワード: {keywords_str}")
        
        # コンテンツアイデアから
        if content_ideas.get('content_ideas'):
            recommendations.append(f"推奨コンテンツ数: {len(content_ideas['content_ideas'])}件のアイデアを検討してください")
        
        return recommendations
