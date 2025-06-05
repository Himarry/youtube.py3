# インストールガイド

YouTube.py3のインストール方法と初期設定について詳しく説明します。

## 📋 システム要件

### 基本要件
- **Python**: 3.7以上（推奨: 3.9以上）
- **OS**: Windows, macOS, Linux
- **メモリ**: 最低512MB（推奨: 1GB以上）
- **ディスク容量**: 100MB以上の空き容量

### 必要な依存関係
- `google-api-python-client >= 2.0.0`
- `google-auth >= 2.0.0`
- `google-auth-oauthlib >= 0.5.0`
- `google-auth-httplib2 >= 0.1.0`

## 🚀 インストール方法

### 方法1: pipを使用（推奨）

最も簡単で推奨される方法です：

```bash
# 最新版をインストール
pip install youtube-py3

# 特定のバージョンをインストール
pip install youtube-py3==1.0.0

# 開発版をインストール（非推奨）
pip install youtube-py3 --pre
```

### 方法2: GitHubから直接インストール

最新の開発版を使用したい場合：

```bash
pip install git+https://github.com/yourusername/youtube-py3.git
```

### 方法3: ソースコードからインストール

開発に参加したい場合：

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/youtube-py3.git
cd youtube-py3

# 開発モードでインストール
pip install -e .

# または通常のインストール
pip install .
```

## 🔑 APIキーの取得と設定

YouTube.py3を使用するには、YouTube Data API v3のAPIキーが必要です。

### Step 1: Google Cloud Consoleでプロジェクトを作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 右上の「プロジェクトを選択」をクリック
3. 「新しいプロジェクト」をクリック
4. プロジェクト名を入力（例: "my-youtube-app"）
5. 「作成」をクリック

### Step 2: YouTube Data API v3を有効化

1. プロジェクトを選択した状態で「APIとサービス」→「ライブラリ」を選択
2. 検索バーに「YouTube Data API v3」と入力
3. 「YouTube Data API v3」を選択
4. 「有効にする」をクリック

### Step 3: APIキーを作成

1. 「APIとサービス」→「認証情報」を選択
2. 「認証情報を作成」→「APIキー」をクリック
3. APIキーが生成されます（後で制限を設定できます）

### Step 4: APIキーに制限を設定（推奨）

セキュリティのため、APIキーに制限をかけることを強く推奨します：

#### APIキーの制限方法
1. 作成したAPIキーの「編集」をクリック
2. 「アプリケーションの制限」を設定：
   - **HTTPリファラー**: Webアプリケーションの場合
   - **IPアドレス**: サーバーアプリケーションの場合
   - **Android アプリ**: Androidアプリの場合
   - **iOS アプリ**: iOSアプリの場合

3. 「API の制限」を設定：
   - 「キーを制限」を選択
   - 「YouTube Data API v3」のみを選択

## 🛠️ 環境設定

### 環境変数を使用した設定（推奨）

APIキーを安全に管理するため、環境変数を使用します：

#### Windows (PowerShell)
```powershell
# 一時的な設定
$env:YOUTUBE_API_KEY = "YOUR_API_KEY_HERE"

# 永続的な設定
[Environment]::SetEnvironmentVariable("YOUTUBE_API_KEY", "YOUR_API_KEY_HERE", "User")
```

#### Windows (コマンドプロンプト)
```cmd
# 一時的な設定
set YOUTUBE_API_KEY=YOUR_API_KEY_HERE

# 永続的な設定
setx YOUTUBE_API_KEY "YOUR_API_KEY_HERE"
```

#### macOS/Linux (Bash)
```bash
# 一時的な設定
export YOUTUBE_API_KEY="YOUR_API_KEY_HERE"

# 永続的な設定（.bashrcまたは.zshrcに追加）
echo 'export YOUTUBE_API_KEY="YOUR_API_KEY_HERE"' >> ~/.bashrc
source ~/.bashrc
```

### .envファイルを使用した設定

プロジェクトごとに設定を管理したい場合：

1. プロジェクトルートに`.env`ファイルを作成：
```
YOUTUBE_API_KEY=YOUR_API_KEY_HERE
```

2. `python-dotenv`をインストール：
```bash
pip install python-dotenv
```

3. Pythonコードで読み込み：
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('YOUTUBE_API_KEY')
```

### 設定ファイルを使用した設定

JSON形式で設定を管理する場合：

1. `config.json`ファイルを作成：
```json
{
    "youtube_api_key": "YOUR_API_KEY_HERE",
    "default_max_results": 50,
    "default_region": "JP"
}
```

2. Pythonコードで読み込み：
```python
import json

with open('config.json', 'r') as f:
    config = json.load(f)

api_key = config['youtube_api_key']
```

## ✅ インストール確認

インストールが正常に完了したかを確認します：

### 基本的な確認
```python
# ライブラリのインポートを確認
try:
    from youtube_py3 import YouTubeAPI
    print("✅ インストール成功: ライブラリを正常にインポートできました")
except ImportError as e:
    print(f"❌ インストール失敗: {e}")

# バージョン確認
try:
    import youtube_py3
    print(f"✅ バージョン: {youtube_py3.__version__}")
except AttributeError:
    print("⚠️ バージョン情報が取得できません")
```

### APIキーの確認
```python
import os
from youtube_py3 import YouTubeAPI, YouTubeAPIError

try:
    # 環境変数からAPIキーを取得
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        print("❌ APIキーが設定されていません")
    else:
        # YouTubeAPIクライアントを初期化
        yt = YouTubeAPI(api_key)
        
        # APIキーの有効性をテスト
        if yt.check_quota_usage():
            print("✅ APIキーは有効です")
        else:
            print("❌ APIキーが無効です")
            
except YouTubeAPIError as e:
    print(f"❌ API エラー: {e}")
except Exception as e:
    print(f"❌ 予期しないエラー: {e}")
```

### 完全な動作確認
```python
import os
from youtube_py3 import YouTubeAPI

def test_installation():
    """インストールの完全テスト"""
    
    print("YouTube.py2 インストール確認テスト")
    print("=" * 40)
    
    # 1. ライブラリのインポート確認
    try:
        from youtube_py3 import YouTubeAPI, YouTubeAPIError
        print("✅ 1. ライブラリインポート: 成功")
    except ImportError as e:
        print(f"❌ 1. ライブラリインポート: 失敗 - {e}")
        return False
    
    # 2. APIキー確認
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ 2. APIキー: 設定されていません")
        print("   環境変数 YOUTUBE_API_KEY を設定してください")
        return False
    else:
        print("✅ 2. APIキー: 設定済み")
    
    # 3. API接続確認
    try:
        yt = YouTubeAPI(api_key)
        print("✅ 3. API初期化: 成功")
    except YouTubeAPIError as e:
        print(f"❌ 3. API初期化: 失敗 - {e}")
        return False
    
    # 4. 簡単なAPI呼び出しテスト
    try:
        categories = yt.get_video_categories()
        print(f"✅ 4. API呼び出し: 成功 ({len(categories)}個のカテゴリを取得)")
    except YouTubeAPIError as e:
        print(f"❌ 4. API呼び出し: 失敗 - {e}")
        return False
    
    print("=" * 40)
    print("🎉 すべてのテストが成功しました！")
    print("YouTube.py2を使用する準備が整いました。")
    return True

if __name__ == "__main__":
    test_installation()
```

## 🐛 トラブルシューティング

### よくある問題

#### 1. `ModuleNotFoundError: No module named 'youtube_py3'`
**原因**: ライブラリがインストールされていない
**解決方法**: 
```bash
pip install youtube-py3
```

#### 2. `ImportError: cannot import name 'YouTubeAPI'`
**原因**: 古いバージョンまたは不完全なインストール
**解決方法**: 
```bash
pip uninstall youtube-py3
pip install youtube-py3
```

#### 3. `YouTubeAPIError: APIキーが必要です`
**原因**: APIキーが設定されていない
**解決方法**: 環境変数`YOUTUBE_API_KEY`を設定

#### 4. `HttpError 403: The request cannot be completed because you have exceeded your quota`
**原因**: API使用量制限に達している
**解決方法**: 
- Google Cloud ConsoleでAPI使用量を確認
- 翌日まで待つか、課金設定を行う

#### 5. 依存関係のエラー
**原因**: 必要なライブラリがインストールされていない
**解決方法**: 
```bash
pip install --upgrade google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
```

### デバッグモード

問題を診断するため、デバッグモードを有効にできます：

```python
import logging

# ログレベルをDEBUGに設定
logging.basicConfig(level=logging.DEBUG)

# YouTube.py2のログを有効化
logger = logging.getLogger('youtube_py2')
logger.setLevel(logging.DEBUG)
```

## 🔄 アップデート

### 最新版への更新
```bash
pip install --upgrade youtube-py3
```

### バージョン確認
```bash
pip show youtube-py3
```

### 特定バージョンへのダウングレード
```bash
pip install youtube-py3==1.0.0
```

## 📚 次のステップ

インストールが完了したら、以下のドキュメントを参照してください：

1. [**クイックスタート**](quickstart.md) - 基本的な使用方法
2. [**APIリファレンス**](api_reference.md) - 全メソッドの詳細
3. [**使用例集**](examples/) - 実践的な例
4. [**チュートリアル**](tutorials/) - ステップバイステップガイド

---

**最終更新**: 2024年12月
**関連ドキュメント**: [README](README.md) | [クイックスタート](quickstart.md) | [トラブルシューティング](troubleshooting.md)
