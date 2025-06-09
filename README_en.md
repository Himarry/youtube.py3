※This library is created for private use only. Not all features are included, but basic usage and available functions are briefly described in Reference.md.※

# YouTube.py3

Private Python wrapper library for YouTube Data API v3.

## Features
- Basic features: video, channel, playlist, search, and comment retrieval
- Comment retrieval supports filters (viewer only, no replies, pagination, etc.)
- API key only (no OAuth required)

## Installation
```
pip install -r requirements.txt
```

## Usage
See `Reference.md` for usage and available features.

```python
from youtube_py3 import YouTube

yt = YouTube(api_key="YOUR_API_KEY")
info = yt.videos.get_video("VIDEO_ID")
for c in yt.comments.get_viewer_comments_paginated("VIDEO_ID", "CHANNEL_ID"):
    print(c)
```

## Notes
- Get your API key from Google Cloud Console
- Be aware of API quota/limits

## License
MIT
