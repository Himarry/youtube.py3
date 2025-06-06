"""
YouTube.py2 Basic Usage Examples
"""

import os
from youtube_py2 import YouTubeAPI

# 環境変数またはdotenvファイルからAPIキーを取得
try:
    from dotenv import load_dotenv
    load_dotenv()  # .envファイルから環境変数を読み込み
except ImportError:
    # python-dotenvがインストールされていない場合はスキップ
    pass

# 環境変数からAPIキーを取得
API_KEY = os.getenv('YOUTUBE_API_KEY')

def main():
    # APIキーの確認
    if not API_KEY:
        print("エラー: YouTube API キーが設定されていません。")
        print("以下のいずれかの方法でAPIキーを設定してください：")
        print("1. 環境変数 YOUTUBE_API_KEY に設定")
        print("2. .env ファイルに YOUTUBE_API_KEY=your_api_key を記述")
        print("3. システムの環境変数に設定")
        return
    
    try:
        # Initialize YouTube API
        yt = YouTubeAPI(API_KEY)
        
        # Example 1: Get channel information
        print("=== Channel Information ===")
        channel = yt.get_channel_info("UC_x5XG1OV2P6uZZ5FSM9Ttw")  # Google Developers
        print(f"Channel: {channel['snippet']['title']}")
        print(f"Subscribers: {channel['statistics']['subscriberCount']}")
        print(f"Videos: {channel['statistics']['videoCount']}")
        print()
        
        # Example 2: Search for videos
        print("=== Video Search ===")
        videos = yt.search_videos("Python programming", max_results=3)
        for i, video in enumerate(videos, 1):
            print(f"{i}. {video['snippet']['title']}")
            print(f"   Channel: {video['snippet']['channelTitle']}")
            print(f"   Video ID: {video['id']['videoId']}")
        print()
        
        # Example 3: Get video information
        if videos:
            print("=== Video Details ===")
            video_id = videos[0]['id']['videoId']
            video_info = yt.get_video_info(video_id)
            print(f"Title: {video_info['snippet']['title']}")
            print(f"Views: {video_info['statistics']['viewCount']}")
            print(f"Likes: {video_info['statistics']['likeCount']}")
            print()
        
        # Example 4: Get comments (if available)
        if videos:
            print("=== Comments ===")
            try:
                comments = yt.get_comments(video_id, max_results=3)
                for i, comment in enumerate(comments, 1):
                    text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
                    author = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
                    print(f"{i}. {author}: {text[:100]}...")
            except Exception as e:
                print(f"Could not get comments: {e}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
