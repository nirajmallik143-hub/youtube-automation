# YouTube Upload Troubleshooting Guide

## Common Upload Errors & Solutions

### 1. **Authentication Errors**

#### Error: "FileNotFoundError: client_secrets.json not found"

**Cause:** Missing OAuth credentials file

**Solution:**
```bash
# 1. Download credentials from Google Cloud Console
# https://console.cloud.google.com/ → APIs & Services → Credentials

# 2. Place the file in config folder
cp ~/Downloads/client_secret_*.json config/client_secrets.json

# 3. Run auth again
python src/auth.py
```

---

#### Error: "The caller does not have permission to access the resource"

**Cause:** YouTube Data API v3 not enabled or not authorized

**Solution:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on your project
3. Go to **APIs & Services** → **Library**
4. Search for **YouTube Data API v3**
5. Click **Enable**
6. Wait 2-3 minutes for changes to propagate
7. Delete `config/credentials.json` and re-authenticate:
   ```bash
   rm config/credentials.json
   python src/auth.py
   ```

---

#### Error: "invalid_grant: Token has been revoked"

**Cause:** OAuth token expired or revoked

**Solution:**
```bash
# Delete the cached credentials and re-authenticate
rm config/credentials.json
python src/auth.py
```

---

### 2. **Upload Failures**

#### Error: "HttpError 400: Invalid Request"

**Cause:** Video metadata or file format issue

**Solution:**
```python
# Check video file exists and is valid
import os
from pathlib import Path

video_path = 'test.mp4'
if os.path.exists(video_path):
    size_mb = os.path.getsize(video_path) / (1024*1024)
    print(f"✅ File found: {size_mb:.2f} MB")
else:
    print(f"❌ File not found: {video_path}")

# Validate video with ffprobe
import subprocess
result = subprocess.run(['ffprobe', video_path], capture_output=True, text=True)
if result.returncode == 0:
    print("✅ Video file is valid")
else:
    print("❌ Video file is corrupted")
```

---

#### Error: "HttpError 403: Insufficient Permission"

**Cause:** Account doesn't have upload permission or quota exceeded

**Solution:**
```python
# Check quota usage
from googleapiclient.discovery import build

youtube = build('youtube', 'v3', credentials=creds)
request = youtube.videos().list(part='processingDetails', mine=True, maxResults=1)
response = request.execute()

if response['items']:
    status = response['items'][0].get('processingDetails', {}).get('processingStatus')
    print(f"Video status: {status}")
```

**Common reasons:**
- Quota exceeded (15,000 units/day max)
- Account restrictions (new accounts may have limits)
- Video violates YouTube policies

**Solution for quota:**
- Wait 24 hours for quota to reset
- Or upgrade to YouTube partner program
- Check quota at: https://console.cloud.google.com/apis/dashboard

---

#### Error: "HttpError 500: Internal Server Error"

**Cause:** YouTube API server issue (temporary)

**Solution:**
```python
# Retry with exponential backoff
import time

def upload_with_retry(uploader, video_path, title, max_retries=3):
    for attempt in range(max_retries):
        try:
            video_id = uploader.upload_video(video_path, title)
            return video_id
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Attempt {attempt+1} failed. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise e

# Usage
video_id = upload_with_retry(uploader, 'test.mp4', 'My Video')
```

---

### 3. **File Issues**

#### Error: "Video file not found"

**Cause:** Wrong file path

**Solution:**
```python
import os
from pathlib import Path

# Check current working directory
print(f"Current dir: {os.getcwd()}")

# List files in current directory
print("Files in current directory:")
for f in os.listdir('.'):
    if f.endswith('.mp4'):
        print(f"  - {f}")

# Use absolute path
video_path = os.path.abspath('test.mp4')
print(f"Absolute path: {video_path}")
```

---

#### Error: "Video file is too large"

**Cause:** File exceeds size limits

**Solution:**
- YouTube max file size: **256 GB**
- But practical limit: **~4 GB** (upload may timeout)

**Reduce file size:**
```bash
# Re-encode with lower bitrate
ffmpeg -i large_video.mp4 -b:v 2000k -b:a 128k small_video.mp4

# Or reduce resolution
ffmpeg -i video.mp4 -vf scale=1280:720 output.mp4
```

---

#### Error: "Unsupported video format"

**Cause:** File format not compatible with YouTube

**Solution - YouTube supports:**
- MOV
- MPEG4
- AVI
- WMV
- FLV
- 3GPP
- WebM
- DNxHD
- ProRes
- CineForm
- HEVC

**Convert to MP4:**
```bash
ffmpeg -i video.avi -c:v libx264 -c:a aac video.mp4
```

---

### 4. **Metadata Issues**

#### Error: "Invalid snippet - title"

**Cause:** Title is empty, too long, or contains invalid characters

**Solution:**
```python
# Title must be:
# - Not empty
# - Max 100 characters
# - No special characters like <>

title = "My Awesome Educational Video"
if len(title) <= 100 and title.strip():
    print("✅ Title is valid")
else:
    print("❌ Title is invalid")
```

---

#### Error: "Invalid category ID"

**Cause:** Category ID doesn't exist or isn't valid

**Solution - Use valid YouTube category IDs:**
```python
YOUTUBE_CATEGORIES = {
    '1': 'Film & Animation',
    '2': 'Autos & Vehicles',
    '10': 'Music',
    '15': 'Pets & Animals',
    '17': 'Sports',
    '18': 'Short Movies',
    '19': 'Travel & Events',
    '20': 'Gaming',
    '21': 'Videoblogging',
    '22': 'People & Blogs',
    '23': 'Comedy',
    '24': 'Entertainment',
    '25': 'News & Politics',
    '26': 'Howto & Style',
    '27': 'Education',  # ← Use this for educational videos
    '28': 'Science & Technology',
    '30': 'Movies',
    '31': 'Anime/Animation',
    '32': 'Action/Adventure',
    '33': 'Classics',
    '34': 'Comedies',
    '35': 'Documentaries',
    '36': 'Dramas',
    '37': 'Family',
    '38': 'Foreign',
    '39': 'Horror',
    '40': 'Sci-Fi/Fantasy',
    '41': 'Thrillers',
    '43': 'Show',
    '44': 'Trailer'
}

# Use category 27 for educational content
category_id = '27'
print(f"Category: {YOUTUBE_CATEGORIES[category_id]}")
```

---

### 5. **Timeout Issues**

#### Error: "Socket timeout" or "Connection reset by peer"

**Cause:** Slow internet or large file upload

**Solution:**
```python
# Increase timeout in upload.py
from googleapiclient.http import MediaFileUpload

media = MediaFileUpload(
    video_path,
    chunksize=1024 * 1024,  # 1MB chunks
    resumable=True,
    mimetype='video/mp4'
)

# The resumable=True is key for large files
# It allows resuming if connection drops
```

**For very slow connections:**
```bash
# Reduce chunk size in upload.py
chunksize=256 * 1024  # 256KB instead of 1MB
```

---

### 6. **Rate Limiting**

#### Error: "Too many requests" or API quota exceeded

**Cause:** Too many uploads in short time

**Solution:**
```python
# Add delays between uploads
import time

def batch_upload_safe(uploader, videos_list):
    for i, video in enumerate(videos_list):
        print(f"Uploading {i+1}/{len(videos_list)}...")
        
        # Upload
        video_id = uploader.upload_video(
            video['path'],
            video['title']
        )
        
        # Wait 5 minutes between uploads
        if i < len(videos_list) - 1:
            print("Waiting 5 minutes before next upload...")
            time.sleep(300)
```

**API Quota Info:**
- Free account: 15,000 units/day
- Each upload: ~6,000 units
- So: ~2 videos/day for free accounts

---

## Debugging Checklist

Before reporting an issue, check:

- [ ] `client_secrets.json` exists in `config/` folder
- [ ] YouTube Data API v3 is **enabled** in Google Cloud Console
- [ ] Credentials are not expired (delete `config/credentials.json` to refresh)
- [ ] Video file exists and is not corrupted
- [ ] Video file is in supported format (MP4, MOV, AVI, etc.)
- [ ] Video title is under 100 characters
- [ ] Video description is under 5000 characters
- [ ] Category ID is valid (27 for Education)
- [ ] API quota is not exceeded
- [ ] Internet connection is stable
- [ ] Account has upload permission

---

## Enable Debug Logging

To see detailed error messages:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Now run upload
uploader = YouTubeUploader()
video_id = uploader.upload_video(
    'test.mp4',
    'Test Video'
)
```

This will print detailed info about:
- API requests
- Authentication steps
- Upload progress
- Error details

---

## Still Having Issues?

1. **Check logs:**
   ```bash
   # View error logs (if enabled)
   cat logs/upload_errors.log
   ```

2. **Test with official YouTube API:**
   - Go to [Google API Explorer](https://developers.google.com/youtube/v3/docs/videos/insert)
   - Use "Try this API" to test directly

3. **Report on GitHub:**
   - Create an issue with:
     - Error message (full stack trace)
     - Steps to reproduce
     - Your Python version
     - Operating system

4. **YouTube Support:**
   - If account issue: https://support.google.com/youtube/
   - If quota issue: https://support.google.com/youtube/answer/

---

## Quick Fix Script

Run this to diagnose issues:

```python
#!/usr/bin/env python3
"""Diagnose YouTube API issues"""

import os
import json
import subprocess
from pathlib import Path

print("🔍 YouTube Automation - Diagnostics\n")

# Check 1: Files
print("1️⃣  Checking files...")
files_to_check = {
    'config/client_secrets.json': 'OAuth credentials',
    'requirements.txt': 'Dependencies list',
    'src/auth.py': 'Auth module'
}

for file_path, desc in files_to_check.items():
    exists = os.path.exists(file_path)
    status = "✅" if exists else "❌"
    print(f"   {status} {file_path}: {desc}")

# Check 2: Python packages
print("\n2️⃣  Checking Python packages...")
packages = [
    'google',
    'google_auth_oauthlib',
    'google_api_python_client'
]

for package in packages:
    try:
        __import__(package)
        print(f"   ✅ {package}")
    except ImportError:
        print(f"   ❌ {package} - Not installed")
        print(f"      Run: pip install {package}")

# Check 3: API credentials
print("\n3️⃣  Checking credentials...")
if os.path.exists('config/client_secrets.json'):
    with open('config/client_secrets.json') as f:
        creds = json.load(f)
    has_required = all(k in creds for k in ['client_id', 'client_secret'])
    status = "✅" if has_required else "❌"
    print(f"   {status} Credentials file is valid")
else:
    print("   ❌ client_secrets.json not found")

# Check 4: FFmpeg
print("\n4️⃣  Checking FFmpeg...")
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
    if result.returncode == 0:
        print("   ✅ FFmpeg installed")
    else:
        print("   ❌ FFmpeg not working properly")
except FileNotFoundError:
    print("   ❌ FFmpeg not installed")
    print("      Run: apt-get install ffmpeg")

print("\n✅ Diagnostics complete!")
```

Save as `diagnose.py` and run:
```bash
python diagnose.py
```
