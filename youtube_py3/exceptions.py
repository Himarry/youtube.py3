"""
YouTube.py3 - 例外クラス定義

YouTube Data API v3の例外処理を定義するモジュールです。
"""


class YouTubeAPIError(Exception):
    """YouTube API関連のエラー例外クラス

    YouTube APIの呼び出し時に発生するエラーをラップし、
    より詳細なエラー情報を提供します。
    """

    def __init__(self, message, error_code=None, status_code=None, details=None):
        """YouTubeAPIErrorを初期化

        Args:
            message (str): エラーメッセージ
            error_code (str): APIエラーコード（オプション）
            status_code (int): HTTPステータスコード（オプション）
            details (dict): 詳細なエラー情報（オプション）
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}

    def __str__(self):
        """エラーの文字列表現を返す"""
        error_parts = [self.message]

        if self.error_code:
            error_parts.append(f"エラーコード: {self.error_code}")

        if self.status_code:
            error_parts.append(f"ステータスコード: {self.status_code}")

        return " | ".join(error_parts)

    def __repr__(self):
        """エラーの詳細な表現を返す"""
        return (
            f"YouTubeAPIError(message='{self.message}', "
            f"error_code='{self.error_code}', "
            f"status_code={self.status_code}, "
            f"details={self.details})"
        )

    def is_quota_exceeded(self):
        """クォータ超過エラーかどうかを判定

        Returns:
            bool: クォータ超過エラーの場合True
        """
        return self.status_code == 403 and (
            self.error_code == "quotaExceeded" or "quota" in self.message.lower()
        )

    def is_api_key_invalid(self):
        """APIキー無効エラーかどうかを判定

        Returns:
            bool: APIキー無効エラーの場合True
        """
        return self.status_code == 400 and (
            "api key" in self.message.lower() or "invalid" in self.message.lower()
        )

    def is_not_found(self):
        """リソースが見つからないエラーかどうかを判定

        Returns:
            bool: リソースが見つからない場合True
        """
        return (
            self.status_code == 404
            or "not found" in self.message.lower()
            or "見つかりません" in self.message
        )

    def is_forbidden(self):
        """アクセス権限エラーかどうかを判定

        Returns:
            bool: アクセス権限エラーの場合True
        """
        return self.status_code == 403

    def get_suggested_action(self):
        """エラーに対する推奨アクションを取得

        Returns:
            str: 推奨アクション
        """
        if self.is_quota_exceeded():
            return (
                "APIクォータが上限に達しています。"
                "しばらく待ってから再試行するか、Google Cloud Consoleで使用量を確認してください。"
            )
        elif self.is_api_key_invalid():
            return (
                "APIキーが無効です。"
                "Google Cloud ConsoleでAPIキーを確認し、YouTube Data API v3が有効になっているか確認してください。"
            )
        elif self.is_not_found():
            return (
                "指定されたリソース（動画、チャンネル、プレイリストなど）が見つかりません。"
                "IDが正しいか確認してください。"
            )
        elif self.is_forbidden():
            return (
                "アクセス権限がありません。"
                "APIキーの制限設定を確認するか、認証が必要な操作の場合はOAuth認証を使用してください。"
            )
        else:
            return "エラーの詳細を確認し、APIドキュメントを参照してください。"