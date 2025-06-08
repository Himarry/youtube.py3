"""
YouTube.py3 - 高度なデータ分析機能モジュール

トレンド分析、競合分析、視聴者層分析、パフォーマンス予測機能を提供します。
"""

import statistics
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import List, Dict, Any, Optional
from .base import YouTubeAPIBase
from .exceptions import YouTubeAPIError
from .utils import YouTubeUtils
import logging

logger = logging.getLogger(__name__)


class AdvancedAnalyticsMixin(YouTubeAPIBase):
    """高度なデータ分析機能を提供するMixin"""
    
    def generate_trending_analysis(self, category_id: Optional[str] = None, 
                                 region_code: str = 'JP', max_results: int = 50) -> Dict[str, Any]:
        """トレンド分析レポート生成
        
        Args:
            category_id (str): 分析するカテゴリID
            region_code (str): 地域コード
            max_results (int): 分析する動画数
            
        Returns:
            dict: トレンド分析結果
        """
        try:
            # トレンド動画取得
            trending_videos = self.get_popular_videos(
                region_code=region_code,
                category_id=category_id,
                max_results=max_results
            )
            
            if not trending_videos:
                return {
                    'error': 'トレンド動画データが取得できませんでした',
                    'region_code': region_code,
                    'category_id': category_id
                }
            
            # 分析データ収集
            total_views = []
            engagement_rates = []
            upload_times = []
            durations = []
            title_keywords = []
            channels = Counter()
            
            for video in trending_videos:
                # 統計データ
                stats = video.get('statistics', {})
                views = int(stats.get('viewCount', 0))
                likes = int(stats.get('likeCount', 0))
                comments = int(stats.get('commentCount', 0))
                
                total_views.append(views)
                
                # エンゲージメント率計算
                if views > 0:
                    engagement_rate = ((likes + comments) / views) * 100
                    engagement_rates.append(engagement_rate)
                
                # アップロード時間分析
                published_at = datetime.fromisoformat(
                    video['snippet']['publishedAt'].replace('Z', '+00:00')
                )
                upload_times.append(published_at.hour)
                
                # 動画長分析
                duration = video.get('contentDetails', {}).get('duration')
                if duration:
                    try:
                        duration_info = YouTubeUtils.parse_duration(duration)
                        durations.append(duration_info['total_seconds'])
                    except:
                        pass
                
                # タイトルキーワード分析
                title = video['snippet']['title']
                keywords = self._extract_trending_keywords(title)
                title_keywords.extend(keywords)
                
                # チャンネル分析
                channel_title = video['snippet']['channelTitle']
                channels[channel_title] += 1
            
            # 分析結果生成
            analysis_result = {
                'analysis_period': datetime.now().isoformat(),
                'region_code': region_code,
                'category_id': category_id,
                'total_videos_analyzed': len(trending_videos),
                
                'view_statistics': {
                    'average_views': round(statistics.mean(total_views)) if total_views else 0,
                    'median_views': round(statistics.median(total_views)) if total_views else 0,
                    'max_views': max(total_views) if total_views else 0,
                    'min_views': min(total_views) if total_views else 0,
                    'total_views': sum(total_views)
                },
                
                'engagement_analysis': {
                    'average_engagement_rate': round(statistics.mean(engagement_rates), 2) if engagement_rates else 0,
                    'median_engagement_rate': round(statistics.median(engagement_rates), 2) if engagement_rates else 0,
                    'high_engagement_threshold': round(statistics.quantile(engagement_rates, 0.9), 2) if len(engagement_rates) > 10 else 0
                },
                
                'timing_insights': {
                    'popular_upload_hours': Counter(upload_times).most_common(5),
                    'peak_hour': Counter(upload_times).most_common(1)[0][0] if upload_times else None
                },
                
                'content_insights': {
                    'average_duration_seconds': round(statistics.mean(durations)) if durations else 0,
                    'average_duration_minutes': round(statistics.mean(durations) / 60, 1) if durations else 0,
                    'popular_keywords': Counter(title_keywords).most_common(15),
                    'top_channels': channels.most_common(10)
                },
                
                'recommendations': self._generate_trend_recommendations(
                    Counter(upload_times), Counter(title_keywords), durations
                )
            }
            
            return analysis_result
            
        except Exception as e:
            raise YouTubeAPIError(f"トレンド分析生成に失敗しました: {str(e)}")
    
    def competitor_analysis(self, channel_ids: List[str], 
                          metrics: List[str] = ['views', 'subscribers']) -> Dict[str, Any]:
        """競合分析機能
        
        Args:
            channel_ids (list): 競合チャンネルIDのリスト
            metrics (list): 分析指標
            
        Returns:
            dict: 競合分析結果
        """
        try:
            competitor_data = {}
            
            for channel_id in channel_ids:
                try:
                    # チャンネル基本情報取得
                    channel_info = self.get_channel_info(channel_id)
                    
                    # 最近の動画取得（過去30日）
                    recent_videos = self.search_videos_filtered(
                        channel_id=channel_id,
                        max_results=50,
                        order='date',
                        published_after=(datetime.now() - timedelta(days=30)).isoformat()
                    )
                    
                    # メトリクス計算
                    channel_metrics = self._calculate_competitor_metrics(channel_info, recent_videos, metrics)
                    competitor_data[channel_id] = channel_metrics
                    
                except Exception as e:
                    logger.warning(f"チャンネル {channel_id} の分析に失敗: {str(e)}")
                    continue
            
            if not competitor_data:
                raise YouTubeAPIError("競合データが取得できませんでした")
            
            # 比較分析
            comparison_result = self._generate_competitor_comparison(competitor_data, metrics)
            
            return {
                'analysis_date': datetime.now().isoformat(),
                'analyzed_channels': len(competitor_data),
                'metrics_analyzed': metrics,
                'competitor_data': competitor_data,
                'comparison_analysis': comparison_result,
                'recommendations': self._generate_competitor_recommendations(comparison_result)
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"競合分析に失敗しました: {str(e)}")
    
    def audience_demographic_analysis(self, channel_id: str) -> Dict[str, Any]:
        """視聴者層分析
        
        Args:
            channel_id (str): 分析するチャンネルID
            
        Returns:
            dict: 視聴者層分析結果
        """
        try:
            # チャンネル情報取得
            channel_info = self.get_channel_info(channel_id)
            
            # 最近の動画とコメント分析
            recent_videos = self.search_videos_filtered(
                channel_id=channel_id,
                max_results=20,
                order='date'
            )
            
            audience_data = {
                'comment_activity': {},
                'engagement_patterns': {},
                'content_preferences': {}
            }
            
            total_comments = 0
            comment_times = []
            engagement_scores = []
            
            for video in recent_videos[:10]:  # 上位10動画を分析
                video_id = video['id']
                
                # コメント取得
                comments = self.get_video_comments(video_id, max_results=100)
                total_comments += len(comments)
                
                # コメント時間分析
                for comment in comments:
                    try:
                        comment_time = datetime.fromisoformat(
                            comment['snippet']['publishedAt'].replace('Z', '+00:00')
                        )
                        comment_times.append(comment_time.hour)
                    except:
                        continue
                
                # エンゲージメント分析
                stats = video.get('statistics', {})
                views = int(stats.get('viewCount', 0))
                likes = int(stats.get('likeCount', 0))
                comments_count = int(stats.get('commentCount', 0))
                
                if views > 0:
                    engagement_score = ((likes + comments_count) / views) * 100
                    engagement_scores.append(engagement_score)
            
            # 分析結果生成
            demographic_analysis = {
                'channel_id': channel_id,
                'channel_name': channel_info.get('snippet', {}).get('title', ''),
                'analysis_date': datetime.now().isoformat(),
                'videos_analyzed': len(recent_videos[:10]),
                
                'engagement_insights': {
                    'total_comments_analyzed': total_comments,
                    'average_engagement_rate': round(statistics.mean(engagement_scores), 2) if engagement_scores else 0,
                    'engagement_consistency': self._calculate_engagement_consistency(engagement_scores)
                },
                
                'activity_patterns': {
                    'peak_comment_hours': Counter(comment_times).most_common(5),
                    'most_active_hour': Counter(comment_times).most_common(1)[0][0] if comment_times else None
                },
                
                'audience_behavior': self._analyze_audience_behavior(recent_videos),
                
                'recommendations': [
                    "視聴者が最も活発な時間帯にコンテンツを投稿することを検討してください",
                    "エンゲージメント率の高い動画の特徴を分析し、今後のコンテンツに活用してください",
                    "コメント欄での視聴者との積極的な交流を心がけてください"
                ]
            }
            
            return demographic_analysis
            
        except Exception as e:
            raise YouTubeAPIError(f"視聴者層分析に失敗しました: {str(e)}")
    
    def content_performance_prediction(self, video_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """コンテンツパフォーマンス予測
        
        Args:
            video_metadata (dict): 動画メタデータ
            
        Returns:
            dict: パフォーマンス予測結果
        """
        try:
            # 予測に使用する要素
            title = video_metadata.get('title', '')
            description = video_metadata.get('description', '')
            tags = video_metadata.get('tags', [])
            category_id = video_metadata.get('categoryId', '22')
            
            # スコア計算
            prediction_scores = {
                'title_score': self._calculate_title_prediction_score(title),
                'description_score': self._calculate_description_score(description),
                'tags_score': self._calculate_tags_score(tags),
                'overall_optimization': 0
            }
            
            # 総合スコア計算
            total_score = sum(prediction_scores.values()) / 3
            prediction_scores['overall_optimization'] = round(total_score, 2)
            
            # 予測結果生成
            performance_prediction = prediction_scores['overall_optimization']
            
            if performance_prediction >= 80:
                prediction_level = 'excellent'
                prediction_message = ' 非常に高いパフォーマンスが期待できます'
            elif performance_prediction >= 60:
                prediction_level = 'good'
                prediction_message = '良好なパフォーマンスが期待できます'
            elif performance_prediction >= 40:
                prediction_level = 'average'
                prediction_message = '平均的なパフォーマンスが予想されます'
            else:
                prediction_level = 'needs_improvement'
                prediction_message = '最適化の余地があります'
            
            return {
                'video_metadata': video_metadata,
                'prediction_date': datetime.now().isoformat(),
                'prediction_scores': prediction_scores,
                'overall_prediction': {
                    'score': performance_prediction,
                    'level': prediction_level,
                    'message': prediction_message
                },
                'improvement_suggestions': self._generate_improvement_suggestions(prediction_scores, video_metadata),
                'estimated_metrics': self._estimate_performance_metrics(performance_prediction)
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"パフォーマンス予測に失敗しました: {str(e)}")
    
    # ヘルパーメソッド
    def _extract_trending_keywords(self, title: str) -> List[str]:
        """トレンドキーワード抽出"""
        import re
        # 日本語と英語のキーワードを抽出
        keywords = re.findall(r'[ぁ-んァ-ヶー一-龠a-zA-Z0-9]+', title)
        return [kw for kw in keywords if len(kw) > 1]
    
    def _generate_trend_recommendations(self, upload_times: Counter, keywords: Counter, durations: List[int]) -> List[str]:
        """トレンド推奨事項生成"""
        recommendations = []
        
        if upload_times:
            peak_hour = upload_times.most_common(1)[0][0]
            recommendations.append(f"トレンド動画は{peak_hour}時頃の投稿が多い傾向があります")
        
        if keywords:
            top_keywords = [kw[0] for kw in keywords.most_common(3)]
            recommendations.append(f"人気キーワード: {', '.join(top_keywords)}")
        
        if durations:
            avg_duration = statistics.mean(durations) / 60
            recommendations.append(f"トレンド動画の平均長は約{avg_duration:.1f}分です")
        
        return recommendations
    
    def _calculate_competitor_metrics(self, channel_info: Dict, recent_videos: List, metrics: List) -> Dict[str, Any]:
        """競合メトリクス計算"""
        stats = channel_info.get('statistics', {})
        
        metrics_data = {
            'channel_title': channel_info.get('snippet', {}).get('title', ''),
            'subscriber_count': int(stats.get('subscriberCount', 0)),
            'total_video_count': int(stats.get('videoCount', 0)),
            'total_view_count': int(stats.get('viewCount', 0)),
            'recent_videos_count': len(recent_videos),
            'recent_performance': {}
        }
        
        # 最近の動画のパフォーマンス
        if recent_videos:
            recent_views = []
            recent_engagement = []
            
            for video in recent_videos:
                video_stats = video.get('statistics', {})
                views = int(video_stats.get('viewCount', 0))
                likes = int(video_stats.get('likeCount', 0))
                comments = int(video_stats.get('commentCount', 0))
                
                recent_views.append(views)
                if views > 0:
                    engagement = ((likes + comments) / views) * 100
                    recent_engagement.append(engagement)
            
            metrics_data['recent_performance'] = {
                'avg_views': round(statistics.mean(recent_views)) if recent_views else 0,
                'avg_engagement_rate': round(statistics.mean(recent_engagement), 2) if recent_engagement else 0,
                'upload_frequency': len(recent_videos) / 30  # 1日あたりの投稿数
            }
        
        return metrics_data
    
    def _generate_competitor_comparison(self, competitor_data: Dict, metrics: List) -> Dict[str, Any]:
        """競合比較分析生成"""
        if not competitor_data:
            return {}
        
        # 各メトリクスでのランキング
        subscriber_ranking = sorted(
            competitor_data.items(),
            key=lambda x: x[1]['subscriber_count'],
            reverse=True
        )
        
        avg_views_ranking = sorted(
            competitor_data.items(),
            key=lambda x: x[1]['recent_performance'].get('avg_views', 0),
            reverse=True
        )
        
        return {
            'subscriber_ranking': [(ch_id, data['channel_title'], data['subscriber_count']) 
                                 for ch_id, data in subscriber_ranking],
            'performance_ranking': [(ch_id, data['channel_title'], data['recent_performance'].get('avg_views', 0))
                                  for ch_id, data in avg_views_ranking],
            'market_insights': self._generate_market_insights(competitor_data)
        }
    
    def _generate_competitor_recommendations(self, comparison: Dict) -> List[str]:
        """競合分析推奨事項生成"""
        return [
            "上位競合の投稿頻度とタイミングを参考にしてください",
            "パフォーマンスの高い競合のコンテンツ戦略を分析してください",
            "市場での自分のポジションを明確にし、差別化要素を強化してください"
        ]
    
    def _analyze_audience_behavior(self, videos: List) -> Dict[str, Any]:
        """視聴者行動分析"""
        return {
            'content_preference_indicators': 'コンテンツタイプの好み分析（実装可能）',
            'interaction_patterns': 'インタラクションパターン分析（実装可能）',
            'retention_indicators': '視聴継続率指標（実装可能）'
        }
    
    def _calculate_engagement_consistency(self, engagement_scores: List[float]) -> str:
        """エンゲージメント一貫性計算"""
        if len(engagement_scores) < 2:
            return 'insufficient_data'
        
        std_dev = statistics.stdev(engagement_scores)
        mean_score = statistics.mean(engagement_scores)
        
        if mean_score > 0:
            cv = std_dev / mean_score  # 変動係数
            if cv < 0.3:
                return 'high_consistency'
            elif cv < 0.6:
                return 'moderate_consistency'
            else:
                return 'low_consistency'
        
        return 'unknown'
    
    def _calculate_title_prediction_score(self, title: str) -> float:
        """タイトル予測スコア計算"""
        score = 0
        
        # 長さスコア
        if 20 <= len(title) <= 60:
            score += 30
        
        # 数字含有
        if any(char.isdigit() for char in title):
            score += 20
        
        # 疑問符含有
        if '?' in title or '？' in title:
            score += 15
        
        # 感情的キーワード
        emotional_keywords = ['驚愕', '衝撃', '必見', '話題', '人気', '注目', '最新', '限定']
        if any(keyword in title for keyword in emotional_keywords):
            score += 25
        
        return min(score, 100)
    
    def _calculate_description_score(self, description: str) -> float:
        """説明文スコア計算"""
        score = 0
        
        # 長さスコア
        if 100 <= len(description) <= 500:
            score += 40
        elif len(description) > 500:
            score += 30
        
        # タグ含有
        if '#' in description:
            score += 20
        
        # リンク含有
        if 'http' in description:
            score += 15
        
        # キーワード密度
        if description:
            score += 25
        
        return min(score, 100)
    
    def _calculate_tags_score(self, tags: List[str]) -> float:
        """タグスコア計算"""
        if not tags:
            return 0
        
        score = 0
        
        # タグ数スコア
        if 5 <= len(tags) <= 15:
            score += 50
        elif len(tags) > 0:
            score += 30
        
        # タグの質（長さと多様性）
        avg_length = sum(len(tag) for tag in tags) / len(tags)
        if 3 <= avg_length <= 20:
            score += 50
        
        return min(score, 100)
    
    def _generate_improvement_suggestions(self, scores: Dict, metadata: Dict) -> List[str]:
        """改善提案生成"""
        suggestions = []
        
        if scores['title_score'] < 70:
            suggestions.append("タイトルに数字や疑問符を含めることを検討してください")
        
        if scores['description_score'] < 70:
            suggestions.append("説明文をより詳細に記載し、関連タグを追加してください")
        
        if scores['tags_score'] < 70:
            suggestions.append("適切な数のタグ（5-15個）を設定してください")
        
        return suggestions
    
    def _estimate_performance_metrics(self, prediction_score: float) -> Dict[str, Any]:
        """パフォーマンス指標推定"""
        # 基本的な推定（実際のデータに基づいてより精密化可能）
        base_views = 1000
        multiplier = prediction_score / 50
        
        return {
            'estimated_views_range': {
                'min': int(base_views * multiplier * 0.5),
                'max': int(base_views * multiplier * 2.0)
            },
            'estimated_engagement_rate': round(prediction_score / 10, 1),
            'confidence_level': 'medium' if prediction_score > 50 else 'low'
        }
    
    def _generate_market_insights(self, competitor_data: Dict) -> Dict[str, Any]:
        """市場インサイト生成"""
        total_subscribers = sum(data['subscriber_count'] for data in competitor_data.values())
        avg_subscribers = total_subscribers / len(competitor_data)
        
        return {
            'market_size_indicator': total_subscribers,
            'average_competitor_size': int(avg_subscribers),
            'market_saturation': 'medium' if len(competitor_data) > 10 else 'low'
        }