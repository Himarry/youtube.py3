"""
YouTube.py3 - マルチメディア処理機能モジュール

動画サムネイル抽出、ハイライト生成、音声文字起こし、字幕生成機能を提供します。
"""

import os
import cv2
import json
import tempfile
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import subprocess
import requests
from .base import YouTubeAPIBase
from .exceptions import YouTubeAPIError
from .utils import YouTubeUtils
import logging

logger = logging.getLogger(__name__)


class MediaProcessingMixin(YouTubeAPIBase):
    """マルチメディア処理機能を提供するMixin"""
    
    def __init__(self):
        super().__init__()
        self.temp_dir = tempfile.mkdtemp()
        self.supported_video_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        self.supported_audio_formats = ['.mp3', '.wav', '.aac', '.m4a']
        
    def extract_video_thumbnails(self, video_id: str, timestamps: List[int], 
                               output_dir: Optional[str] = None, 
                               size: Tuple[int, int] = (1280, 720)) -> Dict[str, Any]:
        """動画サムネイル抽出
        
        Args:
            video_id (str): 動画ID（またはローカル動画パス）
            timestamps (list): 抽出するタイムスタンプ（秒）
            output_dir (str): 出力ディレクトリ
            size (tuple): サムネイルサイズ
            
        Returns:
            dict: 抽出結果
        """
        try:
            if output_dir is None:
                output_dir = self.temp_dir
            
            os.makedirs(output_dir, exist_ok=True)
            
            # 動画ファイルの取得
            video_path = self._get_video_path(video_id)
            
            if not os.path.exists(video_path):
                raise YouTubeAPIError(f"動画ファイルが見つかりません: {video_path}")
            
            # OpenCVで動画を開く
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise YouTubeAPIError(f"動画ファイルを開けません: {video_path}")
            
            # 動画情報取得
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps
            
            extracted_thumbnails = []
            
            for timestamp in timestamps:
                if timestamp > duration:
                    logger.warning(f"タイムスタンプ {timestamp}s は動画の長さ {duration:.2f}s を超えています")
                    continue
                
                # 指定時刻のフレームに移動
                frame_number = int(timestamp * fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                
                ret, frame = cap.read()
                if ret:
                    # フレームをリサイズ
                    resized_frame = cv2.resize(frame, size)
                    
                    # ファイル名生成
                    thumbnail_filename = f"thumbnail_{video_id}_{timestamp}s.jpg"
                    thumbnail_path = os.path.join(output_dir, thumbnail_filename)
                    
                    # サムネイル保存
                    cv2.imwrite(thumbnail_path, resized_frame)
                    
                    # サムネイルに情報追加（オプション）
                    enhanced_thumbnail = self._enhance_thumbnail(
                        thumbnail_path, timestamp, video_id
                    )
                    
                    extracted_thumbnails.append({
                        'timestamp': timestamp,
                        'filename': thumbnail_filename,
                        'path': thumbnail_path,
                        'size': size,
                        'enhanced': enhanced_thumbnail
                    })
                    
                    logger.info(f"サムネイル抽出完了: {timestamp}s")
                else:
                    logger.warning(f"タイムスタンプ {timestamp}s のフレーム取得に失敗")
            
            cap.release()
            
            return {
                'video_id': video_id,
                'total_thumbnails': len(extracted_thumbnails),
                'output_directory': output_dir,
                'thumbnails': extracted_thumbnails,
                'video_info': {
                    'duration': duration,
                    'fps': fps,
                    'total_frames': total_frames
                },
                'extraction_completed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"サムネイル抽出に失敗しました: {str(e)}")
    
    def generate_video_highlights(self, video_id: str, duration: int = 60, 
                                method: str = 'auto') -> Dict[str, Any]:
        """動画ハイライト自動生成
        
        Args:
            video_id (str): 動画ID
            duration (int): ハイライト長さ（秒）
            method (str): 生成方法 ('auto', 'scenes', 'audio')
            
        Returns:
            dict: ハイライト生成結果
        """
        try:
            video_path = self._get_video_path(video_id)
            
            if not os.path.exists(video_path):
                raise YouTubeAPIError(f"動画ファイルが見つかりません: {video_path}")
            
            # 動画分析
            analysis_result = self._analyze_video_content(video_path, method)
            
            # ハイライト区間特定
            highlight_segments = self._identify_highlight_segments(
                analysis_result, duration
            )
            
            # ハイライト動画生成
            highlight_path = self._create_highlight_video(
                video_path, highlight_segments, video_id
            )
            
            # サムネイル生成
            highlight_thumbnail = self._generate_highlight_thumbnail(
                highlight_path, highlight_segments
            )
            
            return {
                'video_id': video_id,
                'original_video_path': video_path,
                'highlight_video_path': highlight_path,
                'highlight_thumbnail': highlight_thumbnail,
                'highlight_duration': duration,
                'generation_method': method,
                'segments_count': len(highlight_segments),
                'highlight_segments': highlight_segments,
                'analysis_data': analysis_result,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"ハイライト生成に失敗しました: {str(e)}")
    
    def transcribe_video_audio(self, video_id: str, language: str = 'ja', 
                             output_format: str = 'srt') -> Dict[str, Any]:
        """動画音声の文字起こし
        
        Args:
            video_id (str): 動画ID
            language (str): 言語コード
            output_format (str): 出力フォーマット ('srt', 'vtt', 'txt')
            
        Returns:
            dict: 文字起こし結果
        """
        try:
            video_path = self._get_video_path(video_id)
            
            # 音声抽出
            audio_path = self._extract_audio_from_video(video_path, video_id)
            
            # 音声認識実行
            transcription_result = self._perform_speech_recognition(
                audio_path, language
            )
            
            # 出力ファイル生成
            output_file = self._format_transcription(
                transcription_result, output_format, video_id
            )
            
            # 精度分析
            accuracy_analysis = self._analyze_transcription_accuracy(
                transcription_result
            )
            
            return {
                'video_id': video_id,
                'audio_file': audio_path,
                'transcription_file': output_file,
                'language': language,
                'output_format': output_format,
                'total_segments': len(transcription_result.get('segments', [])),
                'total_duration': transcription_result.get('duration', 0),
                'accuracy_analysis': accuracy_analysis,
                'raw_transcription': transcription_result,
                'transcribed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"音声文字起こしに失敗しました: {str(e)}")
    
    def generate_video_subtitles(self, video_id: str, target_language: str = 'ja', 
                               source_language: str = 'auto') -> Dict[str, Any]:
        """字幕自動生成
        
        Args:
            video_id (str): 動画ID
            target_language (str): 目標言語
            source_language (str): 元言語（'auto'で自動検出）
            
        Returns:
            dict: 字幕生成結果
        """
        try:
            video_path = self._get_video_path(video_id)
            
            # 音声抽出と文字起こし
            if source_language == 'auto':
                # 言語自動検出
                detected_language = self._detect_audio_language(video_path)
                source_language = detected_language
            
            # 音声文字起こし
            transcription = self.transcribe_video_audio(
                video_id, source_language, 'json'
            )
            
            # 翻訳（必要な場合）
            if source_language != target_language:
                translated_segments = self._translate_transcription(
                    transcription['raw_transcription'], 
                    source_language, 
                    target_language
                )
            else:
                translated_segments = transcription['raw_transcription']
            
            # 字幕ファイル生成
            subtitle_formats = ['srt', 'vtt', 'ass']
            generated_subtitles = {}
            
            for fmt in subtitle_formats:
                subtitle_file = self._generate_subtitle_file(
                    translated_segments, fmt, video_id, target_language
                )
                generated_subtitles[fmt] = subtitle_file
            
            # 字幕プレビュー生成
            preview_image = self._create_subtitle_preview(
                video_path, translated_segments
            )
            
            return {
                'video_id': video_id,
                'source_language': source_language,
                'target_language': target_language,
                'subtitle_files': generated_subtitles,
                'subtitle_preview': preview_image,
                'total_segments': len(translated_segments.get('segments', [])),
                'estimated_accuracy': self._estimate_subtitle_accuracy(translated_segments),
                'generation_metadata': {
                    'method': 'automatic_speech_recognition',
                    'translation_required': source_language != target_language,
                    'generated_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"字幕生成に失敗しました: {str(e)}")
    
    def create_video_montage(self, video_clips: List[Dict[str, Any]], 
                           output_settings: Dict[str, Any]) -> Dict[str, Any]:
        """動画モンタージュ作成
        
        Args:
            video_clips (list): 動画クリップ情報
            output_settings (dict): 出力設定
            
        Returns:
            dict: モンタージュ作成結果
        """
        try:
            montage_id = f"montage_{int(datetime.now().timestamp())}"
            
            # クリップ検証
            validated_clips = []
            for clip in video_clips:
                if self._validate_video_clip(clip):
                    validated_clips.append(clip)
                else:
                    logger.warning(f"無効なクリップをスキップ: {clip}")
            
            if not validated_clips:
                raise YouTubeAPIError("有効な動画クリップがありません")
            
            # モンタージュ作成
            montage_path = self._create_video_montage(
                validated_clips, output_settings, montage_id
            )
            
            # メタデータ生成
            metadata = self._generate_montage_metadata(
                validated_clips, output_settings
            )
            
            return {
                'montage_id': montage_id,
                'output_path': montage_path,
                'input_clips_count': len(validated_clips),
                'total_duration': metadata['total_duration'],
                'resolution': output_settings.get('resolution', '1920x1080'),
                'fps': output_settings.get('fps', 30),
                'metadata': metadata,
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"動画モンタージュ作成に失敗しました: {str(e)}")
    
    # 内部処理メソッド
    def _get_video_path(self, video_id: str) -> str:
        """動画パス取得（ローカルファイルまたはダウンロード）"""
        # ローカルファイルの場合
        if os.path.exists(video_id):
            return video_id
        
        # YouTube動画IDの場合（実装時はyt-dlpなどを使用）
        # ここでは簡略化
        return video_id
    
    def _enhance_thumbnail(self, thumbnail_path: str, timestamp: int, 
                          video_id: str) -> str:
        """サムネイル強化処理"""
        try:
            # PIL で画像を開く
            image = Image.open(thumbnail_path)
            
            # 画像強化
            enhancer = ImageEnhance.Contrast(image)
            enhanced_image = enhancer.enhance(1.2)
            
            # タイムスタンプ追加
            draw = ImageDraw.Draw(enhanced_image)
            
            # フォント設定（システムフォントを使用）
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # タイムスタンプテキスト
            time_text = f"{timestamp // 60:02d}:{timestamp % 60:02d}"
            
            # テキスト位置（右下）
            text_bbox = draw.textbbox((0, 0), time_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = enhanced_image.width - text_width - 10
            y = enhanced_image.height - text_height - 10
            
            # 背景矩形
            draw.rectangle([x-5, y-5, x+text_width+5, y+text_height+5], 
                          fill=(0, 0, 0, 128))
            
            # テキスト描画
            draw.text((x, y), time_text, font=font, fill=(255, 255, 255))
            
            # 強化画像保存
            enhanced_path = thumbnail_path.replace('.jpg', '_enhanced.jpg')
            enhanced_image.save(enhanced_path, 'JPEG', quality=95)
            
            return enhanced_path
            
        except Exception as e:
            logger.warning(f"サムネイル強化に失敗: {str(e)}")
            return thumbnail_path
    
    def _analyze_video_content(self, video_path: str, method: str) -> Dict[str, Any]:
        """動画コンテンツ分析"""
        analysis_data = {
            'method': method,
            'scenes': [],
            'audio_peaks': [],
            'motion_data': [],
            'color_analysis': []
        }
        
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # シーン検出
            if method in ['auto', 'scenes']:
                analysis_data['scenes'] = self._detect_scene_changes(cap, fps)
            
            # 音声分析
            if method in ['auto', 'audio']:
                analysis_data['audio_peaks'] = self._analyze_audio_peaks(video_path)
            
            # モーション分析
            if method == 'auto':
                analysis_data['motion_data'] = self._analyze_motion(cap, fps)
            
            cap.release()
            
        except Exception as e:
            logger.error(f"動画分析エラー: {str(e)}")
        
        return analysis_data
    
    def _identify_highlight_segments(self, analysis: Dict[str, Any], 
                                   duration: int) -> List[Dict[str, Any]]:
        """ハイライト区間特定"""
        segments = []
        
        # シーンベースのセグメント
        for scene in analysis.get('scenes', [])[:5]:  # 上位5シーン
            segments.append({
                'start_time': scene['timestamp'],
                'duration': min(10, duration // 5),  # 最大10秒
                'type': 'scene_change',
                'score': scene.get('score', 0.5)
            })
        
        # 音声ピークベースのセグメント
        for peak in analysis.get('audio_peaks', [])[:3]:  # 上位3ピーク
            segments.append({
                'start_time': peak['timestamp'],
                'duration': 8,
                'type': 'audio_peak',
                'score': peak.get('intensity', 0.5)
            })
        
        # 重複除去とソート
        segments = sorted(segments, key=lambda x: x['score'], reverse=True)
        
        # 時間調整
        total_seg_duration = 0
        selected_segments = []
        
        for segment in segments:
            if total_seg_duration + segment['duration'] <= duration:
                selected_segments.append(segment)
                total_seg_duration += segment['duration']
        
        return selected_segments
    
    def _create_highlight_video(self, video_path: str, segments: List[Dict], 
                              video_id: str) -> str:
        """ハイライト動画作成"""
        output_path = os.path.join(self.temp_dir, f"highlight_{video_id}.mp4")
        
        try:
            # FFmpegを使用してセグメント結合
            filter_complex = []
            inputs = []
            
            for i, segment in enumerate(segments):
                start = segment['start_time']
                duration = segment['duration']
                
                # 各セグメントの抽出
                filter_complex.append(
                    f"[0:v]trim=start={start}:duration={duration},setpts=PTS-STARTPTS[v{i}];"
                    f"[0:a]atrim=start={start}:duration={duration},asetpts=PTS-STARTPTS[a{i}]"
                )
            
            # セグメント結合
            video_inputs = ''.join(f'[v{i}]' for i in range(len(segments)))
            audio_inputs = ''.join(f'[a{i}]' for i in range(len(segments)))
            
            filter_complex.append(f"{video_inputs}concat=n={len(segments)}:v=1:a=0[outv]")
            filter_complex.append(f"{audio_inputs}concat=n={len(segments)}:v=0:a=1[outa]")
            
            cmd = [
                'ffmpeg', '-i', video_path,
                '-filter_complex', ';'.join(filter_complex),
                '-map', '[outv]', '-map', '[outa]',
                '-c:v', 'libx264', '-c:a', 'aac',
                output_path, '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg エラー: {result.stderr}")
                raise YouTubeAPIError("ハイライト動画の作成に失敗しました")
            
            return output_path
            
        except Exception as e:
            logger.error(f"ハイライト動画作成エラー: {str(e)}")
            raise YouTubeAPIError(f"ハイライト動画作成に失敗: {str(e)}")
    
    def _extract_audio_from_video(self, video_path: str, video_id: str) -> str:
        """動画から音声抽出"""
        audio_path = os.path.join(self.temp_dir, f"audio_{video_id}.wav")
        
        try:
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vn', '-acodec', 'pcm_s16le',
                '-ar', '16000', '-ac', '1',
                audio_path, '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise YouTubeAPIError(f"音声抽出に失敗: {result.stderr}")
            
            return audio_path
            
        except Exception as e:
            raise YouTubeAPIError(f"音声抽出エラー: {str(e)}")
    
    def _perform_speech_recognition(self, audio_path: str, language: str) -> Dict[str, Any]:
        """音声認識実行（OpenAI Whisper使用想定）"""
        try:
            # 簡略化された実装例
            # 実際の実装では OpenAI Whisper や Google Speech-to-Text を使用
            
            segments = [
                {
                    'start': 0.0,
                    'end': 10.0,
                    'text': '音声認識のサンプルテキストです。',
                    'confidence': 0.95
                },
                {
                    'start': 10.0,
                    'end': 20.0,
                    'text': '実際の実装では音声認識エンジンを使用します。',
                    'confidence': 0.89
                }
            ]
            
            return {
                'language': language,
                'duration': 20.0,
                'segments': segments,
                'full_text': ' '.join([seg['text'] for seg in segments])
            }
            
        except Exception as e:
            raise YouTubeAPIError(f"音声認識エラー: {str(e)}")
    
    def _format_transcription(self, transcription: Dict[str, Any], 
                            output_format: str, video_id: str) -> str:
        """文字起こし結果のフォーマット"""
        output_path = os.path.join(
            self.temp_dir, 
            f"transcription_{video_id}.{output_format}"
        )
        
        try:
            if output_format == 'srt':
                content = self._generate_srt_content(transcription['segments'])
            elif output_format == 'vtt':
                content = self._generate_vtt_content(transcription['segments'])
            elif output_format == 'txt':
                content = transcription['full_text']
            else:
                content = json.dumps(transcription, ensure_ascii=False, indent=2)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return output_path
            
        except Exception as e:
            raise YouTubeAPIError(f"文字起こしフォーマットエラー: {str(e)}")
    
    def _generate_srt_content(self, segments: List[Dict]) -> str:
        """SRT形式コンテンツ生成"""
        srt_content = []
        
        for i, segment in enumerate(segments, 1):
            start_time = self._seconds_to_srt_time(segment['start'])
            end_time = self._seconds_to_srt_time(segment['end'])
            
            srt_content.append(f"{i}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(segment['text'])
            srt_content.append("")
        
        return '\n'.join(srt_content)
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """秒をSRT時間形式に変換"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    def _detect_scene_changes(self, cap, fps) -> List[Dict[str, Any]]:
        """シーン変化検出"""
        scenes = []
        prev_frame = None
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if prev_frame is not None:
                # フレーム差分計算
                diff = cv2.absdiff(frame, prev_frame)
                score = np.mean(diff)
                
                # しきい値を超えた場合はシーン変化
                if score > 30:  # 調整可能なしきい値
                    timestamp = frame_count / fps
                    scenes.append({
                        'timestamp': timestamp,
                        'score': score / 255.0
                    })
            
            prev_frame = frame.copy()
            frame_count += 1
        
        return sorted(scenes, key=lambda x: x['score'], reverse=True)[:10]
    
    def _analyze_audio_peaks(self, video_path: str) -> List[Dict[str, Any]]:
        """音声ピーク分析"""
        # 簡略化実装
        peaks = [
            {'timestamp': 15.0, 'intensity': 0.8},
            {'timestamp': 45.0, 'intensity': 0.9},
            {'timestamp': 78.0, 'intensity': 0.7}
        ]
        return peaks
    
    def _analyze_motion(self, cap, fps) -> List[Dict[str, Any]]:
        """モーション分析"""
        motion_data = []
        # 実装は省略（光学フローなどを使用）
        return motion_data
    
    def _validate_video_clip(self, clip: Dict[str, Any]) -> bool:
        """動画クリップ検証"""
        required_fields = ['path', 'start_time', 'duration']
        return all(field in clip for field in required_fields)
    
    def _create_video_montage(self, clips: List[Dict], settings: Dict, 
                            montage_id: str) -> str:
        """動画モンタージュ作成"""
        output_path = os.path.join(self.temp_dir, f"montage_{montage_id}.mp4")
        
        # FFmpegを使用したモンタージュ作成
        # 実装詳細は省略
        
        return output_path
    
    def _generate_montage_metadata(self, clips: List[Dict], 
                                 settings: Dict) -> Dict[str, Any]:
        """モンタージュメタデータ生成"""
        total_duration = sum(clip['duration'] for clip in clips)
        
        return {
            'total_duration': total_duration,
            'clips_count': len(clips),
            'settings': settings
        }
    
    def _analyze_transcription_accuracy(self, transcription: Dict) -> Dict[str, Any]:
        """文字起こし精度分析"""
        segments = transcription.get('segments', [])
        
        if not segments:
            return {'accuracy': 'unknown'}
        
        avg_confidence = sum(seg.get('confidence', 0) for seg in segments) / len(segments)
        
        return {
            'average_confidence': avg_confidence,
            'total_segments': len(segments),
            'accuracy_level': 'high' if avg_confidence > 0.9 else 'medium' if avg_confidence > 0.7 else 'low'
        }