# APIリファレンス

YouTube.py3の全メソッドの詳細な説明です。実装済みのメソッドを機能別に分類して説明します。

## 📚 目次

- [基本クラス](#基本クラス)
- [基本情報取得](#基本情報取得)
- [検索機能](#検索機能)
- [リスト取得](#リスト取得)
- [プレイリスト管理](#プレイリスト管理)
- [コメント管理](#コメント管理)
- [チャンネル管理](#チャンネル管理)
- [動画管理](#動画管理)
- [字幕管理](#字幕管理)
- [サブスクリプション管理](#サブスクリプション管理)
- [メンバーシップ管理](#メンバーシップ管理)
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
- `timing_type` (str): タイミングタイプ
- `offset_ms` (int): オフセット（ミリ秒）

**戻り値:**
- `dict`: 設定結果

### unset_watermark()

```python
def unset_watermark(channel_id: str) -> bool
```

チャンネルの透かしを削除します。

**パラメータ:**
- `channel_id` (str): チャンネルID

**戻り値:**
- `bool`: 削除成功フラグ

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
- `category_id` (str): カテゴリID
- `privacy_status` (str): プライバシー設定
- `video_file`: 動画ファイル

**戻り値:**
- `dict`: アップロード結果

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

### update_caption()

```python
def update_caption(caption_id: str, name: str = None, caption_file = None) -> dict
```

字幕を更新します。

**パラメータ:**
- `caption_id` (str): 字幕ID
- `name` (str): 新しい字幕名（オプション）
- `caption_file`: 新しい字幕ファイル（オプション）

**戻り値:**
- `dict`: 更新結果

### delete_caption()

```python
def delete_caption(caption_id: str) -> bool
```

字幕を削除します。

**パラメータ:**
- `caption_id` (str): 字幕ID

**戻り値:**
- `bool`: 削除成功フラグ

---

## サブスクリプション管理

### subscribe_to_channel()

```python
def subscribe_to_channel(channel_id: str) -> dict
```

チャンネルをサブスクライブします。

**パラメータ:**
- `channel_id` (str): サブスクライブするチャンネルID

**戻り値:**
- `dict`: サブスクライブ結果

### unsubscribe_from_channel()

```python
def unsubscribe_from_channel(subscription_id: str) -> bool
```

チャンネルのサブスクライブを解除します。

**パラメータ:**
- `subscription_id` (str): サブスクリプションID

**戻り値:**
- `bool`: 解除成功フラグ

---

## メンバーシップ管理

### get_channel_members()

```python
def get_channel_members(max_results: int = 50) -> list
```

チャンネルメンバーを取得します。

**パラメータ:**
- `max_results` (int): 取得する最大メンバー数

**戻り値:**
- `list`: メンバー情報のリスト

### get_membership_levels()

```python
def get_membership_levels() -> list
```

メンバーシップレベルを取得します。

**戻り値:**
- `list`: メンバーシップレベルのリスト

---

## システム情報

### get_video_categories()

```python
def get_video_categories(region_code: str = "JP") -> list
```

動画カテゴリ一覧を取得します。

**パラメータ:**
- `region_code` (str): 地域コード

**戻り値:**
- `list`: カテゴリ情報のリスト

### get_supported_languages()

```python
def get_supported_languages() -> list
```

サポートされている言語一覧を取得します。

**戻り値:**
- `list`: 言語情報のリスト

### get_supported_regions()

```python
def get_supported_regions() -> list
```

サポートされている地域一覧を取得します。

**戻り値:**
- `list`: 地域情報のリスト

### get_guide_categories()

```python
def get_guide_categories(region_code: str = "JP") -> list
```

ガイドカテゴリを取得します。

**パラメータ:**
- `region_code` (str): 地域コード

**戻り値:**
- `list`: ガイドカテゴリのリスト

---

## ページネーション機能

### 簡略化メソッド（通常のリスト取得版）

これらのメソッドは、ページネーション機能を内部で使用し、指定した件数まで自動的に全件取得します。手動でページングを行う必要がありません。

### get_channel_playlists()

```python
def get_channel_playlists(channel_id: str, max_results: int = 50) -> list
```

チャンネルのプレイリスト一覧を取得します（簡略版）。

**パラメータ:**
- `channel_id` (str): チャンネルID
- `max_results` (int): 最大取得件数（デフォルト: 50）

**戻り値:**
- `list`: プレイリスト一覧

**使用例:**
```python
playlists = yt.get_channel_playlists("UC_x5XG1OV2P6uZZ5FSM9Ttw", max_results=100)
for playlist in playlists:
    print(f"📝 {playlist['snippet']['title']}")
    print(f"   説明: {playlist['snippet']['description'][:100]}...")
```

### search_all_videos()

```python
def search_all_videos(query: str, max_results: int = 500) -> list
```

動画を全件検索します（簡略版）。

**パラメータ:**
- `query` (str): 検索キーワード
- `max_results` (int): 最大取得件数（デフォルト: 500）

**戻り値:**
- `list`: 検索結果

**使用例:**
```python
all_videos = yt.search_all_videos("Python プログラミング", max_results=1000)
print(f"✅ 検索完了: {len(all_videos)} 件の動画を取得")

# チャンネル別統計
channels = {}
for video in all_videos:
    channel = video['snippet']['channelTitle']
    channels[channel] = channels.get(channel, 0) + 1

print("📊 チャンネル別動画数（上位10位）:")
for channel, count in sorted(channels.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {channel}: {count}本")
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
print(f"📹 取得完了: {len(all_videos)} 件の動画")

# 投稿頻度分析
from datetime import datetime
import collections

years = []
for video in all_videos:
    published_at = video['snippet']['publishedAt']
    year = datetime.fromisoformat(published_at.replace('Z', '+00:00')).year
    years.append(year)

year_counts = collections.Counter(years)
print("📊 年別投稿数:")
for year, count in sorted(year_counts.items()):
    print(f"  {year}年: {count}本")
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
all_videos = yt.get_all_playlist_videos("PLxyz123", max_results=200)
print(f"📝 プレイリスト全動画: {len(all_videos)} 件")

# 動画時間の合計計算（duration情報が必要な場合）
total_duration = 0
for video in all_videos:
    video_id = video['snippet']['resourceId']['videoId']
    video_details = yt.get_video_info(video_id)
    # duration処理ロジックをここに追加
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

**例外:**
- `YouTubeAPIError`: コメントが無効化されている場合

**使用例:**
```python
try:
    all_comments = yt.get_all_comments("dQw4w9WgXcQ", max_results=2000)
    print(f"💬 全コメント取得: {len(all_comments)} 件")
    
    # コメント分析
    import re
    from collections import Counter
    
    # 感情分析やキーワード抽出
    keywords = []
    for comment in all_comments:
        text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
        # 簡単なキーワード抽出例
        words = re.findall(r'\w+', text.lower())
        keywords.extend(words)
    
    # 頻出キーワード上位10位
    word_counts = Counter(keywords)
    print("🔥 頻出キーワード:")
    for word, count in word_counts.most_common(10):
        print(f"  {word}: {count}回")
        
except YouTubeAPIError as e:
    if e.is_forbidden():
        print("❌ この動画はコメントが無効化されています")
    else:
        print(f"エラー: {e}")
```

### search_playlists_paginated()

```python
def search_playlists_paginated(query: str, max_results: int = 50, order: str = "relevance", page_token: str = None, **filters) -> dict
```

プレイリスト検索（ページネーション対応）。

**パラメータ:**
- `query` (str): 検索キーワード
- `max_results` (int): 最大取得件数（1-50、デフォルト: 50）
- `order` (str): ソート順序（デフォルト: 'relevance'）
- `page_token` (str): ページトークン（オプション）
- `**filters`: 追加フィルター

**戻り値:**
```python
{
    'items': [...],  # プレイリスト検索結果
    'nextPageToken': 'token_string',  # 次ページのトークン
    'totalResults': 500,  # 総結果数（推定）
    'resultsPerPage': 50  # 1ページあたりの結果数
}
```

**使用例:**
```python
# 基本的なプレイリスト検索
result = yt.search_playlists_paginated("Python 学習", max_results=25)
playlists = result['items']

print(f"🔍 検索結果: {len(playlists)} 件")
for playlist in playlists:
    snippet = playlist['snippet']
    print(f"📝 {snippet['title']}")
    print(f"   チャンネル: {snippet['channelTitle']}")
    print(f"   公開日: {snippet['publishedAt'][:10]}")

# 次のページを取得
if result.get('nextPageToken'):
    next_result = yt.search_playlists_paginated(
        "Python 学習", 
        max_results=25, 
        page_token=result['nextPageToken']
    )
```

### 簡略化メソッドの活用パターン

#### パターン1: 大量データの一括取得

```python
# チャンネルの全動画とコメントを一括分析
channel_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"

# 1. チャンネル情報を取得
channel = yt.get_channel_info(channel_id)
print(f"📺 分析対象: {channel['snippet']['title']}")

# 2. 全動画を取得
all_videos = yt.get_all_channel_videos(channel_id, max_results=1000)
print(f"📹 対象動画数: {len(all_videos)}")

# 3. 人気動画のコメントを分析
popular_videos = all_videos[:10]  # 最新10本を分析
for video in popular_videos:
    video_id = video['id']['videoId']
    try:
        comments = yt.get_all_comments(video_id, max_results=500)
        print(f"💬 {video['snippet']['title']}: {len(comments)}件のコメント")
    except YouTubeAPIError:
        print(f"❌ {video['snippet']['title']}: コメント取得不可")
```

#### パターン2: 検索結果の詳細分析

```python
# 特定トピックの動画とプレイリストを包括分析
query = "機械学習 入門"

# 動画とプレイリストを並行取得
videos = yt.search_all_videos(query, max_results=500)
playlists = yt.paginate_all_results(
    yt.search_playlists_paginated, 
    query, 
    max_total_results=100
)

print(f"🎬 動画: {len(videos)}件")
print(f"📝 プレイリスト: {len(playlists)}件")

# チャンネル別集計
all_content = videos + playlists
channel_stats = {}
for item in all_content:
    channel = item['snippet']['channelTitle']
    if channel not in channel_stats:
        channel_stats[channel] = {'videos': 0, 'playlists': 0}
    
    if 'videoId' in item['id']:
        channel_stats[channel]['videos'] += 1
    else:
        channel_stats[channel]['playlists'] += 1

# 結果表示
print("\n📊 チャンネル別コンテンツ数:")
for channel, stats in sorted(channel_stats.items(), 
                           key=lambda x: x[1]['videos'] + x[1]['playlists'], 
                           reverse=True)[:10]:
    total = stats['videos'] + stats['playlists']
    print(f"  {channel}: 動画{stats['videos']}本 + プレイリスト{stats['playlists']}個 = 計{total}個")
```

#### パターン3: 効率的なデータ収集

```python
# 複数チャンネルの情報を効率的に収集
channels = [
    "UC_x5XG1OV2P6uZZ5FSM9Ttw",
    "UCqnbDFdCpuN8CMEg0VuEBqA",
    # ... 他のチャンネルID
]

all_data = {}
for channel_id in channels:
    try:
        # チャンネル基本情報
        channel_info = yt.get_channel_info(channel_id)
        channel_name = channel_info['snippet']['title']
        
        # 最新動画を効率的に取得
        recent_videos = yt.get_all_channel_videos(channel_id, max_results=50)
        
        # プレイリスト情報
        playlists = yt.get_channel_playlists(channel_id, max_results=20)
        
        all_data[channel_name] = {
            'info': channel_info,
            'recent_videos': recent_videos,
            'playlists': playlists
        }
        
        print(f"✅ {channel_name}: 動画{len(recent_videos)}本, プレイリスト{len(playlists)}個")
        
    except YouTubeAPIError as e:
        print(f"❌ {channel_id}: {e}")

print(f"\n📊 収集完了: {len(all_data)}チャンネル")
```