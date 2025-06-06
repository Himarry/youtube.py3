# youtube.py3

[![PyPI version](https://badge.fury.io/py/youtube-py3.svg)](https://badge.fury.io/py/youtube-py3)
[![Python versions](https://img.shields.io/pypi/pyversions/youtube-py3.svg)](https://pypi.org/project/youtube-py3/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[🇺🇸 English](README_en.md) | 🇯🇵 日本語

YouTube Data API v3を簡単に使用するためのPythonラッパーライブラリです。

## 🚀 クイックスタート

### インストール

```bash
pip install youtube-py3
```

### 基本的な使用例

```python
import os
from youtube_py3 import YouTubeAPI

# 環境変数からAPIキーを取得
api_key = os.getenv('YOUTUBE_API_KEY')
yt = YouTubeAPI(api_key)

# チャンネル情報を取得
channel = yt.get_channel_info("UC_x5XG1OV2P6uZZ5FSM9Ttw")
print(f"チャンネル名: {channel['snippet']['title']}")

# 動画を検索
videos = yt.search_videos("Python プログラミング", max_results=5)
for video in videos:
    print(f"- {video['snippet']['title']}")
```

## 📚 ドキュメント

詳細なドキュメントは[docs/](docs/)フォルダをご覧ください：

- [インストールガイド](docs/installation.md)
- [APIリファレンス](docs/api_reference.md)
- [使用例集](docs/examples/)
- [トラブルシューティング](docs/troubleshooting.md)

## ⚠️ 重要な注意事項

### APIキーについて
- **このライブラリ自体にAPIキーは含まれていません**
- 各ユーザーが個別にGoogle Cloud ConsoleでAPIキーを取得する必要があります
- APIキーの使用量制限やセキュリティは各ユーザーが管理します

### APIキーの取得方法
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成
3. YouTube Data API v3を有効化
4. 認証情報からAPIキーを作成

#
**注意**: このライブラリはYouTube Data API v3の非公式ラッパーです。Google/YouTubeとは関係ありません。
