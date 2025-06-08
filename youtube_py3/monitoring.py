"""
YouTube.py3 - リアルタイム監視機能

チャンネル監視、トレンド追跡、自動アラートなどの機能を提供します。
"""

import time
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Callable, Any
from .base import YouTubeAPIBase
from .exceptions import YouTubeAPIError


class MonitoringMixin(YouTubeAPIBase):
    """リアルタイム監視機能のMixin"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitoring_data = {}

    def monitor_channel_uploads(self, channel_id, callback: Callable = None, check_interval=300):
        """チャンネルの新しいアップロードを監視
        
        Args:
            channel_id (str): 監視するチャンネルID
            callback (callable): 新動画発見時のコールバック関数
            check_interval (int): チェック間隔（秒）
            
        Returns:
            dict: 監視状態
        """
        try:
            # 初回チェック - 最新動画を記録
            latest_videos = self.get_channel_videos_advanced(
                channel_id, 
                max_results=5, 
                order="date"
            )
            
            if not latest_videos:
                raise YouTubeAPIError(f"チャンネル {channel_id} の動画が見つかりません")
            
            # 最新動画IDを保存
            latest_video_id = latest_videos[0]['id']['videoId']
            self.monitoring_data[channel_id] = {
                'latest_video_id': latest_video_id,
                'last_check': datetime.now(),
                'new_videos_found': []
            }
            
            monitoring_info = {
                'channel_id': channel_id,
                'monitoring_started': datetime.now(),
                'latest_video_id': latest_video_id,
                'check_interval': check_interval,
                'status': 'monitoring_started'
            }
            
            if callback:
                callback({
                    'event': 'monitoring_started',
                    'data': monitoring_info
                })
            
            return monitoring_info
            
        except Exception as e:
            raise YouTubeAPIError(f"チャンネル監視開始に失敗しました: {str(e)}")

    def check_for_new_uploads(self, channel_id, callback: Callable = None):
        """新しいアップロードをチェック
        
        Args:
            channel_id (str): チェックするチャンネルID
            callback (callable): 新動画発見時のコールバック関数
            
        Returns:
            dict: チェック結果
        """
        try:
            if channel_id not in self.monitoring_data:
                raise YouTubeAPIError(f"チャンネル {channel_id} は監視対象ではありません")
            
            # 現在の最新動画を取得
            current_videos = self.get_channel_videos_advanced(
                channel_id,
                max_results=10,
                order="date"
            )
            
            if not current_videos:
                return {'status': 'no_videos_found'}
            
            current_latest_id = current_videos[0]['id']['videoId']
            stored_latest_id = self.monitoring_data[channel_id]['latest_video_id']
            
            new_videos = []
            
            # 新しい動画をチェック
            if current_latest_id != stored_latest_id:
                for video in current_videos:
                    video_id = video['id']['videoId']
                    if video_id == stored_latest_id:
                        break
                    new_videos.append(video)
                
                # 監視データ更新
                self.monitoring_data[channel_id]['latest_video_id'] = current_latest_id
                self.monitoring_data[channel_id]['last_check'] = datetime.now()
                self.monitoring_data[channel_id]['new_videos_found'].extend(new_videos)
                
                # コールバック実行
                if callback and new_videos:
                    callback({
                        'event': 'new_videos_found',
                        'channel_id': channel_id,
                        'new_videos': new_videos,
                        'count': len(new_videos)
                    })
            
            return {
                'status': 'checked',
                'channel_id': channel_id,
                'new_videos_count': len(new_videos),
                'new_videos': new_videos,
                'last_check': datetime.now()
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"新アップロードチェックに失敗しました: {str(e)}")

    def monitor_view_milestones(self, video_id, milestones: List[int], callback: Callable = None):
        """再生数マイルストーンを監視
        
        Args:
            video_id (str): 監視する動画ID
            milestones (list): マイルストーン数値のリスト
            callback (callable): マイルストーン到達時のコールバック関数
            
        Returns:
            dict: 監視設定情報
        """
        try:
            # 現在の再生数取得
            video_info = self.get_video_info(video_id)
            current_views = int(video_info.get('statistics', {}).get('viewCount', 0))
            
            # 未達成のマイルストーンをフィルタ
            pending_milestones = [m for m in milestones if m > current_views]
            
            # 監視データ設定
            milestone_key = f"milestone_{video_id}"
            self.monitoring_data[milestone_key] = {
                'video_id': video_id,
                'current_views': current_views,
                'pending_milestones': sorted(pending_milestones),
                'achieved_milestones': [m for m in milestones if m <= current_views],
                'last_check': datetime.now()
            }
            
            return {
                'video_id': video_id,
                'current_views': current_views,
                'pending_milestones': pending_milestones,
                'monitoring_started': datetime.now()
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"マイルストーン監視設定に失敗しました: {str(e)}")

    def check_milestone_progress(self, video_id, callback: Callable = None):
        """マイルストーン進捗をチェック
        
        Args:
            video_id (str): チェックする動画ID
            callback (callable): マイルストーン到達時のコールバック関数
            
        Returns:
            dict: 進捗チェック結果
        """
        try:
            milestone_key = f"milestone_{video_id}"
            
            if milestone_key not in self.monitoring_data:
                raise YouTubeAPIError(f"動画 {video_id} はマイルストーン監視対象ではありません")
            
            # 現在の再生数取得
            video_info = self.get_video_info(video_id)
            current_views = int(video_info.get('statistics', {}).get('viewCount', 0))
            
            monitoring_data = self.monitoring_data[milestone_key]
            previous_views = monitoring_data['current_views']
            pending_milestones = monitoring_data['pending_milestones']
            
            # 新しく達成されたマイルストーン
            newly_achieved = []
            remaining_milestones = []
            
            for milestone in pending_milestones:
                if current_views >= milestone:
                    newly_achieved.append(milestone)
                    monitoring_data['achieved_milestones'].append(milestone)
                else:
                    remaining_milestones.append(milestone)
            
            # 監視データ更新
            monitoring_data['current_views'] = current_views
            monitoring_data['pending_milestones'] = remaining_milestones
            monitoring_data['last_check'] = datetime.now()
            
            # コールバック実行
            if callback and newly_achieved:
                callback({
                    'event': 'milestone_achieved',
                    'video_id': video_id,
                    'newly_achieved': newly_achieved,
                    'current_views': current_views,
                    'video_info': video_info
                })
            
            return {
                'video_id': video_id,
                'current_views': current_views,
                'previous_views': previous_views,
                'view_increase': current_views - previous_views,
                'newly_achieved_milestones': newly_achieved,
                'remaining_milestones': remaining_milestones
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"マイルストーン進捗チェックに失敗しました: {str(e)}")

    def detect_trending_keywords(self, region_code="JP", category_id=None):
        """トレンドキーワードを検出
        
        Args:
            region_code (str): 地域コード
            category_id (str): カテゴリID
            
        Returns:
            dict: トレンドキーワード分析結果
        """
        try:
            # トレンド動画取得
            trending_videos = self.get_trending_videos(
                region_code=region_code,
                category_id=category_id,
                max_results=50
            )
            
            # キーワード抽出
            keyword_frequency = {}
            common_words = {'の', 'に', 'を', 'が', 'は', 'で', 'と', 'から', 'まで', 'より', 'も', 'や'}
            
            for video in trending_videos:
                title = video['snippet']['title']
                description = video['snippet'].get('description', '')
                
                # タイトルからキーワード抽出
                title_words = title.split()
                for word in title_words:
                    word_clean = word.strip('【】()（）｜|').lower()
                    if len(word_clean) > 1 and word_clean not in common_words:
                        keyword_frequency[word_clean] = keyword_frequency.get(word_clean, 0) + 2
                
                # 説明文からもキーワード抽出（重要度低）
                desc_words = description.split()[:20]  # 最初の20語のみ
                for word in desc_words:
                    word_clean = word.strip('【】()（）｜|').lower()
                    if len(word_clean) > 1 and word_clean not in common_words:
                        keyword_frequency[word_clean] = keyword_frequency.get(word_clean, 0) + 1
            
            # 頻出キーワードソート
            trending_keywords = sorted(
                keyword_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )[:20]
            
            # カテゴリ分析
            category_distribution = {}
            for video in trending_videos:
                category = video['snippet'].get('categoryId', 'unknown')
                category_distribution[category] = category_distribution.get(category, 0) + 1
            
            return {
                'trending_keywords': trending_keywords,
                'category_distribution': category_distribution,
                'analysis_date': datetime.now().isoformat(),
                'region_code': region_code,
                'total_videos_analyzed': len(trending_videos)
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"トレンドキーワード検出に失敗しました: {str(e)}")

    def setup_webhook_notifications(self, webhook_url, events: List[str]):
        """Webhook通知を設定
        
        Args:
            webhook_url (str): WebhookのURL
            events (list): 通知するイベントリスト
            
        Returns:
            dict: Webhook設定情報
        """
        self.monitoring_data['webhook_config'] = {
            'url': webhook_url,
            'events': events,
            'created_at': datetime.now()
        }
        
        return {
            'webhook_url': webhook_url,
            'monitored_events': events,
            'status': 'configured'
        }

    def save_monitoring_state(self, filepath):
        """監視状態を保存
        
        Args:
            filepath (str): 保存ファイルパス
        """
        try:
            # datetime オブジェクトを文字列に変換
            serializable_data = {}
            for key, value in self.monitoring_data.items():
                if isinstance(value, dict):
                    serializable_value = {}
                    for k, v in value.items():
                        if isinstance(v, datetime):
                            serializable_value[k] = v.isoformat()
                        else:
                            serializable_value[k] = v
                    serializable_data[key] = serializable_value
                else:
                    serializable_data[key] = value
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            raise YouTubeAPIError(f"監視状態保存に失敗しました: {str(e)}")

    def load_monitoring_state(self, filepath):
        """監視状態を読み込み
        
        Args:
            filepath (str): 読み込みファイルパス
        """
        try:
            if not os.path.exists(filepath):
                return
                
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 文字列を datetime オブジェクトに変換
            for key, value in data.items():
                if isinstance(value, dict):
                    for k, v in value.items():
                        if k in ['last_check', 'monitoring_started', 'created_at'] and isinstance(v, str):
                            try:
                                value[k] = datetime.fromisoformat(v)
                            except:
                                pass
            
            self.monitoring_data = data
            
        except Exception as e:
            raise YouTubeAPIError(f"監視状態読み込みに失敗しました: {str(e)}")
