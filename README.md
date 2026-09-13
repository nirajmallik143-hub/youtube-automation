# YouTube Automation Tool

Automatically upload, schedule, and manage educational cartoon videos on YouTube with AI-powered metadata generation.

## Features

✅ **Video Upload Automation** - Upload multiple videos with automatic metadata
✅ **Smart Scheduler** - Schedule videos at optimal posting times
✅ **Metadata Generator** - Auto-generate titles, descriptions, tags
✅ **Thumbnail Creator** - Generate custom thumbnails automatically
✅ **Analytics Tracker** - Monitor video performance in real-time
✅ **Playlist Manager** - Organize videos into playlists automatically
✅ **Rate Limiting** - Safe posting (1-3 videos/day) to avoid spam detection

## Quick Start

### Prerequisites
- Python 3.8+
- YouTube API credentials
- FFmpeg (for thumbnail generation)

### Installation

```bash
git clone https://github.com/nirajmallik143-hub/youtube-automation.git
cd youtube-automation
pip install -r requirements.txt
```

### Configuration

1. Create a `config.json` file:
```json
{
  "youtube": {
    "api_key": "YOUR_API_KEY",
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET"
  },
  "upload_settings": {
    "max_videos_per_day": 2,
    "optimal_upload_time": "14:00",
    "category": "Education",
    "language": "en"
  },
  "metadata": {
    "channel_name": "Your Channel Name",
    "default_tags": ["educational", "cartoon", "learning"]
  }
}
```

2. Authenticate with YouTube:
```bash
python src/auth.py
```

## Usage

### Upload Single Video
```bash
python src/upload.py --video "path/to/video.mp4" --title "Video Title"
```

### Batch Upload
```bash
python src/batch_upload.py --folder "path/to/videos"
```

### Schedule Videos
```bash
python src/scheduler.py --config "schedule.csv"
```

### Generate Metadata
```bash
python src/metadata_generator.py --topic "Science" --count 5
```

### Track Analytics
```bash
python src/analytics.py --days 7
```

## Project Structure

```
youtube-automation/
├── src/
│   ├── auth.py              # YouTube API authentication
│   ├── upload.py            # Video upload logic
│   ├── batch_upload.py      # Batch upload handler
│   ├── scheduler.py         # Upload scheduler
│   ├── metadata_generator.py # AI metadata generation
│   ├── thumbnail_generator.py # Thumbnail creation
│   ├── analytics.py         # Analytics tracking
│   └── utils.py             # Helper functions
├── config/
│   ├── config.json          # Configuration file
│   └── credentials.json     # YouTube credentials
├── data/
│   ├── videos.csv           # Video metadata database
│   ├── schedule.csv         # Upload schedule
│   └── analytics.db         # Analytics database
├── templates/
│   ├── metadata_templates.json # Metadata templates
│   └── thumbnail_templates/    # Thumbnail templates
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Getting YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop application)
5. Download and save credentials as `credentials.json`
6. Add to `config.json`

## Safe Upload Limits

- **Free Account**: Max 15 uploads/day
- **Recommended**: 1-3 videos/day (sustainable & avoids spam detection)
- **Rate Limiting**: Built-in delays between uploads

## API Documentation

See [API_DOCS.md](docs/API_DOCS.md) for detailed endpoint documentation.

## Best Practices

1. **Content First** - Create quality videos before automating uploads
2. **Consistent Schedule** - Upload at same times for better engagement
3. **Monitor Performance** - Check analytics regularly
4. **Test Small** - Start with 1-2 videos before batch uploading
5. **Follow YouTube Policies** - Avoid spam triggers

## Troubleshooting

### Authentication Issues
```bash
python src/auth.py --refresh
```

### Upload Failures
Check `logs/upload_errors.log` for details

### Rate Limiting
The tool automatically adds delays. Don't bypass them!

## Contributing

Contributions welcome! Please submit pull requests.

## License

MIT License - See LICENSE file

## Support

For issues and questions: [GitHub Issues](https://github.com/nirajmallik143-hub/youtube-automation/issues)

---

**Made for Educational YouTube Creators** 🎓📺
