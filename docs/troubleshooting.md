# トラブルシューティングガイド

YouTube.py2の使用中に発生する可能性のある問題と、その解決方法を詳しく説明します。

## 📋 目次

- [インストール関連の問題](#インストール関連の問題)
- [APIキー関連の問題](#apiキー関連の問題)
- [認証・権限関連の問題](#認証権限関連の問題)
- [API制限・クォータ関連の問題](#api制限クォータ関連の問題)
- [ネットワーク関連の問題](#ネットワーク関連の問題)
- [データ取得関連の問題](#データ取得関連の問題)
- [パフォーマンス関連の問題](#パフォーマンス関連の問題)
- [プラットフォーム固有の問題](#プラットフォーム固有の問題)
- [デバッグとログ](#デバッグとログ)
- [よくあるエラーメッセージ](#よくあるエラーメッセージ)

---

## インストール関連の問題

### 1. `ModuleNotFoundError: No module named 'youtube_py2'`

**症状:**
```
ModuleNotFoundError: No module named 'youtube_py2'
```

**原因:**
- ライブラリがインストールされていない
- 仮想環境が有効になっていない
- 間違ったPython環境を使用している

**解決方法:**

#### A. ライブラリをインストール
```bash
pip install youtube-py2
```

#### B. 仮想環境の確認
```bash
# 仮想環境をアクティベート（Windows）
venv\Scripts\activate

# 仮想環境をアクティベート（macOS/Linux）
source venv/bin/activate

# インストール済みパッケージを確認
pip list | grep youtube
```

#### C. Python環境の確認
```bash
# 使用中のPythonを確認
which python
python --version

# インストール場所を確認
pip show youtube-py2
```

### 2. 依存関係のエラー

**症状:**
```
ERROR: Could not install packages due to an EnvironmentError
```

**原因:**
- Google APIライブラリとの依存関係の競合
- 古いバージョンのpipやsetuptools

**解決方法:**

#### A. pip とsetuptoolsを更新
```bash
pip install --upgrade pip setuptools wheel
```

#### B. 依存関係を明示的にインストール
```bash
pip install --upgrade google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
pip install youtube-py2
```

#### C. 仮想環境を新規作成
```bash
# 新しい仮想環境を作成
python -m venv fresh_venv
cd fresh_venv

# Windows
Scripts\activate

# macOS/Linux
source bin/activate

# クリーンインストール
pip install youtube-py2
```

### 3. 権限エラー

**症状:**
```
PermissionError: [Errno 13] Permission denied
```

**原因:**
- システム領域への書き込み権限がない
- 管理者権限が必要

**解決方法:**

#### A. ユーザー領域にインストール
```bash
pip install --user youtube-py2
```

#### B. 仮想環境を使用
```bash
python -m venv youtube_env
# 仮想環境をアクティベートしてからインストール
```

#### C. 管理者権限でインストール（非推奨）
```bash
# Windows（管理者として実行）
pip install youtube-py2

# macOS/Linux
sudo pip install youtube-py2
```

---

## APIキー関連の問題

### 1. `YouTubeAPIError: APIキーが必要です`

**症状:**
```python
YouTubeAPIError: APIキーが必要です。Google Cloud Consoleで個別に取得してください。
```

**原因:**
- APIキーが設定されていない
- 空の文字列が渡されている
- None値が渡されている

**解決方法:**

#### A. 環境変数の設定確認
```python
import os

# 環境変数の確認
api_key = os.getenv('YOUTUBE_API_KEY')
print(f"APIキー: {api_key[:10]}..." if api_key else "設定されていません")
```

#### B. APIキーの取得手順
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. プロジェクトを作成または選択
3. YouTube Data API v3を有効化
4. 認証情報からAPIキーを作成

#### C. 正しい設定方法
```python
# ❌ 間違った例
yt = YouTubeAPI("")
yt = YouTubeAPI(None)

# ✅ 正しい例
import os
api_key = os.getenv('YOUTUBE_API_KEY')
if not api_key:
    raise ValueError("YOUTUBE_API_KEY環境変数を設定してください")
yt = YouTubeAPI(api_key)
```

### 2. `HttpError 400: Bad Request`

**症状:**
```
HttpError 400: Bad Request. The request contains an invalid argument.
```

**原因:**
- 無効なAPIキー
- APIキーの形式が間違っている
- APIキーに文字化けや余分な文字が含まれている

**解決方法:**

#### A. APIキーの検証
```python
import re

def validate_api_key(api_key):
    """APIキーの形式を検証"""
    if not api_key:
        return False, "APIキーが空です"
    
    # Google APIキーの一般的な形式をチェック
    if not re.match(r'^[A-Za-z0-9_-]{39}$', api_key):
        return False, "APIキーの形式が正しくありません"
    
    return True, "形式は正しいです"

# 使用例
api_key = os.getenv('YOUTUBE_API_KEY')
is_valid, message = validate_api_key(api_key)
print(f"APIキー検証: {message}")
```

#### B. APIキーのテスト
```python
from youtube_py2 import YouTubeAPI, YouTubeAPIError

def test_api_key(api_key):
    """APIキーの有効性をテスト"""
    try:
        yt = YouTubeAPI(api_key)
        result = yt.check_quota_usage()
        print("✅ APIキーは有効です")
        return True
    except YouTubeAPIError as e:
        print(f"❌ APIキーエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False

# 使用例
api_key = os.getenv('YOUTUBE_API_KEY')
test_api_key(api_key)
```

### 3. APIキーの制限設定の問題

**症状:**
```
HttpError 403: Forbidden. The request is missing a valid API key.
```

**原因:**
- APIキーに不適切な制限がかかっている
- IPアドレス制限に引っかかっている
- HTTPリファラー制限に引っかかっている

**解決方法:**

#### A. Google Cloud Consoleで制限を確認
1. Google Cloud Console → APIとサービス → 認証情報
2. 該当のAPIキーを選択
3. 「アプリケーションの制限」を確認
4. 必要に応じて制限を緩和または調整

#### B. 制限の種類と適用例
```python
# 開発環境での設定例

# 1. 制限なし（開発・テスト用のみ）
# - アプリケーションの制限: なし
# ⚠️ 本番環境では使用しない

# 2. IPアドレス制限（サーバーアプリケーション用）
# - アプリケーションの制限: IPアドレス（Webサーバー、cronジョブなど）
# - 許可するIPアドレス: サーバーの固定IP

# 3. HTTPリファラー制限（Webアプリケーション用）
# - アプリケーションの制限: HTTPリファラー（Webサイト）
# - Webサイトの制限: https://yourdomain.com/*
```

---

## 認証・権限関連の問題

### 1. `HttpError 403: Forbidden`

**症状:**
```
HttpError 403: The request cannot be completed because you have exceeded your quota.
```

**原因:**
- APIキーの権限不足
- YouTube Data API v3が有効化されていない
- プロジェクトの設定問題

**解決方法:**

#### A. API有効化の確認
```python
def check_api_status():
    """API有効化状態を確認"""
    try:
        yt = YouTubeAPI(os.getenv('YOUTUBE_API_KEY'))
        # 軽量なAPIコールでテスト
        categories = yt.get_video_categories()
        print("✅ YouTube Data API v3は有効です")
        return True
    except YouTubeAPIError as e:
        if "quota" in str(e).lower():
            print("⚠️ APIは有効ですがクォータ制限に達しています")
        else:
            print(f"❌ API有効化の問題: {e}")
        return False

check_api_status()
```

#### B. プロジェクト設定の確認手順
1. Google Cloud Console → プロジェクトを選択
2. APIとサービス → ライブラリ
3. "YouTube Data API v3"を検索
4. ステータスが「有効」になっているか確認

### 2. 認証スコープの問題

**症状:**
```
HttpError 403: Insufficient Permission
```

**原因:**
- 読み取り専用操作と書き込み操作の混同
- OAuth認証が必要な操作にAPIキーを使用

**解決方法:**

#### A. 操作の分類理解
```python
# ✅ APIキーで可能な操作（読み取り専用）
yt = YouTubeAPI(api_key)
videos = yt.search_videos("Python")          # 検索
channel = yt.get_channel_info("channel_id")  # チャンネル情報取得
comments = yt.get_comments("video_id")       # コメント取得

# ❌ OAuth認証が必要な操作（書き込み・個人データ）
# yt.upload_video(...)           # 動画アップロード
# yt.post_comment_thread(...)    # コメント投稿
# yt.subscribe_to_channel(...)   # チャンネル登録
```

#### B. OAuth認証が必要な場合
```python
# OAuth認証のセットアップが必要
# ※ 現在のバージョンではAPIキーのみサポート
print("注意: 書き込み操作にはOAuth認証が必要です")
print("現在のライブラリはAPIキーベースの読み取り操作のみサポートしています")
```

---

## API制限・クォータ関連の問題

### 1. クォータ制限エラー

**症状:**
```
HttpError 403: The request cannot be completed because you have exceeded your quota.
```

**原因:**
- 1日のAPI使用量制限（10,000クォータ単位）に達した
- 短時間での大量リクエスト

**解決方法:**

#### A. クォータ使用量の確認
```python
def estimate_quota_usage():
    """主要操作のクォータコスト"""
    quota_costs = {
        'search': 100,           # 検索操作
        'videos': 1,             # 動画情報取得
        'channels': 1,           # チャンネル情報取得
        'playlistItems': 1,      # プレイリストアイテム
        'commentThreads': 1,     # コメント取得
        'playlists': 1,          # プレイリスト情報
    }
    
    print("主要操作のクォータコスト:")
    for operation, cost in quota_costs.items():
        print(f"  {operation}: {cost}クォータ単位")
    
    print(f"\n1日の無料制限: 10,000クォータ単位")
    return quota_costs

estimate_quota_usage()
```

#### B. クォータ効率化のテクニック
```python
class QuotaOptimizedYouTubeAPI:
    """クォータを効率的に使用するラッパー"""
    
    def __init__(self, api_key):
        self.yt = YouTubeAPI(api_key)
        self.request_count = 0
        self.quota_used = 0
    
    def search_videos_efficient(self, query, max_results=50):
        """効率的な動画検索"""
        # 大量検索の場合は分割して実行
        results = []
        remaining = max_results
        
        while remaining > 0:
            batch_size = min(50, remaining)  # APIの最大制限
            try:
                batch_results = self.yt.search_videos(
                    query, max_results=batch_size
                )
                results.extend(batch_results)
                remaining -= len(batch_results)
                self.quota_used += 100  # 検索は100クォータ
                
                if len(batch_results) < batch_size:
                    break  # これ以上結果がない
                    
            except YouTubeAPIError as e:
                if "quota" in str(e).lower():
                    print(f"クォータ制限に達しました。{len(results)}件取得済み")
                    break
                raise
        
        return results
    
    def get_quota_status(self):
        """クォータ使用状況を表示"""
        print(f"推定クォータ使用量: {self.quota_used}")
        print(f"残りクォータ: {10000 - self.quota_used}")

# 使用例
optimized_yt = QuotaOptimizedYouTubeAPI(api_key)
videos = optimized_yt.search_videos_efficient("Python", max_results=200)
optimized_yt.get_quota_status()
```

#### C. 制限回避の戦略
```python
import time
from datetime import datetime, timedelta

class RateLimitedAPI:
    """レート制限を考慮したAPIラッパー"""
    
    def __init__(self, api_key, max_requests_per_minute=60):
        self.yt = YouTubeAPI(api_key)
        self.max_requests_per_minute = max_requests_per_minute
        self.request_times = []
    
    def _wait_if_needed(self):
        """必要に応じて待機"""
        now = datetime.now()
        
        # 1分以内のリクエストをフィルタ
        recent_requests = [
            req_time for req_time in self.request_times
            if now - req_time < timedelta(minutes=1)
        ]
        
        if len(recent_requests) >= self.max_requests_per_minute:
            sleep_time = 60 - (now - recent_requests[0]).seconds
            print(f"レート制限のため{sleep_time}秒待機します...")
            time.sleep(sleep_time)
    
    def safe_api_call(self, method, *args, **kwargs):
        """安全なAPI呼び出し"""
        self._wait_if_needed()
        
        try:
            result = method(*args, **kwargs)
            self.request_times.append(datetime.now())
            return result
        except YouTubeAPIError as e:
            if "quota" in str(e).lower():
                print("クォータ制限に達しました")
                raise
            elif "rate" in str(e).lower():
                print("レート制限に達しました。しばらく待機します...")
                time.sleep(60)
                return self.safe_api_call(method, *args, **kwargs)
            else:
                raise

# 使用例
safe_yt = RateLimitedAPI(api_key)
video = safe_yt.safe_api_call(safe_yt.yt.get_video_info, "dQw4w9WgXcQ")
```

### 2. レート制限エラー

**症状:**
```
HttpError 429: Too Many Requests
```

**原因:**
- 短時間での過度なAPIリクエスト
- 同時並行リクエストの過多

**解決方法:**

#### A. 指数バックオフの実装
```python
import time
import random

def exponential_backoff(max_retries=5):
    """指数バックオフデコレータ"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except YouTubeAPIError as e:
                    if "rate" in str(e).lower() or "429" in str(e):
                        if attempt < max_retries - 1:
                            wait_time = (2 ** attempt) + random.uniform(0, 1)
                            print(f"レート制限。{wait_time:.2f}秒後にリトライ...")
                            time.sleep(wait_time)
                        else:
                            print("最大リトライ回数に達しました")
                            raise
                    else:
                        raise
            return None
        return wrapper
    return decorator

# 使用例
@exponential_backoff(max_retries=3)
def get_video_with_retry(yt, video_id):
    return yt.get_video_info(video_id)
```

---

## ネットワーク関連の問題

### 1. 接続タイムアウト

**症状:**
```
TimeoutError: The request timed out
requests.exceptions.ConnectTimeout
```

**原因:**
- ネットワーク接続の問題
- プロキシ設定の問題
- DNSの問題

**解決方法:**

#### A. ネットワーク接続の確認
```python
import requests
import socket

def check_network_connectivity():
    """ネットワーク接続を確認"""
    tests = [
        ("Google DNS", "8.8.8.8", 53),
        ("YouTube API", "www.googleapis.com", 443),
    ]
    
    for name, host, port in tests:
        try:
            socket.setdefaulttimeout(5)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            print(f"✅ {name}: 接続OK")
        except Exception as e:
            print(f"❌ {name}: 接続失敗 - {e}")

check_network_connectivity()
```

#### B. プロキシ設定
```python
import os

# プロキシ設定の確認
def check_proxy_settings():
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    
    print("プロキシ設定:")
    for var in proxy_vars:
        value = os.getenv(var)
        if value:
            print(f"  {var}: {value}")
        else:
            print(f"  {var}: 未設定")

check_proxy_settings()

# プロキシ使用時の設定例
os.environ['HTTPS_PROXY'] = 'http://proxy.company.com:8080'
```

### 2. SSL証明書エラー

**症状:**
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**原因:**
- 古いCA証明書
- 企業ファイアウォールの影響
- システム時刻の問題

**解決方法:**

#### A. システム時刻の確認
```python
from datetime import datetime
import time

def check_system_time():
    """システム時刻を確認"""
    local_time = datetime.now()
    print(f"ローカル時刻: {local_time}")
    
    # NTPサーバーとの比較（簡易版）
    try:
        import ntplib
        ntp_client = ntplib.NTPClient()
        response = ntp_client.request('pool.ntp.org')
        ntp_time = datetime.fromtimestamp(response.tx_time)
        time_diff = abs((local_time - ntp_time).total_seconds())
        
        if time_diff > 300:  # 5分以上の差
            print(f"⚠️ 時刻のずれ: {time_diff:.1f}秒")
        else:
            print("✅ 時刻は正確です")
    except Exception as e:
        print(f"NTP確認失敗: {e}")

check_system_time()
```

#### B. CA証明書の更新
```bash
# macOS
brew install ca-certificates

# Ubuntu/Debian
sudo apt-get update && sudo apt-get install ca-certificates

# Windows
# Windows Updateを実行するか、証明書ストアを手動更新
```

---

## データ取得関連の問題

### 1. 空の結果が返される

**症状:**
```python
results = yt.search_videos("test")
print(len(results))  # 0
```

**原因:**
- 検索キーワードが適切でない
- 地域制限
- プライバシー設定

**解決方法:**

#### A. 検索パラメータの調整
```python
def robust_search(yt, query, max_attempts=3):
    """堅牢な検索機能"""
    
    # 検索戦略を段階的に緩和
    strategies = [
        {"order": "relevance", "regionCode": "JP"},
        {"order": "viewCount", "regionCode": "US"},
        {"order": "date", "regionCode": None},
    ]
    
    for i, strategy in enumerate(strategies):
        try:
            print(f"検索戦略 {i+1}: {strategy}")
            
            # regionCodeがNoneの場合は除外
            params = {"query": query, "max_results": 10}
            if strategy["regionCode"]:
                # 注意: regionCodeパラメータは実際のAPIには存在しない
                # これは検索結果の地域性を説明するための例です
                pass
            
            results = yt.search_videos(query, max_results=10, order=strategy["order"])
            
            if results:
                print(f"✅ {len(results)}件の結果を取得")
                return results
            else:
                print("❌ 結果なし")
                
        except Exception as e:
            print(f"❌ エラー: {e}")
    
    print("すべての検索戦略が失敗しました")
    return []

# 使用例
results = robust_search(yt, "非常に具体的な検索クエリ")
```

#### B. データ存在チェック
```python
def safe_get_video_info(yt, video_id):
    """安全な動画情報取得"""
    try:
        video = yt.get_video_info(video_id)
        
        # データの完全性をチェック
        required_fields = ['snippet', 'statistics']
        missing_fields = [field for field in required_fields if field not in video]
        
        if missing_fields:
            print(f"⚠️ 不完全なデータ。欠損フィールド: {missing_fields}")
        
        return video
        
    except YouTubeAPIError as e:
        if "見つかりません" in str(e):
            print(f"動画 {video_id} は存在しません（削除済み・非公開・地域制限）")
        else:
            print(f"取得エラー: {e}")
        return None

# 使用例
video = safe_get_video_info(yt, "potentially_invalid_id")
if video:
    print(f"タイトル: {video['snippet']['title']}")
```

### 2. 不完全なデータ

**症状:**
```python
video = yt.get_video_info("video_id")
print(video['statistics']['likeCount'])  # KeyError
```

**原因:**
- プライバシー設定により一部データが非公開
- 古い動画でサポートされていない統計
- 地域制限

**解決方法:**

#### A. 安全なデータアクセス
```python
def safe_get_value(data, keys, default="N/A"):
    """安全なネストデータアクセス"""
    try:
        for key in keys:
            data = data[key]
        return data
    except (KeyError, TypeError):
        return default

# 使用例
video = yt.get_video_info("video_id")

title = safe_get_value(video, ['snippet', 'title'], "タイトル不明")
view_count = safe_get_value(video, ['statistics', 'viewCount'], "0")
like_count = safe_get_value(video, ['statistics', 'likeCount'], "非公開")

print(f"タイトル: {title}")
print(f"再生回数: {view_count}")
print(f"いいね数: {like_count}")
```

#### B. データ検証ユーティリティ
```python
class YouTubeDataValidator:
    """YouTube データの検証クラス"""
    
    @staticmethod
    def validate_video_data(video_data):
        """動画データの完全性を検証"""
        issues = []
        
        # 必須フィールドのチェック
        if 'snippet' not in video_data:
            issues.append("snippet フィールドがありません")
        else:
            snippet = video_data['snippet']
            required_snippet_fields = ['title', 'channelTitle', 'publishedAt']
            for field in required_snippet_fields:
                if field not in snippet:
                    issues.append(f"snippet.{field} がありません")
        
        # 統計情報のチェック
        if 'statistics' not in video_data:
            issues.append("statistics フィールドがありません")
        else:
            stats = video_data['statistics']
            if 'viewCount' not in stats:
                issues.append("再生回数が非公開です")
            if 'likeCount' not in stats:
                issues.append("いいね数が非公開です")
        
        return issues
    
    @staticmethod
    def print_data_summary(video_data):
        """データサマリーを表示"""
        issues = YouTubeDataValidator.validate_video_data(video_data)
        
        if not issues:
            print("✅ 完全なデータです")
        else:
            print("⚠️ データの問題:")
            for issue in issues:
                print(f"  - {issue}")

# 使用例
video = yt.get_video_info("video_id")
YouTubeDataValidator.print_data_summary(video)
```

---

## パフォーマンス関連の問題

### 1. 処理速度が遅い

**症状:**
- API呼び出しに時間がかかる
- 大量データ処理が遅い

**原因:**
- 非効率なAPI使用パターン
- 不要な重複リクエスト
- 適切なキャッシュ未使用

**解決方法:**

#### A. キャッシュ機能の実装
```python
import json
import hashlib
from datetime import datetime, timedelta
import os

class CachedYouTubeAPI:
    """キャッシュ機能付きYouTube API"""
    
    def __init__(self, api_key, cache_dir="youtube_cache", cache_duration_hours=24):
        self.yt = YouTubeAPI(api_key)
        self.cache_dir = cache_dir
        self.cache_duration = timedelta(hours=cache_duration_hours)
        
        # キャッシュディレクトリを作成
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, method_name, *args, **kwargs):
        """キャッシュファイルパスを生成"""
        # 引数からユニークなハッシュを生成
        cache_key = f"{method_name}_{str(args)}_{str(sorted(kwargs.items()))}"
        hash_key = hashlib.md5(cache_key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hash_key}.json")
    
    def _is_cache_valid(self, cache_path):
        """キャッシュの有効性をチェック"""
        if not os.path.exists(cache_path):
            return False
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            return datetime.now() - cached_time < self.cache_duration
        except:
            return False
    
    def _load_cache(self, cache_path):
        """キャッシュデータを読み込み"""
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        return cache_data['data']
    
    def _save_cache(self, cache_path, data):
        """キャッシュデータを保存"""
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    
    def get_video_info_cached(self, video_id):
        """キャッシュ付き動画情報取得"""
        cache_path = self._get_cache_path('get_video_info', video_id)
        
        if self._is_cache_valid(cache_path):
            print(f"キャッシュから取得: {video_id}")
            return self._load_cache(cache_path)
        
        print(f"APIから取得: {video_id}")
        data = self.yt.get_video_info(video_id)
        self._save_cache(cache_path, data)
        return data

# 使用例
cached_yt = CachedYouTubeAPI(api_key)

# 初回は時間がかかる
video1 = cached_yt.get_video_info_cached("dQw4w9WgXcQ")  # API呼び出し

# 2回目は高速
video2 = cached_yt.get_video_info_cached("dQw4w9WgXcQ")  # キャッシュから取得
```

#### B. バッチ処理の最適化
```python
def process_videos_efficiently(yt, video_ids, batch_size=50):
    """効率的な動画バッチ処理"""
    results = []
    failed_ids = []
    
    # バッチごとに処理
    for i in range(0, len(video_ids), batch_size):
        batch = video_ids[i:i + batch_size]
        print(f"処理中: {i+1}-{min(i+batch_size, len(video_ids))} / {len(video_ids)}")
        
        for video_id in batch:
            try:
                video = yt.get_video_info(video_id)
                results.append(video)
                
                # レート制限を避けるため短い待機
                time.sleep(0.1)
                
            except YouTubeAPIError as e:
                print(f"失敗: {video_id} - {e}")
                failed_ids.append(video_id)
        
        # バッチ間の待機
        if i + batch_size < len(video_ids):
            time.sleep(1)
    
    print(f"完了: 成功 {len(results)}, 失敗 {len(failed_ids)}")
    return results, failed_ids

# 使用例
video_ids = ["dQw4w9WgXcQ", "video_id_2", "video_id_3"]  # 大量のID
successful, failed = process_videos_efficiently(yt, video_ids)
```

### 2. メモリ使用量が多い

**症状:**
- 大量データ処理時のメモリ不足
- プロセスが重くなる

**解決方法:**

#### A. ジェネレータを使用した処理
```python
def get_channel_videos_generator(yt, channel_id, max_results=1000):
    """メモリ効率的なチャンネル動画取得"""
    current_count = 0
    next_page_token = None
    
    while current_count < max_results:
        try:
            # 50件ずつ取得
            batch_size = min(50, max_results - current_count)
            videos = yt.get_channel_videos(channel_id, max_results=batch_size)
            
            if not videos:
                break
            
            # 1つずつyield（メモリ効率的）
            for video in videos:
                yield video
                current_count += 1
                if current_count >= max_results:
                    break
            
            # 次のページがない場合は終了
            if len(videos) < batch_size:
                break
                
        except YouTubeAPIError as e:
            print(f"エラー: {e}")
            break

# 使用例：大量データを効率的に処理
def process_large_channel(yt, channel_id):
    video_count = 0
    total_views = 0
    
    for video in get_channel_videos_generator(yt, channel_id, max_results=10000):
        view_count = int(video.get('statistics', {}).get('viewCount', 0))
        total_views += view_count
        video_count += 1
        
        if video_count % 100 == 0:
            print(f"処理済み: {video_count}件, 平均再生回数: {total_views//video_count:,}")
    
    print(f"最終結果: {video_count}件, 総再生回数: {total_views:,}")

# 実行
process_large_channel(yt, "UC_x5XG1OV2P6uZZ5FSM9Ttw")
```

---

## プラットフォーム固有の問題

### 1. Windows固有の問題

#### 文字エンコーディング問題
```python
import sys
import locale

def fix_windows_encoding():
    """Windows でのエンコーディング問題を修正"""
    if sys.platform == "win32":
        # UTF-8を強制設定
        import os
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # コンソールエンコーディングを確認
        print(f"システムエンコーディング: {locale.getpreferredencoding()}")
        print(f"標準出力エンコーディング: {sys.stdout.encoding}")

fix_windows_encoding()
```

#### パス区切り文字の問題
```python
import os

def safe_file_path(*parts):
    """安全なファイルパス生成"""
    return os.path.join(*parts)

# 使用例
cache_file = safe_file_path("youtube_cache", "video_data.json")
```

### 2. macOS固有の問題

#### SSL証明書の問題
```bash
# Python 3.6+でSSL証明書をインストール
/Applications/Python\ 3.x/Install\ Certificates.command
```

#### Homebrewとの競合
```python
import sys

def check_python_environment():
    """Python環境を確認"""
    print(f"Python実行パス: {sys.executable}")
    print(f"Pythonバージョン: {sys.version}")
    
    # Homebrewかどうかチェック
    if "/usr/local" in sys.executable or "/opt/homebrew" in sys.executable:
        print("Homebrew Python を使用中")
    elif "/usr/bin" in sys.executable:
        print("システム Python を使用中")
    else:
        print("カスタム Python を使用中")

check_python_environment()
```

### 3. Linux固有の問題

#### 依存関係の問題
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-dev python3-pip

# CentOS/RHEL
sudo yum install python3-devel python3-pip

# Alpine Linux
apk add python3-dev py3-pip gcc musl-dev
```

---

## デバッグとログ

### 1. デバッグモードの有効化

```python
import logging

def setup_debug_logging():
    """デバッグログを設定"""
    # ルートロガーの設定
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('youtube_py2_debug.log', encoding='utf-8')
        ]
    )
    
    # YouTube.py2特有のログ
    youtube_logger = logging.getLogger('youtube_py2')
    youtube_logger.setLevel(logging.DEBUG)
    
    # Google APIクライアントのログ
    googleapi_logger = logging.getLogger('googleapiclient.discovery')
    googleapi_logger.setLevel(logging.WARNING)  # 詳細すぎるので警告以上のみ

setup_debug_logging()

# HTTPリクエストの詳細ログ
import http.client as http_client
http_client.HTTPConnection.debuglevel = 1
```

### 2. カスタムロガーの作成

```python
class YouTubeDebugger:
    """YouTube API デバッガークラス"""
    
    def __init__(self, api_key):
        self.yt = YouTubeAPI(api_key)
        self.logger = logging.getLogger(__name__)
        self.request_history = []
    
    def log_request(self, method_name, args, kwargs, result=None, error=None):
        """リクエストログを記録"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'method': method_name,
            'args': str(args),
            'kwargs': str(kwargs),
            'success': error is None,
            'error': str(error) if error else None,
            'result_size': len(str(result)) if result else 0
        }
        self.request_history.append(log_entry)
        
        if error:
            self.logger.error(f"{method_name} failed: {error}")
        else:
            self.logger.info(f"{method_name} succeeded")
    
    def get_video_info_debug(self, video_id):
        """デバッグ付き動画情報取得"""
        try:
            self.logger.debug(f"動画情報取得開始: {video_id}")
            result = self.yt.get_video_info(video_id)
            self.log_request('get_video_info', (video_id,), {}, result)
            return result
        except Exception as e:
            self.log_request('get_video_info', (video_id,), {}, error=e)
            raise
    
    def print_debug_summary(self):
        """デバッグサマリーを表示"""
        total_requests = len(self.request_history)
        successful_requests = sum(1 for req in self.request_history if req['success'])
        
        print(f"\n=== デバッグサマリー ===")
        print(f"総リクエスト数: {total_requests}")
        print(f"成功: {successful_requests}")
        print(f"失敗: {total_requests - successful_requests}")
        
        # 失敗したリクエストの詳細
        failed_requests = [req for req in self.request_history if not req['success']]
        if failed_requests:
            print(f"\n失敗したリクエスト:")
            for req in failed_requests:
                print(f"  {req['method']}: {req['error']}")

# 使用例
debugger = YouTubeDebugger(api_key)
video = debugger.get_video_info_debug("dQw4w9WgXcQ")
debugger.print_debug_summary()
```

---

## よくあるエラーメッセージ

### 1. API関連エラー

| エラーメッセージ | 原因 | 解決方法 |
|---|---|---|
| `HttpError 400: Bad Request` | 無効なパラメータ | パラメータの形式を確認 |
| `HttpError 403: Forbidden` | 権限不足またはクォータ超過 | APIキー・クォータ確認 |
| `HttpError 404: Not Found` | リソースが存在しない | ID の正確性を確認 |
| `HttpError 429: Too Many Requests` | レート制限 | 待機時間を設ける |

### 2. ネットワーク関連エラー

| エラーメッセージ | 原因 | 解決方法 |
|---|---|---|
| `ConnectionError` | ネットワーク接続問題 | 接続状況を確認 |
| `SSLError` | SSL証明書問題 | 証明書・時刻を確認 |
| `TimeoutError` | リクエストタイムアウト | タイムアウト値を調整 |

### 3. データ関連エラー

| エラーメッセージ | 原因 | 解決方法 |
|---|---|---|
| `KeyError` | データ構造の想定違い | safe_get関数を使用 |
| `UnicodeDecodeError` | 文字エンコーディング問題 | UTF-8設定を確認 |
| `JSONDecodeError` | 不正なJSON | レスポンスの妥当性確認 |

### 4. トラブルシューティングチェックリスト

#### 基本チェック
- [ ] APIキーが正しく設定されている
- [ ] YouTube Data API v3が有効化されている
- [ ] ネットワーク接続が正常
- [ ] Python環境が適切

#### 詳細チェック
- [ ] クォータ使用量が制限内
- [ ] システム時刻が正確
- [ ] 必要な権限が設定されている
- [ ] プロキシ設定が適切

#### デバッグ手順
1. ログレベルをDEBUGに設定
2. 最小限のコードでテスト
3. エラーメッセージを詳しく確認
4. Google Cloud Consoleでログ確認

---

## サポートとヘルプ

### 技術サポート
- **GitHub Issues**: [プロジェクトページ](https://github.com/yourusername/youtube-py2/issues)
- **Discord**: [コミュニティサーバー](https://discord.gg/youtube-py2)
- **Email**: support@youtube-py2.com

### 関連リソース
- [YouTube Data API v3 公式ドキュメント](https://developers.google.com/youtube/v3)
- [Google Cloud Console](https://console.cloud.google.com/)
- [API使用量確認](https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas)

---

**最終更新**: 2024年12月
**関連ドキュメント**: [README](README.md) | [インストールガイド](installation.md) | [APIリファレンス](api_reference.md)
