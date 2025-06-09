class YouTubeAPIError(Exception):
    """YouTube Data API v3用の基本例外クラス"""
    def __init__(self, message=None, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

class YouTubeAuthError(YouTubeAPIError):
    """認証・認可エラー"""
    def __init__(self, message=None, status_code=None, response=None):
        super().__init__(message, status_code, response)

class YouTubeQuotaExceededError(YouTubeAPIError):
    """APIクォータ超過時の例外"""
    def __init__(self, message=None, status_code=None, response=None):
        super().__init__(message, status_code, response)

class YouTubeNotFoundError(YouTubeAPIError):
    """リソースが見つからない場合の例外"""
    def __init__(self, message=None, status_code=None, response=None):
        super().__init__(message, status_code, response)

class YouTubeInvalidRequestError(YouTubeAPIError):
    """リクエストが不正な場合の例外"""
    def __init__(self, message=None, status_code=None, response=None):
        super().__init__(message, status_code, response)

class YouTubeRateLimitError(YouTubeAPIError):
    """レートリミット超過時の例外"""
    def __init__(self, message=None, status_code=None, response=None):
        super().__init__(message, status_code, response)

# 機能別例外
class YouTubeCommentError(YouTubeAPIError):
    """コメント取得・投稿時の例外"""
    def __init__(self, message=None, status_code=None, response=None):
        super().__init__(message, status_code, response)

class YouTubeVideoError(YouTubeAPIError):
    """動画取得・操作時の例外"""
    def __init__(self, message=None, status_code=None, response=None):
        super().__init__(message, status_code, response)

class YouTubeChannelError(YouTubeAPIError):
    """チャンネル取得・操作時の例外"""
    def __init__(self, message=None, status_code=None, response=None):
        super().__init__(message, status_code, response)

class YouTubePlaylistError(YouTubeAPIError):
    """プレイリスト取得・操作時の例外"""
    def __init__(self, message=None, status_code=None, response=None):
        super().__init__(message, status_code, response)

class YouTubeSearchError(YouTubeAPIError):
    """検索時の例外"""
    def __init__(self, message=None, status_code=None, response=None):
        super().__init__(message, status_code, response)
