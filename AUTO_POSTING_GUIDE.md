# YouTube Auto-Posting System Guide

## Overview

The **auto_upload.py** system automatically uploads videos to YouTube on a schedule. Videos are read from a queue file and posted at specified times without manual intervention.

## Features

✅ **Automatic Scheduling** - Upload videos at specific times daily
✅ **Queue Management** - Manage videos in CSV file
✅ **Daily Limits** - Respects YouTube quotas (max 2 videos/day)
✅ **Logging** - Track all uploads and errors
✅ **Status Dashboard** - Monitor upload progress
✅ **Continuous/Background Mode** - Run as background process

---

## Setup

### 1. Install Schedule Library

```bash
pip install schedule
# Already included in requirements.txt
```

### 2. Create Videos Folder

```bash
mkdir -p data/videos
# Place your MP4 videos here
```

### 3. Create Upload Queue

The system uses a CSV file to track videos. Create `data/upload_queue.csv`:

```csv
video_file,title,description,tags,upload_time,privacy_status
video1.mp4,Learn Python Basics,Introduction to Python programming,python;tutorial;education,14:00,public
video2.mp4,Advanced Python Classes,Object-oriented programming in Python,python;oop;classes,15:00,public
video3.mp4,Python Web Development,Build web apps with Flask,python;web;flask,16:00,public
```

**CSV Columns:**
- `video_file` - Filename in data/videos folder
- `title` - Video title (max 100 chars)
- `description` - Video description
- `tags` - Tags separated by semicolons (;)
- `upload_time` - Time to upload (HH:MM format, 24-hour)
- `privacy_status` - "public", "unlisted", or "private"

---

## Usage

### Method 1: Continuous Mode (Blocking)

Runs in foreground and continuously checks for scheduled uploads.

```bash
python auto_upload.py
```

**Output:**
```
2024-09-14 14:00:00 - root - INFO - Uploading video: Learn Python Basics
2024-09-14 14:02:30 - root - INFO - ✅ Video uploaded! ID: dQw4w9WgXcQ
2024-09-14 15:00:00 - root - INFO - Uploading video: Advanced Python Classes
```

**Press Ctrl+C to stop**

---

### Method 2: Background Mode (Non-Blocking)

Runs in background while your script continues executing.

```python
from auto_upload import YouTubeAutoUploader

# Initialize
uploader = YouTubeAutoUploader()
uploader.load_queue_from_csv('data/upload_queue.csv')

# Schedule uploads
uploader.schedule_uploads(upload_time='14:00')

# Start in background
scheduler = uploader.start_background()

# Your script continues here
print("Auto-uploader running in background")
# ... do other things ...

# Stop when done
scheduler.shutdown()
```

---

### Method 3: Custom Schedule

```python
from auto_upload import YouTubeAutoUploader

uploader = YouTubeAutoUploader()
uploader.load_queue_from_csv('data/upload_queue.csv')

# Upload every 30 minutes
uploader.schedule_interval(interval_minutes=30)

# Or at specific time daily
uploader.schedule_uploads(upload_time='14:00')

# Start
uploader.start_continuous()
```

---

## CSV Format Examples

### Example 1: Daily Upload Schedule

```csv
video_file,title,description,tags,upload_time,privacy_status
monday.mp4,Monday Lesson,Week 1 Content,education;monday,10:00,public
tuesday.mp4,Tuesday Lesson,Week 1 Content,education;tuesday,10:00,public
wednesday.mp4,Wednesday Lesson,Week 1 Content,education;wednesday,10:00,public
thursday.mp4,Thursday Lesson,Week 1 Content,education;thursday,10:00,public
friday.mp4,Friday Lesson,Week 1 Content,education;friday,10:00,public
```

### Example 2: Multiple Tags

```csv
video_file,title,description,tags,upload_time,privacy_status
tutorial.mp4,Python Basics,Learn Python,python;programming;tutorial;education;beginner,14:00,public
```

### Example 3: Mixed Privacy Settings

```csv
video_file,title,description,tags,upload_time,privacy_status
draft1.mp4,Draft Video 1,Not ready yet,draft,14:00,private
draft2.mp4,Draft Video 2,Review needed,draft,15:00,unlisted
final.mp4,Final Video,Ready to publish,published,16:00,public
```

---

## Configuration

Edit `config/config.json`:

```json
{
  "upload_settings": {
    "max_videos_per_day": 2,
    "optimal_upload_time": "14:00",
    "category": "27",
    "language": "en"
  },
  "scheduler": {
    "timezone": "America/New_York",
    "auto_retry_on_failure": true
  }
}
```

**Key Settings:**
- `max_videos_per_day` - Daily upload limit (respects YouTube quota)
- `timezone` - Timezone for scheduling (default: UTC)
- `auto_retry_on_failure` - Retry failed uploads automatically

---

## Monitoring & Debugging

### Check Status

```python
from auto_upload import YouTubeAutoUploader

uploader = YouTubeAutoUploader()
uploader.load_queue_from_csv('data/upload_queue.csv')

status = uploader.get_status()
print(f"Videos in queue: {status['total_videos_in_queue']}")
print(f"Uploaded: {status['videos_uploaded']}")
print(f"Pending: {status['videos_pending']}")
```

### View Logs

```bash
# Real-time logs
tail -f logs/auto_upload.log

# Or view entire log
cat logs/auto_upload.log
```

### Sample Log Output

```
2024-09-14 14:00:05 - root - INFO - Uploading video: Learn Python Basics
2024-09-14 14:00:10 - root - INFO - 📝 Uploading video: Learn Python Basics
2024-09-14 14:00:10 - root - INFO - 📊 File: data/videos/video1.mp4
2024-09-14 14:02:30 - root - INFO - ⏳ Upload progress: 50%
2024-09-14 14:05:00 - root - INFO - ⏳ Upload progress: 100%
2024-09-14 14:05:02 - root - INFO - ✅ Video uploaded! ID: dQw4w9WgXcQ
```

---

## Common Tasks

### Add New Video to Queue

Edit `data/upload_queue.csv` and add a row:

```csv
new_video.mp4,My New Video,Description here,tag1;tag2;tag3,14:00,public
```

Restart the auto-uploader and it will pick up the new video.

### Change Upload Time

Edit the `upload_time` column in CSV:

```csv
video1.mp4,Video 1,Description,tags,15:00,public
```

### Skip a Video

Keep the row but set `video_file` to empty:

```csv
,Skipped Video,Description,tags,14:00,public
```

### Pause Auto-Uploading

Stop the process (Ctrl+C) and restart when ready.

### Upload Now (Immediately)

```python
from auto_upload import YouTubeAutoUploader

uploader = YouTubeAutoUploader()
uploader.load_queue_from_csv('data/upload_queue.csv')

# Upload next video immediately
uploader.upload_scheduled_video()
```

---

## Troubleshooting

### Videos Not Uploading

1. **Check logs:**
   ```bash
   tail -f logs/auto_upload.log
   ```

2. **Verify credentials:**
   ```bash
   python src/auth.py
   ```

3. **Check queue file:**
   ```bash
   cat data/upload_queue.csv
   ```

4. **Test manual upload:**
   ```python
   from src.upload import YouTubeUploader
   uploader = YouTubeUploader()
   video_id = uploader.upload_video('data/videos/test.mp4', 'Test')
   ```

### "Daily limit reached"

- Maximum 2 videos/day (configurable in config.json)
- Wait 24 hours or restart the process

### "Video file not found"

- Ensure video exists in `data/videos/` folder
- Check filename matches exactly in CSV (case-sensitive on Linux/Mac)

### "Invalid request" Error

- Check title is under 100 characters
- Check description is under 5000 characters
- Verify video format is MP4, AVI, or MOV

---

## Running as Service (Linux/Mac)

### Create systemd service

Save as `/etc/systemd/system/youtube-auto.service`:

```ini
[Unit]
Description=YouTube Automation Auto-Uploader
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/youtube-automation
ExecStart=/usr/bin/python3 /path/to/youtube-automation/auto_upload.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable youtube-auto
sudo systemctl start youtube-auto
sudo systemctl status youtube-auto
```

View logs:

```bash
sudo journalctl -u youtube-auto -f
```

---

## Running on Windows

### Create Windows Task Scheduler task

1. Open **Task Scheduler**
2. **Create Basic Task**
3. **Name:** YouTube Auto Uploader
4. **Trigger:** Daily at desired time
5. **Action:** Start program
   - Program: `C:\Python\python.exe`
   - Arguments: `C:\path\to\auto_upload.py`
   - Start in: `C:\path\to\youtube-automation`
6. Click **OK**

---

## Running on Cloud (Google Cloud, AWS, etc.)

### Google Cloud Run

```bash
# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "auto_upload.py"]
EOF

# Deploy
gcloud run deploy youtube-auto --source . --memory 512Mi --timeout 3600
```

### AWS Lambda

```python
# lambda_function.py
from auto_upload import YouTubeAutoUploader

def lambda_handler(event, context):
    uploader = YouTubeAutoUploader()
    uploader.load_queue_from_csv('data/upload_queue.csv')
    uploader.upload_scheduled_video()
    
    return {
        'statusCode': 200,
        'body': 'Upload scheduled'
    }
```

Set up CloudWatch Events to trigger hourly.

---

## Performance Tips

1. **Use private/unlisted** for testing to avoid quota waste
2. **Stagger upload times** to spread API requests
3. **Monitor daily quota** - 15,000 units/day free, ~6,000 per upload
4. **Keep video file sizes small** for faster uploads
5. **Run on server** for 24/7 automatic uploads

---

## Example Complete Setup

### 1. Folder Structure

```
youtube-automation/
├── auto_upload.py
├── config/
│   ├── config.json
│   └── client_secrets.json
├── data/
│   ├── videos/
│   │   ├── video1.mp4
│   │   ├── video2.mp4
│   │   └── video3.mp4
│   └── upload_queue.csv
├── logs/
│   └── auto_upload.log
└── src/
    ├── auth.py
    └── upload.py
```

### 2. Create upload_queue.csv

```csv
video_file,title,description,tags,upload_time,privacy_status
video1.mp4,Python Tutorial 1,Basics of Python,python;tutorial,14:00,public
video2.mp4,Python Tutorial 2,Advanced Topics,python;tutorial,15:00,public
video3.mp4,Python Tutorial 3,Web Development,python;web,16:00,public
```

### 3. Run

```bash
python auto_upload.py
```

### 4. Monitor

```bash
tail -f logs/auto_upload.log
```

That's it! Videos will upload automatically at scheduled times! 🚀

---

## API Reference

### YouTubeAutoUploader Methods

```python
# Initialize
uploader = YouTubeAutoUploader(config_file, videos_folder)

# Load videos
uploader.load_queue_from_csv('data/upload_queue.csv')

# Schedule
uploader.schedule_uploads(upload_time='14:00')  # Daily at 2 PM
uploader.schedule_interval(interval_minutes=30)  # Every 30 minutes

# Run
uploader.start_continuous()  # Blocking
scheduler = uploader.start_background()  # Non-blocking

# Monitor
status = uploader.get_status()
uploader.print_status()

# Manual upload
uploader.upload_scheduled_video()

# Get next video
video = uploader.get_next_scheduled_upload()
```

---

## Support

For issues or questions:
- Check logs: `logs/auto_upload.log`
- Review TROUBLESHOOTING.md
- Submit GitHub issue with logs and CSV file
