"""
YouTube.py3 - 感情分析機能

コメントの感情分析、トピック分析などの機能を提供します。
"""

import re
from collections import Counter
from typing import List, Dict, Any
from .base import YouTubeAPIBase
from .exceptions import YouTubeAPIError


class SentimentAnalysisMixin(YouTubeAPIBase):
    """感情分析機能のMixin"""

    def analyze_comment_sentiment(self, video_id, max_comments=200):
        """コメントの感情分析
        
        Args:
            video_id (str): 動画ID
            max_comments (int): 分析するコメント数
            
        Returns:
            dict: 感情分析結果
        """
        try:
            # コメント取得
            comments_data = self.get_video_comments(video_id, max_comments, include_replies=True)
            comments = comments_data.get('comments', [])
            
            if not comments:
                return {'error': 'コメントが見つかりません'}
            
            # 感情分析
            sentiment_results = {
                'positive': [],
                'negative': [],
                'neutral': [],
                'statistics': {
                    'total_comments': len(comments),
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0
                }
            }
            
            # 感情キーワード辞書（日本語）
            positive_words = {
                'すごい', '素晴らしい', '最高', '良い', 'いい', '素敵', '感動', '面白い', 
                'おもしろい', '楽しい', '好き', '愛', 'ありがとう', '感謝', '嬉しい',
                'amazing', 'great', 'awesome', 'good', 'love', 'like', 'thank', 'wonderful'
            }
            
            negative_words = {
                'ひどい', '最悪', '嫌い', 'だめ', 'つまらない', '悪い', '残念', '失望',
                'がっかり', '怒り', '腹立つ', '許せない', 'むかつく', '不快',
                'bad', 'hate', 'terrible', 'awful', 'worst', 'boring', 'stupid', 'angry'
            }
            
            for comment in comments:
                text = comment.get('text_display', '').lower()
                
                # 感情スコア計算
                positive_score = sum(1 for word in positive_words if word in text)
                negative_score = sum(1 for word in negative_words if word in text)
                
                # 感情分類
                if positive_score > negative_score:
                    sentiment = 'positive'
                    sentiment_results['positive'].append(comment)
                    sentiment_results['statistics']['positive_count'] += 1
                elif negative_score > positive_score:
                    sentiment = 'negative'
                    sentiment_results['negative'].append(comment)
                    sentiment_results['statistics']['negative_count'] += 1
                else:
                    sentiment = 'neutral'
                    sentiment_results['neutral'].append(comment)
                    sentiment_results['statistics']['neutral_count'] += 1
                
                # コメントに感情情報を追加
                comment['sentiment'] = sentiment
                comment['positive_score'] = positive_score
                comment['negative_score'] = negative_score
            
            # パーセンテージ計算
            total = sentiment_results['statistics']['total_comments']
            if total > 0:
                sentiment_results['statistics']['positive_percentage'] = round(
                    sentiment_results['statistics']['positive_count'] / total * 100, 1
                )
                sentiment_results['statistics']['negative_percentage'] = round(
                    sentiment_results['statistics']['negative_count'] / total * 100, 1
                )
                sentiment_results['statistics']['neutral_percentage'] = round(
                    sentiment_results['statistics']['neutral_count'] / total * 100, 1
                )
            
            # 感情トレンド分析
            sentiment_results['trend_analysis'] = self._analyze_sentiment_trends(comments)
            
            return sentiment_results
            
        except Exception as e:
            raise YouTubeAPIError(f"感情分析に失敗しました: {str(e)}")

    def extract_comment_topics(self, video_id, max_comments=200):
        """コメントからトピックを抽出
        
        Args:
            video_id (str): 動画ID
            max_comments (int): 分析するコメント数
            
        Returns:
            dict: トピック分析結果
        """
        try:
            # コメント取得
            comments_data = self.get_video_comments(video_id, max_comments, include_replies=True)
            comments = comments_data.get('comments', [])
            
            if not comments:
                return {'error': 'コメントが見つかりません'}
            
            # 全コメントテキストを結合
            all_text = ' '.join([comment.get('text_display', '') for comment in comments])
            
            # キーワード抽出
            keywords = self._extract_keywords_from_comments(all_text)
            
            # トピック分類
            topics = self._classify_topics(keywords, comments)
            
            # 頻出フレーズ抽出
            phrases = self._extract_common_phrases(all_text)
            
            return {
                'total_comments': len(comments),
                'top_keywords': keywords[:20],
                'topics': topics,
                'common_phrases': phrases[:10],
                'keyword_cloud_data': dict(Counter(keywords).most_common(50))
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"トピック抽出に失敗しました: {str(e)}")

    def analyze_user_engagement_patterns(self, video_id):
        """ユーザーエンゲージメントパターン分析
        
        Args:
            video_id (str): 動画ID
            
        Returns:
            dict: エンゲージメントパターン分析結果
        """
        try:
            # コメント取得
            comments_data = self.get_video_comments(video_id, max_results=500, include_replies=True)
            comments = comments_data.get('comments', [])
            
            if not comments:
                return {'error': 'コメントが見つかりません'}
            
            # ユーザー別分析
            user_activity = {}
            reply_patterns = {'has_replies': 0, 'no_replies': 0}
            time_patterns = {}
            
            for comment in comments:
                author = comment.get('author_display_name', 'Unknown')
                comment_type = comment.get('type', 'top_level')
                like_count = comment.get('like_count', 0)
                published_at = comment.get('published_at', '')
                
                # ユーザー別集計
                if author not in user_activity:
                    user_activity[author] = {
                        'comment_count': 0,
                        'total_likes': 0,
                        'top_level_comments': 0,
                        'replies': 0
                    }
                
                user_activity[author]['comment_count'] += 1
                user_activity[author]['total_likes'] += like_count
                
                if comment_type == 'top_level':
                    user_activity[author]['top_level_comments'] += 1
                else:
                    user_activity[author]['replies'] += 1
                
                # 返信パターン
                if comment.get('parent_id'):
                    reply_patterns['has_replies'] += 1
                else:
                    reply_patterns['no_replies'] += 1
                
                # 時間パターン（時間帯別）
                if published_at:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        hour = dt.hour
                        time_patterns[hour] = time_patterns.get(hour, 0) + 1
                    except:
                        pass
            
            # アクティブユーザー特定
            active_users = sorted(
                user_activity.items(),
                key=lambda x: x[1]['comment_count'],
                reverse=True
            )[:10]
            
            # 人気コメント（いいね数順）
            popular_comments = sorted(
                comments,
                key=lambda x: x.get('like_count', 0),
                reverse=True
            )[:5]
            
            return {
                'total_unique_users': len(user_activity),
                'total_comments': len(comments),
                'active_users': active_users,
                'reply_patterns': reply_patterns,
                'time_patterns': time_patterns,
                'popular_comments': popular_comments,
                'engagement_metrics': {
                    'average_likes_per_comment': sum(c.get('like_count', 0) for c in comments) / len(comments),
                    'reply_rate': reply_patterns['has_replies'] / len(comments) * 100 if comments else 0
                }
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"エンゲージメントパターン分析に失敗しました: {str(e)}")

    def detect_spam_comments(self, video_id, max_comments=200):
        """スパムコメント検出
        
        Args:
            video_id (str): 動画ID
            max_comments (int): チェックするコメント数
            
        Returns:
            dict: スパム検出結果
        """
        try:
            # コメント取得
            comments_data = self.get_video_comments(video_id, max_comments, include_replies=True)
            comments = comments_data.get('comments', [])
            
            if not comments:
                return {'error': 'コメントが見つかりません'}
            
            spam_patterns = [
                r'https?://[^\s]+',  # URL
                r'チャンネル登録',
                r'subscribe',
                r'フォロー',
                r'follow',
                r'いいね押して',
                r'like.*video',
                r'check.*channel',
                r'見てください',
                r'クリック',
                r'click'
            ]
            
            spam_comments = []
            suspicious_comments = []
            duplicate_texts = Counter()
            
            for comment in comments:
                text = comment.get('text_display', '').lower()
                spam_score = 0
                
                # パターンマッチング
                for pattern in spam_patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        spam_score += 1
                
                # 重複チェック
                duplicate_texts[text] += 1
                
                # 短すぎるコメント
                if len(text.strip()) < 3:
                    spam_score += 1
                
                # 同じ文字の繰り返し
                if re.search(r'(.)\1{5,}', text):
                    spam_score += 2
                
                # 分類
                if spam_score >= 3:
                    spam_comments.append({
                        'comment': comment,
                        'spam_score': spam_score,
                        'reason': 'high_spam_score'
                    })
                elif spam_score >= 1:
                    suspicious_comments.append({
                        'comment': comment,
                        'spam_score': spam_score,
                        'reason': 'suspicious_patterns'
                    })
            
            # 重複コメント検出
            duplicate_comments = []
            for text, count in duplicate_texts.items():
                if count > 1 and len(text.strip()) > 5:
                    duplicate_comments.append({
                        'text': text,
                        'count': count
                    })
            
            return {
                'total_comments_checked': len(comments),
                'spam_comments': spam_comments,
                'suspicious_comments': suspicious_comments,
                'duplicate_comments': duplicate_comments,
                'statistics': {
                    'spam_count': len(spam_comments),
                    'suspicious_count': len(suspicious_comments),
                    'duplicate_count': len(duplicate_comments),
                    'spam_percentage': len(spam_comments) / len(comments) * 100 if comments else 0
                }
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"スパム検出に失敗しました: {str(e)}")

    def _analyze_sentiment_trends(self, comments):
        """感情トレンド分析"""
        if len(comments) < 10:
            return {'trend': 'insufficient_data'}
        
        # 時系列順にソート
        sorted_comments = sorted(comments, key=lambda x: x.get('published_at', ''))
        
        # 前半と後半に分割
        mid_point = len(sorted_comments) // 2
        first_half = sorted_comments[:mid_point]
        second_half = sorted_comments[mid_point:]
        
        # 各半分の感情スコア計算
        def calculate_sentiment_score(comment_list):
            positive_count = sum(1 for c in comment_list if c.get('sentiment') == 'positive')
            negative_count = sum(1 for c in comment_list if c.get('sentiment') == 'negative')
            total = len(comment_list)
            
            if total == 0:
                return 0
            
            return (positive_count - negative_count) / total
        
        first_score = calculate_sentiment_score(first_half)
        second_score = calculate_sentiment_score(second_half)
        
        if second_score > first_score + 0.1:
            trend = 'improving'
        elif second_score < first_score - 0.1:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'first_half_score': round(first_score, 3),
            'second_half_score': round(second_score, 3),
            'change': round(second_score - first_score, 3)
        }

    def _extract_keywords_from_comments(self, text):
        """コメントからキーワード抽出"""
        # クリーニング
        text = re.sub(r'[!！?？.。,，@#$%^&*()（）\[\]【】]', ' ', text)
        text = re.sub(r'https?://[^\s]+', '', text)  # URL除去
        
        # 単語分割
        words = text.split()
        
        # フィルタリング
        keywords = []
        stop_words = {
            'の', 'に', 'を', 'が', 'は', 'で', 'と', 'から', 'まで', 'より', 'も', 'や',
            'です', 'ます', 'した', 'する', 'ある', 'いる', 'なる', 'れる', 'られる',
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
        
        for word in words:
            word = word.strip().lower()
            if len(word) > 1 and word not in stop_words and not word.isdigit():
                keywords.append(word)
        
        # 頻度でソート
        keyword_freq = Counter(keywords)
        return [word for word, count in keyword_freq.most_common(100)]

    def _classify_topics(self, keywords, comments):
        """トピック分類"""
        topics = {
            'content_quality': {'keywords': ['良い', 'いい', '素晴らしい', '最高', 'good', 'great', 'awesome'], 'count': 0},
            'technical_issues': {'keywords': ['音', '画質', '声', 'sound', 'audio', 'quality'], 'count': 0},
            'requests': {'keywords': ['お願い', 'して', 'please', 'request', '希望'], 'count': 0},
            'appreciation': {'keywords': ['ありがとう', '感謝', 'thank', 'thanks'], 'count': 0}
        }
        
        for comment in comments:
            text = comment.get('text_display', '').lower()
            
            for topic_name, topic_data in topics.items():
                for keyword in topic_data['keywords']:
                    if keyword in text:
                        topic_data['count'] += 1
                        break
        
        return topics

    def _extract_common_phrases(self, text):
        """頻出フレーズ抽出"""
        # 2-3語のフレーズを抽出
        sentences = re.split(r'[.。!！?？\n]', text)
        phrases = []
        
        for sentence in sentences:
            words = sentence.strip().split()
            if 2 <= len(words) <= 4:
                phrase = ' '.join(words)
                if len(phrase) > 5:  # 短すぎるフレーズは除外
                    phrases.append(phrase.lower())
        
        phrase_freq = Counter(phrases)
        return [phrase for phrase, count in phrase_freq.most_common(20) if count > 1]
