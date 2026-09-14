"""YouTube Automation - Automatic Posting System
   
   This script automatically uploads videos to YouTube on a scheduled basis.
   Videos are uploaded from a folder and posted according to the schedule.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
import schedule
import time
import pytz
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.upload import YouTubeUploader
from src.auth import YouTubeAuth
from src.metadata_generator import MetadataGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_upload.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class YouTubeAutoUploader:
    """Automatically upload videos to YouTube on schedule"""
    
    def __init__(self, config_file='config/config.json', videos_folder='data/videos'):
        """Initialize auto-uploader
        
        Args:
            config_file: Path to config file
            videos_folder: Folder containing videos to upload
        """
        self.config_file = config_file
        self.videos_folder = videos_folder
        self.config = self._load_config()
        self.uploader = YouTubeUploader(config_file)
        self.metadata_gen = MetadataGenerator(config_file)
        self.queue = []
        self.uploaded_today = 0
        self.timezone = pytz.timezone(self.config.get('scheduler', {}).get('timezone', 'UTC'))
        
        logger.info("YouTube Auto-Uploader initialized")
        
    def _load_config(self):
        """Load configuration"""
        try:
            with open(self.config_file) as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_file}")
            return {}
    
    def discover_videos(self):
        """Discover all videos in the videos folder
        
        Returns:
            List of video file paths
        """
        if not os.path.exists(self.videos_folder):
            logger.warning(f"Videos folder not found: {self.videos_folder}")
            return []
        
        video_extensions = ['.mp4', '.avi', '.mov', '.flv', '.wmv', '.webm']
        videos = []
        
        for file in os.listdir(self.videos_folder):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                videos.append(os.path.join(self.videos_folder, file))
        
        logger.info(f"Found {len(videos)} videos in {self.videos_folder}")
        return videos
    
    def load_queue_from_csv(self, csv_file):
        """Load video queue from CSV file
        
        CSV format:
        video_file,title,description,tags,upload_time,privacy_status
        
        Args:
            csv_file: Path to CSV file
        """
        import csv
        
        self.queue = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    video_entry = {
                        'video_file': row['video_file'],
                        'title': row['title'],
                        'description': row.get('description', ''),
                        'tags': [tag.strip() for tag in row.get('tags', '').split(',')],
                        'upload_time': row.get('upload_time', '14:00'),
                        'privacy_status': row.get('privacy_status', 'public'),
                        'uploaded': False
                    }
                    self.queue.append(video_entry)
            
            logger.info(f"Loaded {len(self.queue)} videos from queue: {csv_file}")
            return self.queue
            
        except Exception as e:
            logger.error(f"Failed to load queue: {e}")
            return []
    
    def create_sample_queue(self):
        """Create a sample queue file
        
        Returns:
            Path to created CSV file
        """
        import csv
        
        queue_file = 'data/upload_queue.csv'
        os.makedirs('data', exist_ok=True)
        
        sample_data = [
            {
                'video_file': 'test1.mp4',
                'title': 'Introduction to Python',
                'description': 'Learn the basics of Python programming',
                'tags': 'python,programming,tutorial,education',
                'upload_time': '14:00',
                'privacy_status': 'public'
            },
            {
                'video_file': 'test2.mp4',
                'title': 'Advanced Python - Classes',
                'description': 'Master object-oriented programming in Python',
                'tags': 'python,oop,classes,programming',
                'upload_time': '15:00',
                'privacy_status': 'public'
            },
        ]
        
        try:
            with open(queue_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'video_file', 'title', 'description', 'tags', 'upload_time', 'privacy_status'
                ])
                writer.writeheader()
                writer.writerows(sample_data)
            
            logger.info(f"Created sample queue file: {queue_file}")
            return queue_file
            
        except Exception as e:
            logger.error(f"Failed to create queue file: {e}")
            return None
    
    def get_next_scheduled_upload(self):
        """Get the next video scheduled to upload
        
        Returns:
            Video entry if found, None otherwise
        """
        for video in self.queue:
            if not video['uploaded']:
                return video
        return None
    
    def upload_scheduled_video(self):
        """Upload the next scheduled video"""
        max_per_day = self.config.get('upload_settings', {}).get('max_videos_per_day', 2)
        
        # Check if we've exceeded daily limit
        if self.uploaded_today >= max_per_day:
            logger.warning(f"Daily upload limit reached: {self.uploaded_today}/{max_per_day}")
            return
        
        video = self.get_next_scheduled_upload()
        if not video:
            logger.info("No more videos in queue")
            return
        
        try:
            logger.info(f"Uploading video: {video['title']}")
            
            # Construct full path
            video_path = os.path.join(self.videos_folder, video['video_file'])
            
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return
            
            # Upload
            video_id = self.uploader.upload_video(
                video_path=video_path,
                title=video['title'],
                description=video['description'],
                tags=video['tags'],
                privacy_status=video['privacy_status']
            )
            
            if video_id:
                logger.info(f"✅ Video uploaded! ID: {video_id}")
                video['uploaded'] = True
                video['video_id'] = video_id
                video['uploaded_at'] = datetime.now(self.timezone).isoformat()
                self.uploaded_today += 1
                
                # Save updated queue
                self._save_queue()
            else:
                logger.error(f"Upload failed for: {video['title']}")
                
        except Exception as e:
            logger.error(f"Upload error: {e}")
    
    def _save_queue(self):
        """Save current queue to file"""
        import csv
        
        queue_file = 'data/upload_queue.csv'
        try:
            with open(queue_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'video_file', 'title', 'description', 'tags', 'upload_time', 'privacy_status'
                ])
                writer.writeheader()
                
                for video in self.queue:
                    row = {
                        'video_file': video['video_file'],
                        'title': video['title'],
                        'description': video['description'],
                        'tags': ','.join(video['tags']),
                        'upload_time': video['upload_time'],
                        'privacy_status': video['privacy_status']
                    }
                    writer.writerow(row)
            
            logger.info("Queue saved")
        except Exception as e:
            logger.error(f"Failed to save queue: {e}")
    
    def schedule_uploads(self, upload_time='14:00'):
        """Schedule videos to upload at specific time daily
        
        Args:
            upload_time: Time to upload (format: 'HH:MM')
        """
        logger.info(f"Scheduling uploads at {upload_time} daily")
        schedule.every().day.at(upload_time).do(self.upload_scheduled_video)
    
    def schedule_interval(self, interval_minutes=30):
        """Schedule uploads at intervals
        
        Args:
            interval_minutes: Minutes between uploads
        """
        logger.info(f"Scheduling uploads every {interval_minutes} minutes")
        schedule.every(interval_minutes).minutes.do(self.upload_scheduled_video)
    
    def reset_daily_counter(self):
        """Reset daily counter at midnight"""
        def _reset():
            self.uploaded_today = 0
            logger.info("Daily counter reset")
        
        schedule.every().day.at("00:00").do(_reset)
    
    def start_continuous(self):
        """Start continuous scheduling (blocking)"""
        logger.info("🚀 Starting continuous auto-uploader...")
        logger.info("Press Ctrl+C to stop")
        
        # Reset counter daily
        self.reset_daily_counter()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("\n⛔ Auto-uploader stopped by user")
    
    def start_background(self):
        """Start background scheduling (non-blocking)
        
        Returns:
            APScheduler scheduler object
        """
        from apscheduler.schedulers.background import BackgroundScheduler
        
        logger.info("🚀 Starting background auto-uploader...")
        
        scheduler = BackgroundScheduler()
        
        # Add jobs
        scheduler.add_job(self.upload_scheduled_video, 'interval', minutes=30, id='upload_job')
        scheduler.add_job(self._reset_counter, 'cron', hour=0, minute=0, id='reset_job')
        
        scheduler.start()
        logger.info("Background scheduler started")
        
        return scheduler
    
    def _reset_counter(self):
        """Reset daily counter"""
        self.uploaded_today = 0
        logger.info("Daily counter reset")
    
    def get_status(self):
        """Get current status
        
        Returns:
            Dictionary with status info
        """
        not_uploaded = sum(1 for v in self.queue if not v['uploaded'])
        
        return {
            'total_videos_in_queue': len(self.queue),
            'videos_uploaded': len(self.queue) - not_uploaded,
            'videos_pending': not_uploaded,
            'uploaded_today': self.uploaded_today,
            'daily_limit': self.config.get('upload_settings', {}).get('max_videos_per_day', 2),
            'timestamp': datetime.now(self.timezone).isoformat()
        }
    
    def print_status(self):
        """Print current status"""
        status = self.get_status()
        
        print("\n" + "="*60)
        print("📊 YouTube Auto-Uploader Status")
        print("="*60)
        print(f"Total videos in queue: {status['total_videos_in_queue']}")
        print(f"Videos uploaded: {status['videos_uploaded']}")
        print(f"Videos pending: {status['videos_pending']}")
        print(f"Uploaded today: {status['uploaded_today']}/{status['daily_limit']}")
        print(f"Timestamp: {status['timestamp']}")
        print("="*60 + "\n")


def main():
    """Main function"""
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    logger.info("="*60)
    logger.info("YouTube Automation - Auto Uploader Started")
    logger.info("="*60)
    
    # Initialize auto-uploader
    auto_uploader = YouTubeAutoUploader(
        config_file='config/config.json',
        videos_folder='data/videos'
    )
    
    # Load queue from CSV or create sample
    queue_file = 'data/upload_queue.csv'
    if not os.path.exists(queue_file):
        logger.info("Creating sample queue file...")
        auto_uploader.create_sample_queue()
    
    auto_uploader.load_queue_from_csv(queue_file)
    
    # Print status
    auto_uploader.print_status()
    
    # Schedule uploads at 2 PM daily
    auto_uploader.schedule_uploads(upload_time='14:00')
    
    # Start continuous scheduling
    auto_uploader.start_continuous()


if __name__ == "__main__":
    main()
