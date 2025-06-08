"""
YouTube.py3 - 設定管理モジュール

設定ファイルの管理と検証を行うモジュールです。
"""

import json
import os
from .exceptions import YouTubeAPIError


class ConfigManager:
    """設定ファイルを管理するクラス"""
    
    @staticmethod
    def create_oauth_config_template(output_file='oauth_config.json'):
        """OAuth設定テンプレートファイルを作成
        
        Args:
            output_file (str): 出力ファイル名
        
        Returns:
            str: 作成されたファイル名
        """
        template = {
            "client_secrets_file": "client_secrets.json",
            "scopes": ["readonly"],
            "token_file": "youtube_token.pickle",
            "port": 8080,
            "auto_open_browser": True,
            "_comment": {
                "scopes": "利用可能: readonly, upload, full, force_ssl",
                "client_secrets_file": "Google Cloud Consoleでダウンロードしたファイル",
                "token_file": "認証トークンの保存先",
                "port": "ローカルサーバーのポート番号",
                "auto_open_browser": "認証時にブラウザを自動で開くか"
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        return output_file
    
    @staticmethod
    def load_oauth_config(config_file):
        """OAuth設定ファイルを読み込み
        
        Args:
            config_file (str): 設定ファイルパス
        
        Returns:
            dict: OAuth設定
        """
        if not os.path.exists(config_file):
            raise YouTubeAPIError(f"設定ファイルが見つかりません: {config_file}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 必須項目のチェック
            required_fields = ['client_secrets_file', 'scopes']
            for field in required_fields:
                if field not in config:
                    raise YouTubeAPIError(f"設定ファイルに必須項目が不足: {field}")
            
            return config
            
        except json.JSONDecodeError as e:
            raise YouTubeAPIError(f"設定ファイルの形式が正しくありません: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"設定ファイルの読み込みに失敗: {e}")
    
    @staticmethod
    def validate_config(config):
        """設定の妥当性をチェック
        
        Args:
            config (dict): OAuth設定
        
        Returns:
            bool: 設定が有効かどうか
        """
        try:
            # client_secrets_file の存在チェック
            client_secrets = config.get('client_secrets_file')
            if client_secrets and not os.path.exists(client_secrets):
                raise YouTubeAPIError(f"クライアントシークレットファイルが見つかりません: {client_secrets}")
            
            # スコープの妥当性チェック
            valid_scopes = ['readonly', 'upload', 'full', 'force_ssl']
            scopes = config.get('scopes', [])
            for scope in scopes:
                if scope not in valid_scopes and not scope.startswith('https://'):
                    raise YouTubeAPIError(f"無効なスコープ: {scope}")
            
            # ポート番号のチェック
            port = config.get('port', 8080)
            if not isinstance(port, int) or port < 1 or port > 65535:
                raise YouTubeAPIError(f"無効なポート番号: {port}")
            
            return True
            
        except YouTubeAPIError:
            raise
        except Exception as e:
            raise YouTubeAPIError(f"設定の検証でエラーが発生: {e}")