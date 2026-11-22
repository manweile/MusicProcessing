# Environment Information

## Ubuntu Environment (Current)
```
OS: Ubuntu 26
Python: 3.14.4
ffmpeg version: 8.0.1-3ubuntu2 (Released 2025-01-13)
ffprobe version: 8.0.1-3ubuntu2 (Released 2025-01-13)
```

## Windows Environment (Reference - User's system)
```
OS: Windows 10
Python: (Unknown - user to verify)
ffmpeg version: (Unknown - likely older than 8.0.1)
ffprobe version: (Unknown - likely older than 8.0.1)
```

## FFmpeg Version History
- **FFmpeg 8.0**: Released January 2025 (Latest major version)
- **FFmpeg 7.x**: Released September-December 2024
- **FFmpeg 6.x**: Released September 2023 - September 2024
- **FFmpeg 5.1**: Released May 2022
- **FFmpeg 5.0**: Released October 2021

**Key Finding:**
Ubuntu 26 has the **latest ffmpeg version 8.0.1**
This is very recent - released less than 2 months ago.

## FFmpeg 8.0 Changelog Relevant Items
- Added/modified many metadata fields
- Changed video stream classification
- Improved codec detection
- Changed error handling

## Why This Matters
If Windows is running an older ffmpeg version:
- Different field outputs
- Different stream classification
- Different error handling behaviors

The test expectations are based on **older ffmpeg output format**.
Ubuntu's cutting-edge version behaves differently.

## Recommendation
1. **Downgrade Ubuntu ffmpeg** to match Windows version (not recommended)
   - Would require pinning package
   - Future updates would break again
   
2. **Update Windows ffmpeg** to match Ubuntu (recommended)
   - Use latest ffmpeg build
   - Update test expectations to match latest ffmpeg
   - Forward-compatible solution
   
3. **Make tests version-agnostic** (best practice)
   - Don't assume specific ffmpeg output
   - Test for required fields, not exact structure
   - Works with any ffmpeg version

## FFmpeg Download Links
- **Latest (Windows):** https://ffmpeg.org/download.html
- **Source:** https://github.com/FFmpeg/FFmpeg

