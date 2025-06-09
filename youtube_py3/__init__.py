"""
YouTube.py3 - YouTube Data API v3 Python Wrapper Library
"""

from typing import Optional, Dict, Any, Union
from pathlib import Path
from .base import YouTubeAPIClient
from .videos import Videos
from .channels import Channels
from .playlists import Playlists
from .search import Search
from .comments import Comments
from .config_util import ConfigUtil
from .oauth_util import OAuthUtil

# バージョン情報
__version__ = "5.0.0"
__author__ = "Himarry"
__license__ = "MIT"
__description__ = "YouTube Data API v3 Python Wrapper Library"
__url__ = "https://github.com/Himarry/youtube.py3"

# 公開API定義
__all__ = [
]

__all__.append('show_usage_examples')

class YouTube:
    def __init__(self, api_key: str):
        self.client = YouTubeAPIClient(api_key)
        self.videos = Videos(self.client)
        self.channels = Channels(self.client)
        self.playlists = Playlists(self.client)
        self.search = Search(self.client)
        self.comments = Comments(self.client)
        self.config_manager = ConfigUtil()
        self.oauth_manager = OAuthUtil()
