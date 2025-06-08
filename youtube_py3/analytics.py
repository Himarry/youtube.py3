"""
YouTube.py3 - アナリティクス・統計機能

YouTube動画やチャンネルの詳細な分析機能を提供します。
"""

from .base import YouTubeAPIBase
from .exceptions import YouTubeAPIError
from datetime import datetime, timedelta
import statistics
from typing import List, Dict, Any


class AnalyticsMixin(YouTubeAPIBase):
    """アナリティクス・統計機能のMixin"""

    def analyze_channel_performance(self, channel_id, days=30):
        """チャンネルのパフォーマンス分析
        
        Args:
            channel_id (str): チャンネルID
            days (int): 分析期間（日数）
            
        Returns:
            dict: チャンネルパフォーマンス分析結果
        """
        try:
            # 期間設定
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # チャンネル基本情報
            channel_info = self.get_channel_info_simple(channel_id)
            
            # 期間内の動画取得
            videos = self.get_channel_videos_advanced(
                channel_id,
                max_results=200,
                order="date",
                after_date=start_date.strftime("%Y-%m-%d")
            )
            
            # 統計計算
            video_stats = []
            total_views = 0
            total_likes = 0
            total_comments = 0
            
            for video in videos:
                stats = video.get('statistics', {})
                view_count = int(stats.get('viewCount', 0))
                like_count = int(stats.get('likeCount', 0))
                comment_count = int(stats.get('commentCount', 0))
                
                video_stats.append({
                    'video_id': video['id']['videoId'],
                    'title': video['snippet']['title'],
                    'view_count': view_count,
                    'like_count': like_count,
                    'comment_count': comment_count,
                    'engagement_rate': self._calculate_engagement_rate(stats),
                    'published_at': video['snippet']['publishedAt']
                })
                
                total_views += view_count
                total_likes += like_count
                total_comments += comment_count
            
            # パフォーマンス指標
            view_counts = [v['view_count'] for v in video_stats]
            engagement_rates = [v['engagement_rate'] for v in video_stats]
            
            performance_metrics = {
                'total_videos': len(videos),
                'total_views': total_views,
                'total_likes': total_likes,
                'total_comments': total_comments,
                'average_views': statistics.mean(view_counts) if view_counts else 0,
                'median_views': statistics.median(view_counts) if view_counts else 0,
                'max_views': max(view_counts) if view_counts else 0,
                'min_views': min(view_counts) if view_counts else 0,
                'average_engagement_rate': statistics.mean(engagement_rates) if engagement_rates else 0,
                'upload_frequency': len(videos) / days if days > 0 else 0
            }
            
            # トップパフォーマー
            top_videos = sorted(video_stats, key=lambda x: x['view_count'], reverse=True)[:5]
            
            return {
                'channel_info': channel_info,
                'analysis_period': f"{days}日間",
                'performance_metrics': performance_metrics,
                'top_performing_videos': top_videos,
                'all_videos': video_stats,
                'growth_insights': self._calculate_growth_insights(video_stats)
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"チャンネルパフォーマンス分析に失敗しました: {str(e)}")

    def compare_videos_performance(self, video_ids):
        """複数動画のパフォーマンス比較
        
        Args:
            video_ids (list): 比較する動画IDのリスト
            
        Returns:
            dict: 動画パフォーマンス比較結果
        """
        try:
            videos_info = self.get_multiple_video_info(video_ids, include_statistics=True)
            
            comparison_data = []
            for video in videos_info:
                stats = video.get('statistics', {})
                snippet = video.get('snippet', {})
                content_details = video.get('contentDetails', {})
                
                video_data = {
                    'video_id': video['id'],
                    'title': snippet.get('title', ''),
                    'channel_title': snippet.get('channelTitle', ''),
                    'published_at': snippet.get('publishedAt', ''),
                    'duration': content_details.get('duration', ''),
                    'view_count': int(stats.get('viewCount', 0)),
                    'like_count': int(stats.get('likeCount', 0)),
                    'comment_count': int(stats.get('commentCount', 0)),
                    'engagement_rate': self._calculate_engagement_rate(stats)
                }
                comparison_data.append(video_data)
            
            # 比較統計
            view_counts = [v['view_count'] for v in comparison_data]
            engagement_rates = [v['engagement_rate'] for v in comparison_data]
            
            comparison_stats = {
                'total_videos': len(comparison_data),
                'total_views': sum(view_counts),
                'average_views': statistics.mean(view_counts) if view_counts else 0,
                'best_performing': max(comparison_data, key=lambda x: x['view_count']) if comparison_data else None,
                'worst_performing': min(comparison_data, key=lambda x: x['view_count']) if comparison_data else None,
                'highest_engagement': max(comparison_data, key=lambda x: x['engagement_rate']) if comparison_data else None
            }
            
            return {
                'comparison_data': comparison_data,
                'comparison_stats': comparison_stats,
                'recommendations': self._generate_performance_recommendations(comparison_data)
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"動画パフォーマンス比較に失敗しました: {str(e)}")

    def analyze_channel_growth(self, channel_id, months=6):
        """チャンネル成長率分析
        
        Args:
            channel_id (str): チャンネルID
            months (int): 分析期間（月数）
            
        Returns:
            dict: チャンネル成長分析結果
        """
        try:
            # 月別データ収集
            monthly_data = []
            current_date = datetime.now()
            
            for i in range(months):
                month_start = current_date - timedelta(days=30*(i+1))
                month_end = current_date - timedelta(days=30*i)
                
                # その月の動画取得
                videos = self.search_videos_filtered(
                    channel_id=channel_id,
                    max_results=100,
                    published_after=month_start.isoformat(),
                    published_before=month_end.isoformat()
                )
                
                # 月間統計
                month_views = sum(int(v.get('statistics', {}).get('viewCount', 0)) for v in videos)
                month_videos = len(videos)
                
                monthly_data.append({
                    'month': month_start.strftime("%Y-%m"),
                    'video_count': month_videos,
                    'total_views': month_views,
                    'average_views_per_video': month_views / month_videos if month_videos > 0 else 0
                })
            
            # 成長率計算
            growth_metrics = self._calculate_growth_metrics(monthly_data)
            
            return {
                'channel_id': channel_id,
                'analysis_period': f"{months}ヶ月間",
                'monthly_data': monthly_data,
                'growth_metrics': growth_metrics,
                'trends': self._identify_trends(monthly_data)
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"チャンネル成長分析に失敗しました: {str(e)}")

    def detect_viral_videos(self, channel_id, threshold_multiplier=3.0):
        """バイラル動画を検出
        
        Args:
            channel_id (str): チャンネルID
            threshold_multiplier (float): バイラル判定の閾値倍率
            
        Returns:
            dict: バイラル動画検出結果
        """
        try:
            # チャンネルの全動画取得
            videos = self.get_all_channel_videos(channel_id, max_results=500)
            
            # 統計情報付きで詳細取得
            video_ids = [v['id']['videoId'] for v in videos]
            detailed_videos = self.get_multiple_video_info(video_ids)
            
            # 平均視聴回数計算
            view_counts = []
            for video in detailed_videos:
                view_count = int(video.get('statistics', {}).get('viewCount', 0))
                view_counts.append(view_count)
            
            if not view_counts:
                return {'viral_videos': [], 'analysis': 'データが不足しています'}
            
            average_views = statistics.mean(view_counts)
            viral_threshold = average_views * threshold_multiplier
            
            # バイラル動画特定
            viral_videos = []
            for video in detailed_videos:
                view_count = int(video.get('statistics', {}).get('viewCount', 0))
                
                if view_count >= viral_threshold:
                    viral_videos.append({
                        'video_id': video['id'],
                        'title': video['snippet']['title'],
                        'view_count': view_count,
                        'viral_factor': view_count / average_views,
                        'published_at': video['snippet']['publishedAt'],
                        'like_count': int(video.get('statistics', {}).get('likeCount', 0)),
                        'comment_count': int(video.get('statistics', {}).get('commentCount', 0))
                    })
            
            # バイラル度でソート
            viral_videos.sort(key=lambda x: x['viral_factor'], reverse=True)
            
            return {
                'viral_videos': viral_videos,
                'analysis': {
                    'total_videos_analyzed': len(detailed_videos),
                    'viral_videos_count': len(viral_videos),
                    'viral_rate': len(viral_videos) / len(detailed_videos) * 100,
                    'average_views': average_views,
                    'viral_threshold': viral_threshold,
                    'threshold_multiplier': threshold_multiplier
                }
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"バイラル動画検出に失敗しました: {str(e)}")

    def _calculate_engagement_rate(self, statistics):
        """エンゲージメント率計算"""
        try:
            views = int(statistics.get('viewCount', 0))
            likes = int(statistics.get('likeCount', 0))
            comments = int(statistics.get('commentCount', 0))
            
            if views == 0:
                return 0.0
            
            return round((likes + comments) / views * 100, 2)
        except:
            return 0.0

    def _calculate_growth_insights(self, video_stats):
        """成長インサイト計算"""
        if not video_stats:
            return {}
        
        # 時系列順にソート
        sorted_videos = sorted(video_stats, key=lambda x: x['published_at'])
        
        # 直近と過去の比較
        recent_half = sorted_videos[len(sorted_videos)//2:]
        older_half = sorted_videos[:len(sorted_videos)//2]
        
        recent_avg_views = statistics.mean([v['view_count'] for v in recent_half]) if recent_half else 0
        older_avg_views = statistics.mean([v['view_count'] for v in older_half]) if older_half else 0
        
        growth_rate = ((recent_avg_views - older_avg_views) / older_avg_views * 100) if older_avg_views > 0 else 0
        
        return {
            'view_growth_rate': round(growth_rate, 2),
            'trending_direction': 'up' if growth_rate > 5 else 'down' if growth_rate < -5 else 'stable'
        }

    def _calculate_growth_metrics(self, monthly_data):
        """成長指標計算"""
        if len(monthly_data) < 2:
            return {}
        
        # 最新月と前月の比較
        latest = monthly_data[0]
        previous = monthly_data[1]
        
        view_growth = ((latest['total_views'] - previous['total_views']) / previous['total_views'] * 100) if previous['total_views'] > 0 else 0
        video_growth = ((latest['video_count'] - previous['video_count']) / previous['video_count'] * 100) if previous['video_count'] > 0 else 0
        
        return {
            'monthly_view_growth': round(view_growth, 2),
            'monthly_video_growth': round(video_growth, 2),
            'consistency_score': self._calculate_consistency_score(monthly_data)
        }

    def _calculate_consistency_score(self, monthly_data):
        """一貫性スコア計算"""
        if not monthly_data:
            return 0
        
        video_counts = [m['video_count'] for m in monthly_data]
        avg_count = statistics.mean(video_counts)
        
        if avg_count == 0:
            return 0
        
        variance = statistics.variance(video_counts) if len(video_counts) > 1 else 0
        consistency = max(0, 100 - (variance / avg_count * 100))
        
        return round(consistency, 2)

    def _identify_trends(self, monthly_data):
        """トレンド識別"""
        if len(monthly_data) < 3:
            return []
        
        trends = []
        view_data = [m['total_views'] for m in monthly_data]
        
        # 上昇トレンド
        if view_data[0] > view_data[1] > view_data[2]:
            trends.append('views_increasing')
        
        # 下降トレンド
        if view_data[0] < view_data[1] < view_data[2]:
            trends.append('views_decreasing')
        
        return trends

    def _generate_performance_recommendations(self, comparison_data):
        """パフォーマンス推奨事項生成"""
        if not comparison_data:
            return []
        
        recommendations = []
        
        # エンゲージメント率分析
        avg_engagement = statistics.mean([v['engagement_rate'] for v in comparison_data])
        
        if avg_engagement < 2.0:
            recommendations.append("エンゲージメント率が低いです。コメントを促すCTAを追加してください。")
        
        # 動画時間分析
        from .utils import YouTubeUtils
        durations = []
        for video in comparison_data:
            duration_info = YouTubeUtils.parse_duration(video.get('duration', ''))
            durations.append(duration_info['total_seconds'])
        
        if durations:
            avg_duration = statistics.mean(durations)
            if avg_duration > 600:  # 10分以上
                recommendations.append("動画が長すぎる可能性があります。視聴者維持率を確認してください。")
        
        return recommendations
