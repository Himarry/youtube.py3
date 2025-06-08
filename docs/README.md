# YouTube.py3 完全ドキュメント

YouTube.py3は、YouTube Data API v3を簡単に使用するためのPythonラッパーライブラリです。複雑なAPIの詳細を隠蔽し、初心者でも使いやすいインターフェースを提供します。

## 📚 ドキュメント一覧

- [**インストールガイド**](installation.md) - ライブラリのインストール方法
- [**クイックスタート**](quickstart.md) - 最初の一歩
- [**APIリファレンス**](api_reference.md) - 全メソッドの詳細説明
- [**使用例集**](examples/) - 実践的な使用例
- [**チュートリアル**](tutorials/) - ステップバイステップガイド
- [**トラブルシューティング**](troubleshooting.md) - よくある問題と解決方法
- [**開発者ガイド**](developer_guide.md) - 開発に参加したい方向け
- [**FAQ**](faq.md) - よくある質問

## 🎯 主な特徴

### 1. 初心者にやさしい設計
- 複雑なパラメータ設定を簡素化
- 分かりやすい日本語メソッド名
- 詳細なエラーメッセージ

### 2. 豊富な機能
- 動画情報の取得
- チャンネル情報の取得
- プレイリスト管理
- コメント管理
- 検索機能
- ライブストリーミング対応

### 3. 自動化された処理
- ページネーション処理の自動化
- エラーハンドリングの統一
- API制限の考慮

## 🚀 クイックスタート

### 1. APIキーの取得

**重要**: このライブラリを使用するには、各ユーザーが個別にYouTube Data API v3のAPIキーを取得する必要があります。

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成（または既存プロジェクトを選択）
3. YouTube Data API v3を有効化
4. 認証情報ページでAPIキーを作成
5. 必要に応じてAPIキーに制限を設定（推奨）

### 2. インストール

```bash
pip install youtube-py3
```

### 3. 基本的な使用例

```python
import os
from youtube_py3 import YouTubeAPI

# 環境変数からAPIキーを取得（推奨）
api_key = os.getenv('YOUTUBE_API_KEY')
yt = YouTubeAPI(api_key)

# チャンネル情報を取得
channel = yt.get_channel_info("UC_x5XG1OV2P6uZZ5FSM9Ttw")
print(f"チャンネル名: {channel['snippet']['title']}")
print(f"登録者数: {channel['statistics']['subscriberCount']}")

# 動画を検索
videos = yt.search_videos("Python プログラミング", max_results=5)
for video in videos:
    print(f"- {video['snippet']['title']}")
```

## 📖 ドキュメント詳細

### [インストールガイド](installation.md)
- システム要件
- インストール方法
- 依存関係の説明
- APIキー設定方法

### [APIリファレンス](api_reference.md)
全88個のメソッドの完全な説明：

**基本機能**
- `get_channel_info()` - チャンネル情報取得
- `get_video_info()` - 動画情報取得
- `search_videos()` - 動画検索
- `get_comments()` - コメント取得

**プレイリスト管理**
- `get_playlist_videos()` - プレイリスト動画取得
- `create_playlist()` - プレイリスト作成
- `add_video_to_playlist()` - プレイリストに動画追加

**コメント管理**
- `post_comment_thread()` - コメント投稿
- `post_comment_reply()` - コメント返信
- `delete_comment()` - コメント削除

### [使用例集](examples/)
実際のユースケースに基づいた例：
- YouTubeチャンネルの分析
- 動画の自動分類
- コメントの感情分析
- プレイリストの管理

### [チュートリアル](tutorials/)
ステップバイステップのガイド：
- 初心者向けチュートリアル
- 中級者向けチュートリアル
- 上級者向けチュートリアル

## ⚠️ 重要な注意事項

### APIキーについて
- **このライブラリ自体にAPIキーは含まれていません**
- 各ユーザーが個別にGoogle Cloud ConsoleでAPIキーを取得する必要があります
- APIキーの使用量制限やセキュリティは各ユーザーが管理します

### セキュリティベストプラクティス
- APIキーをソースコードに直接書かないでください
- 環境変数や設定ファイルを使用してください
- APIキーに適切な制限をかけてください
- 不要になったAPIキーは削除してください

### 使用量について
- YouTube Data APIは従量課金制です
- 毎日10,000クォータ単位の無料枠があります
- 各APIコールでクォータを消費します（1-100単位程度）
- 使用量はGoogle Cloud Consoleで確認できます

## 🛠️ トラブルシューティング

よくある問題と解決方法は[トラブルシューティングガイド](troubleshooting.md)をご覧ください。

## 🤝 コントリビューション

このプロジェクトへの貢献を歓迎します。詳細は[開発者ガイド](developer_guide.md)をご覧ください。

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

**最終更新**: 2024年12月
**バージョン**: 1.0.0
