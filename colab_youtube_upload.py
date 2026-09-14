"""
Google Colab - YouTube Video Upload Example
============================================

This is a complete step-by-step guide to upload videos to YouTube from Colab.

HOW TO USE:
1. Open this file in Google Colab
2. Run each cell in order
3. Upload your client_secrets.json when prompted
4. Create a test video
5. Upload it to YouTube

"""

# ============================================================================
# STEP 1: Install Required Libraries
# ============================================================================

print("📦 Installing YouTube API libraries...")
import subprocess
import sys

subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", 
                      "google-auth-oauthlib",
                      "google-auth-httplib2", 
                      "google-api-python-client"])

print("✅ Libraries installed!")

# ============================================================================
# STEP 2: Upload client_secrets.json
# ============================================================================

print("\n📝 Upload your client_secrets.json file...")
print("Steps to get it:")
print("1. Go to https://console.cloud.google.com/")
print("2. Create a new project")
print("3. Enable 'YouTube Data API v3'")
print("4. Go to Credentials → Create OAuth 2.0 Client ID (Desktop app)")
print("5. Download the JSON file")
print("\n")

from google.colab import files
print("Click 'Choose Files' below and select client_secrets.json:")
uploaded = files.upload()

if 'client_secrets.json' in uploaded:
    print("✅ client_secrets.json uploaded successfully!")
else:
    print("❌ File not found. Please upload client_secrets.json")
    sys.exit(1)

# ============================================================================
# STEP 3: Authenticate with YouTube
# ============================================================================

print("\n🔐 Authenticating with YouTube API...")

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import pickle
import os

SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

def authenticate_youtube():
    """Authenticate and return YouTube API service"""
    credentials = None
    
    # Try to load cached credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
            print("✅ Loaded cached credentials")
    
    # If no credentials or expired, perform OAuth flow
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("🔄 Refreshing expired credentials...")
            credentials.refresh(Request())
        else:
            print("🔐 Starting OAuth authentication flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', 
                SCOPES
            )
            credentials = flow.run_local_server(port=0)
        
        # Save credentials for next time
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
            print("💾 Credentials saved")
    
    # Build YouTube API service
    youtube = build('youtube', 'v3', credentials=credentials)
    print("✅ Successfully authenticated with YouTube API!")
    
    return youtube

youtube = authenticate_youtube()

# ============================================================================
# STEP 4: Create a Test Video (5 seconds)
# ============================================================================

print("\n🎬 Creating a test video (5 seconds)...")
print("Installing FFmpeg...")

subprocess.check_call(['apt-get', 'update', '-qq'])
subprocess.check_call(['apt-get', 'install', '-y', '-qq', 'ffmpeg'])

print("Generating test video...")
subprocess.check_call([
    'ffmpeg', 
    '-f', 'lavfi', 
    '-i', 'color=c=blue:s=1280x720:d=5',
    '-f', 'lavfi', 
    '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
    '-shortest',
    '-c:v', 'libx264',
    '-c:a', 'aac',
    '-b:a', '128k',
    '-pix_fmt', 'yuv420p',
    'test.mp4',
    '-y'
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print("✅ Test video created: test.mp4")

# Check file size
file_size = os.path.getsize('test.mp4') / (1024 * 1024)  # Convert to MB
print(f"📊 File size: {file_size:.2f} MB")

# ============================================================================
# STEP 5: Upload Video to YouTube
# ============================================================================

print("\n📤 Uploading video to YouTube...")
print("This may take 1-5 minutes depending on file size...\n")

from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

def upload_video(youtube, video_file, title, description, tags=None, 
                 category_id='27', privacy_status='public'):
    """
    Upload a video to YouTube
    
    Args:
        youtube: YouTube API service object
        video_file: Path to video file
        title: Video title (max 100 chars)
        description: Video description (max 5000 chars)
        tags: List of tags
        category_id: YouTube category ID (27=Education)
        privacy_status: 'public', 'unlisted', or 'private'
    
    Returns:
        Video ID if successful, None otherwise
    """
    
    try:
        # Prepare video metadata
        body = {
            'snippet': {
                'title': title[:100],
                'description': description[:5000],
                'tags': tags or [],
                'categoryId': category_id,
                'defaultLanguage': 'en'
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Create media upload object
        media = MediaFileUpload(
            video_file,
            chunksize=1024 * 1024,  # 1MB chunks
            resumable=True,
            mimetype='video/mp4'
        )
        
        print(f"📝 Uploading: {title}")
        print(f"📊 File: {video_file}")
        print(f"🏷️  Tags: {', '.join(tags)}")
        print(f"👁️  Privacy: {privacy_status}\n")
        
        # Create insert request
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        # Execute upload with progress tracking
        response = None
        while response is None:
            try:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"⏳ Upload progress: {progress}%", end='\r')
            except HttpError as e:
                print(f"\n❌ Upload error: {e}")
                return None
        
        video_id = response['id']
        print(f"\n✅ Video uploaded successfully!")
        print(f"🎬 Video ID: {video_id}")
        print(f"🔗 URL: https://www.youtube.com/watch?v={video_id}")
        
        return video_id
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None

# Upload the test video
video_id = upload_video(
    youtube,
    video_file='test.mp4',
    title='Test Video from YouTube Automation',
    description='This is a test video uploaded using YouTube Automation tool. This demonstrates successful API integration!',
    tags=['education', 'automation', 'test', 'tutorial'],
    category_id='27',  # Education category
    privacy_status='unlisted'  # Change to 'public' when ready
)

# ============================================================================
# STEP 6: Display Results
# ============================================================================

if video_id:
    print("\n" + "="*60)
    print("🎉 SUCCESS! Your video has been uploaded!")
    print("="*60)
    print(f"\n📺 Video ID: {video_id}")
    print(f"🔗 Watch it here: https://www.youtube.com/watch?v={video_id}")
    print("\n📌 Next Steps:")
    print("1. Go to YouTube Studio to review the video")
    print("2. Add a custom thumbnail")
    print("3. Change privacy status to 'public'")
    print("4. Add more videos and schedule uploads")
    print("\n💡 Tips:")
    print("- Use privacy_status='private' for drafts")
    print("- Use privacy_status='unlisted' for testing")
    print("- Use privacy_status='public' for published videos")
    print("="*60)
else:
    print("\n❌ Upload failed. Check the error messages above.")

# ============================================================================
# BONUS: Batch Upload Function
# ============================================================================

def batch_upload_videos(youtube, videos_list, delay_seconds=300):
    """
    Upload multiple videos with delay between them
    
    Args:
        youtube: YouTube API service
        videos_list: List of dicts with video info
                    Example: [
                        {
                            'path': 'video1.mp4',
                            'title': 'Video 1',
                            'description': 'Description',
                            'tags': ['tag1', 'tag2']
                        },
                        ...
                    ]
        delay_seconds: Delay between uploads (default 5 minutes)
    
    Returns:
        List of uploaded video IDs
    """
    import time
    
    uploaded_ids = []
    
    for i, video in enumerate(videos_list):
        print(f"\n📤 Uploading video {i+1}/{len(videos_list)}...")
        
        video_id = upload_video(
            youtube,
            video_path=video['path'],
            title=video.get('title', 'Untitled'),
            description=video.get('description', ''),
            tags=video.get('tags', []),
            category_id=video.get('category_id', '27'),
            privacy_status=video.get('privacy_status', 'unlisted')
        )
        
        if video_id:
            uploaded_ids.append(video_id)
        
        # Delay before next upload
        if i < len(videos_list) - 1:
            print(f"\n⏱️  Waiting {delay_seconds}s before next upload...")
            time.sleep(delay_seconds)
    
    print(f"\n✅ Batch upload complete: {len(uploaded_ids)} videos uploaded")
    return uploaded_ids

print("\n" + "="*60)
print("✅ Colab notebook setup complete!")
print("="*60)
print("\nYou can now use these functions:")
print("- upload_video() - Upload a single video")
print("- batch_upload_videos() - Upload multiple videos")
print("\nExample:")
print("""
video_id = upload_video(
    youtube,
    video_file='my_video.mp4',
    title='My Educational Video',
    description='Learn something awesome!',
    tags=['education', 'learning'],
    privacy_status='unlisted'
)
""")
