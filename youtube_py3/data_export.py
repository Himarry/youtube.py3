"""
YouTube.py3 - データエクスポート機能

取得したデータを様々な形式でエクスポートする機能を提供します。
"""

import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from .base import YouTubeAPIBase
from .exceptions import YouTubeAPIError


class DataExportMixin(YouTubeAPIBase):
    """データエクスポート機能のMixin"""

    def export_channel_report(self, channel_id, output_dir="reports", formats=None):
        """チャンネルの包括的レポートを生成・エクスポート
        
        Args:
            channel_id (str): チャンネルID
            output_dir (str): 出力ディレクトリ
            formats (list): エクスポート形式 ['csv', 'json', 'html']
            
        Returns:
            dict: エクスポート結果
        """
        if formats is None:
            formats = ['csv', 'json']
        
        try:
            # ディレクトリ作成
            os.makedirs(output_dir, exist_ok=True)
            
            # チャンネル情報取得
            channel_info = self.get_channel_simple(channel_id)
            
            # 動画一覧取得
            videos = self.get_all_channel_videos(channel_id, max_results=200)
            video_ids = [v['id']['videoId'] for v in videos]
            detailed_videos = self.get_multiple_video_info_batch(video_ids)
            
            # パフォーマンス分析
            performance_analysis = self.analyze_channel_performance(channel_id, days=90)
            
            # レポートデータ作成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"channel_report_{channel_id}_{timestamp}"
            
            report_data = {
                'channel_info': channel_info,
                'videos': detailed_videos,
                'performance_analysis': performance_analysis,
                'export_timestamp': datetime.now().isoformat(),
                'total_videos': len(detailed_videos)
            }
            
            exported_files = []
            
            # CSV形式でエクスポート
            if 'csv' in formats:
                csv_file = os.path.join(output_dir, f"{base_filename}.csv")
                self._export_videos_to_csv(detailed_videos, csv_file)
                exported_files.append(csv_file)
            
            # JSON形式でエクスポート
            if 'json' in formats:
                json_file = os.path.join(output_dir, f"{base_filename}.json")
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
                exported_files.append(json_file)
            
            # HTML形式でエクスポート
            if 'html' in formats:
                html_file = os.path.join(output_dir, f"{base_filename}.html")
                self._export_to_html(report_data, html_file)
                exported_files.append(html_file)
            
            return {
                'success': True,
                'channel_id': channel_id,
                'exported_files': exported_files,
                'total_videos': len(detailed_videos),
                'export_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"チャンネルレポートエクスポートに失敗しました: {str(e)}")

    def export_playlist_backup(self, playlist_id, output_dir="backups", include_metadata=True):
        """プレイリストのバックアップを作成
        
        Args:
            playlist_id (str): プレイリストID
            output_dir (str): 出力ディレクトリ
            include_metadata (bool): メタデータを含めるか
            
        Returns:
            dict: バックアップ結果
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # プレイリスト完全取得
            playlist_data = self.get_playlist_videos_complete(playlist_id, include_unavailable=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"playlist_backup_{playlist_id}_{timestamp}.json"
            backup_file = os.path.join(output_dir, backup_filename)
            
            # バックアップデータ構築
            backup_data = {
                'backup_info': {
                    'playlist_id': playlist_id,
                    'backup_timestamp': datetime.now().isoformat(),
                    'total_videos': playlist_data['total_count'],
                    'available_videos': playlist_data['available_count'],
                    'unavailable_videos': playlist_data['unavailable_count']
                },
                'playlist_info': playlist_data['playlist_info'],
                'available_videos': playlist_data['available_videos'],
                'unavailable_videos': playlist_data['unavailable_videos']
            }
            
            # メタデータ追加
            if include_metadata:
                video_ids = [v['id'] for v in playlist_data['available_videos']]
                if video_ids:
                    detailed_videos = self.get_multiple_video_info_batch(video_ids)
                    backup_data['detailed_metadata'] = detailed_videos
            
            # JSON保存
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
            
            # 簡易CSV保存
            csv_file = os.path.join(output_dir, f"playlist_simple_{playlist_id}_{timestamp}.csv")
            self._export_playlist_to_csv(playlist_data['available_videos'], csv_file)
            
            return {
                'success': True,
                'playlist_id': playlist_id,
                'backup_file': backup_file,
                'csv_file': csv_file,
                'total_videos': playlist_data['total_count'],
                'available_videos': playlist_data['available_count'],
                'unavailable_videos': playlist_data['unavailable_count']
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"プレイリストバックアップに失敗しました: {str(e)}")

    def export_comments_analysis(self, video_id, output_dir="analysis", include_sentiment=True):
        """コメント分析結果をエクスポート
        
        Args:
            video_id (str): 動画ID
            output_dir (str): 出力ディレクトリ
            include_sentiment (bool): 感情分析を含めるか
            
        Returns:
            dict: エクスポート結果
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # コメント取得・分析
            comments_data = self.get_video_comments(video_id, max_results=500)
            
            analysis_data = {
                'video_id': video_id,
                'analysis_timestamp': datetime.now().isoformat(),
                'comments_data': comments_data
            }
            
            # 感情分析追加
            if include_sentiment:
                sentiment_analysis = self.analyze_comment_sentiment(video_id)
                analysis_data['sentiment_analysis'] = sentiment_analysis
            
            # トピック分析追加
            topic_analysis = self.extract_comment_topics(video_id)
            analysis_data['topic_analysis'] = topic_analysis
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # JSON保存
            json_file = os.path.join(output_dir, f"comments_analysis_{video_id}_{timestamp}.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2, default=str)
            
            # コメント一覧CSV保存
            csv_file = os.path.join(output_dir, f"comments_{video_id}_{timestamp}.csv")
            self._export_comments_to_csv(comments_data['comments'], csv_file)
            
            return {
                'success': True,
                'video_id': video_id,
                'json_file': json_file,
                'csv_file': csv_file,
                'total_comments': len(comments_data['comments'])
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"コメント分析エクスポートに失敗しました: {str(e)}")

    def export_trending_analysis(self, region_code="JP", output_dir="trending"):
        """トレンド分析結果をエクスポート
        
        Args:
            region_code (str): 地域コード
            output_dir (str): 出力ディレクトリ
            
        Returns:
            dict: エクスポート結果
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # トレンド動画取得
            trending_videos = self.get_trending_videos(region_code, max_results=50)
            
            # トレンドキーワード検出
            trending_keywords = self.detect_trending_keywords(region_code)
            
            # 分析データ構築
            trending_data = {
                'analysis_timestamp': datetime.now().isoformat(),
                'region_code': region_code,
                'trending_videos': trending_videos,
                'trending_keywords': trending_keywords,
                'summary': {
                    'total_trending_videos': len(trending_videos),
                    'top_keywords': trending_keywords['trending_keywords'][:10] if 'trending_keywords' in trending_keywords else []
                }
            }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # JSON保存
            json_file = os.path.join(output_dir, f"trending_analysis_{region_code}_{timestamp}.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(trending_data, f, ensure_ascii=False, indent=2, default=str)
            
            # トレンド動画CSV保存
            csv_file = os.path.join(output_dir, f"trending_videos_{region_code}_{timestamp}.csv")
            self._export_videos_to_csv(trending_videos, csv_file)
            
            return {
                'success': True,
                'region_code': region_code,
                'json_file': json_file,
                'csv_file': csv_file,
                'trending_videos_count': len(trending_videos)
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"トレンド分析エクスポートに失敗しました: {str(e)}")

    def _export_videos_to_csv(self, videos, filename):
        """動画データをCSV形式でエクスポート"""
        if not videos:
            return
        
        fieldnames = [
            'video_id', 'title', 'channel_title', 'published_at', 'duration',
            'view_count', 'like_count', 'comment_count', 'engagement_rate',
            'description', 'tags', 'category_id'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for video in videos:
                snippet = video.get('snippet', {})
                statistics = video.get('statistics', {})
                content_details = video.get('contentDetails', {})
                
                # エンゲージメント率計算
                view_count = int(statistics.get('viewCount', 0))
                like_count = int(statistics.get('likeCount', 0))
                comment_count = int(statistics.get('commentCount', 0))
                engagement_rate = 0
                if view_count > 0:
                    engagement_rate = round((like_count + comment_count) / view_count * 100, 2)
                
                row = {
                    'video_id': video.get('id', ''),
                    'title': snippet.get('title', ''),
                    'channel_title': snippet.get('channelTitle', ''),
                    'published_at': snippet.get('publishedAt', ''),
                    'duration': content_details.get('duration', ''),
                    'view_count': statistics.get('viewCount', 0),
                    'like_count': statistics.get('likeCount', 0),
                    'comment_count': statistics.get('commentCount', 0),
                    'engagement_rate': engagement_rate,
                    'description': snippet.get('description', '')[:200] + '...' if len(snippet.get('description', '')) > 200 else snippet.get('description', ''),
                    'tags': ', '.join(snippet.get('tags', [])),
                    'category_id': snippet.get('categoryId', '')
                }
                writer.writerow(row)

    def _export_comments_to_csv(self, comments, filename):
        """コメントデータをCSV形式でエクスポート"""
        if not comments:
            return
        
        fieldnames = [
            'comment_id', 'video_id', 'author_name', 'comment_text', 
            'like_count', 'published_at', 'comment_type', 'is_author_comment'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for comment in comments:
                row = {
                    'comment_id': comment.get('id', ''),
                    'video_id': comment.get('video_id', ''),
                    'author_name': comment.get('author_display_name', ''),
                    'comment_text': comment.get('text_display', ''),
                    'like_count': comment.get('like_count', 0),
                    'published_at': comment.get('published_at', ''),
                    'comment_type': comment.get('type', ''),
                    'is_author_comment': comment.get('is_author_comment', False)
                }
                writer.writerow(row)

    def _export_playlist_to_csv(self, videos, filename):
        """プレイリスト動画をCSV形式でエクスポート"""
        if not videos:
            return
        
        fieldnames = ['position', 'video_id', 'title', 'channel_title', 'published_at']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for video in videos:
                snippet = video.get('snippet', {})
                row = {
                    'position': video.get('playlist_position', ''),
                    'video_id': video.get('id', ''),
                    'title': snippet.get('title', ''),
                    'channel_title': snippet.get('channelTitle', ''),
                    'published_at': snippet.get('publishedAt', '')
                }
                writer.writerow(row)

    def _export_to_html(self, report_data, filename):
        """HTMLレポート生成"""
        html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube チャンネルレポート</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .metrics {{ display: flex; gap: 20px; margin: 20px 0; }}
        .metric {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; flex: 1; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>YouTube チャンネルレポート</h1>
        <p><strong>チャンネル名:</strong> {report_data['channel_info'].get('title', 'Unknown')}</p>
        <p><strong>チャンネルID:</strong> {report_data['channel_info'].get('id', 'Unknown')}</p>
        <p><strong>レポート生成日時:</strong> {report_data.get('export_timestamp', '')}</p>
    </div>
    
    <div class="section">
        <h2>チャンネル統計</h2>
        <div class="metrics">
            <div class="metric">
                <h3>チャンネル登録者数</h3>
                <p>{report_data['channel_info'].get('subscriber_count', 0):,}</p>
            </div>
            <div class="metric">
                <h3>総動画数</h3>
                <p>{report_data['channel_info'].get('video_count', 0):,}</p>
            </div>
            <div class="metric">
                <h3>総再生回数</h3>
                <p>{report_data['channel_info'].get('view_count', 0):,}</p>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>最新動画一覧</h2>
        <table>
            <tr>
                <th>タイトル</th>
                <th>公開日</th>
                <th>再生回数</th>
                <th>いいね数</th>
                <th>コメント数</th>
            </tr>
"""
        
        # 動画リスト追加（最新10件）
        for video in report_data['videos'][:10]:
            snippet = video.get('snippet', {})
            statistics = video.get('statistics', {})
            
            html_content += f"""
            <tr>
                <td>{snippet.get('title', '')[:50]}...</td>
                <td>{snippet.get('publishedAt', '')[:10]}</td>
                <td>{int(statistics.get('viewCount', 0)):,}</td>
                <td>{int(statistics.get('likeCount', 0)):,}</td>
                <td>{int(statistics.get('commentCount', 0)):,}</td>
            </tr>
"""
        
        html_content += """
        </table>
    </div>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
