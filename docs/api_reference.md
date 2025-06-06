# APIリファレンス

YouTube.py3の全メソッドの詳細な説明です。実装済みのメソッドを機能別に分類して説明します。

## 📚 目次

- [基本クラス](#基本クラス)
- [基本情報取得](#基本情報取得)
- [検索機能](#検索機能)
- [プレイリスト管理](#プレイリスト管理)
- [コメント管理](#コメント管理)
- [チャンネル管理](#チャンネル管理)
- [動画管理](#動画管理)
- [ライブストリーミング](#ライブストリーミング)
- [字幕管理](#字幕管理)
- [サブスクリプション管理](#サブスクリプション管理)
- [システム情報](#システム情報)
- [ページネーション機能](#ページネーション機能)
- [エラーハンドリング](#エラーハンドリング)
- [使用パターン集](#使用パターン集)

---

## 基本クラス

### YouTubeAPI

```python
class YouTubeAPI(api_key: str)
```

YouTube Data API v3のメインクラス。

**パラメータ:**
- `api_key` (str): YouTube Data API v3のAPIキー
  - [Google Cloud Console](https://console.cloud.google.com/)で取得可能
  - YouTube Data API v3を有効化する必要があります

**例外:**
- `YouTubeAPIError`: APIキーが無効な場合

**基本的な使用例:**
```python
from youtube_py3 import YouTubeAPI
import os

# 環境変数からAPIキーを取得（推奨）
api_key = os.getenv('YOUTUBE_API_KEY')
yt = YouTubeAPI(api_key)

# 直接指定も可能（セキュリティに注意）
# yt = YouTubeAPI('your_api_key_here')
```

**APIキーの設定方法:**
```bash
# Windows
set YOUTUBE_API_KEY=your_api_key_here

# macOS/Linux
export YOUTUBE_API_KEY=your_api_key_here
```

### YouTubeAPIError

```python
class YouTubeAPIError(Exception)
```

YouTube API関連のエラー例外クラス。

**メソッド:**
- `is_quota_exceeded()`: クォータ超過エラーかどうかを判定
- `is_api_key_invalid()`: APIキー無効エラーかどうかを判定
- `is_not_found()`: リソースが見つからないエラーかどうかを判定
- `is_forbidden()`: アクセス権限エラーかどうかを判定
- `get_suggested_action()`: エラーに対する推奨アクションを取得

**詳細な使用例:**
```python
try:
    video = yt.get_video_info("invalid_id")
except YouTubeAPIError as e:
    print(f"エラーが発生しました: {e}")
    
    # エラーの種類に応じた詳細な対処
    if e.is_quota_exceeded():
        print("❌ APIクォータが制限を超えました")
        print("💡 推奨アクション:", e.get_suggested_action())
        # 明日まで待つか、課金を検討
        
    elif e.is_api_key_invalid():
        print("❌ APIキーが無効です")
        print("💡 推奨アクション:", e.get_suggested_action())
        # APIキーを確認・再生成
        
    elif e.is_not_found():
        print("❌ 指定されたリソースが見つかりません")
        print("💡 推奨アクション:", e.get_suggested_action())
        # IDを確認
        
    elif e.is_forbidden():
        print("❌ アクセス権限がありません")
        print("💡 推奨アクション:", e.get_suggested_action())
        # 非公開動画の可能性
```

---

## 基本情報取得

### check_quota_usage()

```python
def check_quota_usage() -> bool
```

APIクォータの使用量を確認するヘルパーメソッド。

**戻り値:**
- `bool`: APIキーが有効かどうか

**例外:**
- `YouTubeAPIError`: APIキーが無効または制限されている場合

**実践的な使用例:**
```python
# アプリケーション開始時の確認
try:
    if yt.check_quota_usage():
        print("✅ APIキーは有効です。処理を開始します。")
        # メイン処理を実行
    else:
        print("❌ APIキーに問題があります。")
except YouTubeAPIError as e:
    print(f"APIエラー: {e}")
    
# バッチ処理での定期確認
import time

def safe_batch_process():
    for i, item in enumerate(batch_items):
        if i % 10 == 0:  # 10件ごとにチェック
            if not yt.check_quota_usage():
                print("クォータ制限に達しました。処理を中断します。")
                break
        
        # 実際の処理
        process_item(item)
        time.sleep(0.1)  # レート制限対策
```

### get_channel_info()

```python
def get_channel_info(channel_id: str) -> dict
```

チャンネル情報を取得します。

**パラメータ:**
- `channel_id` (str): YouTubeチャンネルのID
  - URLから抜き出す: `https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw`
  - または `@username` 形式も対応予定

**戻り値の構造:**
```python
{
    'snippet': {
        'title': 'チャンネル名',
        'description': 'チャンネル説明',
        'customUrl': 'カスタムURL',
        'publishedAt': '2020-01-01T00:00:00Z',
        'thumbnails': { ... },
        'country': 'JP'
    },
    'statistics': {
        'viewCount': '1234567',
        'subscriberCount': '12345',
        'videoCount': '100'
    }
}
```

**例外:**
- `YouTubeAPIError`: チャンネルが見つからない場合

**詳細な使用例:**
```python
# 基本的な情報取得
channel_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"
try:
    channel = yt.get_channel_info(channel_id)
    
    # 基本情報の表示
    print(f"📺 チャンネル名: {channel['snippet']['title']}")
    print(f"📅 開設日: {channel['snippet']['publishedAt'][:10]}")
    print(f"🌍 国: {channel['snippet'].get('country', 'N/A')}")
    
    # 統計情報の表示
    stats = channel['statistics']
    print(f"👥 登録者数: {int(stats['subscriberCount']):,}")
    print(f"📹 動画数: {int(stats['videoCount']):,}")
    print(f"👀 総再生回数: {int(stats['viewCount']):,}")
    
    # サムネイル取得
    thumbnail_url = channel['snippet']['thumbnails']['high']['url']
    print(f"🖼️ サムネイル: {thumbnail_url}")
    
except YouTubeAPIError as e:
    if e.is_not_found():
        print("❌ 指定されたチャンネルが見つかりません")
    else:
        print(f"エラー: {e}")

# URLからチャンネルIDを抽出する関数の例
def extract_channel_id(url: str) -> str:
    """YouTube URLからチャンネルIDを抽出"""
    import re
    patterns = [
        r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
        r'youtube\.com/c/([a-zA-Z0-9_-]+)',
        r'youtube\.com/@([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("有効なYouTubeチャンネルURLではありません")

# 使用例
channel_url = "https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw"
channel_id = extract_channel_id(channel_url)
channel_info = yt.get_channel_info(channel_id)
```

### get_video_info()

```python
def get_video_info(video_id: str) -> dict
```

動画情報を取得します。

**パラメータ:**
- `video_id` (str): YouTube動画のID
  - URLから抽出: `https://www.youtube.com/watch?v=dQw4w9WgXcQ` → `dQw4w9WgXcQ`

**戻り値の構造:**
```python
{
    'snippet': {
        'title': '動画タイトル',
        'description': '動画説明',
        'channelTitle': 'チャンネル名',
        'publishedAt': '2020-01-01T00:00:00Z',
        'thumbnails': { ... },
        'tags': ['タグ1', 'タグ2'],
        'categoryId': '10',
        'duration': 'PT4M33S'  # ISO 8601形式
    },
    'statistics': {
        'viewCount': '1234567',
        'likeCount': '12345',
        'commentCount': '678'
    }
}
```

**詳細な使用例:**
```python
import re
from datetime import datetime

def extract_video_id(url: str) -> str:
    """YouTube URLから動画IDを抽出"""
    patterns = [
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'youtu\.be/([a-zA-Z0-9_-]+)',
        r'youtube\.com/embed/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("有効なYouTube動画URLではありません")

def parse_duration(duration: str) -> str:
    """ISO 8601時間形式を読みやすい形式に変換"""
    import re
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration)
    
    if not match:
        return "不明"
    
    hours, minutes, seconds = match.groups()
    hours = int(hours) if hours else 0
    minutes = int(minutes) if minutes else 0
    seconds = int(seconds) if seconds else 0
    
    if hours > 0:
        return f"{hours}時間{minutes}分{seconds}秒"
    elif minutes > 0:
        return f"{minutes}分{seconds}秒"
    else:
        return f"{seconds}秒"

# 実践的な使用例
video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
video_id = extract_video_id(video_url)

try:
    video = yt.get_video_info(video_id)
    snippet = video['snippet']
    stats = video['statistics']
    
    # 基本情報
    print(f"🎬 タイトル: {snippet['title']}")
    print(f"📺 チャンネル: {snippet['channelTitle']}")
    print(f"📅 公開日: {snippet['publishedAt'][:10]}")
    print(f"⏱️ 再生時間: {parse_duration(snippet.get('duration', 'PT0S'))}")
    
    # 統計情報
    print(f"👀 再生回数: {int(stats['viewCount']):,}")
    print(f"👍 いいね数: {int(stats.get('likeCount', 0)):,}")
    print(f"💬 コメント数: {int(stats.get('commentCount', 0)):,}")
    
    # タグ情報
    if 'tags' in snippet:
        print(f"🏷️ タグ: {', '.join(snippet['tags'][:5])}...")
    
    # サムネイル
    thumbnail = snippet['thumbnails']['maxres']['url']
    print(f"🖼️ サムネイル: {thumbnail}")
    
    # 説明文の一部
    description = snippet['description']
    if len(description) > 100:
        print(f"📝 説明: {description[:100]}...")
    else:
        print(f"📝 説明: {description}")
        
except YouTubeAPIError as e:
    if e.is_not_found():
        print("❌ 指定された動画が見つかりません（削除済みまたは非公開）")
    else:
        print(f"エラー: {e}")

# 複数動画の一括取得例
def get_multiple_videos(video_ids: list) -> list:
    """複数の動画情報を効率的に取得"""
    videos = []
    for video_id in video_ids:
        try:
            video = yt.get_video_info(video_id)
            videos.append(video)
        except YouTubeAPIError as e:
            print(f"動画 {video_id} の取得に失敗: {e}")
            continue
    return videos

video_ids = ["dQw4w9WgXcQ", "9bZkp7q19f0", "invalid_id"]
videos = get_multiple_videos(video_ids)
print(f"✅ {len(videos)}件の動画情報を取得しました")
```

### get_channel_statistics_only()

```python
def get_channel_statistics_only(channel_id: str) -> dict
```

チャンネルの統計情報のみを効率的に取得します。

**パラメータ:**
- `channel_id` (str): YouTubeチャンネルのID

**戻り値:**
- `dict`: 統計情報のみ（クォータ消費を最小化）

**使用例:**
```python
# 大量のチャンネルの統計を効率的に取得
channel_ids = ["UC_x5XG1OV2P6uZZ5FSM9Ttw", "UC-lHJZR3Gqxm24_Vd_AJ5Yw"]

for channel_id in channel_ids:
    try:
        stats = yt.get_channel_statistics_only(channel_id)
        print(f"チャンネル {channel_id}: 登録者数 {stats['subscriberCount']}")
    except YouTubeAPIError:
        print(f"チャンネル {channel_id}: 取得失敗")
```

**注意:**
このメソッドは現在実装中です。

### get_video_statistics_only()

```python
def get_video_statistics_only(video_id: str) -> dict
```

動画の統計情報のみを効率的に取得します。

**パラメータ:**
- `video_id` (str): YouTube動画のID

**戻り値:**
- `dict`: 統計情報のみ

**使用例:**
```python
# 動画の人気度を素早くチェック
video_id = "dQw4w9WgXcQ"
stats = yt.get_video_statistics_only(video_id)
print(f"再生回数: {stats['viewCount']:,}")
```

**注意:**
このメソッドは現在実装中です。

---

## 検索機能

### search_videos()

```python
def search_videos(query: str, max_results: int = 5, order: str = "relevance") -> list
```

動画を検索します。

**パラメータ:**
- `query` (str): 検索キーワード
  - 日本語、英語対応
  - AND検索: `"Python AND 機械学習"`
  - OR検索: `"Python OR JavaScript"`
  - 除外: `"Python -Java"`
- `max_results` (int): 取得する最大結果数（1-50、デフォルト: 5）
- `order` (str): ソート順序（デフォルト: 'relevance'）
  - `'relevance'`: 関連度順（推奨）
  - `'date'`: 投稿日時順（新しい順）
  - `'rating'`: 評価順
  - `'viewCount'`: 再生回数順
  - `'title'`: タイトル順（アルファベット順）

**戻り値:**
各動画情報を含むリスト

**詳細な使用例:**
```python
# 基本的な検索
videos = yt.search_videos("Python プログラミング", max_results=10)
for i, video in enumerate(videos, 1):
    snippet = video['snippet']
    print(f"{i}. {snippet['title']}")
    print(f"   チャンネル: {snippet['channelTitle']}")
    print(f"   公開日: {snippet['publishedAt'][:10]}")
    print()

# 高度な検索例
def advanced_search_videos():
    """高度な動画検索の例"""
    
    # 1. 最新の動画を検索
    print("=== 最新のPython動画 ===")
    latest_videos = yt.search_videos(
        query="Python tutorial",
        max_results=5,
        order="date"
    )
    
    # 2. 人気順で検索
    print("=== 人気のAI動画 ===")
    popular_videos = yt.search_videos(
        query="人工知能 AI",
        max_results=5,
        order="viewCount"
    )
    
    # 3. 特定の条件で検索
    print("=== 機械学習の入門動画 ===")
    ml_videos = yt.search_videos(
        query="機械学習 入門 -上級",  # 上級を除外
        max_results=10,
        order="relevance"
    )
    
    return latest_videos, popular_videos, ml_videos

# 検索結果のフィルタリング
def filter_videos_by_duration(videos: list, min_duration_sec: int = 300):
    """指定した最小時間以上の動画をフィルタリング"""
    filtered = []
    for video in videos:
        try:
            # 動画詳細を取得して時間をチェック
            video_detail = yt.get_video_info(video['id']['videoId'])
            duration = video_detail['snippet'].get('duration', 'PT0S')
            
            # PT5M33S → 333秒に変換
            import re
            pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
            match = re.match(pattern, duration)
            
            if match:
                hours, minutes, seconds = match.groups()
                total_seconds = (
                    (int(hours) if hours else 0) * 3600 +
                    (int(minutes) if minutes else 0) * 60 +
                    (int(seconds) if seconds else 0)
                )
                
                if total_seconds >= min_duration_sec:
                    filtered.append(video)
                    
        except Exception as e:
            print(f"動画 {video['id']['videoId']} の詳細取得に失敗: {e}")
            continue
            
    return filtered

# 実践的な検索とフィルタリング
search_results = yt.search_videos("Python データ分析", max_results=20)
long_videos = filter_videos_by_duration(search_results, min_duration_sec=600)  # 10分以上
print(f"10分以上の動画: {len(long_videos)}件")
```

### search_channels()

```python
def search_channels(query: str, max_results: int = 5, order: str = "relevance") -> list
```

チャンネルを検索します。

**詳細な使用例:**
```python
# プログラミング系チャンネルの検索
channels = yt.search_channels("プログラミング 初心者", max_results=10)

print("=== おすすめプログラミングチャンネル ===")
for i, channel in enumerate(channels, 1):
    snippet = channel['snippet']
    print(f"{i}. {snippet['title']}")
    print(f"   説明: {snippet['description'][:100]}...")
    print(f"   チャンネルID: {channel['id']['channelId']}")
    
    # チャンネル詳細を取得
    try:
        channel_detail = yt.get_channel_info(channel['id']['channelId'])
        stats = channel_detail['statistics']
        print(f"   📊 登録者数: {int(stats['subscriberCount']):,}")
        print(f"   📹 動画数: {int(stats['videoCount']):,}")
    except YouTubeAPIError:
        print("   📊 統計情報の取得に失敗")
    print()

# チャンネルの詳細情報付き検索結果
def search_channels_with_details(query: str, max_results: int = 5):
    """チャンネル検索結果に詳細情報を付加"""
    channels = yt.search_channels(query, max_results)
    detailed_channels = []
    
    for channel in channels:
        try:
            channel_id = channel['id']['channelId']
            detail = yt.get_channel_info(channel_id)
            
            # 基本情報と詳細情報をマージ
            enhanced_channel = {
                'basic_info': channel,
                'detailed_info': detail,
                'subscriber_count': int(detail['statistics']['subscriberCount']),
                'video_count': int(detail['statistics']['videoCount'])
            }
            detailed_channels.append(enhanced_channel)
            
        except YouTubeAPIError as e:
            print(f"チャンネル詳細取得エラー: {e}")
            continue
    
    # 登録者数でソート
    detailed_channels.sort(key=lambda x: x['subscriber_count'], reverse=True)
    return detailed_channels

# 使用例
tech_channels = search_channels_with_details("技術 プログラミング", max_results=10)
print("登録者数順:")
for channel in tech_channels:
    title = channel['basic_info']['snippet']['title']
    subscribers = channel['subscriber_count']
    print(f"- {title}: {subscribers:,}人")
```

### search_playlists()

```python
def search_playlists(query: str, max_results: int = 5, order: str = "relevance") -> list
```

プレイリストを検索します。

**詳細な使用例:**
```python
# 学習用プレイリストの検索
playlists = yt.search_playlists("Python 入門 講座", max_results=15)

print("=== Python学習プレイリスト ===")
for i, playlist in enumerate(playlists, 1):
    snippet = playlist['snippet']
    print(f"{i}. {snippet['title']}")
    print(f"   チャンネル: {snippet['channelTitle']}")
    print(f"   作成日: {snippet['publishedAt'][:10]}")
    
    # プレイリストの詳細を取得
    try:
        playlist_id = playlist['id']['playlistId']
        playlist_videos = yt.get_playlist_videos(playlist_id, max_results=1)
        
        if playlist_videos:
            video_count = len(yt.get_playlist_videos(playlist_id, max_results=50))
            print(f"   📹 動画数: {video_count}本")
            
    except YouTubeAPIError:
        print("   📹 動画数: 取得失敗")
    print()

# プレイリスト分析機能
def analyze_playlist(playlist_id: str):
    """プレイリストを詳細分析"""
    try:
        # プレイリスト基本情報
        playlist_info = yt.get_playlist_info(playlist_id)
        videos = yt.get_playlist_videos(playlist_id, max_results=200)
        
        # 分析データの収集
        channels = {}
        total_views = 0
        total_likes = 0
        publish_dates = []
        
        print("📊 プレイリスト分析中...")
        for i, video in enumerate(videos):
            snippet = video['snippet']
            
            # チャンネル集計
            channel = snippet['channelTitle']
            channels[channel] = channels.get(channel, 0) + 1
            
            # 統計情報取得
            try:
                video_id = snippet['resourceId']['videoId']
                video_detail = yt.get_video_info(video_id)
                stats = video_detail['statistics']
                
                total_views += int(stats['viewCount'])
                total_likes += int(stats.get('likeCount', 0))
                publish_dates.append(snippet['publishedAt'])
                
            except YouTubeAPIError:
                continue
            
            # 進捗表示
            if (i + 1) % 10 == 0:
                print(f"  処理済み: {i + 1}/{len(videos)}")
        
        # 分析結果
        analysis = {
            'playlist_title': playlist_info['snippet']['title'],
            'total_videos': len(videos),
            'total_views': total_views,
            'total_likes': total_likes,
            'average_views': total_views // len(videos) if videos else 0,
            'unique_channels': len(channels),
            'top_channels': sorted(channels.items(), key=lambda x: x[1], reverse=True)[:5],
            'date_range': {
                'oldest': min(publish_dates) if publish_dates else None,
                'newest': max(publish_dates) if publish_dates else None
            }
        }
        
        return analysis
        
    except YouTubeAPIError as e:
        return {'error': str(e)}

# プレイリスト分析の実行
analysis = analyze_playlist("PLxyz123")

if 'error' not in analysis:
    print("=== プレイリスト分析結果 ===")
    print(f"📝 プレイリスト: {analysis['playlist_title']}")
    print(f"📹 動画数: {analysis['total_videos']}")
    print(f"👀 総再生回数: {analysis['total_views']:,}")
    print(f"👍 総いいね数: {analysis['total_likes']:,}")
    print(f"📊 平均再生回数: {analysis['average_views']:,}")
    print(f"📺 関連チャンネル数: {analysis['unique_channels']}")
    
    print("\n🔝 上位チャンネル:")
    for channel, count in analysis['top_channels']:
        print(f"  - {channel}: {count}本")
    
    if analysis['date_range']['oldest']:
        print(f"\n📅 期間: {analysis['date_range']['oldest'][:10]} ～ {analysis['date_range']['newest'][:10]}")

# プレイリストのエクスポート
def export_playlist_to_csv(playlist_id: str, filename: str = None):
    """プレイリストをCSVファイルにエクスポート"""
    import csv
    from datetime import datetime
    
    if not filename:
        filename = f"playlist_{playlist_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        videos = yt.get_playlist_videos(playlist_id, max_results=500)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['順番', 'タイトル', 'チャンネル', '動画ID', 'URL', '追加日']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for i, video in enumerate(videos, 1):
                snippet = video['snippet']
                video_id = snippet['resourceId']['videoId']
                
                writer.writerow({
                    '順番': i,
                    'タイトル': snippet['title'],
                    'チャンネル': snippet['channelTitle'],
                    '動画ID': video_id,
                    'URL': f"https://www.youtube.com/watch?v={video_id}",
                    '追加日': snippet['publishedAt'][:10]
                })
        
        print(f"✅ プレイリストを {filename} にエクスポートしました")
        return filename
        
    except Exception as e:
        print(f"❌ エクスポートエラー: {e}")
        return None

# CSVエクスポートの実行
export_playlist_to_csv("PLxyz123")
```

### get_channel_playlists()

```python
def get_channel_playlists(channel_id: str, max_results: int = 50) -> list
```

チャンネルのプレイリスト一覧を取得します。

**詳細な使用例:**
```python
# チャンネルのプレイリスト一覧を取得
channel_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"

try:
    playlists = yt.get_channel_playlists(channel_id, max_results=100)
    
    print(f"📺 チャンネルに {len(playlists)} 個のプレイリストがあります")
    print()
    
    # プレイリストの詳細表示
    for i, playlist in enumerate(playlists, 1):
        snippet = playlist['snippet']
        
        print(f"{i}. {snippet['title']}")
        print(f"   📅 作成日: {snippet['publishedAt'][:10]}")
        print(f"   🔗 ID: {playlist['id']}")
        
        # プレイリスト内の動画数を取得
        try:
            videos = yt.get_playlist_videos(playlist['id'], max_results=1)
            # 正確な動画数を取得するため、さらに詳細を取得
            all_videos = yt.get_playlist_videos(playlist['id'], max_results=200)
            print(f"   📹 動画数: {len(all_videos)}")
        except YouTubeAPIError:
            print(f"   📹 動画数: 取得失敗")
        
        # 説明文（短縮版）
        description = snippet.get('description', '')
        if description:
            print(f"   📝 説明: {description[:100]}...")
        
        print()

except YouTubeAPIError as e:
    if e.is_not_found():
        print("❌ 指定されたチャンネルが見つかりません")
    else:
        print(f"エラー: {e}")

# チャンネルのコンテンツ構造分析
def analyze_channel_playlists(channel_id: str):
    """チャンネルのプレイリスト構造を分析"""
    try:
        # チャンネル基本情報
        channel_info = yt.get_channel_info(channel_id)
        playlists = yt.get_channel_playlists(channel_id, max_results=100)
        
        print(f"=== {channel_info['snippet']['title']} のコンテンツ分析 ===")
        print()
        
        total_playlist_videos = 0
        playlist_details = []
        
        # 各プレイリストの詳細分析
        for playlist in playlists:
            try:
                videos = yt.get_playlist_videos(playlist['id'], max_results=200)
                video_count = len(videos)
                total_playlist_videos += video_count
                
                playlist_details.append({
                    'title': playlist['snippet']['title'],
                    'video_count': video_count,
                    'created_date': playlist['snippet']['publishedAt'],
                    'id': playlist['id']
                })
                
            except YouTubeAPIError:
                continue
        
        # プレイリストを動画数でソート
        playlist_details.sort(key=lambda x: x['video_count'], reverse=True)
        
        # 結果表示
        print(f"📊 プレイリスト数: {len(playlists)}")
        print(f"📹 プレイリスト内総動画数: {total_playlist_videos}")
        print(f"📈 平均動画数/プレイリスト: {total_playlist_videos // len(playlists) if playlists else 0}")
        print()
        
        print("🔝 動画数上位のプレイリスト:")
        for i, playlist in enumerate(playlist_details[:10], 1):
            print(f"  {i}. {playlist['title']}: {playlist['video_count']}本")
        
        # 最近作成されたプレイリスト
        recent_playlists = sorted(playlist_details, 
                                key=lambda x: x['created_date'], reverse=True)[:5]
        
        print("\n🆕 最近のプレイリスト:")
        for playlist in recent_playlists:
            date = playlist['created_date'][:10]
            print(f"  - {playlist['title']} ({date})")
        
        return playlist_details
        
    except YouTubeAPIError as e:
        print(f"分析エラー: {e}")
        return []

# チャンネル分析の実行
channel_analysis = analyze_channel_playlists("UC_x5XG1OV2P6uZZ5FSM9Ttw")

# 特定のプレイリストタイプを検索
def find_playlists_by_keyword(channel_id: str, keywords: list):
    """チャンネル内で特定のキーワードを含むプレイリストを検索"""
    try:
        playlists = yt.get_channel_playlists(channel_id)
        matched_playlists = []
        
        for playlist in playlists:
            title = playlist['snippet']['title'].lower()
            description = playlist['snippet'].get('description', '').lower()
            
            for keyword in keywords:
                if keyword.lower() in title or keyword.lower() in description:
                    matched_playlists.append({
                        'playlist': playlist,
                        'matched_keyword': keyword
                    })
                    break
        
        return matched_playlists
        
    except YouTubeAPIError as e:
        print(f"検索エラー: {e}")
        return []

# キーワード検索の例
keywords = ['入門', '基礎', 'tutorial', '講座', 'course']
matched = find_playlists_by_keyword("UC_x5XG1OV2P6uZZ5FSM9Ttw", keywords)

print(f"=== キーワードマッチしたプレイリスト ({len(matched)}件) ===")
for match in matched:
    playlist = match['playlist']
    keyword = match['matched_keyword']
    print(f"📝 {playlist['snippet']['title']}")
    print(f"   🔍 マッチキーワード: {keyword}")
    print(f"   🔗 ID: {playlist['id']}")
    print()
```

---

## ページネーション機能

YouTube.py3では、大量のデータを効率的に取得するためのページネーション機能を提供しています。これにより、APIクォータを節約しながら必要なデータを段階的に取得できます。

### search_videos_paginated()

```python
def search_videos_paginated(query: str, max_results: int = 50, order: str = "relevance", page_token: str = None) -> dict
```

ページネーション対応の動画検索機能。

**パラメータ:**
- `query` (str): 検索キーワード
- `max_results` (int): 1ページあたりの最大結果数（1-50、デフォルト: 50）
- `order` (str): ソート順序（デフォルト: 'relevance'）
- `page_token` (str): 次ページ取得用のトークン（オプション）

**戻り値:**
```python
{
    'items': [...],  # 検索結果のリスト
    'nextPageToken': 'token_string',  # 次ページのトークン
    'prevPageToken': 'token_string',  # 前ページのトークン（存在する場合）
    'pageInfo': {
        'totalResults': 1000000,  # 総結果数
        'resultsPerPage': 50      # 1ページあたりの結果数
    }
}
```

**詳細な使用例:**
```python
# 基本的なページネーション
def paginated_video_search(query: str, total_videos: int = 200):
    """ページネーションを使用して大量の動画を検索"""
    all_videos = []
    next_page_token = None
    page_count = 0
    
    while len(all_videos) < total_videos:
        try:
            # 1ページあたり50件取得
            remaining = min(50, total_videos - len(all_videos))
            
            result = yt.search_videos_paginated(
                query=query,
                max_results=remaining,
                page_token=next_page_token
            )
            
            # 結果を追加
            all_videos.extend(result['items'])
            page_count += 1
            
            print(f"ページ {page_count}: {len(result['items'])}件取得 "
                  f"(累計: {len(all_videos)}件)")
            
            # 次ページトークンをチェック
            next_page_token = result.get('nextPageToken')
            if not next_page_token:
                print("最後のページに到達しました")
                break
                
            # レート制限対策
            import time
            time.sleep(0.1)
            
        except YouTubeAPIError as e:
            print(f"エラー: {e}")
            break
    
    print(f"✅ 合計 {len(all_videos)} 件の動画を取得しました")
    return all_videos

# 使用例
videos = paginated_video_search("Python プログラミング", total_videos=500)

# 進捗表示付きの高度な例
def advanced_paginated_search(query: str, max_videos: int = 1000):
    """進捗表示とエラーハンドリング付きの検索"""
    videos = []
    next_token = None
    page = 0
    
    print(f"🔍 '{query}' の検索を開始...")
    print(f"📊 目標取得数: {max_videos}件")
    print("-" * 50)
    
    while len(videos) < max_videos:
        page += 1
        remaining = min(50, max_videos - len(videos))
        
        try:
            result = yt.search_videos_paginated(
                query=query,
                max_results=remaining,
                page_token=next_token
            )
            
            page_videos = result['items']
            videos.extend(page_videos)
            
            # 進捗表示
            progress = (len(videos) / max_videos) * 100
            print(f"📄 ページ {page:2d}: {len(page_videos):2d}件 | "
                  f"累計 {len(videos):4d}件 ({progress:5.1f}%)")
            
            # 次ページチェック
            next_token = result.get('nextPageToken')
            if not next_token:
                print("📋 利用可能なすべての結果を取得しました")
                break
            
            # レート制限対策（1秒あたり100リクエスト制限）
            time.sleep(0.01)
            
        except YouTubeAPIError as e:
            if e.is_quota_exceeded():
                print("❌ APIクォータ制限に達しました")
                print(f"💡 現在までに {len(videos)} 件取得済み")
                break
            else:
                print(f"⚠️ エラーが発生しましたが継続します: {e}")
                continue
    
    print("-" * 50)
    print(f"✅ 検索完了: {len(videos)} 件取得")
    return videos
```

### get_playlist_videos_paginated()

```python
def get_playlist_videos_paginated(playlist_id: str, max_results: int = 50, page_token: str = None) -> dict
```

ページネーション対応のプレイリスト動画取得機能。

**詳細な使用例:**
```python
def get_full_playlist(playlist_id: str, max_videos: int = None):
    """プレイリストの全動画を取得（ページネーション使用）"""
    all_videos = []
    next_token = None
    page = 0
    
    print(f"📝 プレイリスト {playlist_id} の動画を取得中...")
    
    while True:
        page += 1
        
        try:
            result = yt.get_playlist_videos_paginated(
                playlist_id=playlist_id,
                max_results=50,
                page_token=next_token
            )
            
            page_videos = result['items']
            all_videos.extend(page_videos)
            
            print(f"📄 ページ {page}: {len(page_videos)}件取得 "
                  f"(累計: {len(all_videos)}件)")
            
            # 最大数チェック
            if max_videos and len(all_videos) >= max_videos:
                all_videos = all_videos[:max_videos]
                print(f"🎯 目標数 {max_videos} に到達")
                break
            
            # 次ページチェック
            next_token = result.get('nextPageToken')
            if not next_token:
                print("📋 プレイリストの最後に到達")
                break
                
            time.sleep(0.05)  # レート制限対策
            
        except YouTubeAPIError as e:
            print(f"エラー: {e}")
            break
    
    return all_videos

# 大規模プレイリストの分析
def analyze_large_playlist(playlist_id: str):
    """大規模プレイリストの詳細分析"""
    print("📊 大規模プレイリスト分析を開始...")
    
    # プレイリスト基本情報
    try:
        playlist_info = yt.get_playlist_info(playlist_id)
        print(f"📝 プレイリスト: {playlist_info['snippet']['title']}")
    except YouTubeAPIError:
        print("📝 プレイリスト情報の取得に失敗")
    
    # 全動画を段階的に取得
    videos = get_full_playlist(playlist_id)
    
    if not videos:
        print("❌ 動画の取得に失敗しました")
        return
    
    # 分析データの収集
    channels = {}
    categories = {}
    total_duration = 0
    dates = []
    
    print("🔍 動画詳細を分析中...")
    for i, video in enumerate(videos):
        try:
            video_id = video['snippet']['resourceId']['videoId']
            detail = yt.get_video_info(video_id)
            
            # チャンネル集計
            channel = detail['snippet']['channelTitle']
            channels[channel] = channels.get(channel, 0) + 1
            
            # 日付収集
            dates.append(detail['snippet']['publishedAt'])
            
            # 進捗表示（100件ごと）
            if (i + 1) % 100 == 0:
                progress = ((i + 1) / len(videos)) * 100
                print(f"  進捗: {i + 1}/{len(videos)} ({progress:.1f}%)")
            
        except YouTubeAPIError:
            continue
    
    # 分析結果の表示
    print("\n=== 分析結果 ===")
    print(f"📹 総動画数: {len(videos)}")
    print(f"📺 関連チャンネル数: {len(channels)}")
    
    # トップチャンネル
    top_channels = sorted(channels.items(), key=lambda x: x[1], reverse=True)[:10]
    print("\n🔝 上位チャンネル:")
    for i, (channel, count) in enumerate(top_channels, 1):
        print(f"  {i:2d}. {channel}: {count}本")
    
    # 期間分析
    if dates:
        dates.sort()
        print(f"\n📅 期間: {dates[0][:10]} ～ {dates[-1][:10]}")
    
    return {
        'total_videos': len(videos),
        'channels': channels,
        'date_range': (dates[0], dates[-1]) if dates else None
    }
```

### get_comments_paginated()

```python
def get_comments_paginated(video_id: str, max_results: int = 100, page_token: str = None) -> dict
```

ページネーション対応のコメント取得機能。

**詳細な使用例:**
```python
def get_all_comments(video_id: str, max_comments: int = 1000):
    """動画の全コメントを取得（ページネーション使用）"""
    all_comments = []
    next_token = None
    page = 0
    
    print(f"💬 動画 {video_id} のコメントを取得中...")
    
    while len(all_comments) < max_comments:
        page += 1
        remaining = min(100, max_comments - len(all_comments))
        
        try:
            result = yt.get_comments_paginated(
                video_id=video_id,
                max_results=remaining,
                page_token=next_token
            )
            
            page_comments = result['items']
            all_comments.extend(page_comments)
            
            print(f"📄 ページ {page}: {len(page_comments)}件 "
                  f"(累計: {len(all_comments)}件)")
            
            next_token = result.get('nextPageToken')
            if not next_token:
                print("📋 すべてのコメントを取得しました")
                break
                
            time.sleep(0.1)  # レート制限対策
            
        except YouTubeAPIError as e:
            if e.is_forbidden():
                print("❌ コメントが無効化されています")
                break
            else:
                print(f"エラー: {e}")
                break
    
    return all_comments

# コメント感情分析（大規模）
def analyze_comments_sentiment(video_id: str):
    """大量のコメントの感情分析"""
    comments = get_all_comments(video_id, max_comments=5000)
    
    if not comments:
        print("コメントが取得できませんでした")
        return
    
    # 感情分析用キーワード
    positive_keywords = [
        '良い', 'いい', 'すごい', '素晴らしい', '最高', '感動',
        'ありがとう', '助かった', '勉強になる', '分かりやすい'
    ]
    
    negative_keywords = [
        '悪い', 'だめ', 'つまらない', '分からない', '難しい',
        'イマイチ', '微妙', '期待外れ'
    ]
    
    # 感情分類
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    
    for comment in comments:
        text = comment['snippet']['topLevelComment']['snippet']['textDisplay'].lower()
        
        is_positive = any(keyword in text for keyword in positive_keywords)
        is_negative = any(keyword in text for keyword in negative_keywords)
        
        if is_positive and not is_negative:
            positive_count += 1
        elif is_negative and not is_positive:
            negative_count += 1
        else:
            neutral_count += 1
    
    total = len(comments)
    print(f"\n=== コメント感情分析結果 ===")
    print(f"💬 総コメント数: {total}")
    print(f"😊 ポジティブ: {positive_count} ({positive_count/total*100:.1f}%)")
    print(f"😞 ネガティブ: {negative_count} ({negative_count/total*100:.1f}%)")
    print(f"😐 中立: {neutral_count} ({neutral_count/total*100:.1f}%)")
    
    return {
        'total': total,
        'positive': positive_count,
        'negative': negative_count,
        'neutral': neutral_count
    }
```

### get_channel_videos_paginated()

```python
def get_channel_videos_paginated(channel_id: str, max_results: int = 50, page_token: str = None) -> dict
```

ページネーション対応のチャンネル動画取得機能。

**詳細な使用例:**
```python
def get_all_channel_videos(channel_id: str):
    """チャンネルの全動画を取得"""
    all_videos = []
    next_token = None
    page = 0
    
    try:
        # チャンネル情報を取得
        channel_info = yt.get_channel_info(channel_id)
        channel_name = channel_info['snippet']['title']
        total_videos = int(channel_info['statistics']['videoCount'])
        
        print(f"📺 {channel_name} の動画を取得中...")
        print(f"📊 総動画数: {total_videos}")
        print("-" * 50)
        
    except YouTubeAPIError:
        print("チャンネル情報の取得に失敗")
        return []
    
    while True:
        page += 1
        
        try:
            result = yt.get_channel_videos_paginated(
                channel_id=channel_id,
                max_results=50,
                page_token=next_token
            )
            
            page_videos = result['items']
            all_videos.extend(page_videos)
            
            progress = (len(all_videos) / total_videos) * 100
            print(f"📄 ページ {page:2d}: {len(page_videos):2d}件 | "
                  f"累計 {len(all_videos):4d}件 ({progress:5.1f}%)")
            
            next_token = result.get('nextPageToken')
            if not next_token:
                print("📋 すべての動画を取得しました")
                break
                
            time.sleep(0.05)
            
        except YouTubeAPIError as e:
            print(f"エラー: {e}")
            break
    
    return all_videos

# チャンネルの成長分析
def analyze_channel_growth_over_time(channel_id: str):
    """チャンネルの時系列成長分析"""
    videos = get_all_channel_videos(channel_id)
    
    if not videos:
        return
    
    # 動画を公開日でソート
    videos_with_dates = []
    
    print("📊 動画詳細を取得中...")
    for i, video in enumerate(videos):
        try:
            video_detail = yt.get_video_info(video['id']['videoId'])
            videos_with_dates.append({
                'date': video_detail['snippet']['publishedAt'],
                'views': int(video_detail['statistics']['viewCount']),
                'title': video_detail['snippet']['title']
            })
            
            if (i + 1) % 50 == 0:
                print(f"  進捗: {i + 1}/{len(videos)}")
                
        except YouTubeAPIError:
            continue
    
    # 日付でソート
    videos_with_dates.sort(key=lambda x: x['date'])
    
    # 月別集計
    from collections import defaultdict
    monthly_data = defaultdict(list)
    
    for video in videos_with_dates:
        month = video['date'][:7]  # YYYY-MM
        monthly_data[month].append(video)
    
    print("\n=== 月別動画投稿分析 ===")
    print(f"{'月':<10} {'動画数':<6} {'平均再生数':<12} {'最高再生数':<12}")
    print("-" * 50)
    
    for month in sorted(monthly_data.keys()):
        videos_in_month = monthly_data[month]
        avg_views = sum(v['views'] for v in videos_in_month) / len(videos_in_month)
        max_views = max(v['views'] for v in videos_in_month)
        
        print(f"{month:<10} {len(videos_in_month):<6} {avg_views:>10,.0f} {max_views:>10,}")
```

### ページネーション使用のベストプラクティス

```python
class PaginationHelper:
    """ページネーション処理のヘルパークラス"""
    
    def __init__(self, youtube_api):
        self.yt = youtube_api
        self.request_count = 0
        self.start_time = time.time()
    
    def get_all_results(self, search_function, *args, max_total=None, **kwargs):
        """汎用的なページネーション処理"""
        all_results = []
        next_token = None
        page = 0
        
        while True:
            page += 1
            self.request_count += 1
            
            try:
                # ページトークンを追加してリクエスト
                if 'page_token' in kwargs:
                    kwargs['page_token'] = next_token
                else:
                    kwargs = {**kwargs, 'page_token': next_token}
                
                result = search_function(*args, **kwargs)
                
                # 結果を追加
                page_results = result['items']
                all_results.extend(page_results)
                
                # 進捗表示
                elapsed = time.time() - self.start_time
                rate = self.request_count / elapsed if elapsed > 0 else 0
                
                print(f"📄 ページ {page}: {len(page_results)}件 | "
                      f"累計: {len(all_results)}件 | "
                      f"レート: {rate:.1f}req/s")
                
                # 制限チェック
                if max_total and len(all_results) >= max_total:
                    all_results = all_results[:max_total]
                    print(f"🎯 制限数 {max_total} に到達")
                    break
                
                # 次ページチェック
                next_token = result.get('nextPageToken')
                if not next_token:
                    print("📋 最後のページに到達")
                    break
                
                # レート制限対策
                self._rate_limit()
                
            except YouTubeAPIError as e:
                print(f"⚠️ エラー: {e}")
                if e.is_quota_exceeded():
                    print("❌ クォータ制限に達しました")
                    break
                elif e.is_forbidden():
                    print("❌ アクセス権限がありません")
                    break
                else:
                    print("🔄 エラーを無視して継続します")
                    continue
        
        return all_results
    
    def _rate_limit(self):
        """レート制限対策"""
        # YouTube API は1秒あたり100リクエストまで
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            current_rate = self.request_count / elapsed
            if current_rate > 90:  # 安全マージン
                sleep_time = (self.request_count / 90) - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)

# 使用例
helper = PaginationHelper(yt)

# 大量の動画検索
videos = helper.get_all_results(
    yt.search_videos_paginated,
    "Python 機械学習",
    max_results=50,
    max_total=1000
)

# チャンネルの全動画取得
channel_videos = helper.get_all_results(
    yt.get_channel_videos_paginated,
    "UC_x5XG1OV2P6uZZ5FSM9Ttw",
    max_results=50
)

print(f"📊 APIリクエスト総数: {helper.request_count}")
print(f"⏱️ 実行時間: {time.time() - helper.start_time:.1f}秒")
```

---

**最終更新**: 2024年12月
**関連ドキュメント**: [README](README.md) | [インストールガイド](installation.md) | [トラブルシューティング](troubleshooting.md)