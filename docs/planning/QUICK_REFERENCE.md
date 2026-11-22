# Quick Reference: 5 Failed Tests

## 1️⃣ test_extract_ffmpeg_art_no_stream
- **Status:** ❌ FAILED (Expected exception not raised)
- **Why:** ffmpeg on Ubuntu doesn't throw error for missing video stream in WMA
- **Fix:** Handle both error and non-error cases OR skip test on Ubuntu

## 2️⃣ test_has_video_stream_false  
- **Status:** ❌ FAILED (Returns True, expected False)
- **Why:** Ubuntu's ffprobe treats embedded artwork as a video stream
- **Fix:** Update stream detection logic OR use OS-specific assertion

## 3️⃣ test_create_album_dir_exec
- **Status:** ❌ ERROR (FileNotFoundError during setup)
- **Why:** `shutil.copymode()` fails on Linux - destination file issue
- **Fix:** Ensure parent directory exists before copy
  ```python
  os.makedirs(os.path.dirname(dest_path), exist_ok=True)
  shutil.copy(src_genre, dest_path)
  ```

## 4️⃣ test_get_media_info
- **Status:** ❌ FAILED (Dictionary mismatch)
- **Why:** ffprobe outputs different fields; Ubuntu missing `closed_captions`, `film_grain`
- **Fix:** Use flexible assertions for critical fields instead of exact dict match

## 5️⃣ test_get_media_info_walk
- **Status:** ❌ FAILED (Expected 56 keys, got 54)
- **Why:** Ubuntu's ffprobe for M4A returns 54 keys instead of 56
- **Fix:** Check for required fields instead of exact key count

---

## Root Cause Categories

### 🔴 ffprobe/ffmpeg Version Differences (3 tests)
- Tests #2, #4, #5
- Ubuntu has older/different ffmpeg build
- Missing newer metadata fields

### 🟠 ffmpeg Behavior Differences (1 test)
- Test #1
- Different error handling for missing streams

### 🟡 Linux Filesystem Permissions (1 test)
- Test #3
- `shutil.copymode()` strict on POSIX systems

---

## Quick Fixes Priority

```
1. 🔴 HIGH   - Test #3: Fix shutil.copy setup bug
2. 🔴 HIGH   - Tests #4,#5: Update ffprobe assertion logic
3. 🟡 MEDIUM - Tests #1,#2: Add OS detection or mocking
```

---

## Test Commands

**Run all 5 failing tests:**
```bash
pytest tests/test_models_audio_art.py::TestAudioArt::test_extract_ffmpeg_art_no_stream \
        tests/test_models_audio_art.py::TestAudioArt::test_has_video_stream_false \
        tests/test_models_audio_metadata.py::TestAudioMetadata::test_create_album_dir_exec \
        tests/test_models_audio_metadata.py::TestAudioMetadata::test_get_media_info \
        tests/test_models_audio_metadata.py::TestAudioMetadata::test_get_media_info_walk -v
```

**Run just the audio_art tests:**
```bash
pytest tests/test_models_audio_art.py::TestAudioArt::test_extract_ffmpeg_art_no_stream \
        tests/test_models_audio_art.py::TestAudioArt::test_has_video_stream_false -v
```

**Run just the audio_metadata tests:**
```bash
pytest tests/test_models_audio_metadata.py::TestAudioMetadata::test_create_album_dir_exec \
        tests/test_models_audio_metadata.py::TestAudioMetadata::test_get_media_info \
        tests/test_models_audio_metadata.py::TestAudioMetadata::test_get_media_info_walk -v
```

---

## Environment Info

**Ubuntu System:**
- OS: Ubuntu 26
- Python: 3.14.4
- ffmpeg/ffprobe: Installed via package manager (likely older version)

**Windows System (reference):**
- OS: Windows 10
- ffmpeg/ffprobe: Likely newer or manually installed

**Key Difference:** Ubuntu uses older ffmpeg from package repos; Windows likely has newer build.

---

## Code Examples

### Problem: test_create_album_dir_exec
**Current code fails:**
```python
shutil.copy(src_genre, dest_path)  # Fails on Linux with FileNotFoundError
```

**Fixed code:**
```python
# Ensure parent directories exist
os.makedirs(os.path.dirname(dest_path), exist_ok=True)
shutil.copy(src_genre, dest_path)  # Now works on both OS
```

### Problem: test_get_media_info_walk
**Current assertion is too strict:**
```python
# Fails when ffprobe versions differ in field count
self.assertIn(f"{self.m4a_line} has 56 keys\n", lines)
```

**Better approach:**
```python
# Check for required fields instead of exact count
required_fields = ['codec_name', 'duration', 'size', 'bit_rate']
for field in required_fields:
    self.assertIn(f"key: {field}", output_line)
```

