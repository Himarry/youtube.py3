# APIリファレンス

YouTube.py3の全メソッドの詳細な説明です。実装済みのメソッドを機能別に分類して説明します。

## 📚 目次

- [基本クラス](#基本クラス)
- [基本情報取得](#基本情報取得)
- [検索機能](#検索機能)
- [リスト取得](#リスト取得)
- [プレイリスト管理](#プレイリスト管理)
- [プレイリスト画像管理](#プレイリスト画像管理)
- [コメント管理](#コメント管理)
- [チャンネル管理](#チャンネル管理)
- [動画管理](#動画管理)
- [字幕管理](#字幕管理)
- [サブスクリプション管理](#サブスクリプション管理)
- [メンバーシップ管理](#メンバーシップ管理)
- [透かし管理](#透かし管理)
- [システム情報](#システム情報)
- [ページネーション機能](#ページネーション機能)
- [簡略化メソッド](#簡略化メソッド)
- [エラーハンドリング](#エラーハンドリング)
- [使用パターン集](#使用パターン集)
- [便利なヘルパーメソッド](#便利なヘルパーメソッド)

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
        
    elif e.is_api_key_invalid():
        print("❌ APIキーが無効です")
        print("💡 推奨アクション:", e.get_suggested_action())
        
    elif e.is_not_found():
        print("❌ 指定されたリソースが見つかりません")
        print("💡 推奨アクション:", e.get_suggested_action())
        
    elif e.is_forbidden():
        print("❌ アクセス権限がありません")
        print("💡 推奨アクション:", e.get_suggested_action())
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
try:
    if yt.check_quota_usage():
        print("✅ APIキーは有効です")
    else:
        print("❌ APIキーに問題があります")
except YouTubeAPIError as e:
    print(f"APIエラー: {e}")
```

### get_channel_info()

```python
def get_channel_info(channel_id: str) -> dict
```

チャンネル情報を取得します。

**パラメータ:**
- `channel_id` (str): YouTubeチャンネルのID

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

**使用例:**
```python
try:
    channel = yt.get_channel_info("UC_x5XG1OV2P6uZZ5FSM9Ttw")
    print(f"📺 チャンネル名: {channel['snippet']['title']}")
    print(f"👥 登録者数: {int(channel['statistics']['subscriberCount']):,}")
    print(f"📹 動画数: {int(channel['statistics']['videoCount']):,}")
except YouTubeAPIError as e:
    if e.is_not_found():
        print("❌ 指定されたチャンネルが見つかりません")
    else:
        print(f"エラー: {e}")
```

### get_video_info()

```python
def get_video_info(video_id: str) -> dict
```

動画情報を取得します。

**パラメータ:**
- `video_id` (str): YouTube動画のID

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
        'categoryId': '10'
    },
    'statistics': {
        'viewCount': '1234567',
        'likeCount': '12345',
        'commentCount': '678'
    }
}
```

**使用例:**
```python
try:
    video = yt.get_video_info("dQw4w9WgXcQ")
    print(f"🎬 タイトル: {video['snippet']['title']}")
    print(f"📺 チャンネル: {video['snippet']['channelTitle']}")
    print(f"👀 再生回数: {int(video['statistics']['viewCount']):,}")
    print(f"👍 いいね数: {int(video['statistics'].get('likeCount', 0)):,}")
except YouTubeAPIError as e:
    if e.is_not_found():
        print("❌ 指定された動画が見つかりません")
    else:
        print(f"エラー: {e}")
```

### get_playlist_info()

```python
def get_playlist_info(playlist_id: str) -> dict
```

プレイリスト情報を取得します。

**パラメータ:**
- `playlist_id` (str): プレイリストID

**戻り値:**
- `dict`: プレイリスト情報

**使用例:**
```python
try:
    playlist = yt.get_playlist_info("PLxyz123")
    print(f"📝 プレイリスト: {playlist['snippet']['title']}")
    print(f"📅 作成日: {playlist['snippet']['publishedAt'][:10]}")
    print(f"📊 動画数: {playlist['contentDetails']['itemCount']}")
except YouTubeAPIError as e:
    print(f"エラー: {e}")
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
print(f"総再生回数: {stats['viewCount']}")
print(f"動画数: {stats['videoCount']}")
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
print(f"いいね数: {stats.get('likeCount', 0)}")
print(f"コメント数: {stats.get('commentCount', 0)}")
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
- `max_results` (int): 取得する最大結果数（1-50、デフォルト: 5）
- `order` (str): ソート順序（デフォルト: 'relevance'）
  - `'relevance'`: 関連度順（推奨）
  - `'date'`: 投稿日時順（新しい順）
  - `'rating'`: 評価順
  - `'viewCount'`: 再生回数順
  - `'title'`: タイトル順（アルファベット順）

**戻り値:**
- `list`: 検索結果のリスト

**使用例:**
```python
videos = yt.search_videos("Python プログラミング", max_results=10)
for i, video in enumerate(videos, 1):
    snippet = video['snippet']
    print(f"{i}. {snippet['title']}")
    print(f"   チャンネル: {snippet['channelTitle']}")
    print(f"   公開日: {snippet['publishedAt'][:10]}")
```

### search_channels()

```python
def search_channels(query: str, max_results: int = 5, order: str = "relevance") -> list
```

チャンネルを検索します。

**パラメータ:**
- `query` (str): 検索キーワード
- `max_results` (int): 取得する最大結果数
- `order` (str): ソート順序

**戻り値:**
- `list`: 検索結果のリスト

**使用例:**
```python
channels = yt.search_channels("プログラミング", max_results=10)
for channel in channels:
    snippet = channel['snippet']
    print(f"📺 {snippet['title']}")
    print(f"   説明: {snippet['description'][:100]}...")
```

### search_playlists()

```python
def search_playlists(query: str, max_results: int = 5, order: str = "relevance") -> list
```

プレイリストを検索します。

**パラメータ:**
- `query` (str): 検索キーワード
- `max_results` (int): 取得する最大結果数
- `order` (str): ソート順序

**戻り値:**
- `list`: 検索結果のリスト

**使用例:**
```python
playlists = yt.search_playlists("Python 講座", max_results=10)
for playlist in playlists:
    snippet = playlist['snippet']
    print(f"📝 {snippet['title']}")
    print(f"   チャンネル: {snippet['channelTitle']}")
```

---

## リスト取得

### get_playlist_videos()

```python
def get_playlist_videos(playlist_id: str, max_results: int = 50) -> list
```

プレイリストの動画一覧を取得します。

**パラメータ:**
- `playlist_id` (str): プレイリストID
- `max_results` (int): 取得する最大動画数（デフォルト: 50）

**戻り値:**
- `list`: 動画情報のリスト

**使用例:**
```python
videos = yt.get_playlist_videos("PLxyz123", max_results=100)
for i, video in enumerate(videos, 1):
    snippet = video['snippet']
    print(f"{i}. {snippet['title']}")
    print(f"   チャンネル: {snippet['channelTitle']}")
```

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
try:
    comments = yt.get_comments("dQw4w9WgXcQ", max_results=50)
    for comment in comments:
        text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
        author = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
        print(f"💬 {author}: {text[:100]}...")
except YouTubeAPIError as e:
    if e.is_forbidden():
        print("❌ この動画はコメントが無効化されています")
```

### get_channel_videos()

```python
def get_channel_videos(channel_id: str, max_results: int = 50, order: str = "date") -> list
```

チャンネルの動画を取得します。

**パラメータ:**
- `channel_id` (str): チャンネルID
- `max_results` (int): 取得する最大動画数
- `order` (str): ソート順序

**戻り値:**
- `list`: 動画のリスト

**使用例:**
```python
videos = yt.get_channel_videos("UC_x5XG1OV2P6uZZ5FSM9Ttw", max_results=20)
for video in videos:
    snippet = video['snippet']
    print(f"🎬 {snippet['title']}")
    print(f"   公開日: {snippet['publishedAt'][:10]}")
```

---

## プレイリスト管理

### create_playlist()

```python
def create_playlist(title: str, description: str = "", privacy_status: str = "private") -> dict
```

プレイリストを作成します。

**パラメータ:**
- `title` (str): プレイリストタイトル
- `description` (str): プレイリスト説明
- `privacy_status` (str): プライバシー設定（'private', 'public', 'unlisted'）

**戻り値:**
- `dict`: 作成されたプレイリスト情報

**使用例:**
```python
playlist = yt.create_playlist(
    title="Python学習動画",
    description="Python学習に役立つ動画集",
    privacy_status="public"
)
print(f"✅ プレイリスト作成: {playlist['snippet']['title']}")
print(f"🔗 ID: {playlist['id']}")
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

### delete_playlist()

```python
def delete_playlist(playlist_id: str) -> bool
```

プレイリストを削除します。

**パラメータ:**
- `playlist_id` (str): プレイリストID

**戻り値:**
- `bool`: 削除成功フラグ

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
result = yt.add_video_to_playlist("PLxyz123", "dQw4w9WgXcQ")
print(f"✅ 動画をプレイリストに追加しました")
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

### update_playlist_item_position()

```python
def update_playlist_item_position(playlist_item_id: str, new_position: int) -> dict
```

プレイリスト内動画の位置を更新します。

**パラメータ:**
- `playlist_item_id` (str): プレイリストアイテムID
- `new_position` (int): 新しい位置

**戻り値:**
- `dict`: 更新結果

**使用例:**
```python
result = yt.update_playlist_item_position("PLI_abc123", 0)
print("✅ 動画をプレイリストの先頭に移動しました")
```

---

## プレイリスト画像管理

### get_playlist_images()

```python
def get_playlist_images(playlist_id: str) -> list
```

プレイリスト画像を取得します。

**パラメータ:**
- `playlist_id` (str): プレイリストID

**戻り値:**
- `list`: プレイリスト画像のリスト

**使用例:**
```python
images = yt.get_playlist_images("PLxyz123")
for image in images:
    print(f"🖼️ 画像URL: {image['snippet']['url']}")
```

### upload_playlist_image()

```python
def upload_playlist_image(playlist_id: str, image_file) -> dict
```

プレイリスト画像をアップロードします。

**パラメータ:**
- `playlist_id` (str): プレイリストID
- `image_file`: 画像ファイル

**戻り値:**
- `dict`: アップロード結果

**使用例:**
```python
with open("playlist_thumbnail.jpg", "rb") as f:
    result = yt.upload_playlist_image("PLxyz123", f)
    print("✅ プレイリスト画像をアップロードしました")
```

---

## コメント管理

### get_comment_details()

```python
def get_comment_details(comment_id: str) -> dict
```

コメント詳細を取得します。

**パラメータ:**
- `comment_id` (str): コメントID

**戻り値:**
- `dict`: コメント詳細情報

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

### delete_comment()

```python
def delete_comment(comment_id: str) -> bool
```

コメントを削除します。

**パラメータ:**
- `comment_id` (str): コメントID

**戻り値:**
- `bool`: 削除成功フラグ

### mark_comment_as_spam()

```python
def mark_comment_as_spam(comment_id: str) -> bool
```

コメントをスパムとしてマークします。

**パラメータ:**
- `comment_id` (str): コメントID

**戻り値:**
- `bool`: 成功フラグ

### set_comment_moderation_status()

```python
def set_comment_moderation_status(comment_id: str, moderation_status: str) -> bool
```

コメントのモデレーション状態を設定します。

**パラメータ:**
- `comment_id` (str): コメントID
- `moderation_status` (str): モデレーション状態（'published', 'heldForReview', 'likelySpam', 'rejected'）

**戻り値:**
- `bool`: 成功フラグ

---

## チャンネル管理

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

### upload_channel_banner()

```python
def upload_channel_banner(image_file) -> dict
```

チャンネルバナーをアップロードします。

**パラメータ:**
- `image_file`: 画像ファイル

**戻り値:**
- `dict`: アップロード結果（URLを含む）

### create_channel_section()

```python
def create_channel_section(channel_id: str, section_type: str, title: str, position: int = 0) -> dict
```

チャンネルセクションを作成します。

**パラメータ:**
- `channel_id` (str): チャンネルID
- `section_type` (str): セクションタイプ
- `title` (str): セクションタイトル
- `position` (int): 表示位置

**戻り値:**
- `dict`: 作成結果

### update_channel_section()

```python
def update_channel_section(section_id: str, title: str = None, position: int = None) -> dict
```

チャンネルセクションを更新します。

### delete_channel_section()

```python
def delete_channel_section(section_id: str) -> bool
```

チャンネルセクションを削除します。

### set_watermark()

```python
def set_watermark(channel_id: str, image_file, timing_type: str = "offsetFromStart", offset_ms: int = 15000) -> dict
```

チャンネルに透かしを設定します。

**パラメータ:**
- `channel_id` (str): チャンネルID
- `image_file`: 透かし画像ファイル
- `timing_type` (str): タイミングタイプ（'offsetFromStart', 'offsetFromEnd'）
- `offset_ms` (int): オフセット（ミリ秒、デフォルト: 15000）

**戻り値:**
- `dict`: 設定結果

**使用例:**
```python
with open("watermark.png", "rb") as f:
    result = yt.set_watermark(
        "UC_x5XG1OV2P6uZZ5FSM9Ttw", 
        f, 
        timing_type="offsetFromStart", 
        offset_ms=10000
    )
    print("✅ 透かし設定完了")
```

### unset_watermark()

```python
def unset_watermark(channel_id: str) -> bool
```

チャンネルの透かしを削除します。

**パラメータ:**
- `channel_id` (str): チャンネルID

**戻り値:**
- `bool`: 削除成功フラグ

**使用例:**
```python
success = yt.unset_watermark("UC_x5XG1OV2P6uZZ5FSM9Ttw")
if success:
    print("✅ 透かし削除完了")
```

---

## 動画管理

### upload_video()

```python
def upload_video(title: str, description: str, tags: list = None, category_id: str = "22", privacy_status: str = "private", video_file = None) -> dict
```

動画をアップロードします。

**パラメータ:**
- `title` (str): 動画タイトル
- `description` (str): 動画説明
- `tags` (list): タグのリスト
- `category_id` (str): カテゴリID（デフォルト: "22" = People & Blogs）
- `privacy_status` (str): プライバシー設定（'private', 'public', 'unlisted'）
- `video_file`: 動画ファイル

**戻り値:**
- `dict`: アップロード結果

**使用例:**
```python
with open("my_video.mp4", "rb") as f:
    result = yt.upload_video(
        title="Python チュートリアル",
        description="初心者向けPython解説動画",
        tags=["Python", "プログラミング", "初心者"],
        privacy_status="public",
        video_file=f
    )
    print(f"✅ 動画アップロード完了: {result['id']}")
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

### delete_video()

```python
def delete_video(video_id: str) -> bool
```

動画を削除します。

**パラメータ:**
- `video_id` (str): 動画ID

**戻り値:**
- `bool`: 削除成功フラグ

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

### get_video_rating()

```python
def get_video_rating(video_id: str) -> dict
```

動画の評価を取得します。

**パラメータ:**
- `video_id` (str): 動画ID

**戻り値:**
- `dict`: 評価情報

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
with open("thumbnail.jpg", "rb") as f:
    result = yt.set_video_thumbnail("dQw4w9WgXcQ", f)
    print("✅ サムネイル設定完了")
```

### report_video_abuse()

```python
def report_video_abuse(video_id: str, reason_id: str, comments: str = "") -> bool
```

動画を報告します。

**パラメータ:**
- `video_id` (str): 動画ID
- `reason_id` (str): 報告理由ID
- `comments` (str): 追加コメント

**戻り値:**
- `bool`: 報告成功フラグ

---

## 透かし管理

### set_watermark()

```python
def set_watermark(channel_id: str, image_file, timing_type: str = "offsetFromStart", offset_ms: int = 15000) -> dict
```

チャンネルに透かしを設定します。

**パラメータ:**
- `channel_id` (str): チャンネルID
- `image_file`: 透かし画像ファイル
- `timing_type` (str): タイミングタイプ（'offsetFromStart', 'offsetFromEnd'）
- `offset_ms` (int): オフセット（ミリ秒、デフォルト: 15000）

**戻り値:**
- `dict`: 設定結果

**使用例:**
```python
with open("watermark.png", "rb") as f:
    result = yt.set_watermark(
        "UC_x5XG1OV2P6uZZ5FSM9Ttw", 
        f, 
        timing_type="offsetFromStart", 
        offset_ms=10000
    )
    print("✅ 透かし設定完了")
```

### unset_watermark()

```python
def unset_watermark(channel_id: str) -> bool
```

チャンネルの透かしを削除します。

**パラメータ:**
- `channel_id` (str): チャンネルID

**戻り値:**
- `bool`: 削除成功フラグ

**使用例:**
```python
success = yt.unset_watermark("UC_x5XG1OV2P6uZZ5FSM9Ttw")
if success:
    print("✅ 透かし削除完了")
```

---

## 簡略化メソッド

これらのメソッドは、複雑なページネーション処理を内部で自動化し、簡単に大量のデータを取得できるように設計されています。

### get_channel_playlists()

```python
def get_channel_playlists(channel_id: str, max_results: int = 50) -> list
```

チャンネルのプレイリスト一覧を取得します（簡略版）。

**パラメータ:**
- `channel_id` (str): チャンネルID
- `max_results` (int): 最大取得件数

**戻り値:**
- `list`: プレイリスト一覧

**使用例:**
```python
playlists = yt.get_channel_playlists("UC_x5XG1OV2P6uZZ5FSM9Ttw", max_results=100)
print(f"📝 取得したプレイリスト数: {len(playlists)}")
```

### search_all_videos()

```python
def search_all_videos(query: str, max_results: int = 500, channel_id: str = None) -> list
```

動画を全件検索します（簡略版）。

**パラメータ:**
- `query` (str): 検索キーワード
- `max_results` (int): 最大取得件数（デフォルト: 500）
- `channel_id` (str): 特定のチャンネル内で検索する場合のチャンネルID（オプション）

**戻り値:**
- `list`: 検索結果

**使用例:**
```python
# 一般検索
videos = yt.search_all_videos("Python プログラミング", max_results=1000)

# 特定チャンネル内検索
channel_videos = yt.search_all_videos(
    "機械学習", 
    max_results=200,
    channel_id="UC_x5XG1OV2P6uZZ5FSM9Ttw"
)
```

### get_all_channel_videos()

```python
def get_all_channel_videos(channel_id: str, max_results: int = 500) -> list
```

チャンネルの全動画を取得します（簡略版）。

**パラメータ:**
- `channel_id` (str): チャンネルID
- `max_results` (int): 最大取得件数（デフォルト: 500）

**戻り値:**
- `list`: 動画一覧

**使用例:**
```python
all_videos = yt.get_all_channel_videos("UC_x5XG1OV2P6uZZ5FSM9Ttw", max_results=1000)
print(f"🎬 取得した動画数: {len(all_videos)}")

# 最新の動画を表示
for video in all_videos[:5]:
    print(f"  • {video['snippet']['title']}")
```

### get_all_playlist_videos()

```python
def get_all_playlist_videos(playlist_id: str, max_results: int = 500) -> list
```

プレイリストの全動画を取得します（簡略版）。

**パラメータ:**
- `playlist_id` (str): プレイリストID
- `max_results` (int): 最大取得件数（デフォルト: 500）

**戻り値:**
- `list`: 動画一覧

**使用例:**
```python
playlist_videos = yt.get_all_playlist_videos("PLxyz123", max_results=300)
print(f"📹 プレイリスト内動画数: {len(playlist_videos)}")
```

### get_all_comments()

```python
def get_all_comments(video_id: str, max_results: int = 1000) -> list
```

動画の全コメントを取得します（簡略版）。

**パラメータ:**
- `video_id` (str): 動画ID
- `max_results` (int): 最大取得件数（デフォルト: 1000）

**戻り値:**
- `list`: コメント一覧

**使用例:**
```python
try:
    all_comments = yt.get_all_comments("dQw4w9WgXcQ", max_results=2000)
    print(f"💬 取得したコメント数: {len(all_comments)}")
    
    # 最新のコメントを表示
    for comment in all_comments[:5]:
        text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
        author = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
        print(f"  {author}: {text[:50]}...")
except YouTubeAPIError as e:
    if e.is_forbidden():
        print("❌ この動画はコメントが無効化されています")
```

---

## エラーハンドリング

### YouTubeAPIError の詳細

YouTube.py3では、APIエラーを詳細に分類し、適切な対処法を提供します。

```python
try:
    videos = yt.search_videos("Python")
except YouTubeAPIError as e:
    # エラーの種類に応じた処理
    if e.is_quota_exceeded():
        print("⏰ クォータ制限に達しました。しばらく待ってから再試行してください。")
    elif e.is_api_key_invalid():
        print("🔑 APIキーが無効です。設定を確認してください。")
    elif e.is_not_found():
        print("🔍 リソースが見つかりません。IDを確認してください。")
    elif e.is_forbidden():
        print("🚫 アクセス権限がありません。認証設定を確認してください。")
    else:
        print(f"❌ その他のエラー: {e}")
```

---

## 使用パターン集

### パターン1: 基本的な情報取得

```python
# チャンネル情報と最新動画を取得
channel_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"

channel = yt.get_channel_info(channel_id)
videos = yt.get_channel_videos_paginated(channel_id, max_results=10)

print(f"📺 {channel['snippet']['title']}")
print(f"👥 登録者数: {channel['statistics']['subscriberCount']}")
print("🆕 最新動画:")
for video in videos['items']:
    print(f"  • {video['snippet']['title']}")
```

### パターン2: 大量データの効率的な取得

```python
# チャンネルの全動画を効率的に取得
all_videos = yt.paginate_all_results(
    yt.get_channel_videos_paginated, 
    "CHANNEL_ID", 
    max_total_results=1000
)

print(f"✅ {len(all_videos)} 件の動画を取得しました")

# 簡略版も利用可能
all_videos_simple = yt.get_all_channel_videos("CHANNEL_ID", max_results=1000)
```

### パターン3: 検索結果の詳細分析

```python
# 検索結果を取得して詳細分析
search_results = yt.search_all_videos("機械学習", max_results=500)

# 統計分析
channels = {}
for video in search_results:
    channel = video['snippet']['channelTitle']
    channels[channel] = channels.get(channel, 0) + 1

print("📊 チャンネル別動画数:")
for channel, count in sorted(channels.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {channel}: {count}本")
```

### パターン4: 特定チャンネル内での検索

```python
# 特定のチャンネル内で検索
channel_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"
search_results = yt.search_all_videos(
    "Python", 
    max_results=100,
    channel_id=channel_id
)

print(f"🔍 チャンネル内検索結果: {len(search_results)}件")
for video in search_results[:5]:
    print(f"  • {video['snippet']['title']}")
```

### パターン5: プレイリスト管理の自動化

```python
# プレイリストを作成して動画を追加
playlist = yt.create_playlist(
    title="Python学習コレクション",
    description="Python学習に役立つ動画をまとめました",
    privacy_status="public"
)

# Python関連動画を検索して追加
python_videos = yt.search_all_videos("Python チュートリアル", max_results=20)
for video in python_videos:
    try:
        yt.add_video_to_playlist(playlist['id'], video['id']['videoId'])
        print(f"✅ 追加: {video['snippet']['title']}")
    except YouTubeAPIError as e:
        print(f"❌ スキップ: {e}")
```

### パターン6: エラーハンドリングの実装

```python
def safe_get_channel_info(channel_id):
    """安全なチャンネル情報取得"""
    try:
        return yt.get_channel_info(channel_id)
    except YouTubeAPIError as e:
        if e.is_quota_exceeded():
            print("⏰ クォータ制限です。しばらく待ってから再試行してください。")
            return None
        elif e.is_not_found():
            print(f"❌ チャンネルが見つかりません: {channel_id}")
            return None
        else:
            print(f"❌ エラー: {e}")
            return None

# 使用例
channel = safe_get_channel_info("UC_x5XG1OV2P6uZZ5FSM9Ttw")
if channel:
    print(f"✅ チャンネル取得成功: {channel['snippet']['title']}")
```

---

## 便利なヘルパーメソッド

これらのメソッドは、よく使われる操作を簡略化し、より直感的なインターフェースを提供します。

### get_basic_info()

```python
def get_basic_info(resource_id: str, resource_type: str = "auto") -> dict
```

リソースの基本情報を自動判別して取得します。

**パラメータ:**
- `resource_id` (str): YouTube ID（動画、チャンネル、プレイリスト）
- `resource_type` (str): リソースタイプ（'auto', 'video', 'channel', 'playlist'）

**戻り値:**
- `dict`: 基本情報

**使用例:**
```python
# 自動判別での取得
video_info = yt.get_basic_info("dQw4w9WgXcQ")  # 動画として認識
channel_info = yt.get_basic_info("UC_x5XG1OV2P6uZZ5FSM9Ttw")  # チャンネルとして認識

# 明示的にタイプを指定
playlist_info = yt.get_basic_info("PLxyz123", resource_type="playlist")
```

### quick_search()

```python
def quick_search(query: str, count: int = 10, content_type: str = "video") -> list
```

クイック検索（結果を簡潔に返す）。

**パラメータ:**
- `query` (str): 検索キーワード
- `count` (int): 取得件数（デフォルト: 10）
- `content_type` (str): コンテンツタイプ（'video', 'channel', 'playlist', 'all'）

**戻り値:**
- `list`: 簡潔な検索結果

**使用例:**
```python
# 動画のみ検索
results = yt.quick_search("Python プログラミング", count=5)
for result in results:
    print(f"🎬 {result['title']}")
    print(f"   ID: {result['id']}")
    print(f"   説明: {result['description']}")

# 全コンテンツタイプを検索
all_results = yt.quick_search("機械学習", count=15, content_type="all")
for result in all_results:
    print(f"{result['type']}: {result['title']}")
```

### get_stats_summary()

```python
def get_stats_summary(resource_id: str, resource_type: str = "auto") -> dict
```

統計情報のサマリーを取得します。

**パラメータ:**
- `resource_id` (str): リソースID
- `resource_type` (str): リソースタイプ（'auto', 'video', 'channel'）

**戻り値:**
- `dict`: 統計サマリー

**使用例:**
```python
# 動画の統計取得
video_stats = yt.get_stats_summary("dQw4w9WgXcQ")
print(f"📊 動画統計:")
print(f"   再生回数: {yt.format_view_count(video_stats['view_count'])}")
print(f"   いいね数: {video_stats['like_count']:,}")
print(f"   コメント数: {video_stats['comment_count']:,}")

# チャンネルの統計取得
channel_stats = yt.get_stats_summary("UC_x5XG1OV2P6uZZ5FSM9Ttw")
print(f"📺 チャンネル統計:")
print(f"   登録者数: {yt.format_subscriber_count(channel_stats['subscriber_count'])}")
print(f"   動画数: {channel_stats['video_count']:,}")
print(f"   総再生回数: {yt.format_view_count(channel_stats['view_count'])}")
```

### bulk_get_video_info()

```python
def bulk_get_video_info(video_ids: list) -> list
```

複数の動画情報を一括取得します。

**パラメータ:**
- `video_ids` (list): 動画IDのリスト（最大50件）

**戻り値:**
- `list`: 動画情報のリスト

**例外:**
- `YouTubeAPIError`: 50件を超えるIDが指定された場合

**使用例:**
```python
video_ids = ["dQw4w9WgXcQ", "jNQXAC9IVRw", "kJQP7kiw5Fk"]
videos = yt.bulk_get_video_info(video_ids)

for video in videos:
    snippet = video['snippet']
    stats = video['statistics']
    print(f"🎬 {snippet['title']}")
    print(f"   再生回数: {stats.get('viewCount', 0)}")
    print(f"   チャンネル: {snippet['channelTitle']}")
```

### bulk_get_channel_info()

```python
def bulk_get_channel_info(channel_ids: list) -> list
```

複数のチャンネル情報を一括取得します。

**パラメータ:**
- `channel_ids` (list): チャンネルIDのリスト（最大50件）

**戻り値:**
- `list`: チャンネル情報のリスト

**使用例:**
```python
channel_ids = ["UC_x5XG1OV2P6uZZ5FSM9Ttw", "UChIs72whgZI9w6d6FhwGGHA"]
channels = yt.bulk_get_channel_info(channel_ids)

for channel in channels:
    snippet = channel['snippet']
    stats = channel['statistics']
    print(f"📺 {snippet['title']}")
    print(f"   登録者数: {stats.get('subscriberCount', 0)}")
```

### get_trending_videos()

```python
def get_trending_videos(region_code: str = "JP", category_id: str = None, max_results: int = 50) -> list
```

トレンド動画を取得します。

**パラメータ:**
- `region_code` (str): 地域コード（デフォルト: "JP"）
- `category_id` (str): カテゴリID（オプション）
- `max_results` (int): 最大取得件数（デフォルト: 50）

**戻り値:**
- `list`: トレンド動画のリスト

**使用例:**
```python
# 日本のトレンド動画
trending_jp = yt.get_trending_videos(region_code="JP", max_results=20)
print("🔥 日本のトレンド動画:")
for i, video in enumerate(trending_jp[:10], 1):
    snippet = video['snippet']
    stats = video['statistics']
    print(f"{i:2d}. {snippet['title']}")
    print(f"     再生回数: {yt.format_view_count(stats['viewCount'])}")

# 特定カテゴリのトレンド
gaming_trending = yt.get_trending_videos(
    region_code="US",
    category_id="20",  # Gaming
    max_results=15
)
```

### get_channel_from_username()

```python
def get_channel_from_username(username: str) -> dict
```

ユーザー名からチャンネル情報を取得します。

**パラメータ:**
- `username` (str): YouTubeユーザー名

**戻り値:**
- `dict`: チャンネル情報

**例外:**
- `YouTubeAPIError`: ユーザーが見つからない場合

**使用例:**
```python
try:
    channel = yt.get_channel_from_username("GoogleDevelopers")
    print(f"📺 {channel['snippet']['title']}")
    print(f"   登録者数: {channel['statistics']['subscriberCount']}")
except YouTubeAPIError as e:
    print(f"❌ ユーザーが見つかりません: {e}")
```

### extract_video_id_from_url()

```python
def extract_video_id_from_url(youtube_url: str) -> str
```

YouTube URLから動画IDを抽出します。

**パラメータ:**
- `youtube_url` (str): YouTube URL

**戻り値:**
- `str`: 動画ID

**例外:**
- `YouTubeAPIError`: 有効なYouTube URLでない場合

**使用例:**
```python
urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://www.youtube.com/embed/dQw4w9WgXcQ"
]

for url in urls:
    try:
        video_id = yt.extract_video_id_from_url(url)
        print(f"✅ URL: {url}")
        print(f"   動画ID: {video_id}")
        
        # 抽出したIDで動画情報を取得
        video = yt.get_video_info(video_id)
        print(f"   タイトル: {video['snippet']['title']}")
    except YouTubeAPIError as e:
        print(f"❌ 無効なURL: {e}")
```

### extract_playlist_id_from_url()

```python
def extract_playlist_id_from_url(youtube_url: str) -> str
```

YouTube URLからプレイリストIDを抽出します。

**パラメータ:**
- `youtube_url` (str): YouTube URL

**戻り値:**
- `str`: プレイリストID

**使用例:**
```python
playlist_url = "https://www.youtube.com/playlist?list=PLxyz123"
playlist_id = yt.extract_playlist_id_from_url(playlist_url)
print(f"プレイリストID: {playlist_id}")

# 抽出したIDでプレイリスト情報を取得
playlist = yt.get_playlist_info(playlist_id)
print(f"プレイリスト名: {playlist['snippet']['title']}")
```

### get_video_duration_seconds()

```python
def get_video_duration_seconds(video_id: str) -> int
```

動画の長さを秒で取得します。

**パラメータ:**
- `video_id` (str): 動画ID

**戻り値:**
- `int`: 動画の長さ（秒）

**使用例:**
```python
def format_duration(seconds):
    """秒を時:分:秒形式に変換"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

# 動画の長さを取得
duration_sec = yt.get_video_duration_seconds("dQw4w9WgXcQ")
print(f"動画の長さ: {format_duration(duration_sec)}")

# 複数動画の長さを一括チェック
video_ids = ["dQw4w9WgXcQ", "jNQXAC9IVRw"]
for video_id in video_ids:
    duration = yt.get_video_duration_seconds(video_id)
    video = yt.get_video_info(video_id)
    print(f"🎬 {video['snippet']['title']}")
    print(f"   長さ: {format_duration(duration)}")
```

### format_view_count()

```python
def format_view_count(view_count: int) -> str
```

再生回数を読みやすい形式にフォーマットします。

**パラメータ:**
- `view_count` (int): 再生回数

**戻り値:**
- `str`: フォーマット済み文字列

**使用例:**
```python
# 様々な再生回数をフォーマット
view_counts = [1234, 12345, 123456, 1234567, 123456789]

for count in view_counts:
    formatted = yt.format_view_count(count)
    print(f"{count:>9,} 回 → {formatted}")

# 出力例:
#     1,234 回 → 1,234回
#    12,345 回 → 1.2万回
#   123,456 回 → 12.3万回
# 1,234,567 回 → 123.5万回
```

### format_subscriber_count()

```python
def format_subscriber_count(subscriber_count: int) -> str
```

登録者数を読みやすい形式にフォーマットします。

**パラメータ:**
- `subscriber_count` (int): 登録者数

**戻り値:**
- `str`: フォーマット済み文字列

**使用例:**
```python
channel = yt.get_channel_info("UC_x5XG1OV2P6uZZ5FSM9Ttw")
subscriber_count = int(channel['statistics']['subscriberCount'])

formatted = yt.format_subscriber_count(subscriber_count)
print(f"📺 {channel['snippet']['title']}")
print(f"   登録者数: {formatted}")
```

### search_and_get_details()

```python
def search_and_get_details(query: str, max_results: int = 10, include_stats: bool = True) -> list
```

検索して詳細情報も一緒に取得します。

**パラメータ:**
- `query` (str): 検索キーワード
- `max_results` (int): 最大結果数（デフォルト: 10）
- `include_stats` (bool): 統計情報を含めるか（デフォルト: True）

**戻り値:**
- `list`: 詳細情報付きの検索結果

**使用例:**
```python
# 詳細情報付きで検索
results = yt.search_and_get_details("Python チュートリアル", max_results=5)

print("🔍 検索結果（詳細情報付き）:")
for i, video in enumerate(results, 1):
    snippet = video['snippet']
    print(f"{i}. {snippet['title']}")
    print(f"   チャンネル: {snippet['channelTitle']}")
    print(f"   再生回数: {yt.format_view_count(video['view_count'])}")
    print(f"   いいね数: {video['like_count']:,}")
    print(f"   コメント数: {video['comment_count']:,}")
    print()

# 基本情報のみで検索（統計情報なし）
basic_results = yt.search_and_get_details(
    "機械学習", 
    max_results=10, 
    include_stats=False
)
```

### get_channel_upload_playlist()

```python
def get_channel_upload_playlist(channel_id: str) -> str
```

チャンネルのアップロードプレイリストIDを取得します。

**パラメータ:**
- `channel_id` (str): チャンネルID

**戻り値:**
- `str`: アップロードプレイリストID

**使用例:**
```python
# チャンネルのアップロードプレイリストを取得
uploads_playlist_id = yt.get_channel_upload_playlist("UC_x5XG1OV2P6uZZ5FSM9Ttw")
print(f"アップロードプレイリストID: {uploads_playlist_id}")

# そのプレイリストから最新動画を取得
latest_videos = yt.get_playlist_videos(uploads_playlist_id, max_results=10)
print("📹 最新動画:")
for video in latest_videos:
    print(f"  • {video['snippet']['title']}")
```

### get_latest_videos_from_channel()

```python
def get_latest_videos_from_channel(channel_id: str, max_results: int = 10) -> list
```

チャンネルの最新動画を効率的に取得します。

**パラメータ:**
- `channel_id` (str): チャンネルID
- `max_results` (int): 最大取得件数（デフォルト: 10）

**戻り値:**
- `list`: 最新動画のリスト

**使用例:**
```python
# 効率的に最新動画を取得
latest_videos = yt.get_latest_videos_from_channel(
    "UC_x5XG1OV2P6uZZ5FSM9Ttw", 
    max_results=15
)

print("🆕 最新動画:")
for video in latest_videos:
    snippet = video['snippet']
    published = snippet['publishedAt'][:10]  # 日付部分のみ
    print(f"📅 {published} - {snippet['title']}")
```

---

## 実用的な使用パターン

### パターン1: URL解析と情報取得の自動化

```python
def analyze_youtube_url(url):
    """YouTube URLを解析して詳細情報を取得"""
    try:
        # 動画URLかプレイリストURLかを判定
        if "watch?v=" in url or "youtu.be/" in url:
            video_id = yt.extract_video_id_from_url(url)
            info = yt.get_basic_info(video_id, "video")
            stats = yt.get_stats_summary(video_id, "video")
            
            print(f"🎬 動画: {info['snippet']['title']}")
            print(f"   チャンネル: {info['snippet']['channelTitle']}")
            print(f"   再生回数: {yt.format_view_count(stats['view_count'])}")
            
        elif "playlist?list=" in url:
            playlist_id = yt.extract_playlist_id_from_url(url)
            info = yt.get_basic_info(playlist_id, "playlist")
            videos = yt.get_playlist_videos(playlist_id, max_results=5)
            
            print(f"📝 プレイリスト: {info['snippet']['title']}")
            print(f"   動画数: {len(videos)} 件（先頭5件表示）")
            for video in videos:
                print(f"   • {video['snippet']['title']}")
                
    except YouTubeAPIError as e:
        print(f"❌ エラー: {e}")

# 使用例
urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/playlist?list=PLxyz123"
]

for url in urls:
    analyze_youtube_url(url)
    print()
```

### パターン2: チャンネル比較分析

```python
def compare_channels(channel_ids):
    """複数チャンネルの統計を比較"""
    channels = yt.bulk_get_channel_info(channel_ids)
    
    print("📊 チャンネル比較:")
    print("=" * 80)
    
    for channel in channels:
        snippet = channel['snippet']
        stats = channel['statistics']
        
        print(f"📺 {snippet['title']}")
        print(f"   登録者数: {yt.format_subscriber_count(int(stats['subscriberCount']))}")
        print(f"   動画数: {stats['videoCount']} 本")
        print(f"   総再生回数: {yt.format_view_count(int(stats['viewCount']))}")
        
        # 最新動画も表示
        latest = yt.get_latest_videos_from_channel(channel['id'], max_results=3)
        print("   最新動画:")
        for video in latest:
            print(f"     • {video['snippet']['title']}")
        print()

# 使用例
tech_channels = [
    "UC_x5XG1OV2P6uZZ5FSM9Ttw",  # Google Developers
    "UChIs72whgZI9w6d6FhwGGHA"   # freeCodeCamp
]
compare_channels(tech_channels)
```

### パターン3: コンテンツ分析とレポート

```python
def generate_content_report(query, max_videos=50):
    """検索結果の詳細分析レポート"""
    print(f"📊 コンテンツ分析レポート: '{query}'")
    print("=" * 60)
    
    # 詳細検索結果を取得
    results = yt.search_and_get_details(query, max_results=max_videos)
    
    # 統計計算
    total_views = sum(video['view_count'] for video in results)
    total_likes = sum(video['like_count'] for video in results)
    avg_views = total_views // len(results) if results else 0
    
    print(f"📈 総合統計:")
    print(f"   検索結果数: {len(results)} 件")
    print(f"   総再生回数: {yt.format_view_count(total_views)}")
    print(f"   平均再生回数: {yt.format_view_count(avg_views)}")
    print(f"   総いいね数: {total_likes:,}")
    print()
    
    # チャンネル別分析
    channel_stats = {}
    for video in results:
        channel = video['snippet']['channelTitle']
        if channel not in channel_stats:
            channel_stats[channel] = {
                'count': 0,
                'total_views': 0,
                'total_likes': 0
            }
        
        channel_stats[channel]['count'] += 1
        channel_stats[channel]['total_views'] += video['view_count']
        channel_stats[channel]['total_likes'] += video['like_count']
    
    print("🏆 チャンネル別ランキング（動画数順）:")
    sorted_channels = sorted(
        channel_stats.items(), 
        key=lambda x: x[1]['count'], 
        reverse=True
    )
    
    for i, (channel, stats) in enumerate(sorted_channels[:10], 1):
        print(f"{i:2d}. {channel}")
        print(f"     動画数: {stats['count']} 本")
        print(f"     総再生回数: {yt.format_view_count(stats['total_views'])}")
    
    # トップ動画
    print("\n🥇 再生回数トップ5:")
    top_videos = sorted(results, key=lambda x: x['view_count'], reverse=True)[:5]
    for i, video in enumerate(top_videos, 1):
        snippet = video['snippet']
        print(f"{i}. {snippet['title'][:50]}...")
        print(f"   再生回数: {yt.format_view_count(video['view_count'])}")
        print(f"   チャンネル: {snippet['channelTitle']}")

# 使用例
generate_content_report("Python プログラミング", max_videos=100)
```