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
- [便利なヘルパーメソッド](#便利なヘルパーメソッド)
- [動画分析・比較機能](#動画分析比較機能)
- [データエクスポート機能](#データエクスポート機能)
- [高度な検索・フィルタリング](#高度な検索フィルタリング)
- [バッチ処理・一括操作](#バッチ処理一括操作)
- [通知・監視機能](#通知監視機能)
- [ユーティリティ機能](#ユーティリティ機能)
- [OAuth認証管理](#oauth認証管理)
- [OAuth必須機能](#oauth必須機能)
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

**例外:**
- `YouTubeAPIError`: API呼び出しに失敗した場合

**使用例:**
```python
captions = yt.get_video_captions("dQw4w9WgXcQ")
for caption in captions:
    print(f"言語: {caption['snippet']['language']}")
    print(f"名前: {caption['snippet']['name']}")
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
print(caption_text)
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

**使用例:**
```python
result = yt.subscribe_to_channel("UC_x5XG1OV2P6uZZ5FSM9Ttw")
print("✅ チャンネルをサブスクライブしました")
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

**使用例:**
```python
members = yt.get_channel_members(max_results=100)
for member in members:
    print(f"メンバー: {member['snippet']['memberDetails']['displayName']}")
```

### get_membership_levels()

```python
def get_membership_levels() -> list
```

メンバーシップレベルを取得します。

**戻り値:**
- `list`: メンバーシップレベルのリスト

**使用例:**
```python
levels = yt.get_membership_levels()
for level in levels:
    print(f"レベル: {level['snippet']['creatorChannelId']}")
```

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

**使用例:**
```python
categories = yt.get_video_categories("JP")
for category in categories:
    print(f"{category['id']}: {category['snippet']['title']}")
```

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

これらのメソッドは、大量のデータを効率的に処理するためのページネーション機能を提供します。

### get_channel_videos_paginated()

```python
def get_channel_videos_paginated(channel_id: str, max_results: int = None, order: str = "date", page_token: str = None) -> dict
```

チャンネル動画を取得（ページネーション対応）。

**パラメータ:**
- `channel_id` (str): チャンネルID
- `max_results` (int): 最大取得件数（Noneの場合は50件）
- `order` (str): ソート順序（'date', 'relevance', 'rating', 'title', 'viewCount'）
- `page_token` (str): ページトークン（次のページ用）

**戻り値:**
- `dict`: 検索結果とページ情報
  - `'items'`: 動画リスト
  - `'nextPageToken'`: 次のページトークン（存在する場合）
  - `'totalResults'`: 総件数（推定）

**使用例:**
```python
result = yt.get_channel_videos_paginated("UC_x5XG1OV2P6uZZ5FSM9Ttw", max_results=25)
print(f"取得件数: {len(result['items'])}")
if result.get('nextPageToken'):
    print("次のページが利用可能です")
```

### search_videos_paginated()

```python
def search_videos_paginated(query: str, max_results: int = None, order: str = "relevance", page_token: str = None, channel_id: str = None, **filters) -> dict
```

動画検索（ページネーション対応）。

**パラメータ:**
- `query` (str): 検索キーワード
- `max_results` (int): 最大取得件数（Noneの場合は50件）
- `order` (str): ソート順序
- `page_token` (str): ページトークン
- `channel_id` (str): 特定のチャンネル内で検索する場合のチャンネルID（オプション）
- `**filters`: 追加フィルター

**戻り値:**
- `dict`: 検索結果とページ情報

**使用例:**
```python
# 特定のチャンネル内でページネーション検索
result = yt.search_videos_paginated(
    "Python", 
    max_results=25,
    channel_id="UC_x5XG1OV2P6uZZ5FSM9Ttw"
)
```

### get_playlist_videos_paginated()

```python
def get_playlist_videos_paginated(playlist_id: str, max_results: int = None, page_token: str = None) -> dict
```

プレイリスト動画を取得（ページネーション対応）。

**パラメータ:**
- `playlist_id` (str): プレイリストID
- `max_results` (int): 最大取得件数
- `page_token` (str): ページトークン

**戻り値:**
- `dict`: 検索結果とページ情報

### get_comments_paginated()

```python
def get_comments_paginated(video_id: str, max_results: int = None, order: str = "time", page_token: str = None) -> dict
```

コメントを取得（ページネーション対応）。

**パラメータ:**
- `video_id` (str): 動画ID
- `max_results` (int): 最大取得件数
- `order` (str): ソート順序（'time', 'relevance'）
- `page_token` (str): ページトークン

**戻り値:**
- `dict`: 検索結果とページ情報

### search_playlists_paginated()

```python
def search_playlists_paginated(query: str, max_results: int = None, order: str = "relevance", page_token: str = None, **filters) -> dict
```
プレイリスト検索（ページネーション対応）。

**パラメータ:**
- `query` (str): 検索キーワード
- `max_results` (int): 最大取得件数
- `order` (str): ソート順序
- `page_token` (str): ページトークン
- `**filters`: 追加フィルター

**戻り値:**
- `dict`: 検索結果とページ情報

### paginate_all_results()

```python
def paginate_all_results(paginated_func, *args, max_total_results: int = None, **kwargs) -> list
```

ページネーション対応関数で全件取得するヘルパー。

**パラメータ:**
- `paginated_func`: ページネーション対応関数
- `*args`: 関数の引数
- `max_total_results` (int): 最大総取得件数
- `**kwargs`: 関数のキーワード引数

**戻り値:**
- `list`: 全ての結果

**使用例:**
```python
# チャンネルの全動画を取得
all_videos = yt.paginate_all_results(
    yt.get_channel_videos_paginated, 
    "CHANNEL_ID", 
    max_total_results=500
)

# 検索結果を全件取得
all_results = yt.paginate_all_results(
    yt.search_videos_paginated, 
    "Python", 
    max_total_results=1000
)
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

## 便利なヘルパーメソッド

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
# 自動判別
info = yt.get_basic_info("dQw4w9WgXcQ")  # 動画として認識
info = yt.get_basic_info("UC_x5XG1OV2P6uZZ5FSM9Ttw")  # チャンネルとして認識
```

### quick_search()

```python
def quick_search(query: str, count: int = 10, content_type: str = "video") -> list
```

クイック検索（結果を簡潔に返します）。

**パラメータ:**
- `query` (str): 検索キーワード
- `count` (int): 取得件数
- `content_type` (str): コンテンツタイプ（'video', 'channel', 'playlist', 'all'）

**戻り値:**
- `list`: 簡潔な検索結果

**使用例:**
```python
results = yt.quick_search("Python プログラミング", count=5)
for result in results:
    print(f"{result['title']} - {result['id']}")
```

### get_stats_summary()

```python
def get_stats_summary(resource_id: str, resource_type: str = "auto") -> dict
```

統計情報のサマリーを取得します。

**パラメータ:**
- `resource_id` (str): リソースID
- `resource_type` (str): リソースタイプ

**戻り値:**
- `dict`: 統計サマリー

**使用例:**
```python
stats = yt.get_stats_summary("dQw4w9WgXcQ")
print(f"再生回数: {stats['view_count']:,}")
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

**使用例:**
```python
videos = yt.bulk_get_video_info(["dQw4w9WgXcQ", "jNQXAC9IVRw"])
for video in videos:
    print(f"タイトル: {video['snippet']['title']}")
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

### get_trending_videos()

```python
def get_trending_videos(region_code: str = "JP", category_id: str = None, max_results: int = 50) -> list
```

トレンド動画を取得します。

**パラメータ:**
- `region_code` (str): 地域コード
- `category_id` (str): カテゴリID（オプション）
- `max_results` (int): 最大取得件数

**戻り値:**
- `list`: トレンド動画のリスト

**使用例:**
```python
trending = yt.get_trending_videos("JP", max_results=20)
for video in trending:
    print(f"📈 {video['snippet']['title']}")
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

### get_my_channel()

```python
def get_my_channel() -> dict
```

自分のチャンネル情報を取得します（OAuth認証が必要）。

**戻り値:**
- `dict`: 自分のチャンネル情報

### extract_video_id_from_url()

```python
def extract_video_id_from_url(youtube_url: str) -> str
```

YouTube URLから動画IDを抽出します。

**パラメータ:**
- `youtube_url` (str): YouTube URL

**戻り値:**
- `str`: 動画ID

**使用例:**
```python
video_id = yt.extract_video_id_from_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
print(f"動画ID: {video_id}")
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
duration = yt.get_video_duration_seconds("dQw4w9WgXcQ")
print(f"動画の長さ: {duration//60}分{duration%60}秒")
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
formatted = yt.format_view_count(1234567)  # "123.5万回"
print(f"再生回数: {formatted}")
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
formatted = yt.format_subscriber_count(123456)  # "12.3万人"
print(f"登録者数: {formatted}")
```

### search_and_get_details()

```python
def search_and_get_details(query: str, max_results: int = 10, include_stats: bool = True) -> list
```

検索して詳細情報も一緒に取得します。

**パラメータ:**
- `query` (str): 検索キーワード
- `max_results` (int): 最大結果数
- `include_stats` (bool): 統計情報を含めるか

**戻り値:**
- `list`: 詳細情報付きの検索結果

**使用例:**
```python
results = yt.search_and_get_details("Python", max_results=5)
for video in results:
    print(f"{video['snippet']['title']} - {video['view_count']}回再生")
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

### get_latest_videos_from_channel()

```python
def get_latest_videos_from_channel(channel_id: str, max_results: int = 10) -> list
```

チャンネルの最新動画を効率的に取得します。

**パラメータ:**
- `channel_id` (str): チャンネルID
- `max_results` (int): 最大取得件数

**戻り値:**
- `list`: 最新動画のリスト

---

## 動画分析・比較機能

### compare_videos()

```python
def compare_videos(video_ids: list, metrics: list = None) -> dict
```

複数の動画を比較分析します。

**パラメータ:**
- `video_ids` (list): 動画IDのリスト（最大50件）
- `metrics` (list): 比較する指標 ['views', 'likes', 'comments', 'duration']

**戻り値:**
- `dict`: 比較結果とランキング

**使用例:**
```python
comparison = yt.compare_videos(["dQw4w9WgXcQ", "jNQXAC9IVRw"])
print(f"最も再生された動画: {comparison['rankings']['views'][0]['title']}")
```

### analyze_channel_performance()

```python
def analyze_channel_performance(channel_id: str, days_back: int = 30, max_videos: int = 50) -> dict
```

チャンネルのパフォーマンス分析を行います。

**パラメータ:**
- `channel_id` (str): チャンネルID
- `days_back` (int): 分析対象期間（日数）
- `max_videos` (int): 分析する最大動画数

**戻り値:**
- `dict`: パフォーマンス分析結果

**使用例:**
```python
analysis = yt.analyze_channel_performance("UC_x5XG1OV2P6uZZ5FSM9Ttw", days_back=30)
print(f"エンゲージメント率: {analysis['engagement_rate']:.2f}%")
```

---

## データエクスポート機能

### export_search_results_to_csv()

```python
def export_search_results_to_csv(query: str, filename: str = None, max_results: int = 100) -> str
```

検索結果をCSVファイルにエクスポートします。

**パラメータ:**
- `query` (str): 検索キーワード
- `filename` (str): 出力ファイル名（Noneの場合は自動生成）
- `max_results` (int): 最大結果数

**戻り値:**
- `str`: 作成されたファイル名

**使用例:**
```python
filename = yt.export_search_results_to_csv("Python プログラミング", max_results=50)
print(f"CSVファイルを作成しました: {filename}")
```

### export_channel_videos_to_json()

```python
def export_channel_videos_to_json(channel_id: str, filename: str = None, max_videos: int = 100) -> str
```

チャンネルの動画情報をJSONファイルにエクスポートします。

**パラメータ:**
- `channel_id` (str): チャンネルID
- `filename` (str): 出力ファイル名
- `max_videos` (int): 最大動画数

**戻り値:**
- `str`: 作成されたファイル名

---

## 高度な検索・フィルタリング

### search_videos_advanced()

```python
def search_videos_advanced(query: str, filters: dict = None, sort_by: str = 'relevance') -> list
```

高度な動画検索（複数フィルター対応）を行います。

**パラメータ:**
- `query` (str): 検索キーワード
- `filters` (dict): フィルター条件
- `sort_by` (str): ソート順序

**戻り値:**
- `list`: フィルター済み検索結果

**使用例:**
```python
filters = {
    'min_duration': 300,  # 5分以上
    'max_duration': 3600,  # 60分以下
    'min_views': 10000,   # 1万回以上再生
    'published_after': '2023-01-01',
    'channel_subscriber_min': 1000  # 登録者1000人以上のチャンネル
}
results = yt.search_videos_advanced("Python tutorial", filters=filters)
```

---

## バッチ処理・一括操作

### batch_analyze_channels()

```python
def batch_analyze_channels(channel_ids: list, metrics: list = ['subscribers', 'videos', 'views']) -> dict
```

複数チャンネルの一括分析を行います。

**パラメータ:**
- `channel_ids` (list): チャンネルIDのリスト
- `metrics` (list): 分析する指標

**戻り値:**
- `dict`: 分析結果とランキング

**使用例:**
```python
analysis = yt.batch_analyze_channels(["UC1", "UC2", "UC3"])
print(f"総登録者数: {analysis['summary']['total_subscribers']:,}")
```

---

## 通知・監視機能

### monitor_channel_for_new_videos()

```python
def monitor_channel_for_new_videos(channel_id: str, last_video_id: str = None) -> dict
```

チャンネルの新しい動画をチェックします。

**パラメータ:**
- `channel_id` (str): 監視するチャンネルID
- `last_video_id` (str): 前回チェック時の最新動画ID

**戻り値:**
- `dict`: 新しい動画の情報

**使用例:**
```python
result = yt.monitor_channel_for_new_videos("UC_x5XG1OV2P6uZZ5FSM9Ttw")
if result['count'] > 0:
    print(f"新しい動画が{result['count']}本投稿されました")
    for video in result['new_videos']:
        print(f"  • {video['title']}")
```

---

## ユーティリティ機能

### generate_video_summary()

```python
def generate_video_summary(video_id: str) -> dict
```

動画の包括的なサマリーを生成します。

**パラメータ:**
- `video_id` (str): 動画ID

**戻り値:**
- `dict`: 動画の包括的な情報

**使用例:**
```python
summary = yt.generate_video_summary("dQw4w9WgXcQ")
print(f"パフォーマンススコア: {summary['analysis']['performance_score']}")
print(f"エンゲージメントレベル: {summary['analysis']['engagement_level']}")
```

**戻り値の構造:**
```python
{
    'basic_info': {
        'title': '動画タイトル',
        'channel': 'チャンネル名',
        'published': '公開日',
        'duration': '4:13',
        'duration_seconds': 253,
        'url': 'YouTube URL'
    },
    'performance': {
        'views': 1234567,
        'views_formatted': '123.5万回',
        'likes': 12345,
        'comments': 678,
        'engagement_rate': 1.05
    },
    'content': {
        'description_length': 500,
        'description_preview': '説明文の最初の200文字...',
        'tags': ['タグ1', 'タグ2'],
        'category_id': '10'
    },
    'analysis': {
        'performance_score': 85.2,
        'content_type': '短編（5分未満）',
        'engagement_level': '普通'
    }
}
```

### 内部ヘルパーメソッド

```python
def _calculate_performance_score(views: int, likes: int, comments: int, duration: int) -> float
```

動画のパフォーマンススコアを計算（0-100）。

```python
def _classify_video_length(duration: int) -> str
```

動画の長さで分類します。
- `duration < 60`: "ショート（1分未満）"
- `duration < 300`: "短編（5分未満）"
- `duration < 1200`: "中編（20分未満）"
- `duration >= 1200`: "長編（20分以上）"

```python
def _classify_engagement(engagement_rate: float) -> str
```

エンゲージメント率で分類します。
- `>= 10%`: "非常に高い"
- `>= 5%`: "高い"
- `>= 2%`: "普通"
- `>= 1%`: "低い"
- `< 1%`: "非常に低い"

---

## 高度な使用パターン

### パターン1: 基本的な情報取得

```python
# チャンネル情報と最新動画を取得
channel_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"

channel = yt.get_channel_info(channel_id)
videos = yt.get_channel_videos_paginated(channel_id, max_results=10)

print(f"📺 チャンネル名: {channel['snippet']['title']}")
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

### パターン7: 包括的なチャンネル分析

```python
# チャンネルの包括的な分析
channel_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"

# 基本情報取得
channel_info = yt.get_channel_info(channel_id)
channel_stats = yt.get_stats_summary(channel_id)

# 最新動画の分析
latest_videos = yt.get_latest_videos_from_channel(channel_id, max_results=20)
video_ids = [v['snippet']['resourceId']['videoId'] for v in latest_videos]
video_comparison = yt.compare_videos(video_ids)

# パフォーマンス分析
performance = yt.analyze_channel_performance(channel_id, days_back=30)

print(f"📺 チャンネル名: {channel_info['snippet']['title']}")
print(f"👥 登録者数: {yt.format_subscriber_count(channel_stats['subscriber_count'])}")
print(f"📊 平均エンゲージメント率: {performance['engagement_rate']:.2f}%")
print(f"🏆 トップパフォーマー: {performance['top_performer']['title']}")
```

### パターン8: 高度な検索とフィルタリング

```python
# 詳細なフィルター条件での検索
advanced_filters = {
    'min_duration': 600,    # 10分以上
    'max_duration': 1800,   # 30分以下
    'min_views': 50000,     # 5万回以上
    'published_after': '2023-01-01',
    'channel_subscriber_min': 10000
}

# 高度な検索実行
results = yt.search_videos_advanced(
    "機械学習 チュートリアル", 
    filters=advanced_filters,
    sort_by='views'
)

# 結果の分析
for video in results[:5]:
    summary = yt.generate_video_summary(video['id']['videoId'])
    print(f"🎬 {video['snippet']['title']}")
    print(f"   パフォーマンス: {summary['analysis']['performance_score']}/100")
    print(f"   エンゲージメント: {summary['analysis']['engagement_level']}")
```
### パターン9: データエクスポートとレポート生成

```python
# 検索結果をCSVにエクスポート
csv_file = yt.export_search_results_to_csv(
    "Python プログラミング",
    filename="python_videos_report.csv",
    max_results=100
)

# チャンネル動画をJSONにエクスポート
json_file = yt.export_channel_videos_to_json(
    "UC_x5XG1OV2P6uZZ5FSM9Ttw",
    filename="channel_analysis.json",
    max_videos=200
)

print(f"📄 CSVレポート: {csv_file}")
print(f"📋 JSONデータ: {json_file}")
```

### パターン10: チャンネル監視システム

```python
import time
import json

def monitor_multiple_channels(channel_ids, check_interval=3600):
    """複数チャンネルの監視システム"""
    last_videos = {}
    
    # 初期状態を記録
    for channel_id in channel_ids:
        try:
            latest = yt.get_latest_videos_from_channel(channel_id, max_results=1)
            if latest:
                last_videos[channel_id] = latest[0]['snippet']['resourceId']['videoId']
        except YouTubeAPIError as e:
            print(f"❌ チャンネル {channel_id} の初期化に失敗: {e}")
    
    while True:
        print("🔍 チャンネル監視中...")
        for channel_id in channel_ids:
            try:
                result = yt.monitor_channel_for_new_videos(
                    channel_id, 
                    last_videos.get(channel_id)
                )
                
                if result['count'] > 0:
                    channel_info = yt.get_channel_info(channel_id)
                    print(f"🆕 {channel_info['snippet']['title']} に新動画！")
                    
                    for video in result['new_videos']:
                        print(f"   📹 {video['title']}")
                    
                    # 最新動画IDを更新
                    last_videos[channel_id] = result['latest_video_id']
                    
            except YouTubeAPIError as e:
                print(f"❌ 監視エラー {channel_id}: {e}")
        
        time.sleep(check_interval)

# 使用例
channels_to_monitor = [
    "UC_x5XG1OV2P6uZZ5FSM9Ttw",
    "UCxxxxxxxxxxxxxxxxxxxxxxx"
]
# monitor_multiple_channels(channels_to_monitor, check_interval=1800)  # 30分間隔
```

---

## OAuth認証管理

### YouTubeAPI(api_key, oauth_credentials, oauth_config)

```python
class YouTubeAPI(api_key=None, oauth_credentials=None, oauth_config=None)
```

OAuth対応のYouTube APIクライアントを初期化します。

**パラメータ:**
- `api_key` (str): YouTube Data API v3のAPIキー（読み取り専用操作用）
- `oauth_credentials`: OAuth認証情報オブジェクト（オプション）
- `oauth_config` (dict): OAuth設定辞書（オプション）

**OAuth設定辞書の構造:**
```python
{
    'client_secrets_file': 'client_secrets.json',  # Google Cloud Consoleからダウンロードしたファイル
    'scopes': ['full'],  # 必要なスコープのリスト
    'token_file': 'youtube_token.pickle',  # 認証トークン保存ファイル名
    'port': 8080,  # ローカルサーバーポート番号
    'auto_open_browser': True  # ブラウザ自動起動フラグ
}
```

**利用可能なスコープ:**
- `'readonly'`: 読み取り専用アクセス
- `'upload'`: 動画アップロード権限
- `'full'`: 全機能アクセス権限
- `'force_ssl'`: SSL強制アクセス権限

**使用例:**
```python
# APIキーのみ（読み取り専用）
yt = YouTubeAPI(api_key="YOUR_API_KEY")

# OAuth設定で初期化
oauth_config = {
    'client_secrets_file': 'client_secrets.json',
    'scopes': ['full'],
    'token_file': 'youtube_token.pickle',
    'port': 8080,
    'auto_open_browser': True
}
yt = YouTubeAPI(api_key="YOUR_API_KEY", oauth_config=oauth_config)

# 既存の認証情報を使用
yt = YouTubeAPI(api_key="YOUR_API_KEY", oauth_credentials=existing_credentials)
```

### setup_oauth_interactive()

```python
def setup_oauth_interactive(client_secrets_file, scopes=None, token_file=None) -> bool
```

対話的にOAuth認証をセットアップします。

**パラメータ:**
- `client_secrets_file` (str): クライアントシークレットファイルのパス
- `scopes` (list): 必要なスコープ（デフォルト: ['readonly']）
- `token_file` (str): トークン保存ファイル（デフォルト: 'youtube_token.pickle'）

**戻り値:**
- `bool`: セットアップ成功フラグ

**例外:**
- `YouTubeAPIError`: OAuth設定に失敗した場合

**使用例:**
```python
yt = YouTubeAPI(api_key="YOUR_API_KEY")

# 基本的なセットアップ
success = yt.setup_oauth_interactive('client_secrets.json')

# 詳細設定
success = yt.setup_oauth_interactive(
    'client_secrets.json',
    scopes=['full'],
    token_file='my_token.pickle'
)

if success:
    print("✅ OAuth認証が完了しました")
    # これで OAuth が必要なメソッドが使用可能
    my_channel = yt.get_my_channel()
    print(f"チャンネル名: {my_channel['snippet']['title']}")
```
### get_oauth_authorization_url()

```python
def get_oauth_authorization_url(client_secrets_file, scopes=None, state=None) -> tuple
```

OAuth認証URLを取得します（手動認証用）。

**パラメータ:**
- `client_secrets_file` (str): クライアントシークレットファイル
- `scopes` (list): 必要なスコープ
- `state` (str): 状態パラメータ（オプション）

**戻り値:**
- `tuple`: (認証URL, flowオブジェクト)

**使用例:**
```python
# 認証URLを取得
auth_url, flow = yt.get_oauth_authorization_url(
    'client_secrets.json', 
    ['full']
)

print(f"🔗 このURLにアクセスしてください:")
print(auth_url)
print()
print("ブラウザで認証を完了し、表示された認証コードを次のステップで入力してください。")

# ユーザーがブラウザで認証を完了
# 認証コードが表示される
```

### complete_oauth_flow()

```python
def complete_oauth_flow(flow, authorization_code, token_file=None) -> bool
```

OAuth認証フローを完了します（手動認証用）。

**パラメータ:**
- `flow`: get_oauth_authorization_urlで取得したflowオブジェクト
- `authorization_code` (str): ブラウザで取得した認証コード
- `token_file` (str): トークン保存ファイル（オプション）

**戻り値:**
- `bool`: 認証完了フラグ

**使用例:**
```python
# 前のステップで取得したflow使用
auth_url, flow = yt.get_oauth_authorization_url('client_secrets.json', ['full'])
print(f"認証URL: {auth_url}")

# ユーザーがブラウザで認証後、認証コードを取得
code = input("📝 認証コードを入力してください: ")

success = yt.complete_oauth_flow(flow, code, 'my_token.pickle')
if success:
    print("✅ 認証が完了しました")
    print("OAuth必須機能が利用可能になりました")
```
### get_oauth_info()

```python
def get_oauth_info() -> dict
```

現在のOAuth認証情報を取得します。

**戻り値:**
- `dict`: OAuth認証情報
  - `'authenticated'`: 認証状態（bool）
  - `'scopes'`: 許可されたスコープのリスト
  - `'expires_at'`: トークンの有効期限
  - `'token_valid'`: トークンの有効性
  - `'has_refresh_token'`: リフレッシュトークンの有無

**使用例:**
```python
info = yt.get_oauth_info()
print(f"🔐 認証状態: {info['authenticated']}")
print(f"📋 許可スコープ: {info['scopes']}")
print(f"✅ トークン有効: {info['token_valid']}")

if info['expires_at']:
    print(f"⏰ 有効期限: {info['expires_at']}")

if not info['authenticated']:
    print("❌ OAuth認証が必要です")
elif not info['token_valid']:
    print("⚠️ トークンをリフレッシュしてください")
```

### check_oauth_scopes()

```python
def check_oauth_scopes(required_scopes) -> dict
```

必要なスコープが許可されているかチェックします。

**パラメータ:**
- `required_scopes` (list): 必要なスコープリスト

**戻り値:**
- `dict`: スコープチェック結果
  - `'has_all_scopes'`: 全てのスコープが許可されているか
  - `'missing_scopes'`: 不足しているスコープのリスト
  - `'current_scopes'`: 現在許可されているスコープ

**使用例:**
```python
# 動画アップロードに必要なスコープをチェック
scope_check = yt.check_oauth_scopes(['upload'])

if scope_check['has_all_scopes']:
    print("✅ 必要なスコープがすべて許可されています")
    print("動画アップロードが可能です")
else:
    print("❌ 不足しているスコープがあります:")
    for scope in scope_check['missing_scopes']:
        print(f"  - {scope}")
    print("再認証が必要です")

# 複数スコープのチェック
scope_check = yt.check_oauth_scopes(['upload', 'full'])
print(f"現在のスコープ: {scope_check['current_scopes']}")
```

### refresh_oauth_token()

```python
def refresh_oauth_token(token_file=None) -> bool
```

OAuth認証トークンをリフレッシュします。

**パラメータ:**
- `token_file` (str): トークンファイル（オプション）

**戻り値:**
- `bool`: リフレッシュ成功フラグ

**例外:**
- `YouTubeAPIError`: OAuth認証が設定されていない、またはリフレッシュに失敗した場合

**使用例:**
```python
try:
    success = yt.refresh_oauth_token('my_token.pickle')
    if success:
        print("✅ トークンをリフレッシュしました")
        print("OAuth機能が再び利用可能です")
except YouTubeAPIError as e:
    print(f"❌ リフレッシュ失敗: {e}")
    print("💡 再認証が必要かもしれません")
    
    # 自動的に再認証を試行
    try:
        yt.setup_oauth_interactive('client_secrets.json', ['full'])
        print("✅ 再認証が完了しました")
    except YouTubeAPIError as e2:
        print(f"❌ 再認証も失敗: {e2}")
```

### revoke_oauth_token()

```python
def revoke_oauth_token(token_file=None) -> bool
```

OAuth認証トークンを無効化し、認証を解除します。

**パラメータ:**
- `token_file` (str): 削除するトークンファイル（オプション）

**戻り値:**
- `bool`: 無効化成功フラグ

**使用例:**
```python
success = yt.revoke_oauth_token('my_token.pickle')
if success:
    print("✅ 認証を解除しました")
    print("📖 APIキーのみでの読み取り専用モードに切り替わりました")
    
    # OAuth必須機能は使用不可になる
    try:
        yt.get_my_channel()
    except YouTubeAPIError as e:
        print(f"予想通りエラー: {e}")
```

### create_oauth_config_template()

```python
@classmethod
def create_oauth_config_template(output_file='oauth_config.json') -> str
```

OAuth設定テンプレートファイルを作成します。

**パラメータ:**
- `output_file` (str): 出力ファイル名（デフォルト: 'oauth_config.json'）

**戻り値:**
- `str`: 作成されたファイル名

**使用例:**
```python
# 設定テンプレート作成
template_file = YouTubeAPI.create_oauth_config_template('my_oauth_config.json')
print(f"📄 設定テンプレートを作成: {template_file}")

# 作成されたテンプレートの内容例
"""
{
  "client_secrets_file": "client_secrets.json",
  "scopes": ["readonly"],
  "token_file": "youtube_token.pickle",
  "port": 8080,
  "auto_open_browser": true,
  "_comment": {
    "scopes": "利用可能: readonly, upload, full, force_ssl",
    "client_secrets_file": "Google Cloud Consoleでダウンロードしたファイル",
    "token_file": "認証トークンの保存先",
    "port": "ローカルサーバーのポート番号",
    "auto_open_browser": "認証時にブラウザを自動で開くか"
  }
}
"""

# テンプレートを編集後、設定ファイルとして使用
import json
with open('my_oauth_config.json', 'r') as f:
    oauth_config = json.load(f)

# 必要に応じて設定を変更
oauth_config['client_secrets_file'] = 'path/to/your/client_secrets.json'
oauth_config['scopes'] = ['full']  # 必要なスコープに変更

# OAuth設定で初期化
yt = YouTubeAPI(api_key="YOUR_API_KEY", oauth_config=oauth_config)
```

---

## OAuth必須機能

以下の機能はOAuth認証が必要です。事前に認証設定を完了してください。

### get_my_channel()

```python
def get_my_channel() -> dict
```

自分のチャンネル情報を取得します（OAuth認証が必要）。

**戻り値:**
- `dict`: 自分のチャンネル情報

**例外:**
- `YouTubeAPIError`: OAuth認証が必要、またはチャンネルが見つからない場合

**使用例:**
```python
try:
    my_channel = yt.get_my_channel()
    print(f"📺 チャンネル名: {my_channel['snippet']['title']}")
    print(f"👥 登録者数: {my_channel['statistics']['subscriberCount']}")
    print(f"📹 動画数: {my_channel['statistics']['videoCount']}")
    print(f"👀 総再生回数: {my_channel['statistics']['viewCount']}")
except YouTubeAPIError as e:
    if "OAuth認証が必要" in str(e):
        print("❌ 先にOAuth認証を設定してください")
        print("💡 yt.setup_oauth_interactive('client_secrets.json') を実行")
    else:
        print(f"エラー: {e}")
```

### get_my_subscriptions()

```python
def get_my_subscriptions(max_results=50) -> list
```

自分のサブスクリプション一覧を取得します。

**パラメータ:**
- `max_results` (int): 最大取得件数（デフォルト: 50）

**戻り値:**
- `list`: サブスクライブしているチャンネルのリスト

**使用例:**
```python
subscriptions = yt.get_my_subscriptions(100)
print(f"📺 登録チャンネル数: {len(subscriptions)}個")

print("\n最近登録したチャンネル:")
for sub in subscriptions[:10]:  # 最初の10つを表示
    channel_name = sub['snippet']['title']
    channel_id = sub['snippet']['resourceId']['channelId']
    published = sub['snippet']['publishedAt'][:10]  # 登録日
    print(f"  📺 {channel_name} (登録日: {published})")
    print(f"      ID: {channel_id}")
```

### get_my_playlists()

```python
def get_my_playlists(max_results=50) -> list
```

自分のプレイリスト一覧を取得します。

**パラメータ:**
- `max_results` (int): 最大取得件数（デフォルト: 50）

**戻り値:**
- `list`: プレイリスト情報のリスト

**使用例:**
```python
playlists = yt.get_my_playlists()
print(f"🎵 プレイリスト数: {len(playlists)}")

print("\nプレイリスト一覧:")
for playlist in playlists:
    title = playlist['snippet']['title']
    privacy = playlist['status']['privacyStatus']
    item_count = playlist['contentDetails']['itemCount']
    created = playlist['snippet']['publishedAt'][:10]
    
    privacy_icon = {
        'public': '🌍',
        'unlisted': '🔗', 
        'private': '🔒'
    }.get(privacy, '❓')
    
    print(f"  {privacy_icon} {title} ({item_count}本, {privacy})")
    print(f"      作成日: {created}")
```

### get_my_videos()

```python
def get_my_videos(max_results=50) -> list
```

自分がアップロードした動画一覧を取得します。

**パラメータ:**
- `max_results` (int): 最大取得件数（デフォルト: 50）

**戻り値:**
- `list`: 動画情報のリスト

**使用例:**
```python
my_videos = yt.get_my_videos(20)
print(f"🎬 アップロード動画数: {len(my_videos)}")

print("\n最新のアップロード動画:")
for video in my_videos:
    video_id = video['snippet']['resourceId']['videoId']
    
    # 詳細情報を取得
    try:
        video_details = yt.get_video_info(video_id)
        title = video_details['snippet']['title']
        views = int(video_details['statistics'].get('viewCount', 0))
        likes = int(video_details['statistics'].get('likeCount', 0))
        published = video_details['snippet']['publishedAt'][:10]
        
        print(f"  🎬 {title}")
        print(f"      👀 {views:,}回再生 | 👍 {likes:,}いいね | 📅 {published}")
        print(f"      🔗 https://youtube.com/watch?v={video_id}")
    except YouTubeAPIError:
        print(f"  ❌ 動画情報取得失敗: {video_id}")
```

### upload_video()

```python
def upload_video(title, description, tags=None, category_id="22", privacy_status="private", video_file=None) -> dict
```

動画をアップロードします。

**パラメータ:**
- `title` (str): 動画タイトル
- `description` (str): 動画説明
- `tags` (list): タグリスト（オプション）
- `category_id` (str): カテゴリID（デフォルト: "22" = People & Blogs）
- `privacy_status` (str): プライバシー設定（'private', 'public', 'unlisted'）
- `video_file`: 動画ファイルオブジェクト（オプション）

**戻り値:**
- `dict`: アップロード結果

**必要なスコープ:** `upload`

**使用例:**
```python
# まずuploadスコープがあるかチェック
scope_check = yt.check_oauth_scopes(['upload'])
if not scope_check['has_all_scopes']:
    print("❌ アップロードにはuploadスコープが必要です")
    print("💡 再認証してください:")
    print("yt.setup_oauth_interactive('client_secrets.json', scopes=['upload'])")
else:
    # 動画アップロード
    from googleapiclient.http import MediaFileUpload
    
    # 動画ファイルの準備
    media = MediaFileUpload(
        'my_video.mp4', 
        chunksize=-1,  # ファイル全体を一度にアップロード
        resumable=True  # 再開可能アップロード
    )
    
    try:
        video = yt.upload_video(
            title="Python チュートリアル動画",
            description="""
            初心者向けPython講座の第1回です。
            
            📚 この動画で学べること:
            - Pythonの基本文法
            - 変数と型
            - 条件分岐とループ
            
            🔗 関連リンク:
            - GitHub: https://github.com/username/repo
            - 公式ドキュメント: https://docs.python.org/
            """,
            tags=["Python", "プログラミング", "チュートリアル", "初心者"],
            category_id="27",  # Education
            privacy_status="private",  # 最初はプライベートで
            video_file=media
        )
        
        video_id = video['id']
        video_url = f"https://youtube.com/watch?v={video_id}"
        
        print("✅ 動画アップロード完了!")
        print(f"🎬 タイトル: {video['snippet']['title']}")
        print(f"🔗 URL: {video_url}")
        print(f"🔒 プライバシー: {video['status']['privacyStatus']}")
        
    except YouTubeAPIError as e:
        print(f"❌ アップロード失敗: {e}")
```

### create_playlist()

```python
def create_playlist(title, description="", privacy_status="private") -> dict
```

プレイリストを作成します。

**パラメータ:**
- `title` (str): プレイリストタイトル
- `description` (str): プレイリスト説明（デフォルト: ""）
- `privacy_status` (str): プライバシー設定（デフォルト: "private"）

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

### subscribe_to_channel()

```python
def subscribe_to_channel(channel_id) -> dict
```

チャンネルをサブスクライブします。

**パラメータ:**
- `channel_id` (str): サブスクライブするチャンネルのID

**戻り値:**
- `dict`: サブスクライブ結果

**使用例:**
```python
# 特定のチャンネルをサブスクライブ
channel_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"

try:
    # チャンネル情報を先に取得
    channel_info = yt.get_channel_info(channel_id)
    channel_name = channel_info['snippet']['title']
    
    print(f"📺 {channel_name} をサブスクライブしますか？")
    confirm = input("y/N: ")
    
    if confirm.lower() == 'y':
        result = yt.subscribe_to_channel(channel_id)
        print(f"✅ {channel_name} をサブスクライブしました")
        
        # サブスクライブ確認
        subscriptions = yt.get_my_subscriptions(10)
        for sub in subscriptions:
            if sub['snippet']['resourceId']['channelId'] == channel_id:
                sub_date = sub['snippet']['publishedAt'][:10]
                print(f"✓ 確認済み: {sub['snippet']['title']} (登録日: {sub_date})")
                break
    else:
        print("❌ サブスクライブをキャンセルしました")
        
except YouTubeAPIError as e:
    if "already subscribed" in str(e).lower():
        print(f"📺 {channel_name} は既にサブスクライブ済みです")
    else:
        print(f"❌ サブスクライブ失敗: {e}")
```

### OAuth認証設定の完全な例

```python
# OAuth認証の設定から使用まで完全な例

from youtube_py3 import YouTubeAPI
import os

# 1. APIキーでライブラリを初期化
api_key = os.getenv('YOUTUBE_API_KEY')
yt = YouTubeAPI(api_key=api_key)

# 2. OAuth設定テンプレートを作成（初回のみ）
template_file = YouTubeAPI.create_oauth_config_template('oauth_config.json')
print(f"📄 設定ファイルを作成: {template_file}")
print("client_secrets.jsonファイルのパスを編集してください")

# 3. 対話的にOAuth認証を設定
try:
    success = yt.setup_oauth_interactive(
        client_secrets_file='client_secrets.json',
        scopes=['full'],  # 全機能を使用
        token_file='youtube_management_token.pickle'
    )
    
    if not success:
        print("❌ OAuth認証に失敗しました")
        return
        
except YouTubeAPIError as e:
    print(f"❌ OAuth設定エラー: {e}")
    return

print("✅ OAuth認証完了")
    
# 2. 自分のチャンネル分析
print("\n🔍 チャンネル分析...")
my_channel = yt.get_my_channel()
channel_name = my_channel['snippet']['title']
subscriber_count = int(my_channel['statistics']['subscriberCount'])

print(f"📺 チャンネル名: {channel_name}")
print(f"👥 登録者数: {subscriber_count:,}人")
    
# 3. 自分の動画パフォーマンス分析
print("\n📊 動画パフォーマンス分析...")
my_videos = yt.get_my_videos(10)  # 最新10本

if my_videos:
    total_views = 0
    video_performances = []
    
    for video_item in my_videos:
        video_id = video_item['snippet']['resourceId']['videoId']
        try:
            video_details = yt.get_video_info(video_id)
            summary = yt.generate_video_summary(video_id)
            
            performance = {
                'title': video_details['snippet']['title'],
                'views': int(video_details['statistics'].get('viewCount', 0)),
                'likes': int(video_details['statistics'].get('likeCount', 0)),
                'comments': int(video_details['statistics'].get('commentCount', 0)),
                'score': summary['analysis']['performance_score'],
                'engagement': summary['analysis']['engagement_level']
            }
            video_performances.append(performance)
            total_views += performance['views']
            
        except YouTubeAPIError:
            continue

    # トップパフォーマー表示
    if video_performances:
        top_video = max(video_performances, key=lambda x: x['score'])
        avg_views = total_views / len(video_performances)
        
        print(f"🏆 トップパフォーマー:")
        print(f"   📹 {top_video['title']}")
        print(f"   👀 {top_video['views']:,}回再生")
        print(f"   📊 スコア: {top_video['score']:.1f}/100")
        print(f"   💝 エンゲージメント: {top_video['engagement']}")
        print(f"📈 平均再生回数: {avg_views:,.0f}回")
    

# 4. プレイリスト管理
print("\n🎵 プレイリスト管理...")
playlists = yt.get_my_playlists()

# 統計プレイリストを作成（存在しない場合）
stats_playlist_name = "📊 パフォーマンス上位動画"
stats_playlist = None

for playlist in playlists:
    if playlist['snippet']['title'] == stats_playlist_name:
        stats_playlist = playlist
        break

if not stats_playlist and video_performances:
    try:
        stats_playlist = yt.create_playlist(
            title=stats_playlist_name,
            description="自動生成: パフォーマンススコアが高い動画のコレクション",
            privacy_status="private"
        )
        print(f"✅ 統計プレイリスト作成: {stats_playlist_name}")
    except YouTubeAPIError as e:
        print(f"❌ プレイリスト作成失敗: {e}")

# 5. コンテンツ戦略提案
print("\n💡 コンテンツ戦略提案...")

if video_performances:
    # 高パフォーマンス動画の特徴分析
    high_performers = [v for v in video_performances if v['score'] >= 70]
    
    if high_performers:
        avg_high_views = sum(v['views'] for v in high_performers) / len(high_performers)
        print(f"🎯 高パフォーマンス動画（スコア70+）: {len(high_performers)}本")
        print(f"📊 平均再生回数: {avg_high_views:,.0f}回")
        
        # タグ分析（簡易版）
        print("🏷️  成功パターンを分析して類似コンテンツの作成を検討してください")
    else:
        print("📈 パフォーマンス向上の余地があります")
        print("💡 提案:")
        print("   - より魅力的なタイトルとサムネイル")
        print("   - 視聴者とのエンゲージメント向上")
        print("   - 定期的な投稿スケジュール")

# 6. サブスクリプション分析
print("\n👥 サブスクリプション分析...")
subscriptions = yt.get_my_subscriptions(20)

if subscriptions:
    print(f"📺 フォロー中のチャンネル: {len(subscriptions)}個")
    
    # 最近サブスクライブしたチャンネル
    recent_subs = subscriptions[:5]
    print("🆕 最近サブスクライブしたチャンネル:")
    for sub in recent_subs:
        name = sub['snippet']['title']
        sub_date = sub['snippet']['publishedAt'][:10]
        print(f"   📺 {name} ({sub_date})")
    
# 7. レポート生成
print("\n📋 レポート生成...")

report = {
    'channel_name': channel_name,
    'subscriber_count': subscriber_count,
    'video_count': len(my_videos) if my_videos else 0,
    'total_views': total_views if 'total_views' in locals() else 0,
    'playlist_count': len(playlists),
    'subscription_count': len(subscriptions) if subscriptions else 0,
    'analysis_date': time.strftime('%Y-%m-%d %H:%M:%S')
}

# JSONレポート出力
import json
report_file = f"youtube_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"📄 詳細レポートを保存: {report_file}")

print("\n✅ YouTube管理分析完了!")
print("📈 定期的にこの分析を実行して、チャンネルの成長を追跡しましょう")
```

このOAuth機能拡張により、YouTube.py3ライブラリは以下の能力を獲得しました：

## 🚀 新機能ハイライト

### **完全なYouTube API対応**
- **読み取り専用**: APIキーでの基本情報取得
- **書き込み対応**: OAuth認証での高度な操作
- **個人データアクセス**: 自分のチャンネル、動画、プレイリスト管理

### **セキュアな認証システム**
- 自動OAuth設定
- 手動認証フロー対応
- トークン管理（リフレッシュ、無効化）
- スコープベースの権限管理

### **実用的な機能セット**
- 動画アップロード
- プレイリスト作成・管理
- チャンネル登録管理
- 包括的な分析とレポート

**総メソッド数**: **108個から122個**に増加し、YouTube Data API v3の機能を完全網羅したライブラリとなりました。

---

## 📋 完全機能リスト

このAPIリファレンスには以下のすべての機能が含まれています：

### ✅ 実装済み機能（全108メソッド）

**基本クラス（2）**
- YouTubeAPI
- YouTubeAPIError

**基本情報取得（6）**  
- check_quota_usage(), get_channel_info(), get_video_info(), get_playlist_info()
- get_channel_statistics_only(), get_video_statistics_only()

**検索機能（3）**
- search_videos(), search_channels(), search_playlists()

**リスト取得（3）**
- get_playlist_videos(), get_comments(), get_channel_videos()

**ページネーション機能（6）**
- get_channel_videos_paginated(), search_videos_paginated(), get_playlist_videos_paginated()
- get_comments_paginated(), search_playlists_paginated(), paginate_all_results()

**簡略化メソッド（5）**
- get_channel_playlists(), search_all_videos(), get_all_channel_videos()
- get_all_playlist_videos(), get_all_comments()

**便利なヘルパーメソッド（15）**
- get_basic_info(), quick_search(), get_stats_summary(), bulk_get_video_info()
- bulk_get_channel_info(), get_trending_videos(), get_channel_from_username()
- get_my_channel(), extract_video_id_from_url(), extract_playlist_id_from_url()
- get_video_duration_seconds(), format_view_count(), format_subscriber_count()
- search_and_get_details(), get_channel_upload_playlist(), get_latest_videos_from_channel()

**プレイリスト管理（6）**
- create_playlist(), update_playlist(), delete_playlist()
- add_video_to_playlist(), remove_video_from_playlist(), update_playlist_item_position()

**プレイリスト画像管理（2）**
- get_playlist_images(), upload_playlist_image()

**コメント管理（7）**
- get_comment_details(), post_comment_reply(), post_comment_thread()
- update_comment(), delete_comment(), mark_comment_as_spam(), set_comment_moderation_status()

**チャンネル管理（6）**
- update_channel(), upload_channel_banner(), create_channel_section()
- update_channel_section(), delete_channel_section()

**動画管理（8）**
- upload_video(), update_video(), delete_video(), rate_video()
- get_video_rating(), set_video_thumbnail(), report_video_abuse()

**字幕管理（5）**
- get_video_captions(), download_caption(), upload_caption()
- update_caption(), delete_caption()

**サブスクリプション管理（2）**
- subscribe_to_channel(), unsubscribe_from_channel()

**メンバーシップ管理（2）**
- get_channel_members(), get_membership_levels()

**透かし管理（2）**
- set_watermark(), unset_watermark()

**システム情報（4）**
- get_video_categories(), get_supported_languages(), get_supported_regions(), get_guide_categories()

**動画分析・比較機能（2）**
- compare_videos(), analyze_channel_performance()

**データエクスポート機能（2）**
- export_search_results_to_csv(), export_channel_videos_to_json()

**高度な検索・フィルタリング（1）**
- search_videos_advanced()

**バッチ処理・一括操作（1）**
- batch_analyze_channels()

**通知・監視機能（1）**
- monitor_channel_for_new_videos()

**ユーティリティ機能（4）**
- generate_video_summary(), _calculate_performance_score()
- _classify_video_length(), _classify_engagement()

**OAuth認証管理（8）**

- setup_oauth_interactive(), get_oauth_authorization_url(), complete_oauth_flow()
- get_oauth_info(), check_oauth_scopes(), refresh_oauth_token()
- revoke_oauth_token(), create_oauth_config_template()

**OAuth必須機能（6）**

- get_my_channel(), get_my_subscriptions(), get_my_playlists()
- get_my_videos(), upload_video(), subscribe_to_channel()

**最終更新**: 2025年 6月  
**関連ドキュメント**: [README](README.md) | [インストールガイド](installation.md) | [トラブルシューティング](troubleshooting.md)