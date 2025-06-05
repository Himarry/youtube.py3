"""
YouTube.py2 Advanced Usage Examples
環境変数を使用した高度な機能のデモンストレーション
"""

import os
from youtube_py2 import YouTubeAPI, YouTubeAPIError

# 環境変数から設定を読み込み
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 設定値を環境変数から取得
API_KEY = os.getenv('YOUTUBE_API_KEY')
REGION_CODE = os.getenv('DEFAULT_REGION_CODE', 'JP')
LANGUAGE_CODE = os.getenv('DEFAULT_LANGUAGE_CODE', 'ja')

def main():
    if not API_KEY:
        print("エラー: YOUTUBE_API_KEY 環境変数が設定されていません。")
        return
    
    try:
        # YouTube API初期化
        yt = YouTubeAPI(API_KEY)
        
        print("=== YouTube.py2 高度な使用例 ===\n")
        
        # 例1: 人気動画取得（地域別）
        print(f"=== {REGION_CODE} の人気動画 ===")
        popular_videos = yt.get_popular_videos(region_code=REGION_CODE, max_results=3)
        for i, video in enumerate(popular_videos, 1):
            title = video['snippet']['title']
            views = video['statistics']['viewCount']
            print(f"{i}. {title}")
            print(f"   再生回数: {int(views):,}")
        print()
        
        # 例2: 動画カテゴリ取得
        print("=== 動画カテゴリ一覧 ===")
        categories = yt.get_video_categories(region_code=REGION_CODE)
        for category in categories[:5]:  # 最初の5つだけ表示
            print(f"- {category['snippet']['title']} (ID: {category['id']})")
        print()
        
        # 例3: チャンネル検索
        print("=== チャンネル検索: 'Python' ===")
        channels = yt.search_channels("Python", max_results=3)
        for i, channel in enumerate(channels, 1):
            title = channel['snippet']['title']
            description = channel['snippet']['description'][:100]
            print(f"{i}. {title}")
            print(f"   説明: {description}...")
        print()
        
        # 例4: プレイリスト検索と詳細取得
        print("=== プレイリスト検索: 'プログラミング' ===")
        playlists = yt.search_playlists("プログラミング", max_results=2)
        for i, playlist in enumerate(playlists, 1):
            title = playlist['snippet']['title']
            playlist_id = playlist['id']['playlistId']
            print(f"{i}. {title}")
            print(f"   プレイリストID: {playlist_id}")
            
            # プレイリストの詳細情報を取得
            try:
                playlist_info = yt.get_playlist_info(playlist_id)
                item_count = playlist_info['contentDetails']['itemCount']
                print(f"   動画数: {item_count}")
            except YouTubeAPIError as e:
                print(f"   詳細取得エラー: {e}")
        print()
        
        # 例5: サポートされている言語・地域
        print("=== システム情報 ===")
        try:
            languages = yt.get_supported_languages()
            regions = yt.get_supported_regions()
            print(f"サポート言語数: {len(languages)}")
            print(f"サポート地域数: {len(regions)}")
            
            # 日本関連の情報を探す
            jp_language = next((lang for lang in languages 
                              if lang['snippet']['hl'] == 'ja'), None)
            jp_region = next((region for region in regions 
                            if region['snippet']['gl'] == 'JP'), None)
            
            if jp_language:
                print(f"日本語表示名: {jp_language['snippet']['name']}")
            if jp_region:
                print(f"日本地域表示名: {jp_region['snippet']['name']}")
        except YouTubeAPIError as e:
            print(f"システム情報取得エラー: {e}")
        print()
        
        # 例6: 統計情報のみの効率的な取得
        print("=== 効率的な統計取得 ===")
        test_video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
        try:
            stats = yt.get_video_statistics_only(test_video_id)
            print(f"テスト動画統計:")
            print(f"  再生回数: {int(stats['viewCount']):,}")
            print(f"  いいね数: {int(stats['likeCount']):,}")
            print(f"  コメント数: {int(stats['commentCount']):,}")
        except YouTubeAPIError as e:
            print(f"統計取得エラー: {e}")
        
    except YouTubeAPIError as e:
        print(f"YouTube API エラー: {e}")
    except Exception as e:
        print(f"予期しないエラー: {e}")

if __name__ == "__main__":
    main()
