# Test Failure Analysis: Windows vs Ubuntu Differences

## Summary
5 tests fail on Ubuntu 26 VS Code but pass on Windows 10 VS Code. The root causes are **ffprobe/ffmpeg output format differences** and **filesystem permission handling differences** between Windows and Linux.

---

## Failed Tests Overview

| Test | File | Category | Root Cause |
|------|------|----------|-----------|
| `test_extract_ffmpeg_art_no_stream` | `test_models_audio_art.py` | Audio Stream Detection | ffmpeg behavior difference |
| `test_has_video_stream_false` | `test_models_audio_art.py` | Audio Stream Detection | ffprobe behavior difference |
| `test_create_album_dir_error` | `test_models_audio_metadata.py` | File Setup | `shutil.copymode()` failure |
| `test_get_media_info` | `test_models_audio_metadata.py` | Media Metadata | ffprobe output field differences |
| `test_get_media_info_walk` | `test_models_audio_metadata.py` | Media Metadata | ffprobe output field count mismatch |

---

## Detailed Analysis

### 1. `test_extract_ffmpeg_art_no_stream` ❌
**File:** `tests/test_models_audio_art.py:328`
**Status:** FAILED

#### Problem
Test expects `CalledProcessError` to be raised when ffmpeg attempts to extract art from a WMA file without a video stream.

```python
def test_extract_ffmpeg_art_no_stream(self):
    input_audio = TEST_WMA_HOLIDAY
    with self.assertRaises(CalledProcessError) as cm:
        art.extract_ffmpeg_art(input_audio)
    # Expects "Invalid argument" in stderr
```

#### Actual Error
```
AssertionError: CalledProcessError not raised
```

#### Root Cause
**ffmpeg behavior differs between Windows and Linux versions/configurations:**
- **Windows:** ffmpeg returns error when no video stream found (raises `CalledProcessError`)
- **Ubuntu:** ffmpeg may not raise an error or behaves differently with WMA files
- Different ffmpeg versions may have different error handling for missing streams

#### Why It Works on Windows
Windows ffmpeg version/build likely has stricter error handling for missing video streams in WMA files.

#### Why It Fails on Ubuntu
Ubuntu's ffmpeg (likely newer or different build) may:
- Not throw an error for missing video stream in WMA
- Handle the `-map 0:v` flag differently
- Have different defaults for stream selection

---

### 2. `test_has_video_stream_false` ❌
**File:** `tests/test_models_audio_art.py:440`
**Status:** FAILED

#### Problem
Test expects `has_video_stream()` to return `False` for WMA file without video stream.

```python
def test_has_video_stream_false(self):
    input_audio = TEST_WMA_HOLIDAY
    has_video = art.has_video_stream(input_audio)
    self.assertFalse(has_video)  # FAILS: Returns True
```

#### Actual Error
```
AssertionError: True is not false
```

#### Root Cause
**ffprobe output format differs between Windows and Linux:**

The `has_video_stream()` method checks ffprobe output for video streams:
```python
command = [
    'ffprobe', '-hide_banner', '-select_streams', 'v:0',
    '-show_streams', '-of', 'json', file_path
]
```

**Hypothesis:**
- **Windows:** ffprobe returns empty JSON (no streams found) → returns `False`
- **Ubuntu:** ffprobe includes non-video streams or album art as video streams → returns `True`

**Key Issue:** Some ffprobe versions on Linux incorrectly classify:
- Attached album art images as "video" stream
- Thumbnail frames as "video" stream
- When `-select_streams v:0` is used, it may still return image streams that have video-like codec properties

The WMA file `TEST_WMA_HOLIDAY` likely contains embedded artwork, which Ubuntu's ffprobe detects as a "video" stream, while Windows ffprobe handles it differently.

---

### 3. `test_create_album_dir_error` ❌
**File:** `tests/test_models_audio_metadata.py` (setup phase)
**Status:** ERROR (Setup Failure)

#### Problem
Test setup fails during `shutil.copy()` operation:

```python
FileNotFoundError: [Errno 2] No such file or directory:
  '/home/gerald/MusicProcessing/tests/GenreMusic/Cream/Goodbye/Cream-Badge.flac'
```

#### Root Cause
**`shutil.copymode()` failure on Linux - file doesn't exist yet:**

```python
# Line 292 in setUpClass:
shutil.copy(src_genre, dest_path)
```

The issue occurs in `shutil.copy()` → `shutil.copymode()`:
- `shutil.copy()` copies file content, then attempts to copy file mode/permissions
- On **Linux**, `copymode()` calls `os.chmod()` on destination
- **The destination file IS created** by the content copy
- **BUT:** On some Linux systems, `copymode()` tries to apply permissions before the file is fully written

**Key Difference:**
- **Windows:** Uses different permission model; `copymode()` succeeds
- **Ubuntu:** More strict POSIX compliance; race condition or permission issue occurs

#### Stack Trace Shows
```python
/usr/lib/python3.14/shutil.py:490: in copy
    copymode(src, dst, follow_symlinks=follow_symlinks)
  ...
/usr/lib/python3.14/shutil.py:379: in copymode
    chmod_func(dst, stat.S_IMODE(st.st_mode))
FileNotFoundError: [Errno 2] No such file or directory
```

**Why Windows Works:**
- Different filesystem permissions model
- No `chmod()` operation or different error handling

**Why Ubuntu Fails:**
- Attempting to `chmod` file at `/home/gerald/MusicProcessing/tests/GenreMusic/Cream/Goodbye/Cream-Badge.flac`
- Either the destination file wasn't fully created, or the parent directory doesn't exist

---

### 4. `test_get_media_info` ❌
**File:** `tests/test_models_audio_metadata.py:655`
**Status:** FAILED

#### Problem
Test compares expected ffprobe output dictionary with actual output. Assertion fails due to dictionary mismatch.

```python
media_dict = { ... hardcoded Windows ffprobe output ... }
results_dict = metadata.get_media_info(TEST_MP3_CRUSH)
self.assertDictEqual(media_dict, results_dict)  # FAILS
```

#### Actual Error
```
AssertionError: Dictionaries differ (3486 character diff)
```

#### Root Cause
**ffprobe output fields differ between Windows and Linux versions:**

The hardcoded baseline (`media_dict`) contains fields that Ubuntu's ffprobe doesn't include, or vice versa:

Expected fields in test (Windows output):
- `'closed_captions': '0'`
- `'film_grain': '0'`
- Some other video stream fields

Ubuntu's ffprobe output is missing these fields OR has different fields with different values.

**Why This Happens:**
1. ffprobe version differences between Windows and Ubuntu ffmpeg distributions
2. Ubuntu likely has an older or newer version than Windows test baseline
3. Different ffprobe versions report different metadata fields
4. Some fields were added/removed in ffprobe updates

**Example:** The fields `'closed_captions'` and `'film_grain'` are newer additions to ffprobe that may not exist in older versions on Ubuntu.

---

### 5. `test_get_media_info_walk` ❌
**File:** `tests/test_models_audio_metadata.py:705`
**Status:** FAILED

#### Problem
Test walks directory and checks metadata key count for M4A file.

```python
self.assertIn(f"{self.m4a_line} has 56 keys\n", lines)
# Expected: "...The Eagles-Desperado.m4a has 56 keys"
# Actual: "...The Eagles-Desperado.m4a has 54 keys"
```

#### Actual Error
```
AssertionError:
  '/home/gerald/MusicProcessing/tests/ConvertedMusic/The Eagles/Desperado/The Eagles-Desperado.m4a has 56 keys\n'
  not found in [actual output with 54 keys]
```

#### Root Cause
**ffprobe outputs fewer fields on Ubuntu than on Windows for M4A files:**

- **Expected (Windows):** 56 keys in ffprobe output for M4A
- **Actual (Ubuntu):** 54 keys in ffprobe output for M4A

The 2 missing fields are likely the same newer fields missing in test #4:
- `'closed_captions'`
- `'film_grain'`

**Other files have different key counts:**
- MP3: 37 keys (matches expected ✓)
- FLAC: 54 keys (not 56, but test doesn't check this)
- M4A: 54 keys (expected 56) ❌
- WMA: 38 keys (matches expected ✓)

**Why It Works on Windows:**
- Newer or different ffprobe version on Windows that includes `closed_captions` and `film_grain` fields

**Why It Fails on Ubuntu:**
- Older ffprobe version on Ubuntu that doesn't include these newer fields

---

## Summary of Root Causes

| Issue Type | Tests Affected | Cause |
|-----------|-----------------|--------|
| **ffprobe Version Mismatch** | #2, #4, #5 | Ubuntu has older/different ffprobe; missing newer metadata fields |
| **ffmpeg Behavior** | #1 | Ubuntu ffmpeg handles missing streams differently than Windows |
| **Filesystem/Permissions** | #3 | Linux `shutil.copymode()` fails; parent directory issue or race condition |

---

## Recommendations

### For Issue #1 & #2 (Audio Stream Detection)
**Problem:** WMA file detection differs
**Solutions:**
1. **Conditional Testing:** Add OS detection and use different test files for Linux/Windows
2. **Robust Error Handling:** Update `extract_ffmpeg_art()` to handle both error and non-error cases
3. **Mock ffmpeg Output:** Mock ffprobe/ffmpeg responses instead of using real files

**Suggested Fix Priority:** Medium

### For Issue #3 (shutil.copymode)
**Problem:** Parent directory doesn't exist or permission race condition
**Solution:**
1. Ensure parent directory exists before `shutil.copy()`
2. Use `shutil.copy2()` with error handling
3. Create destination directory explicitly:
   ```python
   os.makedirs(os.path.dirname(dest_path), exist_ok=True)
   shutil.copy(src_genre, dest_path)
   ```

**Suggested Fix Priority:** High (This is a setup bug)

### For Issue #4 & #5 (ffprobe Output Mismatch)
**Problem:** Different ffprobe versions output different fields
**Solutions:**
1. **Dynamic Baseline:** Instead of hardcoding field count, check for REQUIRED fields
2. **Version Detection:** Detect ffprobe version and use version-specific baselines
3. **Flexible Assertions:** Assert on presence of critical fields, ignore version-specific fields
4. **Update Baselines:** Update Windows baseline to match Ubuntu ffprobe output

**Suggested Fix Priority:** High (Affects 2 tests)

---

## Technical Differences

### Windows vs Ubuntu Environment Variables
- **PATH differences:** Different ffprobe/ffmpeg locations
- **ffmpeg build:** Windows typically uses pre-built binaries; Ubuntu uses package manager (possibly outdated)
- **Audio library versions:** Different codec library versions

### Why Tests Pass on Windows
1. ffmpeg/ffprobe built for Windows handles WMA streams differently
2. Newer version on Windows includes `closed_captions` and `film_grain` fields
3. NTFS filesystem permissions model doesn't trigger `copymode()` issues

### Why Tests Fail on Ubuntu
1. Package manager ffmpeg/ffprobe may be older or different build
2. Missing metadata fields in older ffprobe
3. POSIX filesystem permissions stricter; `copymode()` encounters issues
4. Different codec library versions from OS packages

---

## Action Items

| Priority | Test | Action | Owner |
|----------|------|--------|-------|
| **HIGH** | #3 | Fix `shutil.copymode()` - ensure parent dir exists | Dev |
| **HIGH** | #4, #5 | Update ffprobe output baseline or use flexible assertions | Dev |
| **MEDIUM** | #1, #2 | Add OS-specific test handling or mock ffprobe output | Dev |
| **LOW** | All | Update Ubuntu ffmpeg packages to latest version | Infra |

