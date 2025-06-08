"""
YouTube.py3 - リアルタイム機能モジュール

リアルタイム通知、ライブチャット監視、チャンネルアクティビティ監視機能を提供します。
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Any, Optional
from .base import YouTubeAPIBase
from .exceptions import YouTubeAPIError
import logging

logger = logging.getLogger(__name__)


class RealtimeMixin(YouTubeAPIBase):
    """リアルタイム機能を提供するMixin"""
    
    def __init__(self):
        super().__init__()
        self.realtime_monitors = {}
        self.webhook_callbacks = {}
        self.live_chat_threads = {}
        
    def setup_webhook_notifications(self, callback_url: str, events: List[str]) -> Dict[str, Any]:
        """リアルタイム通知のセットアップ
        
        Args:
            callback_url (str): コールバックURL
            events (list): 監視するイベントタイプ
            
        Returns:
            dict: セットアップ結果
        """
        try:
            webhook_id = f"webhook_{len(self.webhook_callbacks)}"
            
            self.webhook_callbacks[webhook_id] = {
                'callback_url': callback_url,
                'events': events,
                'created_at': datetime.now(),
                'status': 'active'
            }
            
            logger.info(f"Webhook {webhook_id} が設定されました")
            
            return {
                'webhook_id': webhook_id,
                'callback_url': callback_url,
                'events': events,
                'status': 'active',
                'message': 'Webhook通知が正常に設定されました'
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"Webhook設定に失敗しました: {str(e)}")
    
    def stream_live_chat(self, video_id: str, callback: Optional[Callable] = None, 
                        interval: int = 5) -> Dict[str, Any]:
        """ライブチャットのリアルタイムストリーミング
        
        Args:
            video_id (str): ライブ動画ID
            callback (callable): チャットメッセージ受信時のコールバック
            interval (int): チェック間隔（秒）
            
        Returns:
            dict: ストリーミング設定情報
        """
        try:
            # ライブ動画の確認
            video_info = self.get_video_info(video_id)
            if not video_info.get('snippet', {}).get('liveBroadcastContent') == 'live':
                raise YouTubeAPIError(f"動画 {video_id} はライブ配信ではありません")
            
            # ライブチャットID取得
            live_chat_id = video_info.get('liveStreamingDetails', {}).get('activeLiveChatId')
            if not live_chat_id:
                raise YouTubeAPIError("ライブチャットIDが取得できません")
            
            def monitor_live_chat():
                """ライブチャット監視スレッド"""
                last_message_time = datetime.now()
                
                while video_id in self.live_chat_threads:
                    try:
                        # ライブチャットメッセージ取得
                        request = self.youtube.liveChatMessages().list(
                            liveChatId=live_chat_id,
                            part='snippet,authorDetails'
                        )
                        response = self._execute_request(request)
                        
                        messages = response.get('items', [])
                        new_messages = []
                        
                        for message in messages:
                            message_time = datetime.fromisoformat(
                                message['snippet']['publishedAt'].replace('Z', '+00:00')
                            )
                            
                            if message_time > last_message_time:
                                new_messages.append({
                                    'message_id': message['id'],
                                    'author': message['authorDetails']['displayName'],
                                    'message': message['snippet']['displayMessage'],
                                    'timestamp': message_time.isoformat(),
                                    'author_channel_id': message['authorDetails'].get('channelId', ''),
                                    'is_moderator': message['authorDetails'].get('isChatModerator', False),
                                    'is_owner': message['authorDetails'].get('isChatOwner', False)
                                })
                        
                        if new_messages and callback:
                            callback({
                                'event': 'new_chat_messages',
                                'video_id': video_id,
                                'live_chat_id': live_chat_id,
                                'messages': new_messages,
                                'message_count': len(new_messages)
                            })
                        
                        if new_messages:
                            last_message_time = max(
                                datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
                                for msg in new_messages
                            )
                        
                        time.sleep(interval)
                        
                    except Exception as e:
                        logger.error(f"ライブチャット監視エラー: {str(e)}")
                        time.sleep(interval * 2)  # エラー時は間隔を延ばす
            
            # 監視スレッド開始
            thread = threading.Thread(target=monitor_live_chat, daemon=True)
            self.live_chat_threads[video_id] = thread
            thread.start()
            
            return {
                'video_id': video_id,
                'live_chat_id': live_chat_id,
                'monitoring': True,
                'interval': interval,
                'started_at': datetime.now().isoformat(),
                'message': 'ライブチャット監視を開始しました'
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"ライブチャットストリーミング開始に失敗しました: {str(e)}")
    
    def monitor_channel_activity(self, channel_id: str, interval: int = 60, 
                               callback: Optional[Callable] = None) -> Dict[str, Any]:
        """チャンネルアクティビティのリアルタイム監視
        
        Args:
            channel_id (str): 監視するチャンネルID
            interval (int): チェック間隔（秒）
            callback (callable): アクティビティ検出時のコールバック
            
        Returns:
            dict: 監視設定情報
        """
        try:
            def monitor_activity():
                """チャンネルアクティビティ監視スレッド"""
                last_check = datetime.now() - timedelta(hours=1)
                
                while channel_id in self.realtime_monitors:
                    try:
                        # 最新動画取得
                        recent_videos = self.search_videos_filtered(
                            channel_id=channel_id,
                            max_results=5,
                            order='date',
                            published_after=last_check.isoformat()
                        )
                        
                        # 新しい動画があった場合
                        if recent_videos:
                            new_videos = []
                            for video in recent_videos:
                                published_at = datetime.fromisoformat(
                                    video['snippet']['publishedAt'].replace('Z', '+00:00')
                                )
                                
                                if published_at > last_check:
                                    new_videos.append({
                                        'video_id': video['id'],
                                        'title': video['snippet']['title'],
                                        'published_at': published_at.isoformat(),
                                        'description': video['snippet'].get('description', '')[:200] + '...',
                                        'thumbnail': video['snippet']['thumbnails'].get('medium', {}).get('url', '')
                                    })
                            
                            if new_videos and callback:
                                callback({
                                    'event': 'new_videos_uploaded',
                                    'channel_id': channel_id,
                                    'new_videos': new_videos,
                                    'video_count': len(new_videos),
                                    'detected_at': datetime.now().isoformat()
                                })
                        
                        # チャンネル統計の変化監視
                        current_stats = self.get_channel_info(channel_id)
                        if hasattr(self, '_last_channel_stats') and channel_id in self._last_channel_stats:
                            last_stats = self._last_channel_stats[channel_id]
                            current_subs = int(current_stats.get('statistics', {}).get('subscriberCount', 0))
                            last_subs = int(last_stats.get('statistics', {}).get('subscriberCount', 0))
                            
                            if current_subs != last_subs and callback:
                                callback({
                                    'event': 'subscriber_count_changed',
                                    'channel_id': channel_id,
                                    'previous_count': last_subs,
                                    'current_count': current_subs,
                                    'change': current_subs - last_subs,
                                    'detected_at': datetime.now().isoformat()
                                })
                        
                        # 統計を保存
                        if not hasattr(self, '_last_channel_stats'):
                            self._last_channel_stats = {}
                        self._last_channel_stats[channel_id] = current_stats
                        
                        last_check = datetime.now()
                        time.sleep(interval)
                        
                    except Exception as e:
                        logger.error(f"チャンネルアクティビティ監視エラー: {str(e)}")
                        time.sleep(interval * 2)
            
            # 監視スレッド開始
            thread = threading.Thread(target=monitor_activity, daemon=True)
            self.realtime_monitors[channel_id] = thread
            thread.start()
            
            return {
                'channel_id': channel_id,
                'monitoring': True,
                'interval': interval,
                'started_at': datetime.now().isoformat(),
                'events': ['new_videos', 'subscriber_changes'],
                'message': 'チャンネルアクティビティ監視を開始しました'
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"チャンネルアクティビティ監視開始に失敗しました: {str(e)}")
    
    def stop_live_chat_monitoring(self, video_id: str) -> Dict[str, Any]:
        """ライブチャット監視停止"""
        try:
            if video_id in self.live_chat_threads:
                del self.live_chat_threads[video_id]
                return {
                    'video_id': video_id,
                    'status': 'stopped',
                    'message': 'ライブチャット監視を停止しました'
                }
            else:
                return {
                    'video_id': video_id,
                    'status': 'not_found',
                    'message': '指定された動画の監視は実行されていません'
                }
        except Exception as e:
            raise YouTubeAPIError(f"ライブチャット監視停止に失敗しました: {str(e)}")
    
    def stop_channel_monitoring(self, channel_id: str) -> Dict[str, Any]:
        """チャンネル監視停止"""
        try:
            if channel_id in self.realtime_monitors:
                del self.realtime_monitors[channel_id]
                return {
                    'channel_id': channel_id,
                    'status': 'stopped',
                    'message': 'チャンネル監視を停止しました'
                }
            else:
                return {
                    'channel_id': channel_id,
                    'status': 'not_found',
                    'message': '指定されたチャンネルの監視は実行されていません'
                }
        except Exception as e:
            raise YouTubeAPIError(f"チャンネル監視停止に失敗しました: {str(e)}")
    
    def get_active_monitors(self) -> Dict[str, Any]:
        """アクティブな監視の一覧取得"""
        return {
            'realtime_monitors': list(self.realtime_monitors.keys()),
            'live_chat_monitors': list(self.live_chat_threads.keys()),
            'webhook_callbacks': list(self.webhook_callbacks.keys()),
            'total_active': len(self.realtime_monitors) + len(self.live_chat_threads)
        }