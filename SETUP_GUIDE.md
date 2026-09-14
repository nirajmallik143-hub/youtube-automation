# YouTube Automation - Complete Setup Guide

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Create Project** and enter a project name (e.g., "YouTube Automation")
3. Wait for project creation (2-3 seconds)

## Step 2: Enable YouTube Data API v3

1. In Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for **YouTube Data API v3**
3. Click on it and press **Enable**
4. Wait for activation

## Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth 2.0 Client ID**
3. Select **Desktop application** as the application type
4. Click **Create**
5. A popup shows your credentials - **click Download** (or Download JSON)
6. The downloaded file is your `client_secrets.json`

## Step 4: Set Up Your Project

### Local Setup (on your computer):

```bash
# 1. Clone the repository
git clone https://github.com/nirajmallik143-hub/youtube-automation.git
cd youtube-automation

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place credentials in config folder
# Copy your downloaded client_secrets.json to:
# config/client_secrets.json

# 4. Create config.json
# See next section for template
```

### Google Colab Setup:

```python
# In Colab, upload your client_secrets.json first

# Install dependencies
!pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Import and authenticate
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

SCOPES = ['https://www.googleapis.com/auth/youtube.upload',
          'https://www.googleapis.com/auth/youtube',
          'https://www.googleapis.com/auth/youtube.force-ssl']

def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return creds

creds = authenticate()
print("✅ Authentication successful!")
```

## Step 5: Create config/config.json

Create a file `config/config.json` in your project with this structure:

```json
{
  "youtube": {
    "type": "service_account",
    "project_id": "your-project-id",
    "private_key_id": "from-client-secrets",
    "private_key": "from-client-secrets",
    "client_email": "from-client-secrets",
    "client_id": "from-client-secrets",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "from-client-secrets"
  },
  "upload_settings": {
    "max_videos_per_day": 2,
    "optimal_upload_time": "14:00",
    "category": "27",
    "language": "en"
  },
  "metadata": {
    "channel_name": "Your Channel Name",
    "default_tags": ["educational", "cartoon", "learning"]
  }
}
```

**Alternative: Use client_secrets.json directly (simpler)**

Just copy your `client_secrets.json` to `config/` folder and the auth module will use it.

## Step 6: Test Authentication

```bash
# Run the authentication test
python src/auth.py
```

Or in Colab:
```python
from src.auth import YouTubeAuth

auth = YouTubeAuth()
creds = auth.authenticate()
print("✅ Connected to YouTube API successfully!")
```

## Step 7: Upload Your First Video

### Local:
```bash
python src/upload.py --video "test.mp4" --title "My First Video"
```

### Colab:
```python
from src.upload import YouTubeUploader

uploader = YouTubeUploader()

video_id = uploader.upload_video(
    video_path='test.mp4',
    title='My First Educational Video',
    description='This is an awesome educational video!',
    tags=['education', 'learning', 'tutorial'],
    category_id='27',  # Education category
    privacy_status='public'
)

print(f"✅ Video uploaded! ID: {video_id}")
```

## Troubleshooting

### Error: "client_secrets.json not found"
- Make sure you downloaded the OAuth credentials from Google Cloud Console
- Place it in the `config/` folder
- Check the filename: `client_secrets.json` (exact spelling)

### Error: "The caller does not have permission to access the resource"
- Make sure YouTube Data API v3 is **enabled** in Google Cloud
- Wait 2-3 minutes after enabling the API
- Re-authenticate by deleting `config/credentials.json` and running again

### Error: "Invalid OAuth scope"
- Make sure you're using the correct scopes:
  ```
  https://www.googleapis.com/auth/youtube.upload
  https://www.googleapis.com/auth/youtube
  https://www.googleapis.com/auth/youtube.force-ssl
  ```

### Upload takes too long
- Check your internet connection
- Reduce video file size or resolution
- The uploader uses 1MB chunks - this is normal

## What Each File Does

- **config/client_secrets.json** - Your Google OAuth credentials (download from Cloud Console)
- **config/credentials.json** - Auto-generated after first authentication (do not edit)
- **src/auth.py** - Handles authentication and token refresh
- **src/upload.py** - Handles video uploads (single or batch)

## API Quotas

YouTube API has quotas:
- **Free tier**: 15,000 units/day
- Each video upload: ~6,000 units
- So you can upload ~2 videos/day for free

The tool has built-in rate limiting to respect quotas.

## Next Steps

1. ✅ Set up credentials (Steps 1-5 above)
2. ✅ Test authentication (Step 6)
3. ✅ Upload test video (Step 7)
4. Then modify `metadata_generator.py` for AI-powered titles/descriptions
5. Use `scheduler.py` to schedule uploads

---

**Questions?** Check the [Issues](https://github.com/nirajmallik143-hub/youtube-automation/issues) page or submit a new issue.
