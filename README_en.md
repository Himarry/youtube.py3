# youtube.py3

[![PyPI version](https://badge.fury.io/py/youtube-py3.svg)](https://badge.fury.io/py/youtube-py3)
[![Python versions](https://img.shields.io/pypi/pyversions/youtube-py3.svg)](https://pypi.org/project/youtube-py3/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python wrapper library for easy use of YouTube Data API v3.

## 🎯 Features

- **Beginner-friendly**: Simplified complex API parameters
- **Rich functionality**: Video, channel, playlist, and comment management
- **Automated processing**: Pagination and error handling
- **Japanese support**: Easy-to-understand method names and descriptions

## 🚀 Quick Start

### Installation

```bash
pip install youtube-py3
```

### Basic Usage Example

```python
import os
from youtube_py3 import YouTubeAPI

# Get API key from environment variable
api_key = os.getenv('YOUTUBE_API_KEY')
yt = YouTubeAPI(api_key)

# Get channel information
channel = yt.get_channel_info("UC_x5XG1OV2P6uZZ5FSM9Ttw")
print(f"Channel name: {channel['snippet']['title']}")

# Search videos
videos = yt.search_videos("Python programming", max_results=5)
for video in videos:
    print(f"- {video['snippet']['title']}")
```

## 📚 Documentation

For detailed documentation, please see the [docs/](docs/) folder:

- [Installation Guide](docs/installation.md)
- [API Reference](docs/api_reference.md)
- [Examples](docs/examples/)
- [Troubleshooting](docs/troubleshooting.md)

## ⚠️ Important Notes

### About API Keys
- **This library does not include an API key**
- Each user must obtain an API key individually from Google Cloud Console
- API key usage limits and security are managed by each user

### How to Get an API Key
1. Access [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable YouTube Data API v3
4. Create an API key from credentials

#

**Note**: This library is an unofficial wrapper for YouTube Data API v3. It is not affiliated with Google/YouTube.