# YouTube Automation Setup Guide

## Step 1: Get YouTube API Credentials

### Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "NEW PROJECT"
4. Enter project name (e.g., "YouTube Automation")
5. Click "CREATE"

### Enable YouTube Data API
1. In Cloud Console, go to "APIs & Services" → "Library"
2. Search for "YouTube Data API v3"
3. Click on it and press "ENABLE"

### Create OAuth 2.0 Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "+ CREATE CREDENTIALS"
3. Choose "OAuth client ID"
4. Select "Desktop application"
5. Click "CREATE"
6. Download the JSON file
7. Rename and save as `config/credentials.json`

## Step 2: Install Python Dependencies

```bash
# Clone the repository
git clone https://github.com/nirajmallik143-hub/youtube-automation.git
cd youtube-automation

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure the Application

1. Copy the example config:
```bash
cp config/config.example.json config/config.json
```

2. Edit `config/config.json`:
   - Add your YouTube API credentials
   - Set upload preferences
   - Configure AI metadata (optional)

## Step 4: First Authentication

```bash
python src/auth.py
```

This will:
1. Open a browser for authentication
2. Ask for YouTube permissions
3. Save credentials locally

## Step 5: Test Upload

```bash
# Test with a sample video
python src/upload.py
```

## Troubleshooting

### "Credentials not found"
- Run `python src/auth.py` again
- Make sure `config/credentials.json` exists

### "API not enabled"
- Go to Google Cloud Console
- Enable YouTube Data API v3
- Wait 5-10 minutes for changes to propagate

### "Invalid authentication"
- Delete `config/credentials.json`
- Run `python src/auth.py` again

## Next Steps

1. **Prepare your videos** - Have MP4 files ready
2. **Create metadata** - Titles, descriptions, tags
3. **Schedule uploads** - Set up posting schedule
4. **Monitor analytics** - Track video performance

---

For more help, check [API_DOCS.md](API_DOCS.md) or open an issue on GitHub.
