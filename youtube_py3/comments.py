"""
YouTube.py3 - コメント関連機能

コメントの取得、投稿、管理、統計などの機能を提供します。
"""

from .exceptions import YouTubeAPIError
from googleapiclient.errors import HttpError


class CommentsMixin:
    """コメント関連の機能を提供するMixin"""

    def get_playlist_videos(self, playlist_id, max_results=50):
        """プレイリストの動画一覧を取得

        Args:
            playlist_id (str): YouTubeプレイリストのID
            max_results (int): 取得する最大動画数 (デフォルト: 50)

        Returns:
            list: 動画情報の辞書のリスト

        Raises:
            YouTubeAPIError: プレイリストが見つからない、またはAPI呼び出しに失敗した場合
        """
        videos = []
        next_page_token = None

        while len(videos) < max_results:
            request = self.youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token,
            )
            response = self._execute_request(request)

            videos.extend(response["items"])

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return videos[:max_results]

    def get_comments(self, video_id, max_results=100):
        """動画のコメントを取得

        Args:
            video_id (str): YouTube動画のID
            max_results (int): 取得する最大コメント数 (デフォルト: 100)

        Returns:
            list: コメント情報の辞書のリスト

        Raises:
            YouTubeAPIError: コメントが無効化されている、またはAPI呼び出しに失敗した場合
        """
        comments = []
        next_page_token = None

        while len(comments) < max_results:
            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(100, max_results - len(comments)),
                pageToken=next_page_token,
                order="time",
            )
            
            try:
                response = self._execute_request(request)
            except YouTubeAPIError as e:
                if e.status_code == 403:
                    raise YouTubeAPIError("この動画のコメントは無効化されています")
                raise

            comments.extend(response["items"])

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return comments[:max_results]

    def get_comment_details(self, comment_id):
        """コメント詳細を取得

        Args:
            comment_id (str): コメントID

        Returns:
            dict: コメント詳細情報
        """
        try:
            request = self.youtube.comments().list(part="snippet", id=comment_id)
            response = request.execute()

            if not response["items"]:
                raise YouTubeAPIError(f"コメントが見つかりません: {comment_id}")

            return response["items"][0]
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def post_comment_reply(self, parent_comment_id, text):
        """コメントに返信

        Args:
            parent_comment_id (str): 親コメントID
            text (str): 返信テキスト

        Returns:
            dict: 投稿結果
        """
        try:
            body = {"snippet": {"parentId": parent_comment_id, "textOriginal": text}}

            request = self.youtube.comments().insert(part="snippet", body=body)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def update_comment(self, comment_id, text):
        """コメントを更新

        Args:
            comment_id (str): コメントID
            text (str): 新しいテキスト

        Returns:
            dict: 更新結果
        """
        try:
            # 現在のコメント情報を取得
            current_comment = self.get_comment_details(comment_id)

            body = current_comment
            body["snippet"]["textOriginal"] = text

            request = self.youtube.comments().update(part="snippet", body=body)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def mark_comment_as_spam(self, comment_id):
        """コメントをスパムとしてマーク

        Args:
            comment_id (str): コメントID

        Returns:
            bool: 成功フラグ
        """
        try:
            request = self.youtube.comments().markAsSpam(id=comment_id)
            request.execute()
            return True
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def set_comment_moderation_status(self, comment_id, moderation_status):
        """コメントのモデレーション状態を設定

        Args:
            comment_id (str): コメントID
            moderation_status (str): モデレーション状態 ('published', 'heldForReview', 'likelySpam', 'rejected')

        Returns:
            bool: 成功フラグ
        """
        try:
            request = self.youtube.comments().setModerationStatus(
                id=comment_id, moderationStatus=moderation_status
            )
            request.execute()
            return True
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def delete_comment(self, comment_id):
        """コメントを削除

        Args:
            comment_id (str): コメントID

        Returns:
            bool: 削除成功フラグ
        """
        try:
            request = self.youtube.comments().delete(id=comment_id)
            request.execute()
            return True
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def post_comment_thread(self, video_id, text, channel_id=None):
        """新しいコメントスレッドを投稿

        Args:
            video_id (str): 動画ID（動画へのコメントの場合）
            text (str): コメントテキスト
            channel_id (str): チャンネルID（チャンネルへのコメントの場合）

        Returns:
            dict: 投稿結果
        """
        try:
            body = {"snippet": {"topLevelComment": {"snippet": {"textOriginal": text}}}}

            if video_id:
                body["snippet"]["videoId"] = video_id
            elif channel_id:
                body["snippet"]["channelId"] = channel_id
            else:
                raise YouTubeAPIError(
                    "video_id または channel_id のいずれかを指定してください"
                )

            request = self.youtube.commentThreads().insert(part="snippet", body=body)
            response = request.execute()
            return response
        except HttpError as e:
            raise YouTubeAPIError(f"API エラー: {e}")
        except Exception as e:
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def get_total_comments_excluding_channels(self, video_id, exclude_channels=None, max_comments=1000):
        """指定したチャンネルを除いた動画の総コメント数を取得"""
        if exclude_channels is None:
            exclude_channels = []
        
        try:
            # 動画のコメントを取得
            all_comments = self.get_all_comments(video_id, max_results=max_comments)
            
            if not all_comments:
                return {
                    'total_comments': 0,
                    'excluded_comments': 0,
                    'original_total': 0,
                    'exclude_channels': [],
                    'filtered_comments': []
                }
            
            # 除外チャンネルの情報を正規化
            exclude_channel_ids = set()
            exclude_channel_names = set()
            
            for channel in exclude_channels:
                if len(channel) == 24 and channel.startswith('UC'):
                    exclude_channel_ids.add(channel)
                else:
                    exclude_channel_names.add(channel.lower())
            
            # コメントをフィルタリング
            filtered_comments = []
            excluded_count = 0
            exclude_info = []
            
            for comment in all_comments:
                comment_snippet = comment['snippet']['topLevelComment']['snippet']
                author_channel_id = comment_snippet.get('authorChannelId', {}).get('value', '')
                author_name = comment_snippet.get('authorDisplayName', '')
                
                # 除外対象かチェック
                should_exclude = False
                exclude_reason = None
                
                if author_channel_id and author_channel_id in exclude_channel_ids:
                    should_exclude = True
                    exclude_reason = 'channel_id'
                elif author_name.lower() in exclude_channel_names:
                    should_exclude = True
                    exclude_reason = 'channel_name'
                
                if should_exclude:
                    excluded_count += 1
                    exclude_info.append({
                        'channel_id': author_channel_id,
                        'channel_name': author_name,
                        'reason': exclude_reason
                    })
                else:
                    filtered_comments.append(comment)
            
            # 除外されたチャンネルの統計
            excluded_channels_summary = {}
            for info in exclude_info:
                channel_key = info['channel_id'] if info['channel_id'] else info['channel_name']
                if channel_key not in excluded_channels_summary:
                    excluded_channels_summary[channel_key] = {
                        'channel_id': info['channel_id'],
                        'channel_name': info['channel_name'],
                        'excluded_count': 0
                    }
                excluded_channels_summary[channel_key]['excluded_count'] += 1
            
            return {
                'total_comments': len(filtered_comments),
                'excluded_comments': excluded_count,
                'original_total': len(all_comments),
                'exclude_channels': list(excluded_channels_summary.values()),
                'filtered_comments': filtered_comments,
                'filter_summary': {
                    'exclusion_rate': (excluded_count / len(all_comments) * 100) if all_comments else 0,
                    'most_excluded_channel': max(excluded_channels_summary.values(), 
                                               key=lambda x: x['excluded_count']) if excluded_channels_summary else None
                }
            }
            
        except YouTubeAPIError:
            raise
        except Exception as e:
            raise YouTubeAPIError(f"コメント集計処理でエラーが発生しました: {str(e)}")

    def get_comments_statistics_by_channel(self, video_id, max_comments=1000):
        """動画のコメントをチャンネル別に統計"""
        try:
            all_comments = self.get_all_comments(video_id, max_results=max_comments)
            
            if not all_comments:
                return {
                    'total_comments': 0,
                    'channel_stats': [],
                    'top_commenters': [],
                    'unique_channels': 0
                }
            
            # チャンネル別統計を集計
            channel_stats = {}
            
            for comment in all_comments:
                comment_snippet = comment['snippet']['topLevelComment']['snippet']
                author_channel_id = comment_snippet.get('authorChannelId', {}).get('value', 'unknown')
                author_name = comment_snippet.get('authorDisplayName', 'Unknown')
                
                channel_key = author_channel_id if author_channel_id != 'unknown' else author_name
                
                if channel_key not in channel_stats:
                    channel_stats[channel_key] = {
                        'channel_id': author_channel_id if author_channel_id != 'unknown' else None,
                        'channel_name': author_name,
                        'comment_count': 0,
                        'comments': []
                    }
                
                channel_stats[channel_key]['comment_count'] += 1
                channel_stats[channel_key]['comments'].append({
                    'text': comment_snippet.get('textOriginal', ''),
                    'published_at': comment_snippet.get('publishedAt', ''),
                    'like_count': comment_snippet.get('likeCount', 0)
                })
            
            # 統計をリストに変換してソート
            stats_list = list(channel_stats.values())
            stats_list.sort(key=lambda x: x['comment_count'], reverse=True)
            
            # 上位コメント投稿者（コメント数でソート）
            top_commenters = stats_list[:10]
            
            return {
                'total_comments': len(all_comments),
                'channel_stats': stats_list,
                'top_commenters': top_commenters,
                'unique_channels': len(channel_stats),
                'analysis': {
                    'average_comments_per_channel': len(all_comments) / len(channel_stats) if channel_stats else 0,
                    'most_active_commenter': stats_list[0] if stats_list else None,
                    'single_comment_channels': len([c for c in stats_list if c['comment_count'] == 1])
                }
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"コメント統計処理でエラーが発生しました: {str(e)}")

    def get_my_comments_on_channel_paginated(self, channel_id, next_page_token=None, max_results=50):
        """指定チャンネルの動画で自分のコメントのみを取得（ページネーション対応）
        
        OAuth認証が必要です。指定したチャンネルの動画から、
        認証ユーザー（自分）のコメントのみを取得します。
        
        Args:
            channel_id (str): 対象チャンネルのID
            next_page_token (str): 次のページのトークン
            max_results (int): 1回のAPI呼び出しで取得する最大件数
            
        Returns:
            dict: コメントリストとページネーション情報
            
        Raises:
            YouTubeAPIError: OAuth認証が設定されていない場合
        """
        if not self.service:
            raise YouTubeAPIError("OAuth認証が必要です。この機能にはOAuth設定が必要です。")
        
        try:
            # まず自分のチャンネル情報を取得
            my_channel = self.service.channels().list(
                part="id",
                mine=True
            ).execute()
            
            if not my_channel.get('items'):
                raise YouTubeAPIError("認証されたチャンネル情報を取得できませんでした。")
            
            my_channel_id = my_channel['items'][0]['id']
            
            # 指定チャンネルの動画を取得
            search_response = self.service.search().list(
                part="id",
                channelId=channel_id,
                type="video",
                maxResults=50,
                order="date"
            ).execute()
            
            all_my_comments = []
            
            # 各動画で自分のコメントを検索
            for video_item in search_response.get('items', []):
                video_id = video_item['id']['videoId']
                
                # 動画のコメントを取得
                comments_response = self.service.commentThreads().list(
                    part="snippet,replies",
                    videoId=video_id,
                    maxResults=100,
                    order="time"
                ).execute()
                
                # 自分のコメントのみフィルタリング
                for comment_thread in comments_response.get('items', []):
                    top_comment = comment_thread['snippet']['topLevelComment']['snippet']
                    
                    # トップレベルコメントが自分のものかチェック
                    if top_comment['authorChannelId']['value'] == my_channel_id:
                        all_my_comments.append({
                            'video_id': video_id,
                            'comment_type': 'top_level',
                            'comment_data': comment_thread,
                            'comment_text': top_comment['textDisplay'],
                            'published_at': top_comment['publishedAt']
                        })
                    
                    # 返信コメントもチェック
                    if 'replies' in comment_thread:
                        for reply in comment_thread['replies']['comments']:
                            reply_snippet = reply['snippet']
                            if reply_snippet['authorChannelId']['value'] == my_channel_id:
                                all_my_comments.append({
                                    'video_id': video_id,
                                    'comment_type': 'reply',
                                    'comment_data': reply,
                                    'comment_text': reply_snippet['textDisplay'],
                                    'published_at': reply_snippet['publishedAt'],
                                    'parent_comment_id': reply_snippet['parentId']
                                })
            
            return {
                'items': all_my_comments,
                'total_results': len(all_my_comments),
                'nextPageToken': None  # 簡易実装のため
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"自分のコメント取得に失敗しました: {str(e)}")

    def get_comments_excluding_author_paginated(self, video_id, next_page_token=None, max_results=50):
        """動画のコメントを投稿主のコメントを除外して取得（ページネーション対応）
        
        Args:
            video_id (str): 動画ID
            next_page_token (str): 次のページのトークン
            max_results (int): 1回のAPI呼び出しで取得する最大件数
            
        Returns:
            dict: コメントリストとページネーション情報（投稿主のコメントを除外）
        """
        try:
            # まず動画情報を取得して投稿主のチャンネルIDを特定
            video_response = self.service.videos().list(
                part="snippet",
                id=video_id
            ).execute()
            
            if not video_response.get('items'):
                raise YouTubeAPIError(f"動画ID {video_id} の情報を取得できませんでした。")
            
            author_channel_id = video_response['items'][0]['snippet']['channelId']
            
            # コメントを取得
            params = {
                'part': 'snippet,replies',
                'videoId': video_id,
                'maxResults': max_results,
                'order': 'time'
            }
            
            if next_page_token:
                params['pageToken'] = next_page_token
            
            response = self.service.commentThreads().list(**params).execute()
            
            # 投稿主のコメントを除外してフィルタリング
            filtered_items = []
            
            for comment_thread in response.get('items', []):
                top_comment = comment_thread['snippet']['topLevelComment']['snippet']
                
                # トップレベルコメントが投稿主でない場合は追加
                if top_comment.get('authorChannelId', {}).get('value') != author_channel_id:
                    # 返信も投稿主のものを除外
                    if 'replies' in comment_thread:
                        filtered_replies = []
                        for reply in comment_thread['replies']['comments']:
                            reply_snippet = reply['snippet']
                            if reply_snippet.get('authorChannelId', {}).get('value') != author_channel_id:
                                filtered_replies.append(reply)
                        
                        if filtered_replies:
                            comment_thread['replies']['comments'] = filtered_replies
                        else:
                            # 返信がすべて投稿主のものだった場合、repliesキーを削除
                            del comment_thread['replies']
                    
                    filtered_items.append(comment_thread)
            
            return {
                'items': filtered_items,
                'nextPageToken': response.get('nextPageToken'),
                'pageInfo': response.get('pageInfo', {}),
                'total_results': len(filtered_items)
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"コメント取得に失敗しました: {str(e)}")

    def get_video_comments(self, video_id, max_results=100, include_replies=True, order="time"):
        """動画のコメント一覧を取得（統合版）
        
        Args:
            video_id (str): 動画ID
            max_results (int): 最大取得件数（デフォルト: 100）
            include_replies (bool): 返信コメントも含めるか（デフォルト: True）
            order (str): ソート順序 ("time", "relevance")
            
        Returns:
            dict: コメント情報と統計
            {
                'comments': [...],  # コメントリスト
                'total_comments': int,  # 取得したコメント総数
                'top_level_count': int,  # トップレベルコメント数
                'reply_count': int,  # 返信コメント数
                'has_more': bool,  # さらにコメントがあるか
                'video_info': {...}  # 動画の基本情報
            }
        """
        try:
            # 動画情報を取得
            video_info = self.get_video_info(video_id)
            
            all_comments = []
            top_level_count = 0
            reply_count = 0
            next_page_token = None
            
            while len(all_comments) < max_results:
                # ページネーション対応でコメント取得
                page_result = self.get_comments_paginated(
                    video_id, 
                    next_page_token=next_page_token,
                    max_results=min(100, max_results - len(all_comments))
                )
                
                if not page_result.get('items'):
                    break
                
                # コメントを処理
                for comment_thread in page_result['items']:
                    # トップレベルコメント
                    top_comment = comment_thread['snippet']['topLevelComment']['snippet']
                    
                    comment_data = {
                        'id': comment_thread['snippet']['topLevelComment']['id'],
                        'type': 'top_level',
                        'text_display': top_comment['textDisplay'],
                        'text_original': top_comment.get('textOriginal', top_comment['textDisplay']),
                        'author_display_name': top_comment['authorDisplayName'],
                        'author_channel_id': top_comment.get('authorChannelId', {}).get('value'),
                        'author_channel_url': top_comment.get('authorChannelUrl'),
                        'author_profile_image_url': top_comment.get('authorProfileImageUrl'),
                        'like_count': top_comment.get('likeCount', 0),
                        'published_at': top_comment['publishedAt'],
                        'updated_at': top_comment.get('updatedAt'),
                        'can_rate': top_comment.get('canRate', False),
                        'viewer_rating': top_comment.get('viewerRating', 'none'),
                        'is_author_comment': self._is_video_author_comment(
                            top_comment.get('authorChannelId', {}).get('value'),
                            video_info.get('snippet', {}).get('channelId')
                        ),
                        'parent_id': None,
                        'video_id': video_id
                    }
                    
                    all_comments.append(comment_data)
                    top_level_count += 1
                    
                    # 返信コメントも取得
                    if include_replies and 'replies' in comment_thread:
                        for reply in comment_thread['replies']['comments']:
                            reply_snippet = reply['snippet']
                            
                            reply_data = {
                                'id': reply['id'],
                                'type': 'reply',
                                'text_display': reply_snippet['textDisplay'],
                                'text_original': reply_snippet.get('textOriginal', reply_snippet['textDisplay']),
                                'author_display_name': reply_snippet['authorDisplayName'],
                                'author_channel_id': reply_snippet.get('authorChannelId', {}).get('value'),
                                'author_channel_url': reply_snippet.get('authorChannelUrl'),
                                'author_profile_image_url': reply_snippet.get('authorProfileImageUrl'),
                                'like_count': reply_snippet.get('likeCount', 0),
                                'published_at': reply_snippet['publishedAt'],
                                'updated_at': reply_snippet.get('updatedAt'),
                                'can_rate': reply_snippet.get('canRate', False),
                                'viewer_rating': reply_snippet.get('viewerRating', 'none'),
                                'is_author_comment': self._is_video_author_comment(
                                    reply_snippet.get('authorChannelId', {}).get('value'),
                                    video_info.get('snippet', {}).get('channelId')
                                ),
                                'parent_id': reply_snippet['parentId'],
                                'video_id': video_id
                            }
                            
                            all_comments.append(reply_data)
                            reply_count += 1
                            
                            if len(all_comments) >= max_results:
                                break
                    
                    if len(all_comments) >= max_results:
                        break
                
                next_page_token = page_result.get('nextPageToken')
                if not next_page_token:
                    break
            
            return {
                'comments': all_comments,
                'total_comments': len(all_comments),
                'top_level_count': top_level_count,
                'reply_count': reply_count,
                'has_more': bool(next_page_token),
                'video_info': video_info
            }
            
        except Exception as e:
            # エラーハンドリング - 部分的な情報でも返す
            return {
                'comments': [],
                'total_comments': 0,
                'top_level_count': 0,
                'reply_count': 0,
                'has_more': False,
                'video_info': {},
                'error': str(e)
            }

    def _is_video_author_comment(self, comment_author_channel_id, video_channel_id):
        """投稿主のコメントかどうかを判定
        
        Args:
            comment_author_channel_id (str): コメント作成者のチャンネルID
            video_channel_id (str): 動画投稿者のチャンネルID
            
        Returns:
            bool: 投稿主のコメントならTrue
        """
        if not comment_author_channel_id or not video_channel_id:
            return False
        return comment_author_channel_id == video_channel_id

    def separate_author_comments(self, video_id, max_results=100):
        """投稿主コメントと視聴者コメントを分離して取得
        
        Args:
            video_id (str): 動画ID
            max_results (int): 最大取得件数
            
        Returns:
            dict: 分離されたコメント情報
            {
                'author_comments': [...],    # 投稿主のコメント
                'viewer_comments': [...],    # 視聴者のコメント
                'statistics': {...}          # 統計情報
            }
        """
        result = self.get_video_comments(video_id, max_results=max_results)
        
        author_comments = []
        viewer_comments = []
        
        for comment in result['comments']:
            if comment['is_author_comment']:
                author_comments.append(comment)
            else:
                viewer_comments.append(comment)
        
        return {
            'author_comments': author_comments,
            'viewer_comments': viewer_comments,
            'statistics': {
                'total_comments': result['total_comments'],
                'author_comment_count': len(author_comments),
                'viewer_comment_count': len(viewer_comments),
                'author_comment_ratio': len(author_comments) / max(result['total_comments'], 1),
                'top_level_count': result['top_level_count'],
                'reply_count': result['reply_count']
            },
            'video_info': result['video_info']
        }