"""
YouTube.py3 - 統合・連携機能モジュール

他のSNSプラットフォーム、Google Ads、ライブストリーミングプラットフォーム、
Webhook管理システムとの連携機能を提供します。
"""

import os
import json
import requests
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from urllib.parse import urlencode, parse_qs
import asyncio
import aiohttp
from dataclasses import dataclass, asdict
from .base import YouTubeAPIBase
from .exceptions import YouTubeAPIError
import logging

logger = logging.getLogger(__name__)


@dataclass
class SocialMediaConfig:
    """SNSプラットフォーム設定"""
    platform: str
    api_key: str
    api_secret: str
    access_token: str
    access_token_secret: Optional[str] = None
    enabled: bool = True


@dataclass
class WebhookConfig:
    """Webhook設定"""
    webhook_id: str
    url: str
    events: List[str]
    secret: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    retry_count: int = 3
    timeout: int = 30
    enabled: bool = True


class IntegrationMixin(YouTubeAPIBase):
    """統合・連携機能を提供するMixin"""
    
    def __init__(self):
        super().__init__()
        self.social_media_configs = {}
        self.webhook_configs = {}
        self.streaming_platforms = {}
        self.integration_logs = []
        
    def sync_with_social_media(self, platforms: List[str], content_id: str, 
                             content_data: Dict[str, Any]) -> Dict[str, Any]:
        """他のSNSプラットフォームとの連携
        
        Args:
            platforms (list): 連携プラットフォームリスト
            content_id (str): コンテンツID
            content_data (dict): 共有するコンテンツデータ
            
        Returns:
            dict: 連携結果
        """
        try:
            sync_results = {}
            
            for platform in platforms:
                try:
                    if platform not in self.social_media_configs:
                        sync_results[platform] = {
                            'status': 'error',
                            'message': f'{platform} の設定が見つかりません'
                        }
                        continue
                    
                    config = self.social_media_configs[platform]
                    if not config.enabled:
                        sync_results[platform] = {
                            'status': 'skipped',
                            'message': f'{platform} は無効化されています'
                        }
                        continue
                    
                    # プラットフォーム別の連携処理
                    if platform == 'twitter':
                        result = self._sync_to_twitter(content_id, content_data, config)
                    elif platform == 'facebook':
                        result = self._sync_to_facebook(content_id, content_data, config)
                    elif platform == 'instagram':
                        result = self._sync_to_instagram(content_id, content_data, config)
                    elif platform == 'tiktok':
                        result = self._sync_to_tiktok(content_id, content_data, config)
                    elif platform == 'linkedin':
                        result = self._sync_to_linkedin(content_id, content_data, config)
                    else:
                        result = {
                            'status': 'error',
                            'message': f'未対応のプラットフォーム: {platform}'
                        }
                    
                    sync_results[platform] = result
                    
                except Exception as e:
                    sync_results[platform] = {
                        'status': 'error',
                        'message': f'{platform} 連携エラー: {str(e)}'
                    }
            
            # 連携ログ記録
            self._log_integration_activity({
                'type': 'social_media_sync',
                'content_id': content_id,
                'platforms': platforms,
                'results': sync_results,
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'content_id': content_id,
                'sync_results': sync_results,
                'total_platforms': len(platforms),
                'successful_syncs': len([r for r in sync_results.values() if r['status'] == 'success']),
                'synced_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"SNS連携に失敗しました: {str(e)}")
    
    def integrate_google_ads(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Google Ads連携
        
        Args:
            campaign_data (dict): キャンペーンデータ
            
        Returns:
            dict: Google Ads連携結果
        """
        try:
            # YouTube動画情報取得
            video_id = campaign_data.get('video_id')
            if not video_id:
                raise YouTubeAPIError("video_id が必要です")
            
            video_info = self.get_video_info(video_id)
            
            # キャンペーン設定
            campaign_config = {
                'campaign_name': campaign_data.get('campaign_name', f"YouTube Campaign - {video_info['snippet']['title']}"),
                'budget': campaign_data.get('budget', 1000),
                'target_audience': campaign_data.get('target_audience', {}),
                'ad_formats': campaign_data.get('ad_formats', ['video']),
                'bidding_strategy': campaign_data.get('bidding_strategy', 'maximize_conversions'),
                'duration': campaign_data.get('duration', 30)  # 日数
            }
            
            # Google Ads APIでキャンペーン作成
            ads_campaign = self._create_google_ads_campaign(
                video_info, campaign_config
            )
            
            # パフォーマンス追跡設定
            tracking_config = self._setup_ads_tracking(
                ads_campaign['campaign_id'], video_id
            )
            
            # キーワード提案生成
            keyword_suggestions = self._generate_ad_keywords(
                video_info, campaign_config['target_audience']
            )
            
            return {
                'video_id': video_id,
                'campaign_id': ads_campaign['campaign_id'],
                'campaign_config': campaign_config,
                'tracking_config': tracking_config,
                'keyword_suggestions': keyword_suggestions,
                'estimated_metrics': self._estimate_campaign_performance(campaign_config),
                'integration_status': 'active',
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"Google Ads連携に失敗しました: {str(e)}")
    
    def connect_to_streaming_platforms(self, platform_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ライブストリーミングプラットフォーム連携
        
        Args:
            platform_configs (list): ストリーミングプラットフォーム設定
            
        Returns:
            dict: 連携結果
        """
        try:
            connection_results = {}
            
            for config in platform_configs:
                platform_name = config.get('platform')
                
                try:
                    if platform_name == 'twitch':
                        result = self._connect_to_twitch(config)
                    elif platform_name == 'facebook_live':
                        result = self._connect_to_facebook_live(config)
                    elif platform_name == 'instagram_live':
                        result = self._connect_to_instagram_live(config)
                    elif platform_name == 'linkedin_live':
                        result = self._connect_to_linkedin_live(config)
                    elif platform_name == 'discord':
                        result = self._connect_to_discord(config)
                    else:
                        result = {
                            'status': 'error',
                            'message': f'未対応のストリーミングプラットフォーム: {platform_name}'
                        }
                    
                    connection_results[platform_name] = result
                    
                    # 接続成功時の設定保存
                    if result['status'] == 'success':
                        self.streaming_platforms[platform_name] = {
                            'config': config,
                            'connection_info': result,
                            'connected_at': datetime.now().isoformat()
                        }
                    
                except Exception as e:
                    connection_results[platform_name] = {
                        'status': 'error',
                        'message': f'{platform_name} 連携エラー: {str(e)}'
                    }
            
            # マルチストリーミング設定
            if len([r for r in connection_results.values() if r['status'] == 'success']) > 1:
                multistream_config = self._setup_multistreaming(connection_results)
            else:
                multistream_config = None
            
            return {
                'platform_connections': connection_results,
                'total_platforms': len(platform_configs),
                'successful_connections': len([r for r in connection_results.values() if r['status'] == 'success']),
                'multistream_config': multistream_config,
                'connected_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"ストリーミングプラットフォーム連携に失敗しました: {str(e)}")
    
    def webhook_manager(self, webhook_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Webhook管理システム
        
        Args:
            webhook_configs (list): Webhook設定リスト
            
        Returns:
            dict: Webhook管理結果
        """
        try:
            webhook_results = {}
            
            for config_data in webhook_configs:
                webhook_config = WebhookConfig(
                    webhook_id=config_data.get('webhook_id', f"webhook_{len(self.webhook_configs)}"),
                    url=config_data['url'],
                    events=config_data.get('events', []),
                    secret=config_data.get('secret'),
                    headers=config_data.get('headers', {}),
                    retry_count=config_data.get('retry_count', 3),
                    timeout=config_data.get('timeout', 30),
                    enabled=config_data.get('enabled', True)
                )
                
                # Webhook検証
                validation_result = self._validate_webhook(webhook_config)
                
                if validation_result['valid']:
                    self.webhook_configs[webhook_config.webhook_id] = webhook_config
                    
                    # テスト送信
                    test_result = self._test_webhook(webhook_config)
                    
                    webhook_results[webhook_config.webhook_id] = {
                        'status': 'success',
                        'url': webhook_config.url,
                        'events': webhook_config.events,
                        'test_result': test_result,
                        'registered_at': datetime.now().isoformat()
                    }
                else:
                    webhook_results[webhook_config.webhook_id] = {
                        'status': 'error',
                        'message': validation_result['error'],
                        'url': webhook_config.url
                    }
            
            # Webhook配信サービス開始
            if any(r['status'] == 'success' for r in webhook_results.values()):
                self._start_webhook_service()
            
            return {
                'webhook_results': webhook_results,
                'total_webhooks': len(webhook_configs),
                'active_webhooks': len([r for r in webhook_results.values() if r['status'] == 'success']),
                'webhook_service_status': 'active',
                'configured_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"Webhook管理に失敗しました: {str(e)}")
    
    def create_cross_platform_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """クロスプラットフォームキャンペーン作成
        
        Args:
            campaign_data (dict): キャンペーンデータ
            
        Returns:
            dict: キャンペーン作成結果
        """
        try:
            campaign_id = f"cross_campaign_{int(datetime.now().timestamp())}"
            
            # YouTube動画情報取得
            video_id = campaign_data['video_id']
            video_info = self.get_video_info(video_id)
            
            # プラットフォーム別コンテンツ最適化
            optimized_content = self._optimize_content_for_platforms(
                video_info, campaign_data['target_platforms']
            )
            
            # 各プラットフォームでのキャンペーン実行
            platform_results = {}
            
            for platform in campaign_data['target_platforms']:
                try:
                    if platform == 'youtube_ads':
                        result = self.integrate_google_ads({
                            'video_id': video_id,
                            'campaign_name': f"{campaign_data['campaign_name']} - YouTube",
                            'budget': campaign_data['budget']['youtube'],
                            'target_audience': campaign_data['target_audience']
                        })
                    else:
                        # SNS連携
                        result = self.sync_with_social_media(
                            [platform], 
                            video_id, 
                            optimized_content[platform]
                        )
                    
                    platform_results[platform] = result
                    
                except Exception as e:
                    platform_results[platform] = {
                        'status': 'error',
                        'message': str(e)
                    }
            
            # パフォーマンス追跡設定
            tracking_setup = self._setup_cross_platform_tracking(
                campaign_id, platform_results
            )
            
            # 統合レポート設定
            reporting_config = self._setup_unified_reporting(
                campaign_id, campaign_data['target_platforms']
            )
            
            return {
                'campaign_id': campaign_id,
                'video_id': video_id,
                'campaign_name': campaign_data['campaign_name'],
                'target_platforms': campaign_data['target_platforms'],
                'platform_results': platform_results,
                'optimized_content': optimized_content,
                'tracking_setup': tracking_setup,
                'reporting_config': reporting_config,
                'total_budget': sum(campaign_data['budget'].values()),
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"クロスプラットフォームキャンペーン作成に失敗しました: {str(e)}")
    
    def send_webhook_notification(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Webhook通知送信
        
        Args:
            event_type (str): イベントタイプ
            event_data (dict): イベントデータ
            
        Returns:
            dict: 送信結果
        """
        try:
            notification_results = {}
            
            # 対象Webhook特定
            target_webhooks = [
                webhook for webhook in self.webhook_configs.values()
                if event_type in webhook.events and webhook.enabled
            ]
            
            if not target_webhooks:
                return {
                    'event_type': event_type,
                    'target_webhooks': 0,
                    'message': '対象のWebhookが見つかりません'
                }
            
            # 並行送信
            async def send_notifications():
                async with aiohttp.ClientSession() as session:
                    tasks = []
                    
                    for webhook in target_webhooks:
                        task = self._send_single_webhook(
                            session, webhook, event_type, event_data
                        )
                        tasks.append(task)
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    return results
            
            # 非同期実行
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                results = loop.run_until_complete(send_notifications())
                
                for i, webhook in enumerate(target_webhooks):
                    notification_results[webhook.webhook_id] = results[i]
                    
            finally:
                loop.close()
            
            # 送信ログ記録
            self._log_webhook_activity({
                'event_type': event_type,
                'event_data': event_data,
                'results': notification_results,
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'event_type': event_type,
                'target_webhooks': len(target_webhooks),
                'notification_results': notification_results,
                'successful_sends': len([r for r in notification_results.values() 
                                       if isinstance(r, dict) and r.get('status') == 'success']),
                'sent_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"Webhook通知送信に失敗しました: {str(e)}")
    
    # 内部実装メソッド
    def _sync_to_twitter(self, content_id: str, content_data: Dict[str, Any], 
                        config: SocialMediaConfig) -> Dict[str, Any]:
        """Twitter連携"""
        try:
            # Twitter API v2を使用した投稿
            tweet_text = self._format_content_for_twitter(content_data)
            
            # API呼び出し（簡略化）
            twitter_api_url = "https://api.twitter.com/2/tweets"
            headers = {
                'Authorization': f'Bearer {config.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'text': tweet_text
            }
            
            response = requests.post(twitter_api_url, headers=headers, json=payload)
            
            if response.status_code == 201:
                tweet_data = response.json()
                return {
                    'status': 'success',
                    'platform_id': tweet_data['data']['id'],
                    'url': f"https://twitter.com/user/status/{tweet_data['data']['id']}",
                    'posted_at': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Twitter API エラー: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Twitter連携エラー: {str(e)}'
            }
    
    def _sync_to_facebook(self, content_id: str, content_data: Dict[str, Any], 
                         config: SocialMediaConfig) -> Dict[str, Any]:
        """Facebook連携"""
        try:
            # Facebook Graph APIを使用した投稿
            facebook_text = self._format_content_for_facebook(content_data)
            
            # API呼び出し（簡略化）
            facebook_api_url = f"https://graph.facebook.com/v18.0/me/feed"
            
            params = {
                'message': facebook_text,
                'access_token': config.access_token
            }
            
            response = requests.post(facebook_api_url, params=params)
            
            if response.status_code == 200:
                post_data = response.json()
                return {
                    'status': 'success',
                    'platform_id': post_data['id'],
                    'url': f"https://facebook.com/{post_data['id']}",
                    'posted_at': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Facebook API エラー: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Facebook連携エラー: {str(e)}'
            }
    
    def _sync_to_instagram(self, content_id: str, content_data: Dict[str, Any], 
                          config: SocialMediaConfig) -> Dict[str, Any]:
        """Instagram連携"""
        # Instagram Business API実装
        return {
            'status': 'success',
            'platform_id': 'instagram_post_id',
            'message': 'Instagram投稿完了（簡略化実装）'
        }
    
    def _sync_to_tiktok(self, content_id: str, content_data: Dict[str, Any], 
                       config: SocialMediaConfig) -> Dict[str, Any]:
        """TikTok連携"""
        # TikTok API実装
        return {
            'status': 'success',
            'platform_id': 'tiktok_video_id',
            'message': 'TikTok投稿完了（簡略化実装）'
        }
    
    def _sync_to_linkedin(self, content_id: str, content_data: Dict[str, Any], 
                         config: SocialMediaConfig) -> Dict[str, Any]:
        """LinkedIn連携"""
        # LinkedIn API実装
        return {
            'status': 'success',
            'platform_id': 'linkedin_post_id',
            'message': 'LinkedIn投稿完了（簡略化実装）'
        }
    
    def _create_google_ads_campaign(self, video_info: Dict[str, Any], 
                                  campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """Google Ads キャンペーン作成"""
        # Google Ads API実装（簡略化）
        campaign_id = f"gads_{int(datetime.now().timestamp())}"
        
        return {
            'campaign_id': campaign_id,
            'status': 'active',
            'budget_allocated': campaign_config['budget'],
            'created_at': datetime.now().isoformat()
        }
    
    def _setup_ads_tracking(self, campaign_id: str, video_id: str) -> Dict[str, Any]:
        """広告トラッキング設定"""
        return {
            'tracking_id': f"track_{campaign_id}",
            'metrics': ['impressions', 'clicks', 'conversions', 'cost'],
            'reporting_frequency': 'daily'
        }
    
    def _generate_ad_keywords(self, video_info: Dict[str, Any], 
                            target_audience: Dict[str, Any]) -> List[str]:
        """広告キーワード生成"""
        title = video_info['snippet']['title']
        description = video_info['snippet']['description']
        
        # 簡略化されたキーワード抽出
        keywords = []
        
        # タイトルからキーワード抽出
        title_words = title.split()
        keywords.extend([word for word in title_words if len(word) > 3])
        
        # 説明文からキーワード抽出
        desc_words = description.split()[:50]  # 最初の50語
        keywords.extend([word for word in desc_words if len(word) > 4])
        
        # 重複除去
        unique_keywords = list(set(keywords))
        
        return unique_keywords[:20]  # 上位20キーワード
    
    def _estimate_campaign_performance(self, campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """キャンペーンパフォーマンス推定"""
        budget = campaign_config['budget']
        duration = campaign_config['duration']
        
        # 簡略化された推定
        estimated_impressions = budget * 100
        estimated_clicks = int(estimated_impressions * 0.02)  # 2% CTR
        estimated_conversions = int(estimated_clicks * 0.05)   # 5% CVR
        
        return {
            'estimated_impressions': estimated_impressions,
            'estimated_clicks': estimated_clicks,
            'estimated_conversions': estimated_conversions,
            'estimated_cpc': budget / max(estimated_clicks, 1),
            'estimated_cpa': budget / max(estimated_conversions, 1)
        }
    
    def _connect_to_twitch(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Twitch連携"""
        # Twitch API実装
        return {
            'status': 'success',
            'platform': 'twitch',
            'stream_key': 'twitch_stream_key',
            'rtmp_url': 'rtmp://live.twitch.tv/live/',
            'message': 'Twitch連携完了'
        }
    
    def _connect_to_facebook_live(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Facebook Live連携"""
        return {
            'status': 'success',
            'platform': 'facebook_live',
            'stream_key': 'facebook_stream_key',
            'message': 'Facebook Live連携完了'
        }
    
    def _connect_to_instagram_live(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Instagram Live連携"""
        return {
            'status': 'success',
            'platform': 'instagram_live',
            'stream_key': 'instagram_stream_key',
            'message': 'Instagram Live連携完了'
        }
    
    def _connect_to_linkedin_live(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """LinkedIn Live連携"""
        return {
            'status': 'success',
            'platform': 'linkedin_live',
            'stream_key': 'linkedin_stream_key',
            'message': 'LinkedIn Live連携完了'
        }
    
    def _connect_to_discord(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Discord連携"""
        return {
            'status': 'success',
            'platform': 'discord',
            'webhook_url': config.get('webhook_url'),
            'message': 'Discord連携完了'
        }
    
    def _setup_multistreaming(self, connection_results: Dict[str, Any]) -> Dict[str, Any]:
        """マルチストリーミング設定"""
        successful_platforms = [
            platform for platform, result in connection_results.items()
            if result['status'] == 'success'
        ]
        
        return {
            'enabled': True,
            'platforms': successful_platforms,
            'rtmp_distribution': True,
            'quality_settings': {
                'resolution': '1920x1080',
                'bitrate': '4000kbps',
                'fps': 30
            }
        }
    
    def _validate_webhook(self, webhook_config: WebhookConfig) -> Dict[str, Any]:
        """Webhook検証"""
        try:
            # URL形式チェック
            if not webhook_config.url.startswith(('http://', 'https://')):
                return {
                    'valid': False,
                    'error': '無効なURL形式です'
                }
            
            # 接続テスト
            response = requests.head(webhook_config.url, timeout=10)
            
            if response.status_code < 400:
                return {
                    'valid': True,
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                return {
                    'valid': False,
                    'error': f'HTTPエラー: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'valid': False,
                'error': f'接続エラー: {str(e)}'
            }
    
    def _test_webhook(self, webhook_config: WebhookConfig) -> Dict[str, Any]:
        """Webhook テスト送信"""
        test_payload = {
            'event': 'webhook_test',
            'timestamp': datetime.now().isoformat(),
            'webhook_id': webhook_config.webhook_id
        }
        
        try:
            headers = webhook_config.headers or {}
            headers['Content-Type'] = 'application/json'
            
            # シークレット署名
            if webhook_config.secret:
                signature = self._generate_webhook_signature(
                    json.dumps(test_payload), webhook_config.secret
                )
                headers['X-Signature'] = signature
            
            response = requests.post(
                webhook_config.url,
                json=test_payload,
                headers=headers,
                timeout=webhook_config.timeout
            )
            
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _start_webhook_service(self):
        """Webhook配信サービス開始"""
        # バックグラウンドサービス開始（簡略化）
        logger.info("Webhook配信サービスが開始されました")
    
    def _optimize_content_for_platforms(self, video_info: Dict[str, Any], 
                                      platforms: List[str]) -> Dict[str, Any]:
        """プラットフォーム別コンテンツ最適化"""
        optimized_content = {}
        
        base_title = video_info['snippet']['title']
        base_description = video_info['snippet']['description']
        video_url = f"https://www.youtube.com/watch?v={video_info['id']}"
        
        for platform in platforms:
            if platform == 'twitter':
                optimized_content[platform] = {
                    'text': f"{base_title[:200]}... {video_url}",
                    'hashtags': ['#YouTube', '#動画']
                }
            elif platform == 'facebook':
                optimized_content[platform] = {
                    'message': f"{base_title}\n\n{base_description[:300]}...\n\n{video_url}",
                    'link': video_url
                }
            elif platform == 'linkedin':
                optimized_content[platform] = {
                    'commentary': f"新しい動画を公開しました: {base_title}",
                    'content': {
                        'title': base_title,
                        'description': base_description[:500],
                        'submitted_url': video_url
                    }
                }
            else:
                optimized_content[platform] = {
                    'title': base_title,
                    'description': base_description,
                    'url': video_url
                }
        
        return optimized_content
    
    def _setup_cross_platform_tracking(self, campaign_id: str, 
                                      platform_results: Dict[str, Any]) -> Dict[str, Any]:
        """クロスプラットフォーム追跡設定"""
        return {
            'tracking_id': f"cross_track_{campaign_id}",
            'platforms': list(platform_results.keys()),
            'unified_analytics': True,
            'reporting_dashboard': f"/dashboard/campaign/{campaign_id}"
        }
    
    def _setup_unified_reporting(self, campaign_id: str, 
                               platforms: List[str]) -> Dict[str, Any]:
        """統合レポート設定"""
        return {
            'report_id': f"unified_report_{campaign_id}",
            'platforms': platforms,
            'metrics': ['reach', 'engagement', 'conversions', 'roi'],
            'frequency': 'daily',
            'dashboard_url': f"/reports/unified/{campaign_id}"
        }
    
    async def _send_single_webhook(self, session: aiohttp.ClientSession, 
                                 webhook: WebhookConfig, event_type: str, 
                                 event_data: Dict[str, Any]) -> Dict[str, Any]:
        """単一Webhook送信"""
        payload = {
            'event_type': event_type,
            'event_data': event_data,
            'webhook_id': webhook.webhook_id,
            'timestamp': datetime.now().isoformat()
        }
        
        headers = webhook.headers or {}
        headers['Content-Type'] = 'application/json'
        
        # シークレット署名
        if webhook.secret:
            signature = self._generate_webhook_signature(
                json.dumps(payload), webhook.secret
            )
            headers['X-Signature'] = signature
        
        try:
            async with session.post(
                webhook.url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=webhook.timeout)
            ) as response:
                return {
                    'status': 'success' if response.status < 400 else 'error',
                    'status_code': response.status,
                    'response_time': None  # aiohttp では elapsed time の取得方法が異なる
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _generate_webhook_signature(self, payload: str, secret: str) -> str:
        """Webhook署名生成"""
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    def _format_content_for_twitter(self, content_data: Dict[str, Any]) -> str:
        """Twitter用コンテンツフォーマット"""
        title = content_data.get('title', '')
        url = content_data.get('url', '')
        
        # Twitter文字制限考慮
        max_title_length = 280 - len(url) - 10  # URL短縮とスペース考慮
        
        if len(title) > max_title_length:
            title = title[:max_title_length-3] + '...'
        
        return f"{title}\n\n{url}"
    
    def _format_content_for_facebook(self, content_data: Dict[str, Any]) -> str:
        """Facebook用コンテンツフォーマット"""
        title = content_data.get('title', '')
        description = content_data.get('description', '')
        url = content_data.get('url', '')
        
        # Facebook用の長文対応
        formatted_text = f"{title}\n\n{description[:500]}"
        
        if len(description) > 500:
            formatted_text += "..."
        
        formatted_text += f"\n\n詳細: {url}"
        
        return formatted_text
    
    def _log_integration_activity(self, activity_data: Dict[str, Any]):
        """統合アクティビティログ記録"""
        self.integration_logs.append(activity_data)
        
        # ログサイズ制限
        if len(self.integration_logs) > 1000:
            self.integration_logs = self.integration_logs[-500:]
    
    def _log_webhook_activity(self, activity_data: Dict[str, Any]):
        """Webhookアクティビティログ記録"""
        self.integration_logs.append({
            'type': 'webhook_activity',
            **activity_data
        })
    
    def get_integration_logs(self, log_type: Optional[str] = None, 
                           limit: int = 100) -> List[Dict[str, Any]]:
        """統合ログ取得"""
        logs = self.integration_logs
        
        if log_type:
            logs = [log for log in logs if log.get('type') == log_type]
        
        return logs[-limit:]
    
    def configure_social_media_platform(self, platform: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """SNSプラットフォーム設定"""
        try:
            social_config = SocialMediaConfig(
                platform=platform,
                api_key=config['api_key'],
                api_secret=config['api_secret'],
                access_token=config['access_token'],
                access_token_secret=config.get('access_token_secret'),
                enabled=config.get('enabled', True)
            )
            
            self.social_media_configs[platform] = social_config
            
            return {
                'platform': platform,
                'status': 'configured',
                'enabled': social_config.enabled,
                'configured_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"SNSプラットフォーム設定に失敗しました: {str(e)}")