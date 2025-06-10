# YouTube.py3 Reference (簡易版)

## 機能一覧
- 動画情報取得（videos）
- チャンネル情報取得（channels）
- プレイリスト情報取得（playlists）
- 動画検索（search）
- コメント取得・フィルタ・ページネーション（comments）

## 使い方例
```python
import youtube_py3

yt = youtube_py3.YouTube(api_key="YOUR_API_KEY")
# 動画情報取得
info = yt.videos.get_video("動画ID")
# コメント（視聴者のみ・返信なし・ページネーション）
for c in yt.comments.get_viewer_comments_paginated("動画ID", "チャンネルID"):
    print(c)
```

## 注意
- APIキーが必要
- 詳細は各メソッドのdocstring参照
