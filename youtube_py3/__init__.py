"""
YouTube.py3 - Binary version
"""

__version__ = "3.0.0"
__author__ = "Chihalu"

# バイナリモジュールから主要クラスをインポート
try:
    from .youtube_py3 import *
except ImportError:
    # フォールバック: 通常のPythonモジュール
    from .youtube_py3 import YouTube
    __all__ = ['YouTube']

__all__ = ['YouTube', '__version__', '__author__']
