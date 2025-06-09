import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from youtube_py3 import YouTube

if __name__ == "__main__":
    # テスト用APIキー（ダミー値）
    api_key = "AIzaSyDUMMYKEY"
    yt = YouTube(api_key)
    print("YouTubeラッパーのインスタンス化成功")
    # 例: チャンネル情報取得（実際のAPIキーでのみ動作）
    # print(yt.channels.get_channel("UC_x5XG1OV2P6uZZ5FSM9Ttw"))
