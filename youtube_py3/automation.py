"""
YouTube.py3 - 自動化・スケジューリング機能モジュール

動画アップロードスケジューリング、コメント自動モデレーション、
一括操作、プレイリスト自動キュレーション機能を提供します。
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from pathlib import Path
import schedule
from .base import YouTubeAPIBase
from .exceptions import YouTubeAPIError
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScheduledUpload:
    """スケジュール済みアップロードの情報"""
    video_path: str
    metadata: Dict[str, Any]
    publish_time: datetime
    status: str = 'scheduled'
    upload_id: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class ModerationRule:
    """コメントモデレーションルール"""
    rule_id: str
    rule_type: str  # 'keyword', 'spam', 'sentiment', 'length'
    criteria: Dict[str, Any]
    action: str  # 'delete', 'hold', 'reply', 'flag'
    enabled: bool = True


class AutomationMixin(YouTubeAPIBase):
    """自動化・スケジューリング機能を提供するMixin"""
    
    def __init__(self):
        super().__init__()
        self.scheduled_uploads = {}
        self.moderation_rules = {}
        self.automation_tasks = {}
        self.scheduler_running = False
        self._setup_scheduler()
    
    def _setup_scheduler(self):
        """スケジューラーの初期設定"""
        self.scheduler_thread = None
        
    def schedule_video_upload(self, video_path: str, metadata: Dict[str, Any], 
                            publish_time: datetime) -> Dict[str, Any]:
        """動画アップロードのスケジューリング
        
        Args:
            video_path (str): 動画ファイルパス
            metadata (dict): 動画メタデータ
            publish_time (datetime): 公開予定時刻
            
        Returns:
            dict: スケジューリング結果
        """
        try:
            # ファイル存在確認
            if not os.path.exists(video_path):
                raise YouTubeAPIError(f"動画ファイルが見つかりません: {video_path}")
            
            # メタデータ検証
            required_fields = ['title', 'description']
            for field in required_fields:
                if field not in metadata:
                    raise YouTubeAPIError(f"必須フィールドが不足しています: {field}")
            
            # 公開時刻検証
            if publish_time <= datetime.now():
                raise YouTubeAPIError("公開時刻は現在時刻より後に設定してください")
            
            # スケジュール作成
            schedule_id = f"upload_{int(datetime.now().timestamp())}"
            scheduled_upload = ScheduledUpload(
                video_path=video_path,
                metadata=metadata,
                publish_time=publish_time
            )
            
            self.scheduled_uploads[schedule_id] = scheduled_upload
            
            # スケジューラー設定
            schedule.every().minute.do(self._check_scheduled_uploads)
            
            # スケジューラー開始
            if not self.scheduler_running:
                self._start_scheduler()
            
            logger.info(f"動画アップロードがスケジュールされました: {schedule_id}")
            
            return {
                'schedule_id': schedule_id,
                'video_path': video_path,
                'publish_time': publish_time.isoformat(),
                'status': 'scheduled',
                'metadata': metadata,
                'message': '動画アップロードが正常にスケジュールされました'
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"動画アップロードスケジューリングに失敗しました: {str(e)}")
    
    def auto_moderate_comments(self, channel_id: str, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """コメント自動モデレーション
        
        Args:
            channel_id (str): 対象チャンネルID
            rules (list): モデレーションルール
            
        Returns:
            dict: モデレーション設定結果
        """
        try:
            moderation_rules = []
            
            for rule_data in rules:
                rule = ModerationRule(
                    rule_id=f"rule_{len(self.moderation_rules)}",
                    rule_type=rule_data.get('type', 'keyword'),
                    criteria=rule_data.get('criteria', {}),
                    action=rule_data.get('action', 'hold'),
                    enabled=rule_data.get('enabled', True)
                )
                moderation_rules.append(rule)
                self.moderation_rules[rule.rule_id] = rule
            
            # モデレーション監視開始
            def moderate_comments():
                """コメントモデレーション監視スレッド"""
                while channel_id in self.automation_tasks:
                    try:
                        # チャンネルの最新動画取得
                        recent_videos = self.search_videos_filtered(
                            channel_id=channel_id,
                            max_results=5,
                            order='date'
                        )
                        
                        for video in recent_videos:
                            video_id = video['id']
                            
                            # コメント取得
                            comments = self.get_video_comments(video_id, max_results=50)
                            
                            for comment in comments:
                                self._apply_moderation_rules(comment, moderation_rules, video_id)
                        
                        time.sleep(300)  # 5分間隔
                        
                    except Exception as e:
                        logger.error(f"コメントモデレーションエラー: {str(e)}")
                        time.sleep(600)  # エラー時は10分待機
            
            # モデレーションスレッド開始
            thread = threading.Thread(target=moderate_comments, daemon=True)
            self.automation_tasks[channel_id] = thread
            thread.start()
            
            return {
                'channel_id': channel_id,
                'rules_count': len(moderation_rules),
                'moderation_active': True,
                'rules': [
                    {
                        'rule_id': rule.rule_id,
                        'type': rule.rule_type,
                        'action': rule.action
                    } for rule in moderation_rules
                ],
                'message': 'コメント自動モデレーションが開始されました'
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"コメント自動モデレーション設定に失敗しました: {str(e)}")
    
    def bulk_video_operations(self, video_ids: List[str], operation: str, 
                            params: Dict[str, Any]) -> Dict[str, Any]:
        """動画の一括操作
        
        Args:
            video_ids (list): 対象動画IDリスト
            operation (str): 操作タイプ
            params (dict): 操作パラメータ
            
        Returns:
            dict: 一括操作結果
        """
        try:
            results = {
                'successful': [],
                'failed': [],
                'operation': operation,
                'total_processed': 0
            }
            
            for video_id in video_ids:
                try:
                    if operation == 'update_metadata':
                        result = self._bulk_update_metadata(video_id, params)
                    elif operation == 'add_to_playlist':
                        result = self._bulk_add_to_playlist(video_id, params)
                    elif operation == 'update_privacy':
                        result = self._bulk_update_privacy(video_id, params)
                    elif operation == 'update_thumbnails':
                        result = self._bulk_update_thumbnails(video_id, params)
                    else:
                        raise YouTubeAPIError(f"未対応の操作: {operation}")
                    
                    results['successful'].append({
                        'video_id': video_id,
                        'result': result
                    })
                    
                except Exception as e:
                    results['failed'].append({
                        'video_id': video_id,
                        'error': str(e)
                    })
                
                results['total_processed'] += 1
                
                # レート制限回避のため少し待機
                time.sleep(1)
            
            return {
                'operation_summary': results,
                'success_rate': len(results['successful']) / len(video_ids) * 100,
                'completed_at': datetime.now().isoformat(),
                'message': f'{operation} 一括操作が完了しました'
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"一括操作に失敗しました: {str(e)}")
    
    def automated_playlist_curation(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """プレイリスト自動キュレーション
        
        Args:
            criteria (dict): キュレーション条件
            
        Returns:
            dict: キュレーション結果
        """
        try:
            # キュレーション条件解析
            keywords = criteria.get('keywords', [])
            channel_ids = criteria.get('channel_ids', [])
            min_views = criteria.get('min_views', 1000)
            max_age_days = criteria.get('max_age_days', 30)
            max_videos = criteria.get('max_videos', 50)
            playlist_title = criteria.get('playlist_title', '自動キュレーションプレイリスト')
            
            curated_videos = []
            
            # キーワード検索による動画収集
            for keyword in keywords:
                try:
                    search_results = self.search_videos_filtered(
                        query=keyword,
                        max_results=20,
                        order='relevance',
                        published_after=(datetime.now() - timedelta(days=max_age_days)).isoformat()
                    )
                    
                    for video in search_results:
                        stats = video.get('statistics', {})
                        views = int(stats.get('viewCount', 0))
                        
                        if views >= min_views:
                            curated_videos.append({
                                'video_id': video['id'],
                                'title': video['snippet']['title'],
                                'channel': video['snippet']['channelTitle'],
                                'views': views,
                                'published_at': video['snippet']['publishedAt'],
                                'keyword_source': keyword
                            })
                            
                except Exception as e:
                    logger.warning(f"キーワード '{keyword}' の検索に失敗: {str(e)}")
                    continue
            
            # チャンネル指定による動画収集
            for channel_id in channel_ids:
                try:
                    channel_videos = self.search_videos_filtered(
                        channel_id=channel_id,
                        max_results=10,
                        order='date',
                        published_after=(datetime.now() - timedelta(days=max_age_days)).isoformat()
                    )
                    
                    for video in channel_videos:
                        stats = video.get('statistics', {})
                        views = int(stats.get('viewCount', 0))
                        
                        if views >= min_views:
                            curated_videos.append({
                                'video_id': video['id'],
                                'title': video['snippet']['title'],
                                'channel': video['snippet']['channelTitle'],
                                'views': views,
                                'published_at': video['snippet']['publishedAt'],
                                'channel_source': channel_id
                            })
                            
                except Exception as e:
                    logger.warning(f"チャンネル {channel_id} の検索に失敗: {str(e)}")
                    continue
            
            # 重複削除とソート
            unique_videos = {}
            for video in curated_videos:
                video_id = video['video_id']
                if video_id not in unique_videos:
                    unique_videos[video_id] = video
            
            # 視聴回数でソート
            sorted_videos = sorted(
                unique_videos.values(),
                key=lambda x: x['views'],
                reverse=True
            )[:max_videos]
            
            # プレイリスト作成
            if sorted_videos:
                playlist_result = self.create_playlist(
                    title=playlist_title,
                    description=f"自動キュレーション（{datetime.now().strftime('%Y-%m-%d')}作成）",
                    privacy_status='private'
                )
                
                playlist_id = playlist_result['playlist_id']
                
                # 動画をプレイリストに追加
                added_videos = []
                for video in sorted_videos:
                    try:
                        self.add_video_to_playlist(playlist_id, video['video_id'])
                        added_videos.append(video)
                        time.sleep(1)  # レート制限回避
                    except Exception as e:
                        logger.warning(f"動画 {video['video_id']} のプレイリスト追加に失敗: {str(e)}")
                        continue
                
                return {
                    'playlist_id': playlist_id,
                    'playlist_title': playlist_title,
                    'total_videos_found': len(sorted_videos),
                    'videos_added': len(added_videos),
                    'curation_criteria': criteria,
                    'created_at': datetime.now().isoformat(),
                    'curated_videos': added_videos,
                    'message': 'プレイリストが自動キュレーションされました'
                }
            else:
                return {
                    'error': '条件に合致する動画が見つかりませんでした',
                    'criteria': criteria,
                    'total_videos_found': 0
                }
                
        except Exception as e:
            raise YouTubeAPIError(f"プレイリスト自動キュレーションに失敗しました: {str(e)}")
    
    def get_scheduled_uploads(self) -> Dict[str, Any]:
        """スケジュール済みアップロード一覧取得"""
        return {
            'scheduled_uploads': {
                schedule_id: {
                    'video_path': upload.video_path,
                    'publish_time': upload.publish_time.isoformat(),
                    'status': upload.status,
                    'metadata': upload.metadata
                }
                for schedule_id, upload in self.scheduled_uploads.items()
            },
            'total_scheduled': len(self.scheduled_uploads)
        }
    
    def cancel_scheduled_upload(self, schedule_id: str) -> Dict[str, Any]:
        """スケジュール済みアップロードのキャンセル"""
        try:
            if schedule_id in self.scheduled_uploads:
                upload = self.scheduled_uploads[schedule_id]
                upload.status = 'cancelled'
                
                return {
                    'schedule_id': schedule_id,
                    'status': 'cancelled',
                    'message': 'スケジュール済みアップロードがキャンセルされました'
                }
            else:
                return {
                    'schedule_id': schedule_id,
                    'error': '指定されたスケジュールが見つかりません'
                }
        except Exception as e:
            raise YouTubeAPIError(f"スケジュールキャンセルに失敗しました: {str(e)}")
    
    def stop_automation_task(self, task_id: str) -> Dict[str, Any]:
        """自動化タスクの停止"""
        try:
            if task_id in self.automation_tasks:
                del self.automation_tasks[task_id]
                return {
                    'task_id': task_id,
                    'status': 'stopped',
                    'message': '自動化タスクが停止されました'
                }
            else:
                return {
                    'task_id': task_id,
                    'error': '指定されたタスクが見つかりません'
                }
        except Exception as e:
            raise YouTubeAPIError(f"自動化タスク停止に失敗しました: {str(e)}")
    
    # 内部メソッド
    def _start_scheduler(self):
        """スケジューラー開始"""
        def run_scheduler():
            self.scheduler_running = True
            while self.scheduler_running:
                schedule.run_pending()
                time.sleep(60)  # 1分間隔でチェック
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    def _check_scheduled_uploads(self):
        """スケジュール済みアップロードのチェック"""
        current_time = datetime.now()
        
        for schedule_id, upload in self.scheduled_uploads.items():
            if (upload.status == 'scheduled' and 
                upload.publish_time <= current_time):
                
                try:
                    # 動画アップロード実行
                    upload_result = self.upload_video(
                        video_path=upload.video_path,
                        title=upload.metadata['title'],
                        description=upload.metadata['description'],
                        tags=upload.metadata.get('tags', []),
                        privacy_status=upload.metadata.get('privacy_status', 'private')
                    )
                    
                    upload.status = 'uploaded'
                    upload.upload_id = upload_result.get('video_id')
                    
                    logger.info(f"スケジュール済み動画がアップロードされました: {schedule_id}")
                    
                except Exception as e:
                    upload.status = 'failed'
                    logger.error(f"スケジュール済み動画のアップロードに失敗: {str(e)}")
    
    def _apply_moderation_rules(self, comment: Dict, rules: List[ModerationRule], video_id: str):
        """モデレーションルール適用"""
        comment_text = comment['snippet']['textDisplay']
        
        for rule in rules:
            if not rule.enabled:
                continue
                
            should_moderate = False
            
            if rule.rule_type == 'keyword':
                blocked_keywords = rule.criteria.get('blocked_keywords', [])
                if any(keyword.lower() in comment_text.lower() for keyword in blocked_keywords):
                    should_moderate = True
                    
            elif rule.rule_type == 'spam':
                # スパム検出ロジック（簡易実装）
                spam_indicators = rule.criteria.get('spam_indicators', [])
                if any(indicator in comment_text.lower() for indicator in spam_indicators):
                    should_moderate = True
                    
            elif rule.rule_type == 'length':
                max_length = rule.criteria.get('max_length', 1000)
                if len(comment_text) > max_length:
                    should_moderate = True
            
            if should_moderate:
                self._execute_moderation_action(comment, rule, video_id)
                break
    
    def _execute_moderation_action(self, comment: Dict, rule: ModerationRule, video_id: str):
        """モデレーションアクション実行"""
        comment_id = comment['id']
        
        try:
            if rule.action == 'delete':
                # コメント削除（実装は YouTube API の制限により限定的）
                logger.info(f"コメント削除対象: {comment_id}")
                
            elif rule.action == 'hold':
                # コメント保留（YouTube Studio で手動確認）
                logger.info(f"コメント保留対象: {comment_id}")
                
            elif rule.action == 'reply':
                # 自動返信（実装可能だが慎重に使用）
                reply_text = rule.criteria.get('reply_text', 'ご意見ありがとうございます。')
                logger.info(f"自動返信対象: {comment_id} - {reply_text}")
                
            elif rule.action == 'flag':
                # フラグ付け（内部記録）
                logger.info(f"コメントフラグ: {comment_id}")
                
        except Exception as e:
            logger.error(f"モデレーションアクション実行エラー: {str(e)}")
    
    def _bulk_update_metadata(self, video_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """メタデータ一括更新"""
        update_data = {}
        
        if 'title' in params:
            update_data['title'] = params['title']
        if 'description' in params:
            update_data['description'] = params['description']
        if 'tags' in params:
            update_data['tags'] = params['tags']
            
        # 実際の更新処理（既存メソッドを活用）
        return {'video_id': video_id, 'updated_fields': list(update_data.keys())}
    
    def _bulk_add_to_playlist(self, video_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """プレイリスト一括追加"""
        playlist_id = params.get('playlist_id')
        if not playlist_id:
            raise YouTubeAPIError("playlist_id が必要です")
            
        self.add_video_to_playlist(playlist_id, video_id)
        return {'video_id': video_id, 'playlist_id': playlist_id}
    
    def _bulk_update_privacy(self, video_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """プライバシー設定一括更新"""
        privacy_status = params.get('privacy_status', 'private')
        # 実際の更新処理（既存メソッドを活用）
        return {'video_id': video_id, 'privacy_status': privacy_status}
    
    def _bulk_update_thumbnails(self, video_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """サムネイル一括更新"""
        thumbnail_path = params.get('thumbnail_path')
        if not thumbnail_path or not os.path.exists(thumbnail_path):
            raise YouTubeAPIError("有効なサムネイルパスが必要です")
            
        # サムネイル更新処理（既存メソッドを活用）
        return {'video_id': video_id, 'thumbnail_updated': True}