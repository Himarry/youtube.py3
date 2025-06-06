"""
YouTube.py3 - YouTube Data API v3 Wrapper Library

YouTube Data API v3を簡単に使用するためのPythonラッパーライブラリです。
"""

__version__ = "1.0.8"
__author__ = "Chihalu"
__email__ = "yanase.ui.prv@gmail.com"
__license__ = "MIT"

from .youtube_py3 import YouTubeAPI, YouTubeAPIError

__all__ = ["YouTubeAPI", "YouTubeAPIError"]
