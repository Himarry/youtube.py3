<!--
YouTube.py3 - High-Functionality Python Wrapper for YouTube Data API v3
-->

# YouTube.py3

> **High-functionality Python wrapper for YouTube Data API v3**  
> Ideal for private use, automation, CLI, and binary distribution

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![YouTube API v3](https://img.shields.io/badge/YouTube%20API-v3-red)](https://developers.google.com/youtube/v3)

---

## Overview

A Python wrapper for YouTube Data API v3 that provides a **simple yet powerful interface** for all major features (videos, channels, playlists, search, comments, etc).

- **Works with API key only**
- **Supports CLI/automation/binary distribution**
- **Includes type hints, robust exceptions, pagination, and OAuth utilities**

---

## Main Features

| Category      | Supported Features Example                        |
|:-------------|:--------------------------------------------------|
| Videos       | Single/multiple video info, pagination            |
| Channels     | Search, info, get latest video ID                 |
| Playlists    | List/details, pagination                          |
| Search       | Video/channel search, pagination                  |
| Comments     | Viewer only, no replies, pagination               |
| Config Mgmt  | API key, channel ID, config file management       |
| OAuth        | Google OAuth2 flow (utility included)             |
| Exceptions   | Fine-grained for API/auth/quota/feature errors    |

---

## Installation

```sh
pip install -r requirements.txt
```

---

## Quick Start

```python
from youtube_py3 import YouTube

yt = YouTube(api_key="YOUR_API_KEY")
# Get video info
info = yt.videos.get_video("VIDEO_ID")
# Get comments (viewer only, no replies, paginated)
for c in yt.comments.get_viewer_comments_paginated("VIDEO_ID", "CHANNEL_ID"):
    print(c)
```

> **See [Reference.md](Reference.md) for detailed usage and API reference.**

---

## Notes

- **Get your API key from Google Cloud Console**
- YouTube Data API v3 terms and quota limits apply
- This library is intended for private use

## Binary Distribution & Source Code Policy

- This package is distributed as binaries (.pyd built with Nuitka) only; no source code (.py) is included.
- There are no plans to make the source code public or open source.
- If you want to see the code, you must reverse-engineer it yourself (at your own risk).

---

## License

MIT License

---
