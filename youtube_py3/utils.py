"""
YouTube.py3 - ユーティリティ関数

データ変換、整形、バッチ処理などの便利な機能を提供します。
"""

import re
import csv
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pytz


class YouTubeUtils:
    """YouTube関連のユーティリティ関数"""
    
    @staticmethod
    def extract_video_id(url: str) -> str:
        """URLから動画IDを抽出"""
        patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
            r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # URLでない場合はそのまま返す（すでにIDの可能性）
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
            
        raise ValueError(f"無効なYouTube URL: {url}")

    @staticmethod
    def extract_channel_id(url: str) -> str:
        """URLからチャンネルIDを抽出"""
        patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/channel/([a-zA-Z0-9_-]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/c/([a-zA-Z0-9_-]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/user/([a-zA-Z0-9_-]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/@([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # URLでない場合はそのまま返す
        if re.match(r'^UC[a-zA-Z0-9_-]{22}$', url):
            return url
            
        raise ValueError(f"無効なYouTubeチャンネルURL: {url}")

    @staticmethod
    def extract_playlist_id(url: str) -> str:
        """URLからプレイリストIDを抽出"""
        patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?.*list=([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # URLでない場合はそのまま返す
        if re.match(r'^[a-zA-Z0-9_-]+$', url):
            return url
            
        raise ValueError(f"無効なYouTubeプレイリストURL: {url}")

    @staticmethod
    def parse_duration(duration: str) -> Dict[str, int]:
        """ISO 8601形式の再生時間を解析
        
        Args:
            duration (str): ISO 8601形式の再生時間 (例: "PT4M13S")
            
        Returns:
            dict: 時間、分、秒の辞書
            {
                'hours': int,
                'minutes': int, 
                'seconds': int,
                'total_seconds': int,
                'formatted': str  # "4:13"形式
            }
        """
        if not duration:
            return {'hours': 0, 'minutes': 0, 'seconds': 0, 'total_seconds': 0, 'formatted': '0:00'}
        
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return {'hours': 0, 'minutes': 0, 'seconds': 0, 'total_seconds': 0, 'formatted': '0:00'}
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        total_seconds = hours * 3600 + minutes * 60 + seconds
        
        # フォーマット
        if hours > 0:
            formatted = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            formatted = f"{minutes}:{seconds:02d}"
        
        return {
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'total_seconds': total_seconds,
            'formatted': formatted
        }

    @staticmethod
    def format_date(date_str: str, format_type: str = "relative") -> str:
        """日時を様々な形式でフォーマット
        
        Args:
            date_str (str): ISO形式の日時文字列
            format_type (str): フォーマット種類
                - "relative": "2時間前", "3日前"など
                - "short": "2024/01/15"
                - "long": "2024年1月15日"
                - "iso": そのまま
                
        Returns:
            str: フォーマット済み日時
        """
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            now = datetime.now(pytz.UTC)
            
            if format_type == "relative":
                diff = now - dt
                
                if diff.days > 365:
                    years = diff.days // 365
                    return f"{years}年前"
                elif diff.days > 30:
                    months = diff.days // 30
                    return f"{months}ヶ月前"
                elif diff.days > 0:
                    return f"{diff.days}日前"
                elif diff.seconds > 3600:
                    hours = diff.seconds // 3600
                    return f"{hours}時間前"
                elif diff.seconds > 60:
                    minutes = diff.seconds // 60
                    return f"{minutes}分前"
                else:
                    return "たった今"
                    
            elif format_type == "short":
                return dt.strftime("%Y/%m/%d")
                
            elif format_type == "long":
                return dt.strftime("%Y年%m月%d日")
                
            else:  # iso
                return date_str
                
        except Exception:
            return date_str

    @staticmethod
    def format_number(number: Any, format_type: str = "compact") -> str:
        """数値を読みやすい形式でフォーマット
        
        Args:
            number: 数値（文字列または整数）
            format_type (str): フォーマット種類
                - "compact": "1.2万", "3.4M"など
                - "comma": "1,234,567"
                - "raw": そのまま
                
        Returns:
            str: フォーマット済み数値
        """
        try:
            num = int(str(number)) if number else 0
            
            if format_type == "compact":
                if num >= 100000000:  # 1億以上
                    return f"{num/100000000:.1f}億"
                elif num >= 10000:  # 1万以上
                    return f"{num/10000:.1f}万"
                elif num >= 1000:  # 1千以上
                    return f"{num/1000:.1f}K"
                else:
                    return str(num)
                    
            elif format_type == "comma":
                return f"{num:,}"
                
            else:  # raw
                return str(num)
                
        except Exception:
            return str(number)

    @staticmethod
    def export_to_csv(data: List[Dict], filename: str, fields: Optional[List[str]] = None):
        """データをCSVファイルにエクスポート
        
        Args:
            data (list): エクスポートするデータ
            filename (str): 出力ファイル名
            fields (list, optional): 出力するフィールド（指定しない場合は全て）
        """
        if not data:
            return
        
        if not fields:
            fields = list(data[0].keys())
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            
            for row in data:
                filtered_row = {field: row.get(field, '') for field in fields}
                writer.writerow(filtered_row)

    @staticmethod
    def export_to_json(data: Any, filename: str, pretty: bool = True):
        """データをJSONファイルにエクスポート
        
        Args:
            data: エクスポートするデータ
            filename (str): 出力ファイル名
            pretty (bool): 整形して出力するか
        """
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            if pretty:
                json.dump(data, jsonfile, ensure_ascii=False, indent=2)
            else:
                json.dump(data, jsonfile, ensure_ascii=False)

    @staticmethod
    def batch_process(items: List[Any], batch_size: int = 50):
        """リストをバッチサイズに分割
        
        Args:
            items (list): 処理対象のリスト
            batch_size (int): バッチサイズ
            
        Yields:
            list: バッチサイズに分割されたリスト
        """
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]

    @staticmethod
    def calculate_engagement_rate(statistics: Dict[str, Any]) -> float:
        """エンゲージメント率を計算
        
        Args:
            statistics (dict): 動画統計情報
            
        Returns:
            float: エンゲージメント率（パーセンテージ）
        """
        try:
            view_count = int(statistics.get('viewCount', 0))
            like_count = int(statistics.get('likeCount', 0))
            comment_count = int(statistics.get('commentCount', 0))
            
            if view_count == 0:
                return 0.0
            
            engagement = (like_count + comment_count) / view_count * 100
            return round(engagement, 2)
            
        except (ValueError, TypeError, ZeroDivisionError):
            return 0.0