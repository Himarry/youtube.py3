# youtube.py3

[![PyPI version](https://badge.fury.io/py/youtube-py3.svg)](https://badge.fury.io/py/youtube-py3)
[![Python versions](https://img.shields.io/pypi/pyversions/youtube-py3.svg)](https://pypi.org/project/youtube-py3/)
[![License: LOL](https://img.shields.io/badge/License-LOL-blue.svg)](LICENSE)

[🇯🇵 日本語](README.md) | 🇺🇸 English

youtube.py3 is a lightweight Python wrapper library for the YouTube Data API v3, designed to make integration quick and easy.

## 🚀 Quickstart

### Installation

```bash
pip install youtube-py3
```

### Basic Usage Example

```python
import os
from youtube_py3 import YouTubeAPI

# Retrieve your API key from an environment variable
api_key = os.getenv('YOUTUBE_API_KEY')
yt = YouTubeAPI(api_key)

# Fetch channel information
channel = yt.get_channel_info("UC_x5XG1OV2P6uZZ5FSM9Ttw")
print(f"Channel name: {channel['snippet']['title']}")

# Search for videos
videos = yt.search_videos("Python programming", max_results=5)
for video in videos:
    print(f"- {video['snippet']['title']}")
```

## 📚 Documentation

For detailed documentation, please refer to the `docs/` directory:

- [Installation Guide](docs/installation.md)
- [API Reference](docs/api_reference.md)
- [Examples](docs/examples/)
- [Troubleshooting](docs/troubleshooting.md)

## ⚠️ Important Notes

### About API Keys
- **This library does not include an API key.**
- Each user must obtain their own key from the Google Cloud Console.
- Users are responsible for managing their quota limits and securing their keys.

### How to Obtain an API Key
1. Visit the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable the YouTube Data API v3.
4. Generate an API key under **Credentials**.

## 📄 License

### Permissions
- ✅ Commercial use
- ✅ Use as a library (import and integrate)

### Prohibitions
- ❌ Modification or enhancement
- ❌ Redistribution or distribution (selling or distributing the library itself)
- ⚠️ The entry point of this package is compiled as a binary to prevent tampering, so the source is not directly viewable.
- ⚠️ If you encounter issues or have feature requests, please open an issue on GitHub with a detailed description.

For full details, see the [LICENSE](LICENSE) file.

---

**Note**: This is an unofficial wrapper for the YouTube Data API v3 and is not affiliated with or endorsed by Google or YouTube.