# YouTube.py3 APIリファレンス

YouTube Data API v3を簡単に使用するためのPythonラッパーライブラリの完全なAPIリファレンスです。

## 📚 目次

- [基本概要](#基本概要)
- [インストールと設定](#インストールと設定)
- [メインクラス](#メインクラス)
- [簡単な使用方法](#簡単な使用方法)
- [簡略化メソッド](#簡略化メソッド)
- [Mixin機能](#mixin機能)
- [メソッド一覧](#メソッド一覧)
- [エラーハンドリング](#エラーハンドリング)
- [実用的な使用例](#実用的な使用例)
- [OAuth認証](#oauth認証)
- [設定とユーティリティ](#設定とユーティリティ)

---

## 基本概要

YouTube.py3は、YouTube Data API v3を初心者でも簡単に使えるようにしたPythonライブラリです。

### 主な特徴

✅ **簡単な初期化**: 環境変数からの自動APIキー取得  
✅ **簡略化メソッド**: 複雑なページネーション処理を自動化  
✅ **OAuth対応**: 動画アップロードやプレイリスト作成に対応  
✅ **エラーハンドリング**: 分かりやすいエラーメッセージと対処法  
✅ **モジュラー設計**: Mixinクラスによる機能分離  
✅ **日本語サポート**: 日本語での詳細なドキュメントとメソッド名

### ライブラリの構造

```
youtube_py3/
├── YouTubeAPI          # メインクラス
├── create_client()     # 簡単初期化関数
├── quick_search()      # ワンライナー検索
└── extract_*_id()      # URL解析ヘルパー
```

---

## インストールと設定

### インストール

```bash
pip install youtube-py3
```

### APIキーの取得

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成
3. YouTube Data API v3を有効化
4. 認証情報ページでAPIキーを作成

### 環境変数の設定

```bash
# Windows
set YOUTUBE_API_KEY=your_api_key_here

# macOS/Linux
export YOUTUBE_API_KEY=your_api_key_here
```

---

## メインクラス

### YouTubeAPI

```python
class YouTubeAPI(api_key=None, oauth_credentials=None, oauth_config=None)
```

YouTube Data API v3のメインクラス。複数のMixinクラスから機能を継承しています。

**継承クラス:**
- `YouTubeAPIBase`: 基本API機能とOAuth管理
- `InfoRetrievalMixin`: 動画・チャンネル・プレイリスト情報取得
- `SearchMixin`: 検索機能
- `PaginationMixin`: ページネーション処理
- `CommentsMixin`: コメント管理
- `PlaylistMixin`: プレイリスト管理
- `ChannelMixin`: チャンネル管理
- `VideoMixin`: 動画管理
- `HelperMixin`: ユーティリティ機能

**パラメータ:**
- `api_key` (str, optional): YouTube Data API v3のAPIキー
- `oauth_credentials` (optional): OAuth認証情報オブジェクト
- `oauth_config` (dict, optional): OAuth設定辞書

**初期化例:**
```python
from youtube_py3 import YouTubeAPI
import os

# 1. 基本的な使用方法
api_key = os.getenv('YOUTUBE_API_KEY')
yt = YouTubeAPI(api_key)

# 2. OAuth設定付き
oauth_config = {
    'client_secrets_file': 'client_secrets.json',
    'scopes': ['https://www.googleapis.com/auth/youtube'],
    'token_file': 'youtube_token.pickle',
    'port': 8080,
    'auto_open_browser': True
}
yt = YouTubeAPI(api_key=api_key, oauth_config=oauth_config)
```

---

## 簡単な使用方法

### create_client()

```python
def create_client(api_key=None, oauth_config=None, auto_setup=True) -> YouTubeAPI
```

YouTubeAPIクライアントを簡単に作成するヘルパー関数。

**パラメータ:**
- `api_key` (str, optional): APIキー（環境変数から自動取得可能）
- `oauth_config` (dict, optional): OAuth設定
- `auto_setup` (bool): 自動セットアップを行うか

**使用例:**
```python
import youtube_py3

# 環境変数から自動取得
yt = youtube_py3.create_client()

# APIキー指定
yt = youtube_py3.create_client(api_key="YOUR_API_KEY")
```

### quick_search()

```python
def quick_search(query, max_results=10, api_key=None) -> list
```

動画を素早く検索するワンライナー関数。

**使用例:**
```python
import youtube_py3

# 簡単な動画検索
videos = youtube_py3.quick_search("Python tutorial", max_results=5)
for video in videos:
    print(video['snippet']['title'])
```

---

## 簡略化メソッド

これらのメソッドは、複雑なページネーション処理を内部で自動化し、大量のデータを簡単に取得できます。

### get_channel_playlists()

```python
def get_channel_playlists(channel_id, max_results=50) -> list
```

チャンネルのプレイリスト一覧を取得します。

**パラメータ:**
- `channel_id` (str): チャンネルID
- `max_results` (int): 最大取得件数（デフォルト: 50）

**戻り値:**
- `list`: プレイリスト情報のリスト

**使用例:**
```python
# チャンネルのプレイリスト取得
playlists = yt.get_channel_playlists("UC_x5XG1OV2P6uZZ5FSM9Ttw", max_results=100)
print(f"📝 プレイリスト数: {len(playlists)}")

for playlist in playlists:
    title = playlist['snippet']['title']
    item_count = playlist['contentDetails']['itemCount']
    print(f"  📋 {title} ({item_count}本)")
```

### search_all_videos()

```python
def search_all_videos(query, max_results=500, channel_id=None) -> list
```

動画を全件検索します。

**パラメータ:**
- `query` (str): 検索キーワード
- `max_results` (int): 最大取得件数（デフォルト: 500）
- `channel_id` (str, optional): 特定チャンネル内検索用のチャンネルID

**使用例:**
```python
# 一般的な動画検索
videos = yt.search_all_videos("Python プログラミング", max_results=100)
print(f"🔍 検索結果: {len(videos)}件")

# 特定チャンネル内での検索
channel_videos = yt.search_all_videos(
    "機械学習", 
    max_results=50,
    channel_id="UC_x5XG1OV2P6uZZ5FSM9Ttw"
)
```

### get_all_channel_videos()

```python
def get_all_channel_videos(channel_id, max_results=500) -> list
```

チャンネルの全動画を取得します。

**パラメータ:**
- `channel_id` (str): チャンネルID
- `max_results` (int): 最大取得件数（デフォルト: 500）

**使用例:**
```python
# チャンネルの全動画取得
all_videos = yt.get_all_channel_videos("UC_x5XG1OV2P6uZZ5FSM9Ttw", max_results=200)
print(f"🎬 動画数: {len(all_videos)}")

# 最新の動画を表示
print("🆕 最新動画:")
for video in all_videos[:5]:
    title = video['snippet']['title']
    published = video['snippet']['publishedAt'][:10]
    print(f"  📹 {title} ({published})")
```

### get_all_playlist_videos()

```python
def get_all_playlist_videos(playlist_id, max_results=500) -> list
```

プレイリストの全動画を取得します。

**パラメータ:**
- `playlist_id` (str): プレイリストID
- `max_results` (int): 最大取得件数（デフォルト: 500）

**使用例:**
```python
# プレイリストの動画一覧取得
playlist_videos = yt.get_all_playlist_videos("PLxyz123", max_results=100)
print(f"📋 プレイリスト動画数: {len(playlist_videos)}")

for i, video in enumerate(playlist_videos, 1):
    title = video['snippet']['title']
    print(f"  {i}. {title}")
```

### get_all_comments()

```python
def get_all_comments(video_id, max_results=1000) -> list
```

動画の全コメントを取得します。

**パラメータ:**
- `video_id` (str): 動画ID
- `max_results` (int): 最大取得件数（デフォルト: 1000）

**使用例:**
```python
try:
    # 動画のコメント取得
    comments = yt.get_all_comments("dQw4w9WgXcQ", max_results=500)
    print(f"💬 コメント数: {len(comments)}")
    
    # コメント内容表示
    for comment in comments[:5]:
        text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
        author = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
        print(f"  {author}: {text[:50]}...")
        
except YouTubeAPIError as e:
    if "コメントが無効" in str(e):
        print("❌ この動画はコメントが無効化されています")
    else:
        print(f"エラー: {e}")
```

---

## Mixin機能

YouTube.py3は機能をMixinクラスに分割しており、各Mixinが特定の機能を提供します。

### YouTubeAPIBase

基本的なAPI接続、OAuth管理、エラーハンドリング機能を提供。

**主な機能:**
- API接続管理
- OAuth認証処理
- エラーハンドリング
- レート制限対応

### InfoRetrievalMixin

各種情報取得機能を提供。

**主なメソッド:**
- `get_channel_info(channel_id)`: チャンネル情報取得
- `get_video_info(video_id)`: 動画情報取得
- `get_playlist_info(playlist_id)`: プレイリスト情報取得

**使用例:**
```python
# チャンネル情報取得
channel = yt.get_channel_info("UC_x5XG1OV2P6uZZ5FSM9Ttw")
print(f"📺 チャンネル名: {channel['snippet']['title']}")
print(f"👥 登録者数: {channel['statistics']['subscriberCount']}")

# 動画情報取得
video = yt.get_video_info("dQw4w9WgXcQ")
print(f"🎬 タイトル: {video['snippet']['title']}")
print(f"👀 再生回数: {video['statistics']['viewCount']}")
```

### SearchMixin

検索機能を提供。

**主なメソッド:**
- `search_videos(query, max_results, order)`: 動画検索
- `search_channels(query, max_results)`: チャンネル検索
- `search_playlists(query, max_results)`: プレイリスト検索

**使用例:**
```python
# 動画検索
videos = yt.search_videos("Python", max_results=10, order="viewCount")
for video in videos:
    print(f"🎬 {video['snippet']['title']}")

# チャンネル検索
channels = yt.search_channels("プログラミング", max_results=5)
for channel in channels:
    print(f"📺 {channel['snippet']['title']}")
```

### PaginationMixin

ページネーション処理を提供。

**主なメソッド:**
- `paginate_all_results(func, *args, max_total_results, **kwargs)`: 全件取得ヘルパー
- 各種`*_paginated`メソッド

**使用例:**
```python
# ページネーションで全件取得
all_results = yt.paginate_all_results(
    yt.search_videos_paginated,
    "Python",
    max_total_results=1000,
    order="date"
)
print(f"📊 総取得件数: {len(all_results)}")
```

### その他のMixin

- **CommentsMixin**: コメント取得・管理
- **PlaylistMixin**: プレイリスト作成・管理（OAuth必須）
- **ChannelMixin**: チャンネル管理（OAuth必須）
- **VideoMixin**: 動画アップロード・管理（OAuth必須）
- **HelperMixin**: ユーティリティ機能

---

## メソッド一覧

### 📋 YouTubeAPIクラスのメソッド

#### 簡略化メソッド（YouTubeAPIクラス独自）

これらのメソッドは `paginate_all_results()` を使用して複雑なページネーション処理を自動化します。

**メソッド一覧:**
```python
# チャンネル関連
get_channel_playlists(channel_id: str, max_results: int = 50) -> list
get_all_channel_videos(channel_id: str, max_results: int = 500) -> list

# 検索関連
search_all_videos(query: str, max_results: int = 500, channel_id: str = None) -> list

# プレイリスト関連
get_all_playlist_videos(playlist_id: str, max_results: int = 500) -> list

# コメント関連
get_all_comments(video_id: str, max_results: int = 1000) -> list
```

**使用例:**
```python
# チャンネルのプレイリスト一覧取得
playlists = yt.get_channel_playlists("UC_x5XG1OV2P6uZZ5FSM9Ttw", max_results=100)

# チャンネルの全動画取得
videos = yt.get_all_channel_videos("UC_x5XG1OV2P6uZZ5FSM9Ttw", max_results=200)

# 検索で大量データ取得
search_results = yt.search_all_videos("Python", max_results=1000)

# 特定チャンネル内検索
channel_search = yt.search_all_videos("機械学習", max_results=100, channel_id="UC_x5XG1OV2P6uZZ5FSM9Ttw")
```

---

#### 基本情報取得（InfoRetrievalMixin）

**メソッド一覧:**
```python
# チャンネル情報
get_channel_info(channel_id: str) -> dict
get_channel_statistics_only(channel_id: str) -> dict
get_channel_from_username(username: str) -> dict

# 動画情報
get_video_info(video_id: str) -> dict
get_video_statistics_only(video_id: str) -> dict
get_video_duration_seconds(video_id: str) -> int

# プレイリスト情報
get_playlist_info(playlist_id: str) -> dict

# システム情報
get_video_categories(region_code: str = "JP") -> list
get_supported_languages() -> list
get_supported_regions() -> list

# OAuth必須
get_my_channel() -> dict
```

**使用例:**
```python
# 基本情報取得
channel = yt.get_channel_info("UC_x5XG1OV2P6uZZ5FSM9Ttw")
video = yt.get_video_info("dQw4w9WgXcQ")

# 統計情報のみ（高速）
stats = yt.get_channel_statistics_only("UC_x5XG1OV2P6uZZ5FSM9Ttw")
print(f"登録者数: {stats['subscriberCount']:,}")

# ユーザー名からチャンネル検索
channel = yt.get_channel_from_username("username")
```

---

#### 検索機能（SearchMixin）

**メソッド一覧:**
```python
# 基本検索
search_videos(query: str, max_results: int = 5, order: str = "relevance") -> list
search_channels(query: str, max_results: int = 5) -> list
search_playlists(query: str, max_results: int = 5) -> list

# ページネーション対応検索
search_videos_paginated(query: str, max_results: int = None, order: str = "relevance", page_token: str = None, channel_id: str = None, **filters) -> dict
search_playlists_paginated(query: str, max_results: int = None, order: str = "relevance", page_token: str = None, **filters) -> dict

# チャンネル動画取得
get_channel_videos(channel_id: str, max_results: int = 50, order: str = "date") -> list
get_channel_videos_paginated(channel_id: str, max_results: int = None, order: str = "date", page_token: str = None) -> dict

# 特殊検索
get_trending_videos(region_code: str = "JP", category_id: str = None, max_results: int = 50) -> list
get_channel_upload_playlist(channel_id: str) -> str
get_latest_videos_from_channel(channel_id: str, max_results: int = 10) -> list
```

**使用例:**
```python
# 基本検索
videos = yt.search_videos("Python", max_results=10, order="viewCount")
channels = yt.search_channels("プログラミング", max_results=5)

# ページネーション検索
result = yt.search_videos_paginated("Python", max_results=50, order="date")
print(f"取得件数: {len(result['items'])}")
if result.get('nextPageToken'):
    print("次のページあり")
```

---

#### プレイリスト管理（PlaylistMixin）

**メソッド一覧:**
```python
# プレイリスト動画取得
get_playlist_videos(playlist_id: str, max_results: int = 50) -> list
get_playlist_videos_paginated(playlist_id: str, max_results: int = None, page_token: str = None) -> dict

# OAuth必須：プレイリスト管理
create_playlist(title: str, description: str = "", privacy_status: str = "private") -> dict
update_playlist(playlist_id: str, title: str = None, description: str = None, privacy_status: str = None) -> dict
delete_playlist(playlist_id: str) -> bool
get_my_playlists(max_results: int = 50) -> list

# OAuth必須：プレイリストアイテム管理
add_video_to_playlist(playlist_id: str, video_id: str, position: int = None) -> dict
remove_video_from_playlist(playlist_item_id: str) -> bool
update_playlist_item_position(playlist_item_id: str, new_position: int) -> dict

# OAuth必須：プレイリスト画像管理
get_playlist_images(playlist_id: str) -> list
upload_playlist_image(playlist_id: str, image_file) -> dict
```

**使用例:**
```python
# プレイリスト動画取得
videos = yt.get_playlist_videos("PLxyz123", max_results=100)

# OAuth必須機能
playlist = yt.create_playlist("学習用", "Python学習動画", "private")
yt.add_video_to_playlist(playlist['id'], "dQw4w9WgXcQ")
```

---

#### コメント管理（CommentsMixin）

**メソッド一覧:**
```python
# コメント取得
get_comments(video_id: str, max_results: int = 100, order: str = "time") -> list
get_comments_paginated(video_id: str, max_results: int = None, order: str = "time", page_token: str = None) -> dict
get_comment_details(comment_id: str) -> dict

# OAuth必須：コメント投稿・管理
post_comment_thread(video_id: str, text: str, channel_id: str = None) -> dict
post_comment_reply(parent_comment_id: str, text: str) -> dict
update_comment(comment_id: str, text: str) -> dict
delete_comment(comment_id: str) -> bool

# OAuth必須：コメントモデレーション
mark_comment_as_spam(comment_id: str) -> bool
set_comment_moderation_status(comment_id: str, moderation_status: str) -> bool
```

**使用例:**
```python
# コメント取得
comments = yt.get_comments("dQw4w9WgXcQ", max_results=50, order="relevance")

# OAuth必須：コメント投稿
comment = yt.post_comment_thread("dQw4w9WgXcQ", "素晴らしい動画です！")
```

---

#### チャンネル管理（ChannelMixin）

**メソッド一覧:**
```python
# OAuth必須：自分のチャンネル管理
get_my_subscriptions(max_results: int = 50) -> list
subscribe_to_channel(channel_id: str) -> dict
unsubscribe_from_channel(subscription_id: str) -> bool

# OAuth必須：チャンネル情報更新
update_channel(channel_id: str, title: str = None, description: str = None, keywords: str = None) -> dict
upload_channel_banner(image_file) -> dict

# OAuth必須：チャンネルセクション管理
create_channel_section(channel_id: str, section_type: str, title: str, position: int = 0) -> dict
update_channel_section(section_id: str, title: str = None, position: int = None) -> dict
delete_channel_section(section_id: str) -> bool

# OAuth必須：透かし管理
set_watermark(channel_id: str, image_file, timing_type: str = "offsetFromStart", offset_ms: int = 15000) -> dict
unset_watermark(channel_id: str) -> bool

# OAuth必須：メンバーシップ
get_channel_members(max_results: int = 50) -> list
get_membership_levels() -> list
```

**使用例:**
```python
# OAuth必須機能
subscriptions = yt.get_my_subscriptions(100)
yt.subscribe_to_channel("UC_x5XG1OV2P6uZZ5FSM9Ttw")

# チャンネル更新
yt.update_channel("my_channel_id", title="新しいチャンネル名")
```

---

#### 動画管理（VideoMixin）

**メソッド一覧:**
```python
# 動画字幕情報取得
get_video_captions(video_id: str) -> list
download_caption(caption_id: str, format: str = "srt") -> str

# OAuth必須：動画管理
upload_video(title: str, description: str, tags: list = None, category_id: str = "22", privacy_status: str = "private", video_file = None) -> dict
update_video(video_id: str, title: str = None, description: str = None, tags: list = None, category_id: str = None) -> dict
delete_video(video_id: str) -> bool
get_my_videos(max_results: int = 50) -> list

# OAuth必須：動画評価
rate_video(video_id: str, rating: str) -> bool
get_video_rating(video_id: str) -> dict

# OAuth必須：サムネイル・字幕管理
set_video_thumbnail(video_id: str, image_file) -> dict
upload_caption(video_id: str, language: str, name: str, caption_file) -> dict
update_caption(caption_id: str, name: str = None, caption_file = None) -> dict
delete_caption(caption_id: str) -> bool

# 報告機能
report_video_abuse(video_id: str, reason_id: str, comments: str = "") -> bool
```

**使用例:**
```python
# 字幕取得
captions = yt.get_video_captions("dQw4w9WgXcQ")

# OAuth必須：動画アップロード
with open("video.mp4", "rb") as f:
    result = yt.upload_video("タイトル", "説明", ["tag1"], video_file=f)
```

---

#### ページネーション（PaginationMixin）

**メソッド一覧:**
```python
# 全件取得ヘルパー
paginate_all_results(paginated_func, *args, max_total_results: int = None, **kwargs) -> list
```

**使用例:**
```python
# 大量データの全件取得
all_results = yt.paginate_all_results(
    yt.search_videos_paginated,
    "Python",
    max_total_results=1000,
    order="date"
)
```

---

#### ヘルパー機能（HelperMixin）

**メソッド一覧:**
```python
# URL解析
extract_video_id_from_url(youtube_url: str) -> str
extract_playlist_id_from_url(youtube_url: str) -> str

# データフォーマット
format_view_count(view_count: int) -> str
format_subscriber_count(subscriber_count: int) -> str

# 一括取得
bulk_get_video_info(video_ids: list) -> list
bulk_get_channel_info(channel_ids: list) -> list

# 統計・分析
get_basic_info(resource_id: str, resource_type: str = "auto") -> dict
get_stats_summary(resource_id: str, resource_type: str = "auto") -> dict
search_and_get_details(query: str, max_results: int = 10, include_stats: bool = True) -> list
quick_search(query: str, count: int = 10, content_type: str = "video") -> list

# OAuth管理
setup_oauth_interactive(client_secrets_file: str, scopes: list = None, token_file: str = None) -> bool
get_oauth_authorization_url(client_secrets_file: str, scopes: list = None, state: str = None) -> tuple
complete_oauth_flow(flow, authorization_code: str, token_file: str = None) -> bool
get_oauth_info() -> dict
check_oauth_scopes(required_scopes: list) -> dict
refresh_oauth_token(token_file: str = None) -> bool
revoke_oauth_token(token_file: str = None) -> bool
create_oauth_config_template(output_file: str = 'oauth_config.json') -> str

# その他ユーティリティ
check_quota_usage() -> bool
```

**使用例:**
```python
# URL解析
video_id = yt.extract_video_id_from_url("https://youtube.com/watch?v=dQw4w9WgXcQ")

# 数値フォーマット
formatted_views = yt.format_view_count(1234567)  # "123.5万回"

# 一括取得
videos = yt.bulk_get_video_info(["dQw4w9WgXcQ", "jNQXAC9IVRw"])
```

---

### 📋 パッケージレベル関数

**メソッド一覧:**
```python
# 初期化ヘルパー
create_client(api_key: str = None, oauth_config: dict = None, auto_setup: bool = True) -> YouTubeAPI

# クイック検索
quick_search(query: str, max_results: int = 10, api_key: str = None) -> list

# URL解析
extract_video_id(url: str) -> str
extract_channel_id(url: str) -> str
extract_playlist_id(url: str) -> str

# 設定・情報
setup_logging(level: str = "WARNING", format: str = None, file: str = None) -> None
get_version() -> str
info() -> None
get_config() -> ConfigManager
```

**使用例:**
```python
# 初期化
yt = youtube_py3.create_client()

# クイック検索
videos = youtube_py3.quick_search("Python", max_results=5)

# URL解析
video_id = youtube_py3.extract_video_id("https://youtube.com/watch?v=dQw4w9WgXcQ")

# ライブラリ情報
youtube_py3.info()
```

---

### 📋 メソッドの分類

#### 🔓 APIキーのみで使用可能（67メソッド）

**情報取得系（47メソッド）**

*基本情報取得 (InfoRetrievalMixin):*
- `get_channel_info(channel_id)` - チャンネル詳細情報
- `get_channel_statistics_only(channel_id)` - チャンネル統計のみ
- `get_channel_from_username(username)` - ユーザー名からチャンネル取得
- `get_video_info(video_id)` - 動画詳細情報
- `get_video_statistics_only(video_id)` - 動画統計のみ
- `get_video_duration_seconds(video_id)` - 動画時間（秒）
- `get_playlist_info(playlist_id)` - プレイリスト詳細情報
- `get_video_categories(region_code)` - 動画カテゴリ一覧
- `get_supported_languages()` - サポート言語一覧
- `get_supported_regions()` - サポート地域一覧

*検索機能 (SearchMixin):*
- `search_videos(query, max_results, order)` - 動画検索
- `search_channels(query, max_results)` - チャンネル検索
- `search_playlists(query, max_results)` - プレイリスト検索
- `search_videos_paginated(...)` - 動画検索（ページネーション）
- `search_playlists_paginated(...)` - プレイリスト検索（ページネーション）
- `get_channel_videos(channel_id, max_results, order)` - チャンネル動画取得
- `get_channel_videos_paginated(...)` - チャンネル動画（ページネーション）
- `get_trending_videos(region_code, category_id, max_results)` - トレンド動画
- `get_channel_upload_playlist(channel_id)` - アップロードプレイリストID
- `get_latest_videos_from_channel(channel_id, max_results)` - 最新動画取得

*プレイリスト動画取得 (PlaylistMixin):*
- `get_playlist_videos(playlist_id, max_results)` - プレイリスト動画
- `get_playlist_videos_paginated(...)` - プレイリスト動画（ページネーション）

*コメント取得 (CommentsMixin):*
- `get_comments(video_id, max_results, order)` - 動画コメント取得
- `get_comments_paginated(...)` - コメント取得（ページネーション）
- `get_comment_details(comment_id)` - コメント詳細

*動画字幕情報 (VideoMixin):*
- `get_video_captions(video_id)` - 字幕リスト取得
- `download_caption(caption_id, format)` - 字幕ダウンロード

*簡略化メソッド (YouTubeAPI独自):*
- `get_channel_playlists(channel_id, max_results)` - チャンネルプレイリスト一覧
- `search_all_videos(query, max_results, channel_id)` - 動画全件検索
- `get_all_channel_videos(channel_id, max_results)` - チャンネル全動画
- `get_all_playlist_videos(playlist_id, max_results)` - プレイリスト全動画
- `get_all_comments(video_id, max_results)` - 動画全コメント

**ユーティリティ系（20メソッド）**

*URL解析 (HelperMixin):*
- `extract_video_id_from_url(youtube_url)` - 動画ID抽出
- `extract_playlist_id_from_url(youtube_url)` - プレイリストID抽出

*データフォーマット (HelperMixin):*
- `format_view_count(view_count)` - 再生回数フォーマット
- `format_subscriber_count(subscriber_count)` - 登録者数フォーマット

*一括取得 (HelperMixin):*
- `bulk_get_video_info(video_ids)` - 動画情報一括取得
- `bulk_get_channel_info(channel_ids)` - チャンネル情報一括取得

*統計・分析 (HelperMixin):*
- `get_basic_info(resource_id, resource_type)` - 基本情報取得
- `get_stats_summary(resource_id, resource_type)` - 統計サマリー
- `search_and_get_details(query, max_results, include_stats)` - 検索＋詳細取得
- `quick_search(query, count, content_type)` - クイック検索

*ページネーション (PaginationMixin):*
- `paginate_all_results(paginated_func, ...)` - 全件取得ヘルパー

*パッケージレベル関数:*
- `create_client(api_key, oauth_config, auto_setup)` - クライアント作成
- `quick_search(query, max_results, api_key)` - パッケージ検索
- `extract_video_id(url)` - パッケージ動画ID抽出
- `extract_channel_id(url)` - パッケージチャンネルID抽出
- `extract_playlist_id(url)` - パッケージプレイリストID抽出
- `setup_logging(level, format, file)` - ログ設定
- `get_version()` - バージョン取得
- `info()` - ライブラリ情報表示
- `get_config()` - 設定管理取得

*その他ユーティリティ (HelperMixin):*
- `check_quota_usage()` - クォータ使用量確認

---

#### 🔐 OAuth認証が必要（35メソッド）

**チャンネル管理（12メソッド）**

*自分のチャンネル情報 (InfoRetrievalMixin):*
- `get_my_channel()` - 自分のチャンネル情報

*サブスクリプション管理 (ChannelMixin):*
- `get_my_subscriptions(max_results)` - 自分のサブスクリプション
- `subscribe_to_channel(channel_id)` - チャンネル登録
- `unsubscribe_from_channel(subscription_id)` - チャンネル登録解除

*チャンネル情報更新 (ChannelMixin):*
- `update_channel(channel_id, title, description, keywords)` - チャンネル情報更新
- `upload_channel_banner(image_file)` - チャンネルバナーアップロード

*チャンネルセクション管理 (ChannelMixin):*
- `create_channel_section(channel_id, section_type, title, position)` - セクション作成
- `update_channel_section(section_id, title, position)` - セクション更新
- `delete_channel_section(section_id)` - セクション削除

*透かし管理 (ChannelMixin):*
- `set_watermark(channel_id, image_file, timing_type, offset_ms)` - 透かし設定
- `unset_watermark(channel_id)` - 透かし削除

*メンバーシップ (ChannelMixin):*
- `get_channel_members(max_results)` - チャンネルメンバー取得
- `get_membership_levels()` - メンバーシップレベル取得

**プレイリスト管理（8メソッド）**

*プレイリスト CRUD (PlaylistMixin):*
- `create_playlist(title, description, privacy_status)` - プレイリスト作成
- `update_playlist(playlist_id, title, description, privacy_status)` - プレイリスト更新
- `delete_playlist(playlist_id)` - プレイリスト削除
- `get_my_playlists(max_results)` - 自分のプレイリスト取得

*プレイリストアイテム管理 (PlaylistMixin):*
- `add_video_to_playlist(playlist_id, video_id, position)` - 動画追加
- `remove_video_from_playlist(playlist_item_id)` - 動画削除
- `update_playlist_item_position(playlist_item_id, new_position)` - 順序変更

*プレイリスト画像管理 (PlaylistMixin):*
- `get_playlist_images(playlist_id)` - プレイリスト画像取得
- `upload_playlist_image(playlist_id, image_file)` - プレイリスト画像アップロード

**動画管理（10メソッド）**

*動画 CRUD (VideoMixin):*
- `upload_video(title, description, tags, category_id, privacy_status, video_file)` - 動画アップロード
- `update_video(video_id, title, description, tags, category_id)` - 動画情報更新
- `delete_video(video_id)` - 動画削除
- `get_my_videos(max_results)` - 自分の動画取得

*動画評価 (VideoMixin):*
- `rate_video(video_id, rating)` - 動画評価（高評価/低評価）
- `get_video_rating(video_id)` - 動画評価取得

*サムネイル管理 (VideoMixin):*
- `set_video_thumbnail(video_id, image_file)` - サムネイル設定

*字幕管理 (VideoMixin):*
- `upload_caption(video_id, language, name, caption_file)` - 字幕アップロード
- `update_caption(caption_id, name, caption_file)` - 字幕更新
- `delete_caption(caption_id)` - 字幕削除

**コメント管理（5メソッド）**

*コメント投稿・編集 (CommentsMixin):*
- `post_comment_thread(video_id, text, channel_id)` - コメントスレッド投稿
- `post_comment_reply(parent_comment_id, text)` - コメント返信
- `update_comment(comment_id, text)` - コメント編集
- `delete_comment(comment_id)` - コメント削除

*コメントモデレーション (CommentsMixin):*
- `mark_comment_as_spam(comment_id)` - スパム報告
- `set_comment_moderation_status(comment_id, moderation_status)` - モデレーション状態設定

**OAuth管理・設定（7メソッド）**

*OAuth設定 (HelperMixin):*
- `setup_oauth_interactive(client_secrets_file, scopes, token_file)` - 対話的OAuth設定
- `get_oauth_authorization_url(client_secrets_file, scopes, state)` - 認証URL取得
- `complete_oauth_flow(flow, authorization_code, token_file)` - OAuth フロー完了
- `get_oauth_info()` - OAuth情報取得
- `check_oauth_scopes(required_scopes)` - スコープ確認
- `refresh_oauth_token(token_file)` - トークン更新
- `revoke_oauth_token(token_file)` - トークン取り消し
- `create_oauth_config_template(output_file)` - OAuth設定テンプレート作成

**その他（3メソッド）**

*報告機能 (VideoMixin):*
- `report_video_abuse(video_id, reason_id, comments)` - 動画通報

---

#### 📊 詳細メソッド統計

**総メソッド数: 102個**

**機能別内訳:**
- **情報取得**: 47個（46%）
  - チャンネル情報: 4個
  - 動画情報: 4個
  - プレイリスト情報: 3個
  - 検索機能: 10個
  - コメント取得: 3個
  - 字幕情報: 2個
  - システム情報: 3個
  - 簡略化メソッド: 5個
  - その他取得: 13個

- **OAuth必須操作**: 35個（34%）
  - チャンネル管理: 12個
  - プレイリスト管理: 8個
  - 動画管理: 10個
  - コメント管理: 5個

- **ユーティリティ**: 20個（20%）
  - URL解析: 5個
  - データフォーマット: 2個
  - 一括処理: 2個
  - 分析機能: 4個
  - ページネーション: 1個
  - パッケージ関数: 6個

**認証要件別:**
- 🔓 **APIキーのみ**: 67個（66%）
- 🔐 **OAuth必須**: 35個（34%）

**アクセスレベル別:**
- **読み取り専用**: 70個（69%）
- **書き込み/変更**: 32個（31%）

**使用頻度予想:**
- **高頻度**: 25個（基本情報取得、検索、簡略化メソッド）
- **中頻度**: 35個（詳細情報取得、ページネーション）
- **低頻度**: 42個（OAuth操作、高度な機能）

---

## エラーハンドリング

### YouTubeAPIError

```python
class YouTubeAPIError(Exception)
```

YouTube API関連のエラー例外クラス。

**判定メソッド:**
- `is_quota_exceeded()`: クォータ超過エラーかどうか
- `is_api_key_invalid()`: APIキー無効エラーかどうか
- `is_not_found()`: リソースが見つからないエラーかどうか
- `is_forbidden()`: アクセス権限エラーかどうか
- `get_suggested_action()`: エラーに対する推奨アクション

**使用例:**
```python
try:
    video = yt.get_video_info("invalid_video_id")
except YouTubeAPIError as e:
    print(f"エラーが発生: {e}")
    
    if e.is_quota_exceeded():
        print("❌ APIクォータが上限に達しました")
        print("💡 対処法:", e.get_suggested_action())
        
    elif e.is_api_key_invalid():
        print("❌ APIキーが無効です")
        print("💡 対処法:", e.get_suggested_action())
        
    elif e.is_not_found():
        print("❌ 指定されたリソースが見つかりません")
        
    elif e.is_forbidden():
        print("❌ アクセス権限がありません")
        print("💡 OAuth認証が必要な可能性があります")
```

---

## 実用的な使用例

### 例1: チャンネル分析

```python
def analyze_channel(channel_id):
    """チャンネルの基本分析を行う"""
    try:
        # チャンネル基本情報
        channel = yt.get_channel_info(channel_id)
        channel_name = channel['snippet']['title']
        subscriber_count = int(channel['statistics']['subscriberCount'])
        
        print(f"📺 チャンネル分析: {channel_name}")
        print(f"👥 登録者数: {subscriber_count:,}人")
        
        # 最新動画の取得
        videos = yt.get_all_channel_videos(channel_id, max_results=20)
        print(f"🎬 最新動画数: {len(videos)}本")
        
        # 動画タイトル一覧
        print("\n🆕 最新動画:")
        for i, video in enumerate(videos[:5], 1):
            title = video['snippet']['title']
            published = video['snippet']['publishedAt'][:10]
            print(f"  {i}. {title} ({published})")
            
        return {
            'channel_name': channel_name,
            'subscriber_count': subscriber_count,
            'recent_videos': videos
        }
        
    except YouTubeAPIError as e:
        print(f"❌ エラー: {e}")
        return None

# 使用例
result = analyze_channel("UC_x5XG1OV2P6uZZ5FSM9Ttw")
```

### 例2: 検索とフィルタリング

```python
def search_and_filter(query, min_views=10000):
    """検索結果を再生回数でフィルタリング"""
    try:
        # 動画検索
        videos = yt.search_all_videos(query, max_results=100)
        
        # 動画の詳細情報を取得してフィルタリング
        filtered_videos = []
        
        for video in videos:
            video_id = video['id']['videoId']
            video_details = yt.get_video_info(video_id)
            
            view_count = int(video_details['statistics'].get('viewCount', 0))
            
            if view_count >= min_views:
                filtered_videos.append({
                    'title': video_details['snippet']['title'],
                    'channel': video_details['snippet']['channelTitle'],
                    'views': view_count,
                    'url': f"https://youtube.com/watch?v={video_id}"
                })
        
        # 再生回数順でソート
        filtered_videos.sort(key=lambda x: x['views'], reverse=True)
        
        print(f"🔍 検索キーワード: {query}")
        print(f"📊 {min_views:,}回以上再生の動画: {len(filtered_videos)}本")
        
        for i, video in enumerate(filtered_videos[:5], 1):
            print(f"\n{i}. {video['title']}")
            print(f"   📺 {video['channel']}")
            print(f"   👀 {video['views']:,}回再生")
            print(f"   🔗 {video['url']}")
            
    except YouTubeAPIError as e:
        print(f"❌ エラー: {e}")

# 使用例
search_and_filter("Python プログラミング", min_views=50000)
```

### 例3: プレイリスト分析

```python
def analyze_playlist(playlist_id):
    """プレイリストの詳細分析"""
    try:
        # プレイリスト基本情報
        playlist = yt.get_playlist_info(playlist_id)
        playlist_title = playlist['snippet']['title']
        
        print(f"📋 プレイリスト分析: {playlist_title}")
        
        # プレイリストの全動画取得
        videos = yt.get_all_playlist_videos(playlist_id)
        print(f"📹 動画数: {len(videos)}本")
        
        # 各動画の詳細情報を取得
        total_views = 0
        channels = {}
        
        for video in videos:
            video_id = video['snippet']['resourceId']['videoId']
            try:
                video_details = yt.get_video_info(video_id)
                views = int(video_details['statistics'].get('viewCount', 0))
                channel = video_details['snippet']['channelTitle']
                
                total_views += views
                channels[channel] = channels.get(channel, 0) + 1
                
            except YouTubeAPIError:
                continue  # 削除された動画などはスキップ
        
        print(f"👀 総再生回数: {total_views:,}回")
        print(f"📊 平均再生回数: {total_views // len(videos):,}回")
        
        # チャンネル別動画数
        print("\n📺 チャンネル別動画数:")
        for channel, count in sorted(channels.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {channel}: {count}本")
            
    except YouTubeAPIError as e:
        print(f"❌ エラー: {e}")

# 使用例
analyze_playlist("PLxyz123")
```

---

## OAuth認証

OAuth認証により、以下の高度な機能が利用可能になります：

- 動画アップロード
- プレイリスト作成・編集
- チャンネル管理
- コメント投稿

### OAuth設定例

```python
# OAuth設定
oauth_config = {
    'client_secrets_file': 'client_secrets.json',  # Google Cloud Consoleからダウンロード
    'scopes': ['https://www.googleapis.com/auth/youtube'],  # 必要な権限
    'token_file': 'youtube_token.pickle',  # トークン保存ファイル
    'port': 8080,  # ローカルサーバーポート
    'auto_open_browser': True  # ブラウザ自動起動
}

# OAuth対応クライアント作成
yt = youtube_py3.create_client(
    api_key="YOUR_API_KEY",
    oauth_config=oauth_config
)

# OAuth必須機能の使用例
try:
    # 自分のチャンネル情報取得
    my_channel = yt.get_my_channel()
    print(f"📺 マイチャンネル: {my_channel['snippet']['title']}")
    
    # プレイリスト作成
    playlist = yt.create_playlist(
        title="自動作成プレイリスト",
        description="YouTube.py3で作成されました",
        privacy_status="private"
    )
    print(f"✅ プレイリスト作成完了: {playlist['snippet']['title']}")
    
except YouTubeAPIError as e:
    if "OAuth" in str(e):
        print("❌ OAuth認証が必要です")
    else:
        print(f"エラー: {e}")
```

---

## 設定とユーティリティ

### バージョン情報

```python
import youtube_py3

print(f"バージョン: {youtube_py3.__version__}")
print(f"作者: {youtube_py3.__author__}")
print(f"ライセンス: {youtube_py3.__license__}")

# ライブラリ情報表示
youtube_py3.info()
```

### ログ設定

```python
# ログレベル設定
youtube_py3.setup_logging(level="INFO")

# ファイル出力
youtube_py3.setup_logging(level="DEBUG", file="youtube_py3.log")
```

### 設定管理

```python
# グローバル設定取得
config = youtube_py3.get_config()

# 設定の確認
print(f"設定値: {config.get_all_settings()}")
```

---

## 完全な機能一覧

### ✅ 実装済みの主要機能

**基本機能**
- ✅ YouTubeAPI（メインクラス）
- ✅ create_client()（簡単初期化）
- ✅ YouTubeAPIError（エラーハンドリング）

**簡略化メソッド**
- ✅ get_channel_playlists()
- ✅ search_all_videos()
- ✅ get_all_channel_videos()
- ✅ get_all_playlist_videos()
- ✅ get_all_comments()

**Mixin機能（各Mixinから継承）**
- ✅ YouTubeAPIBase（基本API・OAuth）
- ✅ InfoRetrievalMixin（情報取得）
- ✅ SearchMixin（検索）
- ✅ PaginationMixin（ページネーション）
- ✅ CommentsMixin（コメント管理）
- ✅ PlaylistMixin（プレイリスト管理）
- ✅ ChannelMixin（チャンネル管理）
- ✅ VideoMixin（動画管理）
- ✅ HelperMixin（ヘルパー）

**ヘルパー関数**
- ✅ quick_search()
- ✅ extract_video_id()
- ✅ extract_channel_id()
- ✅ extract_playlist_id()

**管理・ユーティリティ**
- ✅ OAuthManager（OAuth管理）
- ✅ ConfigManager（設定管理）
- ✅ YouTubeUtils（ユーティリティ）

---

## サポートとリソース

### 公式リンク

- **GitHub**: https://github.com/chihalu/youtube-py3
- **PyPI**: https://pypi.org/project/youtube-py3/
- **ドキュメント**: [README](README.md) | [インストールガイド](installation.md) | [トラブルシューティング](troubleshooting.md)

### サポート

問題や質問がある場合は、GitHubのIssuesページをご利用ください。

### ライセンス

MIT License - 詳細は [LICENSE](../LICENSE) ファイルをご覧ください。

---

## ヘルパー関数

### URL解析系

#### extract_video_id()

**関数シグネチャ:**
```python
def extract_video_id(url) -> str
```

**機能:** YouTube URLから動画IDを抽出します。

**使用例:**
```python
import youtube_py3

# 様々なYouTube URL形式に対応
urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
]

for url in urls:
    video_id = youtube_py3.extract_video_id(url)
    print(f"URL: {url}")
    print(f"動画ID: {video_id}\n")
```

---

#### extract_channel_id()

**関数シグネチャ:**
```python
def extract_channel_id(url) -> str
```

**機能:** YouTube URLからチャンネルIDを抽出します。

**使用例:**
```python
import youtube_py3

# チャンネルURL形式
urls = [
    "https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw",
    "https://www.youtube.com/@username",
    "https://www.youtube.com/c/channelname"
]

for url in urls:
    try:
        channel_id = youtube_py3.extract_channel_id(url)
        print(f"URL: {url}")
        print(f"チャンネルID: {channel_id}\n")
    except ValueError as e:
        print(f"❌ 解析できませんでした: {e}")
```

---

#### extract_playlist_id()

**関数シグネチャ:**
```python
def extract_playlist_id(url) -> str
```

**機能:** YouTube URLからプレイリストIDを抽出します。

**使用例:**
```python
import youtube_py3

# プレイリストURL形式
urls = [
    "https://www.youtube.com/playlist?list=PLxyz123",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLxyz123"
]

for url in urls:
    try:
        playlist_id = youtube_py3.extract_playlist_id(url)
        print(f"URL: {url}")
        print(f"プレイリストID: {playlist_id}\n")
    except ValueError as e:
        print(f"❌ プレイリストIDが見つかりませんでした: {e}")
```

---

### パッケージレベルヘルパー

#### create_client()

**関数シグネチャ:**
```python
def create_client(api_key=None, oauth_config=None, auto_setup=True) -> YouTubeAPI
```

**機能:** YouTubeAPIクライアントを簡単に作成するヘルパー関数。

**パラメータ:**
- `api_key` (str, optional): APIキー（環境変数から自動取得可能）
- `oauth_config` (dict, optional): OAuth設定
- `auto_setup` (bool): 自動セットアップを行うか

**使用例:**
```python
import youtube_py3

# 1. 環境変数から自動取得
yt = youtube_py3.create_client()

# 2. APIキー指定
yt = youtube_py3.create_client(api_key="YOUR_API_KEY")

# 3. OAuth設定付き
oauth_config = {
    'client_secrets_file': 'client_secrets.json',
    'scopes': ['https://www.googleapis.com/auth/youtube']
}
yt = youtube_py3.create_client(api_key="YOUR_API_KEY", oauth_config=oauth_config)

# 4. 自動セットアップなし（手動設定）
yt = youtube_py3.create_client(auto_setup=False)
```

---

#### quick_search()

**関数シグネチャ:**
```python
def quick_search(query, max_results=10, api_key=None) -> list
```

**機能:** 動画を素早く検索するワンライナー関数。

**パラメータ:**
- `query` (str): 検索クエリ
- `max_results` (int): 取得する結果数（デフォルト: 10）
- `api_key` (str, optional): APIキー

**戻り値:**
- `list`: 検索結果のリスト

**使用例:**
```python
import youtube_py3

# 基本的な検索
videos = youtube_py3.quick_search("Python tutorial", max_results=5)
for video in videos:
    print(f"🎬 {video['snippet']['title']}")
    print(f"📺 {video['snippet']['channelTitle']}")
    print(f"🔗 https://youtube.com/watch?v={video['id']['videoId']}\n")

# APIキー指定で検索
videos = youtube_py3.quick_search(
    "機械学習", 
    max_results=3, 
    api_key="YOUR_API_KEY"
)
```