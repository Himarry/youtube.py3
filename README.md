※あくまでもプライベート用に作成したライブラリです。その為全てはありませんが使い方、機能を簡単にReference.mdに書いてあります※

# YouTube.py3

YouTube Data API v3 のプライベート用Pythonラッパーライブラリです。

## 特徴
- 動画・チャンネル・プレイリスト・検索・コメント取得などの基本機能
- コメント取得は視聴者のみ・返信なし・ページネーション等のフィルタ対応
- APIキーのみで利用可能

## インストール
```
pip install -r requirements.txt
```

## 使い方
詳しい使い方・機能は `Reference.md` を参照してください。

```python
from youtube_py3 import YouTube

yt = YouTube(api_key="YOUR_API_KEY")
info = yt.videos.get_video("動画ID")
for c in yt.comments.get_viewer_comments_paginated("動画ID", "チャンネルID"):
    print(c)
```

## 注意
- Google Cloud ConsoleでAPIキーを取得してください
- 利用制限・Quotaに注意

## ライセンス
MIT

