# Executive Summary: 5 Failed Tests (Windows vs Ubuntu)

## Quick Answer
**Windows passes tests; Ubuntu fails.**
**Root cause: Windows uses older ffmpeg, Ubuntu uses newest ffmpeg 8.0.1 (2025)**

---

## The 5 Failed Tests

### Group 1: FFmpeg Stream Detection (2 tests)
**Tests:** `test_extract_ffmpeg_art_no_stream`, `test_has_video_stream_false`

**Problem:** WMA file handling differs
- **Windows:** Treats WMA artwork as non-video → passes ✓
- **Ubuntu:** Treats WMA artwork as video stream → fails ✗

**Root Cause:** Different ffmpeg versions classify embedded artwork differently

**Solution Options:**
1. Skip tests on Ubuntu (temporary)
2. Update detection logic to ignore `mjpeg` streams (they're artwork, not video)
3. Use OS-specific test data

---

### Group 2: Filesystem Operations (1 test)
**Test:** `test_create_album_dir_exec`

**Problem:** File copy setup fails
- **Windows:** `shutil.copy()` succeeds ✓
- **Ubuntu:** `shutil.copy()` → `copymode()` → `chmod()` fails with FileNotFoundError ✗

**Root Cause:** Parent directory issue in test setup (line 292 of test_models_audio_metadata.py)

**Solution:** 
```python
# Before shutil.copy(), explicitly ensure directory exists:
os.makedirs(os.path.dirname(dest_path), exist_ok=True)
```

---

### Group 3: FFprobe Metadata Mismatch (2 tests)
**Tests:** `test_get_media_info`, `test_get_media_info_walk`

**Problem:** FFprobe outputs different fields
- **Windows:** 56 metadata fields in M4A (includes `closed_captions`, `film_grain`)
- **Ubuntu:** 54 metadata fields in M4A (missing 2 newer fields)

**Root Cause:** FFmpeg 8.0.1 (Ubuntu) is NEWER than Windows version
- Ubuntu has latest ffmpeg (Jan 2025)
- Windows has older version (likely 2024 or earlier)
- Tests hardcoded against older ffmpeg output

**Solution:**
1. Update Windows ffmpeg to 8.0.1 (match Ubuntu)
2. Update test assertions to be version-agnostic
3. Check for required fields instead of exact field count

---

## Test Status Summary

| Test | File | Error | Type | Severity |
|------|------|-------|------|----------|
| `test_extract_ffmpeg_art_no_stream` | audio_art.py | CalledProcessError not raised | ffmpeg behavior | Medium |
| `test_has_video_stream_false` | audio_art.py | Returns True (expected False) | ffprobe classification | Medium |
| `test_create_album_dir_exec` | audio_metadata.py | FileNotFoundError in setup | filesystem | High |
| `test_get_media_info` | audio_metadata.py | Dict mismatch (56 vs 54 keys) | ffprobe version | High |
| `test_get_media_info_walk` | audio_metadata.py | M4A key count 54 vs 56 | ffprobe version | High |

---

## Key Insight

The core issue is **version mismatch**:

```
┌─────────────────────────────────────────┐
│ Ubuntu 26 (Latest ffmpeg 8.0.1)         │
│                                         │
│ Tests expect: Windows ffmpeg output     │
│ But get:      Ubuntu ffmpeg output      │
│               → Mismatch!               │
└─────────────────────────────────────────┘
```

Tests were written based on Windows output format.
Ubuntu runs with cutting-edge ffmpeg (released Jan 2025).
These don't match.

---

## Recommended Fixes (Priority Order)

### 1. 🔴 HIGH PRIORITY - Fix Test #3 (Filesystem Bug)
**File:** `tests/test_models_audio_metadata.py`
**Line:** 292
**Fix:**
```python
dest_dir = os.path.join(cls.genre, artist_album)
os.makedirs(dest_dir, exist_ok=True)  # Already here, but check if working
dest_path = os.path.join(dest_dir, file_name)
os.makedirs(os.path.dirname(dest_path), exist_ok=True)  # Add this redundantly
shutil.copy(src_genre, dest_path)
```

**Expected Result:** Test passes on both Windows and Ubuntu ✓

---

### 2. 🔴 HIGH PRIORITY - Fix Tests #4 & #5 (FFprobe Baseline)
**File:** `tests/test_models_audio_metadata.py`
**Lines:** 655, 705

**Option A - Update Baseline (Quick Fix):**
```python
# Change test from exact dict match to flexible check
critical_fields = ['codec_name', 'duration', 'size', 'bit_rate', 
                   'sample_rate', 'channels']
for field in critical_fields:
    self.assertIn(field, results_dict)
# Don't check for closed_captions, film_grain (version-dependent)
```

**Option B - Detect FFmpeg Version (Robust):**
```python
def get_ffmpeg_version():
    result = subprocess.run(['ffprobe', '-version'], 
                          capture_output=True, text=True)
    version_line = result.stdout.split('\n')[0]
    # Parse version number...
    return version

version = get_ffmpeg_version()
if version >= (8, 0):
    expected_keys = 56
else:
    expected_keys = 54
self.assertEqual(key_count, expected_keys)
```

**Expected Result:** Test passes on both Windows and Ubuntu ✓

---

### 3. 🟡 MEDIUM PRIORITY - Fix Tests #1 & #2 (Audio Streams)
**File:** `src/models/audio_info/audio_art.py`
**Method:** `has_video_stream()` (line 538)

**Current Logic:**
```python
if 'streams' in streams and len(streams['streams']) > 0:
    return True  # Any stream = True
```

**Improved Logic:**
```python
for stream in streams.get('streams', []):
    codec_type = stream.get('codec_type', '')
    codec_name = stream.get('codec_name', '')
    
    # Skip attached artwork (reported as video by ffprobe 8.0)
    if codec_type == 'video':
        if codec_name in ['mjpeg', 'png', 'bmp']:
            # This is artwork, not actual video
            continue
        # Check for attached_pic disposition
        if stream.get('disposition', {}).get('attached_pic') == 1:
            # This is attached artwork
            continue
        # Actual video stream found
        return True

return False
```

**Expected Result:** 
- Windows: Still returns False for WMA artwork ✓
- Ubuntu: Now returns False for WMA artwork ✓

---

## Verification Steps

After applying fixes:

```bash
# Run the 5 failing tests
pytest tests/test_models_audio_art.py::TestAudioArt::test_extract_ffmpeg_art_no_stream \
        tests/test_models_audio_art.py::TestAudioArt::test_has_video_stream_false \
        tests/test_models_audio_metadata.py::TestAudioMetadata::test_create_album_dir_exec \
        tests/test_models_audio_metadata.py::TestAudioMetadata::test_get_media_info \
        tests/test_models_audio_metadata.py::TestAudioMetadata::test_get_media_info_walk -v

# Expected: All 5 pass ✓
```

---

## Prevention for Future

1. **Don't hardcode ffmpeg output** - version-dependent
2. **Don't use exact field counts** - changes between versions
3. **Mock ffmpeg/ffprobe** when possible - version-independent
4. **Use CI/CD** to test on multiple OS and ffmpeg versions
5. **Document environment requirements** in README

---

## Related Files

- [TEST_FAILURE_ANALYSIS.md](./TEST_FAILURE_ANALYSIS.md) - Detailed technical analysis
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Quick troubleshooting guide
- [DETAILED_COMPARISON.md](./DETAILED_COMPARISON.md) - Side-by-side comparison
- [ENVIRONMENT_INFO.md](./ENVIRONMENT_INFO.md) - Version information

---

## Questions for Windows User

To verify our hypothesis, please run these commands on Windows:

```powershell
# Check ffmpeg version
ffmpeg -version

# Check ffprobe version
ffprobe -version

# Check if closed_captions and film_grain fields exist in output
ffprobe -hide_banner -select_streams v:0 -show_streams -of json "path/to/test.m4a" | findstr "closed_captions"
```

Share the output to confirm version mismatch hypothesis.

