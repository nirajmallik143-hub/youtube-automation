"""YouTube Video Upload Module

Handles single and batch video uploads to YouTube
"""

import os
import json
import time
import logging
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from .auth import YouTubeAuth

logger = logging.getLogger(__name__)

class YouTubeUploader:
    """Handle YouTube video uploads"""
    
    def __init__(self, config_file='config/config.json'):
        """Initialize uploader
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.auth = YouTubeAuth(config_file)
        self.youtube = None
        self._authenticate()
        
    def _load_config(self):
        """Load configuration from file"""
        with open(self.config_file) as f:
            return json.load(f)
            
    def _authenticate(self):
        """Authenticate with YouTube API"""
        credentials = self.auth.authenticate()
        self.youtube = build('youtube', 'v3', credentials=credentials)
        logger.info("Connected to YouTube API")
        
    def upload_video(self, video_path, title, description, tags=None, 
                    category_id='27', privacy_status='public'):
        """Upload a single video to YouTube
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            category_id: YouTube category ID (27=Education)
            privacy_status: 'public', 'unlisted', or 'private'
            
        Returns:
            Video ID if successful, None otherwise
        """
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return None
            
        try:
            logger.info(f"Uploading video: {title}")
            
            # Prepare request body
            body = {
                'snippet': {
                    'title': title[:100],
                    'description': description[:5000],
                    'tags': tags or [],
                    'categoryId': category_id,
                    'defaultLanguage': self.config['upload_settings']['language']
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Create media upload
            media = MediaFileUpload(
                video_path,
                chunksize=1024 * 1024,  # 1MB chunks
                resumable=True,
                mimetype='video/*'
            )
            
            # Execute upload
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                try:
                    status, response = request.next_chunk()
                    if status:
                        logger.info(f"Upload progress: {int(status.progress() * 100)}%")
                except HttpError as e:
                    logger.error(f"Upload error: {e}")
                    return None
                    
            video_id = response['id']
            logger.info(f"✅ Video uploaded successfully! ID: {video_id}")
            return video_id
            
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return None
            
    def batch_upload(self, videos_data, delay_seconds=300):
        """Upload multiple videos with delay
        
        Args:
            videos_data: List of dicts with video info:
                        [{'path': 'video.mp4', 'title': 'Title', ...}, ...]
            delay_seconds: Delay between uploads (to avoid spam detection)
            
        Returns:
            List of successfully uploaded video IDs
        """
        uploaded_ids = []
        max_per_day = self.config['upload_settings']['max_videos_per_day']
        
        if len(videos_data) > max_per_day:
            logger.warning(f"Limiting uploads to {max_per_day} per day")
            videos_data = videos_data[:max_per_day]
            
        for i, video in enumerate(videos_data):
            try:
                video_id = self.upload_video(
                    video_path=video['path'],
                    title=video.get('title', 'Untitled'),
                    description=video.get('description', ''),
                    tags=video.get('tags', []),
                    category_id=video.get('category_id', '27'),
                    privacy_status=video.get('privacy_status', 'public')
                )
                
                if video_id:
                    uploaded_ids.append(video_id)
                    
                # Delay between uploads
                if i < len(videos_data) - 1:
                    logger.info(f"Waiting {delay_seconds}s before next upload...")
                    time.sleep(delay_seconds)
                    
            except Exception as e:
                logger.error(f"Failed to upload video {i}: {e}")
                
        logger.info(f"Batch upload complete: {len(uploaded_ids)} videos uploaded")
        return uploaded_ids


if __name__ == "__main__":
    uploader = YouTubeUploader()
    
    # Example single upload
    video_id = uploader.upload_video(
        video_path='path/to/video.mp4',
        title='My Educational Video',
        description='Learn something new!',
        tags=['education', 'learning', 'cartoon']
    )
    
    print(f"Uploaded video ID: {video_id}")
