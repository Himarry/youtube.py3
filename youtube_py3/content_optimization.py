"""
YouTube.py3 - コンテンツ最適化支援機能

動画タイトル、サムネイル、投稿時間などの最適化支援機能を提供します。
"""

import re
from datetime import datetime, timedelta
from collections import Counter
from typing import List, Dict, Any
from .base import YouTubeAPIBase
from .exceptions import YouTubeAPIError


class ContentOptimizationMixin(YouTubeAPIBase):
    """コンテンツ最適化支援機能のMixin"""

    def analyze_optimal_upload_time(self, channel_id, days=30):
        """最適なアップロード時間を分析
        
        Args:
            channel_id (str): 分析するチャンネルID
            days (int): 分析期間（日数）
            
        Returns:
            dict: 最適アップロード時間の分析結果
        """
        try:
            # 期間内の動画取得
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # チャンネル動画取得メソッドを正しく呼び出し
            videos = self.search_videos_filtered(
                channel_id=channel_id,
                max_results=200,
                order="date",
                published_after=start_date.isoformat()
            )
            
            if not videos:
                return {
                    'error': 'データ不足',
                    'message': f'過去{days}日間に投稿された動画が見つかりません'
                }
            
            # 時間別パフォーマンス分析
            hourly_performance = {}
            daily_performance = {}
            
            for video in videos:
                try:
                    published_at = datetime.fromisoformat(video['snippet']['publishedAt'].replace('Z', '+00:00'))
                    hour = published_at.hour
                    day_of_week = published_at.weekday()  # 0=月曜日
                    
                    view_count = int(video.get('statistics', {}).get('viewCount', 0))
                    like_count = int(video.get('statistics', {}).get('likeCount', 0))
                    engagement_rate = self._calculate_engagement_rate(video.get('statistics', {}))
                    
                    # 時間別集計
                    if hour not in hourly_performance:
                        hourly_performance[hour] = {'videos': 0, 'total_views': 0, 'total_likes': 0, 'total_engagement': 0}
                    
                    hourly_performance[hour]['videos'] += 1
                    hourly_performance[hour]['total_views'] += view_count
                    hourly_performance[hour]['total_likes'] += like_count
                    hourly_performance[hour]['total_engagement'] += engagement_rate
                    
                    # 曜日別集計
                    if day_of_week not in daily_performance:
                        daily_performance[day_of_week] = {'videos': 0, 'total_views': 0, 'total_likes': 0, 'total_engagement': 0}
                    
                    daily_performance[day_of_week]['videos'] += 1
                    daily_performance[day_of_week]['total_views'] += view_count
                    daily_performance[day_of_week]['total_likes'] += like_count
                    daily_performance[day_of_week]['total_engagement'] += engagement_rate
                    
                except Exception as e:
                    # 個別動画のエラーはスキップ
                    continue
            
            # 平均値計算
            hourly_averages = {}
            for hour, data in hourly_performance.items():
                if data['videos'] > 0:
                    hourly_averages[hour] = {
                        'avg_views': round(data['total_views'] / data['videos'], 2),
                        'avg_likes': round(data['total_likes'] / data['videos'], 2),
                        'avg_engagement': round(data['total_engagement'] / data['videos'], 2),
                        'video_count': data['videos']
                    }
            
            daily_averages = {}
            day_names = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
            for day, data in daily_performance.items():
                if data['videos'] > 0:
                    daily_averages[day_names[day]] = {
                        'avg_views': round(data['total_views'] / data['videos'], 2),
                        'avg_likes': round(data['total_likes'] / data['videos'], 2),
                        'avg_engagement': round(data['total_engagement'] / data['videos'], 2),
                        'video_count': data['videos']
                    }
            
            # 最適時間特定
            best_hour = None
            best_day = None
            
            if hourly_averages:
                best_hour = max(hourly_averages.items(), key=lambda x: x[1]['avg_views'])
            
            if daily_averages:
                best_day = max(daily_averages.items(), key=lambda x: x[1]['avg_views'])
            
            return {
                'analysis_period': f"{days}日間",
                'total_videos_analyzed': len(videos),
                'hourly_performance': hourly_averages,
                'daily_performance': daily_averages,
                'recommendations': {
                    'optimal_hour': f"{best_hour[0]}時" if best_hour else "データ不足",
                    'optimal_day': best_day[0] if best_day else "データ不足",
                    'best_hour_stats': best_hour[1] if best_hour else None,
                    'best_day_stats': best_day[1] if best_day else None,
                    'confidence_level': self._calculate_confidence_level(hourly_averages, daily_averages)
                }
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"最適アップロード時間分析に失敗しました: {str(e)}")

    def analyze_title_performance(self, video_ids):
        """タイトルのパフォーマンス分析
        
        Args:
            video_ids (list): 分析する動画IDのリスト
            
        Returns:
            dict: タイトル分析結果
        """
        try:
            if not video_ids:
                return {'error': '動画IDが指定されていません'}
            
            # 動画情報取得
            videos_info = []
            for video_id in video_ids:
                try:
                    video_info = self.get_video_info(video_id, include_statistics=True)
                    videos_info.append(video_info)
                except:
                    continue  # エラーの場合はスキップ
            
            if not videos_info:
                return {'error': '有効な動画データが取得できませんでした'}
            
            title_analysis = {
                'length_performance': {},
                'keyword_performance': {},
                'pattern_analysis': {},
                'recommendations': []
            }
            
            # タイトル長別分析
            length_groups = {'short': [], 'medium': [], 'long': []}
            keyword_performance = {}
            
            for video in videos_info:
                snippet = video.get('snippet', {})
                title = snippet.get('title', '')
                title_length = len(title)
                view_count = int(video.get('statistics', {}).get('viewCount', 0))
                engagement_rate = self._calculate_engagement_rate(video.get('statistics', {}))
                
                # 長さ別分類
                if title_length <= 30:
                    category = 'short'
                elif title_length <= 60:
                    category = 'medium'
                else:
                    category = 'long'
                
                length_groups[category].append({
                    'title': title,
                    'length': title_length,
                    'views': view_count,
                    'engagement': engagement_rate
                })
                
                # キーワード抽出と分析
                keywords = self._extract_keywords_from_title(title)
                for keyword in keywords:
                    if keyword not in keyword_performance:
                        keyword_performance[keyword] = {'count': 0, 'total_views': 0, 'total_engagement': 0}
                    
                    keyword_performance[keyword]['count'] += 1
                    keyword_performance[keyword]['total_views'] += view_count
                    keyword_performance[keyword]['total_engagement'] += engagement_rate
            
            # 長さ別平均パフォーマンス
            for category, videos in length_groups.items():
                if videos:
                    avg_views = sum(v['views'] for v in videos) / len(videos)
                    avg_engagement = sum(v['engagement'] for v in videos) / len(videos)
                    avg_length = sum(v['length'] for v in videos) / len(videos)
                    
                    title_analysis['length_performance'][category] = {
                        'video_count': len(videos),
                        'avg_views': round(avg_views, 2),
                        'avg_engagement': round(avg_engagement, 2),
                        'avg_length': round(avg_length, 1)
                    }
            
            # キーワード別平均パフォーマンス
            for keyword, data in keyword_performance.items():
                if data['count'] >= 2:  # 2回以上使用されたキーワードのみ
                    title_analysis['keyword_performance'][keyword] = {
                        'usage_count': data['count'],
                        'avg_views': round(data['total_views'] / data['count'], 2),
                        'avg_engagement': round(data['total_engagement'] / data['count'], 2)
                    }
            
            # パターン分析
            title_analysis['pattern_analysis'] = self._analyze_title_patterns(videos_info)
            
            # 推奨事項生成
            title_analysis['recommendations'] = self._generate_title_recommendations(title_analysis)
            
            return title_analysis
            
        except Exception as e:
            raise YouTubeAPIError(f"タイトルパフォーマンス分析に失敗しました: {str(e)}")

    def suggest_video_tags(self, title, description="", similar_video_count=10):
        """動画タグの最適化提案
        
        Args:
            title (str): 動画タイトル
            description (str): 動画説明文
            similar_video_count (int): 類似動画の検索数
            
        Returns:
            dict: タグ提案結果
        """
        try:
            if not title.strip():
                return {'error': 'タイトルが指定されていません'}
            
            # タイトルからキーワード抽出
            title_keywords = self._extract_keywords_from_title(title)
            
            if not title_keywords:
                return {'error': 'タイトルから有効なキーワードを抽出できませんでした'}
            
            # 類似動画検索
            search_query = ' '.join(title_keywords[:3])  # 主要キーワード3つで検索
            
            try:
                similar_videos = self.search_videos_filtered(
                    query=search_query,
                    max_results=similar_video_count,
                    order="relevance"
                )
            except:
                similar_videos = []
            
            # 類似動画のタグ分析（タイトルから推測）
            suggested_tags = set(title_keywords)
            tag_frequency = Counter()
            
            for video in similar_videos:
                snippet = video.get('snippet', {})
                video_title = snippet.get('title', '')
                video_keywords = self._extract_keywords_from_title(video_title)
                
                for keyword in video_keywords:
                    tag_frequency[keyword] += 1
                    if tag_frequency[keyword] >= 2:  # 複数回出現
                        suggested_tags.add(keyword)
            
            # 説明文からも追加キーワード
            if description:
                desc_keywords = self._extract_keywords_from_text(description)
                suggested_tags.update(desc_keywords[:5])  # 上位5つ
            
            # 人気順にソート
            popular_tags = [tag for tag, count in tag_frequency.most_common(20) if tag in suggested_tags]
            
            return {
                'primary_tags': title_keywords[:5],
                'suggested_tags': list(suggested_tags)[:15],
                'popular_tags': popular_tags[:10],
                'tag_analysis': dict(tag_frequency.most_common(10)),
                'similar_videos_analyzed': len(similar_videos),
                'search_query_used': search_query
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"タグ提案に失敗しました: {str(e)}")

    def analyze_thumbnail_effectiveness(self, video_ids):
        """サムネイルの効果分析（メタデータベース）
        
        Args:
            video_ids (list): 分析する動画IDのリスト
            
        Returns:
            dict: サムネイル効果分析結果
        """
        try:
            if not video_ids:
                return {'error': '動画IDが指定されていません'}
            
            videos_info = []
            for video_id in video_ids:
                try:
                    video_info = self.get_video_info(video_id, include_statistics=True)
                    videos_info.append(video_info)
                except:
                    continue
            
            if not videos_info:
                return {'error': '有効な動画データが取得できませんでした'}
            
            thumbnail_analysis = {
                'performance_correlation': {},
                'resolution_analysis': {},
                'recommendations': []
            }
            
            # サムネイル情報とパフォーマンスの相関
            high_res_videos = []
            standard_res_videos = []
            
            for video in videos_info:
                snippet = video.get('snippet', {})
                thumbnails = snippet.get('thumbnails', {})
                statistics = video.get('statistics', {})
                
                view_count = int(statistics.get('viewCount', 0))
                like_count = int(statistics.get('likeCount', 0))
                engagement_rate = self._calculate_engagement_rate(statistics)
                
                video_data = {
                    'video_id': video.get('id', ''),
                    'title': snippet.get('title', '')[:50] + '...' if len(snippet.get('title', '')) > 50 else snippet.get('title', ''),
                    'views': view_count,
                    'likes': like_count,
                    'engagement_rate': engagement_rate
                }
                
                # サムネイルの解像度分析
                if 'maxres' in thumbnails:
                    video_data['thumbnail_quality'] = 'maxres'
                    high_res_videos.append(video_data)
                elif 'high' in thumbnails:
                    video_data['thumbnail_quality'] = 'high'
                    high_res_videos.append(video_data)
                else:
                    video_data['thumbnail_quality'] = 'standard'
                    standard_res_videos.append(video_data)
                
                thumbnail_analysis['performance_correlation'][video.get('id', '')] = video_data
            
            # 解像度別平均パフォーマンス
            if high_res_videos:
                avg_views_high = sum(v['views'] for v in high_res_videos) / len(high_res_videos)
                avg_engagement_high = sum(v['engagement_rate'] for v in high_res_videos) / len(high_res_videos)
                
                thumbnail_analysis['resolution_analysis']['high_resolution'] = {
                    'count': len(high_res_videos),
                    'avg_views': round(avg_views_high, 2),
                    'avg_engagement': round(avg_engagement_high, 2)
                }
            
            if standard_res_videos:
                avg_views_standard = sum(v['views'] for v in standard_res_videos) / len(standard_res_videos)
                avg_engagement_standard = sum(v['engagement_rate'] for v in standard_res_videos) / len(standard_res_videos)
                
                thumbnail_analysis['resolution_analysis']['standard_resolution'] = {
                    'count': len(standard_res_videos),
                    'avg_views': round(avg_views_standard, 2),
                    'avg_engagement': round(avg_engagement_standard, 2)
                }
            
            # 推奨事項生成
            recommendations = []
            
            if high_res_videos and standard_res_videos:
                high_avg = thumbnail_analysis['resolution_analysis']['high_resolution']['avg_views']
                standard_avg = thumbnail_analysis['resolution_analysis']['standard_resolution']['avg_views']
                
                if high_avg > standard_avg * 1.2:
                    recommendations.append("高解像度サムネイルの方がパフォーマンスが良い傾向があります")
                
            recommendations.extend([
                "カスタムサムネイルを使用してください",
                "明るく目立つ色を使用してください",
                "顔やテキストを大きく表示してください",
                "モバイル画面でも見やすいデザインにしてください"
            ])
            
            thumbnail_analysis['recommendations'] = recommendations
            
            return thumbnail_analysis
            
        except Exception as e:
            raise YouTubeAPIError(f"サムネイル効果分析に失敗しました: {str(e)}")

    def generate_content_ideas(self, channel_id, trend_keywords=None):
        """コンテンツアイデア生成
        
        Args:
            channel_id (str): 対象チャンネルID
            trend_keywords (list): トレンドキーワード（オプション）
            
        Returns:
            dict: コンテンツアイデア
        """
        try:
            # チャンネルの過去動画分析
            try:
                channel_videos = self.search_videos_filtered(
                    channel_id=channel_id,
                    max_results=50,
                    order="date"
                )
            except:
                return {'error': 'チャンネル動画の取得に失敗しました'}
            
            if not channel_videos:
                return {'error': 'チャンネルに動画が見つかりません'}
            
            # パフォーマンスの高い動画の特徴抽出
            high_performing = sorted(
                channel_videos,
                key=lambda x: int(x.get('statistics', {}).get('viewCount', 0)),
                reverse=True
            )[:10]
            
            # 成功パターン分析
            successful_keywords = []
            successful_lengths = []
            
            for video in high_performing:
                snippet = video.get('snippet', {})
                title = snippet.get('title', '')
                keywords = self._extract_keywords_from_title(title)
                successful_keywords.extend(keywords)
                
                content_details = video.get('contentDetails', {})
                duration = content_details.get('duration', '')
                if duration:
                    try:
                        from .utils import YouTubeUtils
                        duration_info = YouTubeUtils.parse_duration(duration)
                        successful_lengths.append(duration_info['total_seconds'])
                    except:
                        pass
            
            keyword_frequency = Counter(successful_keywords)
            
            # コンテンツアイデア生成
            content_ideas = []
            
            # トレンドキーワードとの組み合わせ
            if trend_keywords:
                for trend_keyword in trend_keywords[:5]:
                    if isinstance(trend_keyword, (list, tuple)):
                        trend_keyword = trend_keyword[0]  # タプルの場合は最初の要素
                    
                    for popular_keyword, count in keyword_frequency.most_common(3):
                        content_ideas.append({
                            'title_suggestion': f"{trend_keyword} × {popular_keyword}",
                            'trend_keyword': trend_keyword,
                            'channel_keyword': popular_keyword,
                            'confidence': 'high',
                            'rationale': f"トレンド「{trend_keyword}」とチャンネルの人気キーワード「{popular_keyword}」の組み合わせ"
                        })
            
            # チャンネル独自のコンテンツアイデア
            for keyword, count in keyword_frequency.most_common(5):
                content_ideas.append({
                    'title_suggestion': f"{keyword}の新しい使い方",
                    'based_on': 'channel_history',
                    'usage_count': count,
                    'confidence': 'medium',
                    'rationale': f"過去の人気動画で{count}回使用されたキーワード"
                })
                
                # バリエーション追加
                content_ideas.append({
                    'title_suggestion': f"初心者向け{keyword}ガイド",
                    'based_on': 'channel_history',
                    'usage_count': count,
                    'confidence': 'medium',
                    'rationale': f"人気キーワード「{keyword}」の初心者向けコンテンツ"
                })
            
            # 最適な動画長計算
            optimal_duration = 0
            if successful_lengths:
                optimal_duration = sum(successful_lengths) / len(successful_lengths)
            
            return {
                'content_ideas': content_ideas[:15],  # 上位15件
                'successful_patterns': {
                    'popular_keywords': keyword_frequency.most_common(10),
                    'optimal_duration_seconds': round(optimal_duration, 0),
                    'optimal_duration_minutes': round(optimal_duration / 60, 1)
                },
                'recommendations': [
                    "トレンドキーワードを既存の成功パターンと組み合わせる",
                    "過去の人気動画の要素を新しいコンテンツに活用する",
                    f"推奨動画長: {optimal_duration / 60:.1f}分" if optimal_duration > 0 else "最適な動画長のデータが不足しています",
                    "初心者向けコンテンツは安定した需要があります",
                    "季節やイベントに合わせたコンテンツを検討してください"
                ]
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"コンテンツアイデア生成に失敗しました: {str(e)}")

    def _extract_keywords_from_title(self, title):
        """タイトルからキーワードを抽出"""
        if not title:
            return []
        
        # 基本的なクリーニング
        title = re.sub(r'[【】\[\]()（）｜|]', ' ', title)
        title = re.sub(r'[!！?？.。,，]', ' ', title)
        
        # 単語分割
        words = title.split()
        
        # フィルタリング
        keywords = []
        stop_words = {'の', 'に', 'を', 'が', 'は', 'で', 'と', 'から', 'まで', 'より', 'も', 'や', 'など', 'です', 'ます'}
        
        for word in words:
            word = word.strip()
            if len(word) > 1 and word.lower() not in stop_words and not word.isdigit():
                keywords.append(word.lower())
        
        return keywords

    def _extract_keywords_from_text(self, text):
        """テキストからキーワードを抽出"""
        if not text:
            return []
        
        # 改行を空白に変換
        text = text.replace('\n', ' ')
        
        # 基本的なクリーニング
        text = re.sub(r'[【】\[\]()（）｜|]', ' ', text)
        
        # 単語分割
        words = text.split()
        
        # フィルタリングと頻度計算
        word_freq = Counter()
        stop_words = {'の', 'に', 'を', 'が', 'は', 'で', 'と', 'から', 'まで', 'より', 'も', 'や', 'など', 'です', 'ます', 'した', 'する'}
        
        for word in words:
            word = word.strip()
            if len(word) > 1 and word.lower() not in stop_words and not word.isdigit():
                word_freq[word.lower()] += 1
        
        return [word for word, count in word_freq.most_common(10)]

    def _analyze_title_patterns(self, videos_info):
        """タイトルパターン分析"""
        patterns = {
            'question_titles': 0,
            'numbered_titles': 0,
            'how_to_titles': 0,
            'review_titles': 0,
            'list_titles': 0,
            'emotional_titles': 0
        }
        
        for video in videos_info:
            snippet = video.get('snippet', {})
            title = snippet.get('title', '').lower()
            
            if '?' in title or '？' in title:
                patterns['question_titles'] += 1
            
            if re.search(r'\d+', title):
                patterns['numbered_titles'] += 1
            
            if any(word in title for word in ['how to', 'やり方', '方法', '手順']):
                patterns['how_to_titles'] += 1
            
            if any(word in title for word in ['review', 'レビュー', '評価', '感想']):
                patterns['review_titles'] += 1
            
            if any(word in title for word in ['まとめ', 'ランキング', 'top', 'best']):
                patterns['list_titles'] += 1
            
            if any(word in title for word in ['驚き', 'すごい', '感動', '衝撃', '必見']):
                patterns['emotional_titles'] += 1
        
        return patterns

    def _generate_title_recommendations(self, title_analysis):
        """タイトル推奨事項生成"""
        recommendations = []
        
        # 長さ別推奨
        length_perf = title_analysis.get('length_performance', {})
        if length_perf:
            best_length = max(length_perf.items(), key=lambda x: x[1]['avg_views'])
            length_names = {'short': '短い', 'medium': '中程度', 'long': '長い'}
            recommendations.append(
                f"最適なタイトル長: {length_names.get(best_length[0], best_length[0])} "
                f"(平均{best_length[1]['avg_length']:.0f}文字)"
            )
        
        # キーワード推奨
        keyword_perf = title_analysis.get('keyword_performance', {})
        if keyword_perf:
            top_keywords = sorted(keyword_perf.items(), key=lambda x: x[1]['avg_views'], reverse=True)[:3]
            if top_keywords:
                keyword_list = ', '.join([k[0] for k in top_keywords])
                recommendations.append(f"効果的なキーワード: {keyword_list}")
        
        # パターン推奨
        patterns = title_analysis.get('pattern_analysis', {})
        total_videos = sum(patterns.values()) if patterns else 0
        
        if total_videos > 0:
            question_ratio = patterns.get('question_titles', 0) / total_videos
            numbered_ratio = patterns.get('numbered_titles', 0) / total_videos
            
            if question_ratio > 0.3:
                recommendations.append("疑問形タイトルが効果的です")
            
            if numbered_ratio > 0.4:
                recommendations.append("数字を含むタイトルが効果的です")
        
        # 一般的な推奨事項
        if not recommendations:
            recommendations.extend([
                "具体的な数字を含めてください",
                "読者の疑問に答える形にしてください",
                "感情に訴えるキーワードを使用してください"
            ])
        
        return recommendations

    def _calculate_engagement_rate(self, statistics):
        """エンゲージメント率計算"""
        try:
            views = int(statistics.get('viewCount', 0))
            likes = int(statistics.get('likeCount', 0))
            comments = int(statistics.get('commentCount', 0))
            
            if views == 0:
                return 0.0
            
            return round((likes + comments) / views * 100, 2)
        except (ValueError, TypeError, ZeroDivisionError):
            return 0.0

    def _calculate_confidence_level(self, hourly_averages, daily_averages):
        """分析結果の信頼度計算"""
        try:
            total_data_points = len(hourly_averages) + len(daily_averages)
            
            if total_data_points >= 10:
                return 'high'
            elif total_data_points >= 5:
                return 'medium'
            else:
                return 'low'
        except:
            return 'unknown'