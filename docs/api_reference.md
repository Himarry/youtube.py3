# APIリファレンス

YouTube.py2の全メソッドの詳細な説明です。全88個のメソッドを機能別に分類して説明します。

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
- [メンバーシップ管理](#メンバーシップ管理)
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
from youtube_py2 import YouTubeAPI
import os

api_key = os.getenv('YOUTUBE_API_KEY')
yt = YouTubeAPI(api_key)
```

### YouTubeAPIError

```python
class YouTubeAPIError(Exception)
```

YouTube API関連のエラー例外クラス。

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

**使用例:**
```python
stats = yt.get_channel_statistics_only("UC_x5XG1OV2P6uZZ5FSM9Ttw")
print(f"登録者数: {stats['subscriberCount']}")
```

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
stats = yt.get_video_statistics_only("dQw4w9WgXcQ")
print(f"再生回数: {stats['viewCount']}")
```

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

### create_playlist()

```python
def create_playlist(title: str, description: str = "", privacy_status: str = "private") -> dict
```

プレイリストを作成します。

**パラメータ:**
- `title` (str): プレイリストタイトル
- `description` (str): プレイリスト説明（デフォルト: ""）
- `privacy_status` (str): プライバシー設定（デフォルト: 'private'）
  - `'private'`: 非公開
  - `'public'`: 公開
  - `'unlisted'`: 限定公開

**戻り値:**
- `dict`: 作成されたプレイリスト情報

**使用例:**
```python
playlist = yt.create_playlist(
    title="お気に入りの動画",
    description="面白い動画のコレクション",
    privacy_status="public"
)
print(f"プレイリストID: {playlist['id']}")
```

### update_playlist()

```python
def update_playlist(playlist_id: str, title: str = None, description: str = None, privacy_status: str = None) -> dict
```

プレイリストを更新します。

**パラメータ:**
- `playlist_id` (str): プレイリストID
- `title` (str): 新しいタイトル（オプション）
- `description` (str): 新しい説明（オプション）
- `privacy_status` (str): 新しいプライバシー設定（オプション）

**戻り値:**
- `dict`: 更新結果

**使用例:**
```python
result = yt.update_playlist(
    "PLxyz123",
    title="更新されたタイトル",
    description="新しい説明"
)
```

### delete_playlist()

```python
def delete_playlist(playlist_id: str) -> bool
```

プレイリストを削除します。

**パラメータ:**
- `playlist_id` (str): プレイリストID

**戻り値:**
- `bool`: 削除成功フラグ

**使用例:**
```python
if yt.delete_playlist("PLxyz123"):
    print("プレイリストを削除しました")
```

### add_video_to_playlist()

```python
def add_video_to_playlist(playlist_id: str, video_id: str, position: int = None) -> dict
```

プレイリストに動画を追加します。

**パラメータ:**
- `playlist_id` (str): プレイリストID
- `video_id` (str): 動画ID
- `position` (int): 挿入位置（オプション）

**戻り値:**
- `dict`: 追加結果

**使用例:**
```python
result = yt.add_video_to_playlist("PLxyz123", "dQw4w9WgXcQ", position=0)
print("動画をプレイリストに追加しました")
```

### remove_video_from_playlist()

```python
def remove_video_from_playlist(playlist_item_id: str) -> bool
```

プレイリストから動画を削除します。

**パラメータ:**
- `playlist_item_id` (str): プレイリストアイテムID

**戻り値:**
- `bool`: 削除成功フラグ

**使用例:**
```python
if yt.remove_video_from_playlist("PLIxyz123"):
    print("動画をプレイリストから削除しました")
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

### get_comment_details()

```python
def get_comment_details(comment_id: str) -> dict
```

コメント詳細を取得します。

**パラメータ:**
- `comment_id` (str): コメントID

**戻り値:**
- `dict`: コメント詳細情報

**使用例:**
```python
comment = yt.get_comment_details("UgxKREWxxx")
print(f"コメント: {comment['snippet']['textDisplay']}")
```

### post_comment_thread()

```python
def post_comment_thread(video_id: str, text: str, channel_id: str = None) -> dict
```

新しいコメントスレッドを投稿します。

**パラメータ:**
- `video_id` (str): 動画ID（動画へのコメントの場合）
- `text` (str): コメントテキスト
- `channel_id` (str): チャンネルID（チャンネルへのコメントの場合）

**戻り値:**
- `dict`: 投稿結果

**使用例:**
```python
result = yt.post_comment_thread("dQw4w9WgXcQ", "素晴らしい動画です！")
print("コメントを投稿しました")
```

### post_comment_reply()

```python
def post_comment_reply(parent_comment_id: str, text: str) -> dict
```

コメントに返信します。

**パラメータ:**
- `parent_comment_id` (str): 親コメントID
- `text` (str): 返信テキスト

**戻り値:**
- `dict`: 投稿結果

**使用例:**
```python
result = yt.post_comment_reply("UgxKREWxxx", "同感です！")
print("返信を投稿しました")
```

### update_comment()

```python
def update_comment(comment_id: str, text: str) -> dict
```

コメントを更新します。

**パラメータ:**
- `comment_id` (str): コメントID
- `text` (str): 新しいテキスト

**戻り値:**
- `dict`: 更新結果

**使用例:**
```python
result = yt.update_comment("UgxKREWxxx", "更新されたコメントです")
print("コメントを更新しました")
```

### delete_comment()

```python
def delete_comment(comment_id: str) -> bool
```

コメントを削除します。

**パラメータ:**
- `comment_id` (str): コメントID

**戻り値:**
- `bool`: 削除成功フラグ

**使用例:**
```python
if yt.delete_comment("UgxKREWxxx"):
    print("コメントを削除しました")
```

### mark_comment_as_spam()

```python
def mark_comment_as_spam(comment_id: str) -> bool
```

コメントをスパムとしてマークします。

**パラメータ:**
- `comment_id` (str): コメントID

**戻り値:**
- `bool`: 成功フラグ

**使用例:**
```python
if yt.mark_comment_as_spam("UgxKREWxxx"):
    print("コメントをスパムとしてマークしました")
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

### update_channel()

```python
def update_channel(channel_id: str, title: str = None, description: str = None, keywords: str = None) -> dict
```

チャンネル情報を更新します。

**パラメータ:**
- `channel_id` (str): チャンネルID
- `title` (str): 新しいタイトル（オプション）
- `description` (str): 新しい説明（オプション）
- `keywords` (str): 新しいキーワード（オプション）

**戻り値:**
- `dict`: 更新結果

**使用例:**
```python
result = yt.update_channel(
    "UC_x5XG1OV2P6uZZ5FSM9Ttw",
    title="新しいチャンネル名",
    description="チャンネルの新しい説明"
)
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

### upload_video()

```python
def upload_video(title: str, description: str, tags: list = None, category_id: str = "22", privacy_status: str = "private", video_file = None) -> dict
```

動画をアップロードします。

**パラメータ:**
- `title` (str): 動画タイトル
- `description` (str): 動画説明
- `tags` (list): タグのリスト
- `category_id` (str): カテゴリID（デフォルト: "22"）
- `privacy_status` (str): プライバシー設定（デフォルト: 'private'）
- `video_file`: 動画ファイル

**戻り値:**
- `dict`: アップロード結果

**使用例:**
```python
with open('video.mp4', 'rb') as video_file:
    result = yt.upload_video(
        title="テスト動画",
        description="テスト用の動画です",
        tags=["テスト", "動画"],
        privacy_status="unlisted",
        video_file=video_file
    )
print(f"動画ID: {result['id']}")
```

### update_video()

```python
def update_video(video_id: str, title: str = None, description: str = None, tags: list = None, category_id: str = None) -> dict
```

動画情報を更新します。

**パラメータ:**
- `video_id` (str): 動画ID
- `title` (str): 新しいタイトル（オプション）
- `description` (str): 新しい説明（オプション）
- `tags` (list): 新しいタグ（オプション）
- `category_id` (str): 新しいカテゴリID（オプション）

**戻り値:**
- `dict`: 更新結果

**使用例:**
```python
result = yt.update_video(
    "dQw4w9WgXcQ",
    title="更新されたタイトル",
    description="新しい説明"
)
```

### delete_video()

```python
def delete_video(video_id: str) -> bool
```

動画を削除します。

**パラメータ:**
- `video_id` (str): 動画ID

**戻り値:**
- `bool`: 削除成功フラグ

**使用例:**
```python
if yt.delete_video("dQw4w9WgXcQ"):
    print("動画を削除しました")
```

### rate_video()

```python
def rate_video(video_id: str, rating: str) -> bool
```

動画を評価します。

**パラメータ:**
- `video_id` (str): 動画ID
- `rating` (str): 評価（'like', 'dislike', 'none'）

**戻り値:**
- `bool`: 評価成功フラグ

**使用例:**
```python
if yt.rate_video("dQw4w9WgXcQ", "like"):
    print("動画にいいねしました")
```

### set_video_thumbnail()

```python
def set_video_thumbnail(video_id: str, image_file) -> dict
```

動画のサムネイルを設定します。

**パラメータ:**
- `video_id` (str): 動画ID
- `image_file`: サムネイル画像ファイル

**戻り値:**
- `dict`: 設定結果

**使用例:**
```python
with open('thumbnail.jpg', 'rb') as thumb_file:
    result = yt.set_video_thumbnail("dQw4w9WgXcQ", thumb_file)
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

**使用例:**
```python
captions = yt.get_video_captions("dQw4w9WgXcQ")
for caption in captions:
    print(f"言語: {caption['snippet']['language']}")
```

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

**使用例:**
```python
caption_text = yt.download_caption("caption_id", format="srt")
with open("subtitle.srt", "w", encoding="utf-8") as f:
    f.write(caption_text)
```

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

**使用例:**
```python
with open("subtitle.srt", "rb") as caption_file:
    result = yt.upload_caption("dQw4w9WgXcQ", "ja", "日本語字幕", caption_file)
```

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

**使用例:**
```python
subscriptions = yt.get_subscriptions(mine=True)
for sub in subscriptions:
    print(f"チャンネル: {sub['snippet']['title']}")
```

### subscribe_to_channel()

```python
def subscribe_to_channel(channel_id: str) -> dict
```

チャンネルをサブスクライブします。

**パラメータ:**
- `channel_id` (str): サブスクライブするチャンネルID

**戻り値:**
- `dict`: サブスクライブ結果

**使用例:**
```python
result = yt.subscribe_to_channel("UC_x5XG1OV2P6uZZ5FSM9Ttw")
print("チャンネルをサブスクライブしました")
```

### unsubscribe_from_channel()

```python
def unsubscribe_from_channel(subscription_id: str) -> bool
```

チャンネルのサブスクライブを解除します。

**パラメータ:**
- `subscription_id` (str): サブスクリプションID

**戻り値:**
- `bool`: 解除成功フラグ

**使用例:**
```python
if yt.unsubscribe_from_channel("subscription_id"):
    print("サブスクライブを解除しました")
```

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
except Exception as e:
    print(f"予期しないエラー: {e}")
```

### よくあるエラーとその対処法

#### 1. APIキー関連
```python
try:
    yt = YouTubeAPI("")  # 空のAPIキー
except YouTubeAPIError as e:
    # "APIキーが必要です。Google Cloud Consoleで個別に取得してください。"
    print(f"エラー: {e}")
```

#### 2. クォータ制限
```python
try:
    videos = yt.search_videos("Python", max_results=1000)
except YouTubeAPIError as e:
    if "quota" in str(e).lower():
        print("API使用量制限に達しました。時間をおいて再試行してください。")
    else:
        print(f"エラー: {e}")
```

#### 3. リソースが見つからない
```python
try:
    video = yt.get_video_info("nonexistent_video_id")
except YouTubeAPIError as e:
    if "見つかりません" in str(e):
        print("指定された動画は存在しません。")
    else:
        print(f"エラー: {e}")
```

---

**最終更新**: 2024年12月
**関連ドキュメント**: [README](README.md) | [使用例集](examples/) | [トラブルシューティング](troubleshooting.md)
