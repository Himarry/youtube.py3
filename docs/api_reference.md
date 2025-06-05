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
- [エラーハンドリング](#エラーハンドリング)

---

## 基本クラス

### YouTubeAPI

```python
class YouTubeAPI(api_key: str)
```

YouTube Data API v3のメインクラス。

**パラメータ:**
- `api_key` (str): YouTube Data API v3のAPIキー

**例外:**
- `YouTubeAPIError`: APIキーが無効な場合

**使用例:**
```python
from youtube_py3 import YouTubeAPI
import os

api_key = os.getenv('YOUTUBE_API_KEY')
yt = YouTubeAPI(api_key)
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

**使用例:**
```python
try:
    video = yt.get_video_info("invalid_id")
except YouTubeAPIError as e:
    print(f"エラー: {e}")
    if e.is_quota_exceeded():
        print("推奨アクション:", e.get_suggested_action())
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

**使用例:**
```python
if yt.check_quota_usage():
    print("APIキーは有効です")
```

### get_channel_info()

```python
def get_channel_info(channel_id: str) -> dict
```

チャンネル情報を取得します。

**パラメータ:**
- `channel_id` (str): YouTubeチャンネルのID

**戻り値:**
- `dict`: チャンネル情報の辞書
  - `snippet`: チャンネルの基本情報（タイトル、説明など）
  - `statistics`: 統計情報（登録者数、動画数など）

**例外:**
- `YouTubeAPIError`: チャンネルが見つからない場合

**使用例:**
```python
channel = yt.get_channel_info("UC_x5XG1OV2P6uZZ5FSM9Ttw")
print(f"チャンネル名: {channel['snippet']['title']}")
print(f"登録者数: {channel['statistics']['subscriberCount']}")
```

### get_video_info()

```python
def get_video_info(video_id: str) -> dict
```

動画情報を取得します。

**パラメータ:**
- `video_id` (str): YouTube動画のID

**戻り値:**
- `dict`: 動画情報の辞書
  - `snippet`: 動画の基本情報（タイトル、説明、チャンネル名など）
  - `statistics`: 統計情報（再生回数、いいね数など）

**例外:**
- `YouTubeAPIError`: 動画が見つからない場合

**使用例:**
```python
video = yt.get_video_info("dQw4w9WgXcQ")
print(f"動画タイトル: {video['snippet']['title']}")
print(f"再生回数: {video['statistics']['viewCount']}")
```

### get_channel_statistics_only()

```python
def get_channel_statistics_only(channel_id: str) -> dict
```

チャンネルの統計情報のみを効率的に取得します。

**パラメータ:**
- `channel_id` (str): YouTubeチャンネルのID

**戻り値:**
- `dict`: 統計情報のみ

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
- `max_results` (int): 取得する最大結果数（デフォルト: 5）
- `order` (str): ソート順序（デフォルト: 'relevance'）
  - `'relevance'`: 関連度順
  - `'date'`: 投稿日時順
  - `'rating'`: 評価順
  - `'viewCount'`: 再生回数順
  - `'title'`: タイトル順

**戻り値:**
- `list`: 検索結果の動画リスト

**使用例:**
```python
videos = yt.search_videos("Python プログラミング", max_results=10, order="viewCount")
for video in videos:
    print(f"- {video['snippet']['title']}")
```

### search_channels()

```python
def search_channels(query: str, max_results: int = 5, order: str = "relevance") -> list
```

チャンネルを検索します。

**パラメータ:**
- `query` (str): 検索キーワード
- `max_results` (int): 取得する最大結果数（デフォルト: 5）
- `order` (str): ソート順序（デフォルト: 'relevance'）

**戻り値:**
- `list`: 検索結果のチャンネルリスト

**使用例:**
```python
channels = yt.search_channels("Python教育", max_results=5)
for channel in channels:
    print(f"- {channel['snippet']['title']}")
```

### search_playlists()

```python
def search_playlists(query: str, max_results: int = 5, order: str = "relevance") -> list
```

プレイリストを検索します。

**パラメータ:**
- `query` (str): 検索キーワード
- `max_results` (int): 取得する最大結果数（デフォルト: 5）
- `order` (str): ソート順序（デフォルト: 'relevance'）

**戻り値:**
- `list`: 検索結果のプレイリストリスト

**使用例:**
```python
playlists = yt.search_playlists("Python講座", max_results=5)
for playlist in playlists:
    print(f"- {playlist['snippet']['title']}")
```

### search_all()

```python
def search_all(query: str, search_type: str = "video,channel,playlist", max_results: int = 25, order: str = "relevance") -> list
```

動画、チャンネル、プレイリストを横断して検索します。

**パラメータ:**
- `query` (str): 検索キーワード
- `search_type` (str): 検索対象（カンマ区切り）
- `max_results` (int): 取得する最大結果数（デフォルト: 25）
- `order` (str): ソート順序（デフォルト: 'relevance'）

**使用例:**
```python
results = yt.search_all("AI", search_type="video,channel", max_results=20)
for item in results:
    print(f"[{item['id']['kind']}] {item['snippet']['title']}")
```

---

## プレイリスト管理

### get_playlist_info()

```python
def get_playlist_info(playlist_id: str) -> dict
```

プレイリスト情報を取得します。

**パラメータ:**
- `playlist_id` (str): YouTubeプレイリストのID

**戻り値:**
- `dict`: プレイリスト情報

**使用例:**
```python
playlist = yt.get_playlist_info("PLxyz123")
print(f"プレイリスト名: {playlist['snippet']['title']}")
```

### get_playlist_videos()

```python
def get_playlist_videos(playlist_id: str, max_results: int = 50) -> list
```

プレイリストの動画一覧を取得します。

**パラメータ:**
- `playlist_id` (str): YouTubeプレイリストのID
- `max_results` (int): 取得する最大動画数（デフォルト: 50）

**戻り値:**
- `list`: 動画情報のリスト

**使用例:**
```python
videos = yt.get_playlist_videos("PLxyz123", max_results=100)
print(f"プレイリストに{len(videos)}個の動画があります")
```

### get_channel_playlists()

```python
def get_channel_playlists(channel_id: str, max_results: int = 50) -> list
```

チャンネルのプレイリスト一覧を取得します。

**パラメータ:**
- `channel_id` (str): YouTubeチャンネルのID
- `max_results` (int): 取得する最大プレイリスト数（デフォルト: 50）

**戻り値:**
- `list`: プレイリスト情報のリスト

**使用例:**
```python
playlists = yt.get_channel_playlists("UC_x5XG1OV2P6uZZ5FSM9Ttw")
for playlist in playlists:
    print(f"- {playlist['snippet']['title']}")
```

---

## コメント管理

### get_comments()

```python
def get_comments(video_id: str, max_results: int = 100) -> list
```

動画のコメントを取得します。

**パラメータ:**
- `video_id` (str): YouTube動画のID
- `max_results` (int): 取得する最大コメント数（デフォルト: 100）

**戻り値:**
- `list`: コメント情報のリスト

**例外:**
- `YouTubeAPIError`: コメントが無効化されている場合

**使用例:**
```python
comments = yt.get_comments("dQw4w9WgXcQ", max_results=50)
for comment in comments:
    snippet = comment['snippet']['topLevelComment']['snippet']
    print(f"- {snippet['authorDisplayName']}: {snippet['textDisplay']}")
```

### get_video_comments_with_replies()

```python
def get_video_comments_with_replies(video_id: str, max_results: int = 100) -> list
```

動画のコメントを返信付きで取得します。

**パラメータ:**
- `video_id` (str): YouTube動画のID
- `max_results` (int): 取得する最大コメント数（デフォルト: 100）

**戻り値:**
- `list`: コメントと返信を含む情報のリスト

**使用例:**
```python
comments = yt.get_video_comments_with_replies("dQw4w9WgXcQ")
for comment in comments:
    # トップレベルコメント
    top_comment = comment['snippet']['topLevelComment']['snippet']
    print(f"コメント: {top_comment['textDisplay']}")
    
    # 返信がある場合
    if 'replies' in comment:
        for reply in comment['replies']['comments']:
            reply_snippet = reply['snippet']
            print(f"  返信: {reply_snippet['textDisplay']}")
```

---

## チャンネル管理

### get_channel_videos()

```python
def get_channel_videos(channel_id: str, max_results: int = 50) -> list
```

チャンネルの最新動画を取得します。

**パラメータ:**
- `channel_id` (str): YouTubeチャンネルのID
- `max_results` (int): 取得する最大動画数（デフォルト: 50）

**戻り値:**
- `list`: 動画情報のリスト（新しい順）

**使用例:**
```python
videos = yt.get_channel_videos("UC_x5XG1OV2P6uZZ5FSM9Ttw", max_results=20)
for video in videos:
    print(f"- {video['snippet']['title']}")
```

### get_channel_sections()

```python
def get_channel_sections(channel_id: str) -> list
```

チャンネルセクション情報を取得します。

**パラメータ:**
- `channel_id` (str): YouTubeチャンネルのID

**戻り値:**
- `list`: チャンネルセクション情報のリスト

**使用例:**
```python
sections = yt.get_channel_sections("UC_x5XG1OV2P6uZZ5FSM9Ttw")
for section in sections:
    print(f"セクション: {section['snippet']['title']}")
```

### get_channel_activities()

```python
def get_channel_activities(channel_id: str, max_results: int = 50) -> list
```

チャンネルのアクティビティを取得します。

**パラメータ:**
- `channel_id` (str): YouTubeチャンネルのID
- `max_results` (int): 取得する最大アクティビティ数（デフォルト: 50）

**戻り値:**
- `list`: アクティビティ情報のリスト

**使用例:**
```python
activities = yt.get_channel_activities("UC_x5XG1OV2P6uZZ5FSM9Ttw")
for activity in activities:
    print(f"アクティビティ: {activity['snippet']['type']}")
```

---

## 動画管理

### get_popular_videos()

```python
def get_popular_videos(region_code: str = "JP", category_id: str = None, max_results: int = 50) -> list
```

人気動画を取得します。

**パラメータ:**
- `region_code` (str): 地域コード（デフォルト: 'JP'）
- `category_id` (str): カテゴリID（オプション）
- `max_results` (int): 取得する最大動画数（デフォルト: 50）

**戻り値:**
- `list`: 人気動画のリスト

**使用例:**
```python
popular_videos = yt.get_popular_videos(region_code="US", max_results=10)
for video in popular_videos:
    print(f"- {video['snippet']['title']}")
```

### get_video_categories()

```python
def get_video_categories(region_code: str = "JP") -> list
```

動画カテゴリ一覧を取得します。

**パラメータ:**
- `region_code` (str): 地域コード（デフォルト: 'JP'）

**戻り値:**
- `list`: カテゴリ情報のリスト

**使用例:**
```python
categories = yt.get_video_categories()
for category in categories:
    print(f"- {category['snippet']['title']}")
```

---

## ライブストリーミング

### get_live_streams()

```python
def get_live_streams(part: str = "snippet,status", mine: bool = False, max_results: int = 25) -> list
```

ライブストリーム情報を取得します。

**パラメータ:**
- `part` (str): 取得する情報の種類（デフォルト: 'snippet,status'）
- `mine` (bool): 自分のストリームのみ取得するか（デフォルト: False）
- `max_results` (int): 取得する最大結果数（デフォルト: 25）

**戻り値:**
- `list`: ライブストリーム情報のリスト

**使用例:**
```python
streams = yt.get_live_streams(mine=True)
for stream in streams:
    print(f"ストリーム: {stream['snippet']['title']}")
```

### get_live_broadcasts()

```python
def get_live_broadcasts(broadcast_status: str = "all", max_results: int = 25) -> list
```

ライブ配信情報を取得します。

**パラメータ:**
- `broadcast_status` (str): 配信状態（'all', 'active', 'completed', 'upcoming'）
- `max_results` (int): 取得する最大結果数（デフォルト: 25）

**戻り値:**
- `list`: ライブ配信情報のリスト

**使用例:**
```python
broadcasts = yt.get_live_broadcasts(broadcast_status="active")
for broadcast in broadcasts:
    print(f"配信: {broadcast['snippet']['title']}")
```

---

## 字幕管理

### get_video_captions()

```python
def get_video_captions(video_id: str) -> list
```

動画の字幕一覧を取得します。

**パラメータ:**
- `video_id` (str): YouTube動画のID

**戻り値:**
- `list`: 字幕情報のリスト

**注意:**
このメソッドは現在実装中です。

### download_caption()

```python
def download_caption(caption_id: str, format: str = "srt") -> str
```

字幕をダウンロードします。

**パラメータ:**
- `caption_id` (str): 字幕ID
- `format` (str): ダウンロード形式（'srt', 'vtt', 'ttml'）

**戻り値:**
- `str`: 字幕テキスト

**注意:**
このメソッドは現在実装中です。

### upload_caption()

```python
def upload_caption(video_id: str, language: str, name: str, caption_file) -> dict
```

字幕をアップロードします。

**パラメータ:**
- `video_id` (str): YouTube動画のID
- `language` (str): 言語コード（例: 'ja', 'en'）
- `name` (str): 字幕名
- `caption_file`: 字幕ファイル

**戻り値:**
- `dict`: アップロード結果

**注意:**
このメソッドは現在実装中です。

---

## サブスクリプション管理

### get_subscriptions()

```python
def get_subscriptions(channel_id: str = None, mine: bool = False, max_results: int = 50) -> list
```

サブスクリプション一覧を取得します。

**パラメータ:**
- `channel_id` (str): チャンネルID（オプション）
- `mine` (bool): 自分のサブスクリプションを取得するか（デフォルト: False）
- `max_results` (int): 取得する最大数（デフォルト: 50）

**戻り値:**
- `list`: サブスクリプション情報のリスト

**注意:**
このメソッドは現在実装中です。

---

## システム情報

### get_supported_languages()

```python
def get_supported_languages() -> list
```

YouTubeでサポートされている言語一覧を取得します。

**戻り値:**
- `list`: 言語情報のリスト

**使用例:**
```python
languages = yt.get_supported_languages()
for lang in languages:
    print(f"- {lang['snippet']['name']}")
```

### get_supported_regions()

```python
def get_supported_regions() -> list
```

YouTubeでサポートされている地域一覧を取得します。

**戻り値:**
- `list`: 地域情報のリスト

**使用例:**
```python
regions = yt.get_supported_regions()
for region in regions:
    print(f"- {region['snippet']['name']}")
```

### get_video_abuse_report_reasons()

```python
def get_video_abuse_report_reasons() -> list
```

動画の報告理由一覧を取得します。

**戻り値:**
- `list`: 報告理由のリスト

**使用例:**
```python
reasons = yt.get_video_abuse_report_reasons()
for reason in reasons:
    print(f"- {reason['snippet']['label']}")
```

---

## エラーハンドリング

YouTube.py2では、すべてのAPIエラーを`YouTubeAPIError`例外として統一的に処理します。

### 基本的なエラーハンドリング

```python
from youtube_py2 import YouTubeAPI, YouTubeAPIError

try:
    yt = YouTubeAPI(api_key)
    video = yt.get_video_info("invalid_video_id")
except YouTubeAPIError as e:
    print(f"YouTube APIエラー: {e}")
    
    # エラーの種類に応じた処理
    if e.is_quota_exceeded():
        print("推奨アクション:", e.get_suggested_action())
    elif e.is_api_key_invalid():
        print("推奨アクション:", e.get_suggested_action())
    elif e.is_not_found():
        print("推奨アクション:", e.get_suggested_action())
        
except Exception as e:
    print(f"予期しないエラー: {e}")
```

### YouTubeAPIErrorのメソッド

**エラー判定メソッド:**
- `is_quota_exceeded()`: クォータ超過エラーかどうか
- `is_api_key_invalid()`: APIキー無効エラーかどうか
- `is_not_found()`: リソースが見つからないエラーかどうか
- `is_forbidden()`: アクセス権限エラーかどうか

**ヘルパーメソッド:**
- `get_suggested_action()`: エラーに対する推奨アクションを取得

### よくあるエラーとその対処法

#### 1. APIキー関連
```python
try:
    yt = YouTubeAPI("")  # 空のAPIキー
except YouTubeAPIError as e:
    if e.is_api_key_invalid():
        print("推奨アクション:", e.get_suggested_action())
```

#### 2. クォータ制限
```python
try:
    videos = yt.search_videos("Python", max_results=1000)
except YouTubeAPIError as e:
    if e.is_quota_exceeded():
        print("推奨アクション:", e.get_suggested_action())
```

#### 3. リソースが見つからない
```python
try:
    video = yt.get_video_info("nonexistent_video_id")
except YouTubeAPIError as e:
    if e.is_not_found():
        print("推奨アクション:", e.get_suggested_action())
```

---

**最終更新**: 2024年12月
**関連ドキュメント**: [README](README.md) | [インストールガイド](installation.md) | [トラブルシューティング](troubleshooting.md)