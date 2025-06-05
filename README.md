# youtube.py2

YouTube Data API v3の主要機能を簡略化・ラップして使いやすくするPythonライブラリです。

## 特徴

- YouTube Data API v3の複雑さを隠蔽
- 初心者でも使いやすいシンプルなインターフェース
- エラーハンドリングとページネーション対応
- Pythonの辞書・リストで扱いやすいレスポンス

## インストール

```bash
pip install google-api-python-client python-dotenv
```

## 環境設定

### 1. APIキーの取得
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成またはプロジェクトを選択
3. YouTube Data API v3を有効化
4. 認証情報でAPIキーを作成

### 2. 環境変数の設定

#### 方法1: .envファイルを使用（推奨）
```bash
# .env.example を .env にコピー
cp .env.example .env

# .env ファイルを編集してAPIキーを設定
YOUTUBE_API_KEY=your_actual_api_key_here
```

#### 方法2: システム環境変数
```bash
# Windows
set YOUTUBE_API_KEY=your_actual_api_key_here

# macOS/Linux
export YOUTUBE_API_KEY=your_actual_api_key_here
```

#### 方法3: Python実行時に設定
```bash
YOUTUBE_API_KEY=your_api_key python examples/basic_usage.py
```

## 使い方

### 基本的な使用例

```python
import os
from youtube_py2 import YouTubeAPI

# 環境変数からAPIキーを取得
api_key = os.getenv('YOUTUBE_API_KEY')
yt = YouTubeAPI(api_key)

# チャンネル情報取得
channel = yt.get_channel_info("CHANNEL_ID")
print(channel["snippet"]["title"])

# 動画検索
videos = yt.search_videos("Python", max_results=5)
for video in videos:
    print(video["snippet"]["title"])

# 動画情報取得
video_info = yt.get_video_info("VIDEO_ID")
print(f"Views: {video_info['statistics']['viewCount']}")

# コメント取得
comments = yt.get_comments("VIDEO_ID", max_results=10)
for comment in comments:
    text = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
    print(text)

# プレイリストの動画一覧
playlist_videos = yt.get_playlist_videos("PLAYLIST_ID")
```

### サンプルコードの実行

```bash
# 基本的な使用例
python examples/basic_usage.py

# 高度な使用例
python examples/advanced_usage.py
```

## API メソッド

### `get_channel_info(channel_id)`
指定されたチャンネルIDの情報を取得します。

### `get_video_info(video_id)`
指定された動画IDの詳細情報を取得します。

### `search_videos(query, max_results=5, order='relevance')`
キーワードで動画を検索します。

### `get_comments(video_id, max_results=100)`
指定された動画のコメントを取得します。

### `get_playlist_videos(playlist_id, max_results=50)`
プレイリストの動画一覧を取得します。

### `get_channel_videos(channel_id, max_results=50)`
チャンネルの最新動画を取得します。

## 必要要件

- Python 3.7以上
- YouTube Data API v3のAPIキー

## APIキーの取得方法

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成またはプロジェクトを選択
3. YouTube Data API v3を有効化
4. 認証情報でAPIキーを作成

## エラーハンドリング

ライブラリは`YouTubeAPIError`例外を発生させます：

```python
from youtube_py2 import YouTubeAPI, YouTubeAPIError

try:
    yt = YouTubeAPI("invalid_key")
    channel = yt.get_channel_info("invalid_id")
except YouTubeAPIError as e:
    print(f"エラー: {e}")
```

## セキュリティに関する注意

- **APIキーは絶対にコードに直接書かないでください**
- `.env`ファイルはGitリポジトリにコミットしないでください
- APIキーは定期的に再生成することを推奨します
- 本番環境では適切な権限管理を行ってください

## ライセンス

MIT License
