"""YouTube Upload Scheduler Module

Automatically schedules and uploads videos at optimal times
"""

import os
import json
import csv
import logging
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .upload import YouTubeUploader
from .metadata_generator import MetadataGenerator

logger = logging.getLogger(__name__)

class YouTubeScheduler:
    """Schedule automatic video uploads"""
    
    def __init__(self, config_file='config/config.json'):
        """Initialize scheduler
        
        Args:
            config_file: Path to configuration file
        """
        self.config = self._load_config(config_file)
        self.scheduler = BackgroundScheduler()
        self.uploader = YouTubeUploader(config_file)
        self.metadata_gen = MetadataGenerator(config_file)
        self.uploaded_count = 0
        self.max_per_day = self.config['upload_settings']['max_videos_per_day']
        
    def _load_config(self):
        """Load configuration"""
        with open('config/config.json') as f:
            return json.load(f)
            
    def load_schedule_from_csv(self, csv_file):
        """Load upload schedule from CSV file
        
        Args:
            csv_file: Path to CSV file with schedule
            
        Returns:
            List of video upload jobs
        """
        jobs = []
        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    jobs.append({
                        'video_path': row['video_path'],
                        'title': row['title'],
                        'description': row.get('description', ''),
                        'tags': row.get('tags', '').split(';'),
                        'upload_time': row['upload_time'],
                        'privacy_status': row.get('privacy_status', 'public')
                    })
                    
            logger.info(f"Loaded {len(jobs)} jobs from {csv_file}")
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to load schedule: {e}")
            return []
            
    def schedule_upload(self, video_info, upload_time):
        """Schedule a single video upload
        
        Args:
            video_info: Video metadata dict
            upload_time: Upload time (datetime or string)
        """
        if isinstance(upload_time, str):
            upload_time = datetime.fromisoformat(upload_time)
            
        job_id = f"upload_{self.uploaded_count}_{int(upload_time.timestamp())}"
        
        self.scheduler.add_job(
            self._upload_job,
            'date',
            run_date=upload_time,
            args=[video_info],
            id=job_id,
            replace_existing=True
        )
        
        logger.info(f"Scheduled upload: {video_info['title']} at {upload_time}")
        self.uploaded_count += 1
        
    def schedule_batch_uploads(self, jobs, start_time=None, interval_hours=24):
        """Schedule multiple uploads at intervals
        
        Args:
            jobs: List of video info dicts
            start_time: When to start first upload (default: now)
            interval_hours: Hours between uploads
        """
        if start_time is None:
            start_time = datetime.now(pytz.UTC)
            
        # Limit to max per day
        jobs = jobs[:self.max_per_day]
        
        for i, job in enumerate(jobs):
            upload_time = start_time + timedelta(hours=i * interval_hours)
            self.schedule_upload(job, upload_time)
            
        logger.info(f"Scheduled {len(jobs)} uploads starting at {start_time}")
        
    def schedule_daily(self, jobs, upload_hour=14, upload_minute=0):
        """Schedule daily video uploads
        
        Args:
            jobs: List of video info dicts
            upload_hour: Hour of day to upload (0-23)
            upload_minute: Minute of hour
        """
        timezone = pytz.timezone(self.config['scheduler']['timezone'])
        
        # Distribute jobs evenly throughout the day
        upload_interval = 24 // len(jobs)
        
        for i, job in enumerate(jobs):
            hour = (upload_hour + (i * upload_interval)) % 24
            
            trigger = CronTrigger(
                hour=hour,
                minute=upload_minute,
                timezone=timezone
            )
            
            job_id = f"daily_upload_{i}"
            self.scheduler.add_job(
                self._upload_job,
                trigger,
                args=[job],
                id=job_id,
                replace_existing=True
            )
            
            logger.info(f"Scheduled daily upload at {hour:02d}:{upload_minute:02d}")
            
    def _upload_job(self, video_info):
        """Execute video upload
        
        Args:
            video_info: Video metadata dict
        """
        try:
            logger.info(f"Executing upload job: {video_info['title']}")
            
            video_id = self.uploader.upload_video(
                video_path=video_info['video_path'],
                title=video_info['title'],
                description=video_info.get('description', ''),
                tags=video_info.get('tags', []),
                privacy_status=video_info.get('privacy_status', 'public')
            )
            
            if video_id:
                logger.info(f"✅ Upload successful! Video ID: {video_id}")
                return video_id
            else:
                logger.error("Upload failed")
                return None
                
        except Exception as e:
            logger.error(f"Upload job failed: {e}")
            if self.config['scheduler']['auto_retry_on_failure']:
                self._retry_upload(video_info)
            raise
            
    def _retry_upload(self, video_info, max_retries=3):
        """Retry failed upload
        
        Args:
            video_info: Video metadata dict
            max_retries: Maximum retry attempts
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Retry attempt {attempt + 1}/{max_retries}")
                video_id = self.uploader.upload_video(**video_info)
                if video_id:
                    logger.info(f"✅ Retry successful! Video ID: {video_id}")
                    return video_id
            except Exception as e:
                logger.error(f"Retry {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(10 * (attempt + 1))  # Exponential backoff
                    
        logger.error("All retries failed")
        return None
        
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✅ Scheduler started")
            
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
            
    def get_scheduled_jobs(self):
        """Get list of scheduled jobs"""
        return self.scheduler.get_jobs()
        
    def remove_job(self, job_id):
        """Remove a scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed job: {job_id}")
        except Exception as e:
            logger.error(f"Failed to remove job: {e}")


if __name__ == "__main__":
    # Example usage
    scheduler = YouTubeScheduler()
    
    # Load schedule from CSV
    jobs = scheduler.load_schedule_from_csv('data/schedule.example.csv')
    
    # Schedule batch uploads starting now
    scheduler.schedule_batch_uploads(jobs, start_time=datetime.now())
    
    # Start scheduler
    scheduler.start()
    
    # Keep running
    try:
        print("Scheduler running... Press Ctrl+C to stop")
        while True:
            pass
    except KeyboardInterrupt:
        scheduler.stop()
