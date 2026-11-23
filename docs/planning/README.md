# Test Failure Analysis: Windows vs Ubuntu

## 📋 Overview

This directory contains a comprehensive analysis of **5 failing tests** that pass on Windows 10 VS Code but fail on Ubuntu 26 VS Code.

**Key Finding:** Version mismatch in ffmpeg (Windows uses older version; Ubuntu has latest 8.0.1 from 2025)

---

## 📁 Document Guide

### 1. **[EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md)** ⭐ START HERE
   - **For:** Quick understanding of all 5 failures
   - **Contains:** Executive summary, root causes, recommended fixes with priority order
   - **Read time:** 10 minutes
   - **Best for:** Getting the big picture before diving into details

### 2. **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)**
   - **For:** Quick lookup and troubleshooting
   - **Contains:** 5-line summary per test, root cause categories, quick fix commands
   - **Read time:** 5 minutes
   - **Best for:** Finding info quickly when you're in a hurry

### 3. **[TEST_FAILURE_ANALYSIS.md](./TEST_FAILURE_ANALYSIS.md)**
   - **For:** Deep technical analysis
   - **Contains:** Detailed problem descriptions, root cause analysis, stack traces, recommendations
   - **Read time:** 30 minutes
   - **Best for:** Understanding exactly why each test fails

### 4. **[DETAILED_COMPARISON.md](./DETAILED_COMPARISON.md)**
   - **For:** Side-by-side Windows vs Ubuntu comparison
   - **Contains:** What happens on each OS, expected vs actual behavior, code walkthroughs
   - **Read time:** 25 minutes
   - **Best for:** Understanding platform-specific differences

### 5. **[ENVIRONMENT_INFO.md](./ENVIRONMENT_INFO.md)**
   - **For:** Version and environment details
   - **Contains:** FFmpeg versions, release dates, version-specific behaviors
   - **Read time:** 5 minutes
   - **Best for:** Understanding why versions matter

### 6. **[RECOMMENDED_FIXES.md](./RECOMMENDED_FIXES.md)** ⭐ USE THIS TO FIX
   - **For:** Implementing the fixes
   - **Contains:** Exact code changes needed, with before/after comparisons and alternatives
   - **Read time:** 20 minutes (implementation: 30 minutes)
   - **Best for:** Copy-paste ready solutions with explanations

---

## 🚀 Quick Start

### If you want to fix the tests:
1. Read [EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md) (10 min)
2. Go to [RECOMMENDED_FIXES.md](./RECOMMENDED_FIXES.md) and apply fixes (30 min)
3. Run tests to verify (5 min)

### If you want to understand the failures:
1. Read [EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md) (10 min)
2. Read [TEST_FAILURE_ANALYSIS.md](./TEST_FAILURE_ANALYSIS.md) (30 min)
3. Read [DETAILED_COMPARISON.md](./DETAILED_COMPARISON.md) (25 min)

### If you want a quick reference:
- Read [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) (5 min)
- Refer to [RECOMMENDED_FIXES.md](./RECOMMENDED_FIXES.md) as needed

---

## 📊 The 5 Failed Tests at a Glance

| # | Test Name | File | Root Cause | Severity | Fix Priority |
|---|-----------|------|-----------|----------|------------|
| 1 | `test_extract_ffmpeg_art_no_stream` | audio_art.py | ffmpeg behavior difference | Medium | 2 |
| 2 | `test_has_video_stream_false` | audio_art.py | ffprobe detects artwork as video | Medium | 2 |
| 3 | `test_create_album_dir_error` | audio_metadata.py | shutil.copymode() permission issue | **High** | **1** |
| 4 | `test_get_media_info` | audio_metadata.py | ffprobe missing 2 fields (closed_captions, film_grain) | **High** | **1** |
| 5 | `test_get_media_info_walk` | audio_metadata.py | M4A key count mismatch (56 vs 54) | **High** | **1** |

---

## 🔍 Root Cause Summary

```
╔═══════════════════════════════════════════════════════════╗
║           ROOT CAUSE: VERSION MISMATCH                   ║
╠═══════════════════════════════════════════════════════════╣
║ Windows:                   Ubuntu:                        ║
║ FFmpeg: Older (2024?)      FFmpeg: Latest 8.0.1 (2025)   ║
║ → Different output         → Newer metadata fields       ║
║ → Different behavior       → Different stream detection  ║
╚═══════════════════════════════════════════════════════════╝
```

**Problems:**
1. Tests hardcoded against **Windows ffmpeg output**
2. Ubuntu uses **latest ffmpeg** with different output
3. No version detection → hard-coded expectations break

---

## 🛠️ Fix Summary

### High Priority (Do these first)
- **Test #3:** Add `os.makedirs()` to ensure parent directory exists
- **Tests #4-5:** Use flexible assertions instead of exact field counts

### Medium Priority (Then these)
- **Tests #1-2:** Update stream detection to filter out artwork (mjpeg/png)

---

## 🧪 Test Commands

```bash
# Run specific failing test
pytest tests/test_models_audio_art.py::TestAudioArt::test_has_video_stream_false -xvs

# Run all 5 failing tests
pytest \
  tests/test_models_audio_art.py::TestAudioArt::test_extract_ffmpeg_art_no_stream \
  tests/test_models_audio_art.py::TestAudioArt::test_has_video_stream_false \
  tests/test_models_audio_metadata.py::TestAudioMetadata::test_create_album_dir_error \
  tests/test_models_audio_metadata.py::TestAudioMetadata::test_get_media_info \
  tests/test_models_audio_metadata.py::TestAudioMetadata::test_get_media_info_walk \
  -v

# Run all tests
pytest tests/ -v
```

---

## 💡 Key Insights

1. **Windows has older ffmpeg** (tests pass on older version)
2. **Ubuntu has latest ffmpeg 8.0.1** (Jan 2025 release)
3. **Tests are version-specific** (hardcoded expectations)
4. **Solution: Make tests version-agnostic** (check for required fields, not exact structure)

---

## 📝 Notes

- All documents saved in session workspace
- Verification done on Ubuntu 26 with ffmpeg 8.0.1-3ubuntu2
- Windows environment details needed for version confirmation

---

## ✅ Verification Checklist

After applying fixes:

- [ ] Test #3 passes (filesystem)
- [ ] Tests #1-2 pass (stream detection)
- [ ] Tests #4-5 pass (ffprobe metadata)
- [ ] All 161 tests pass
- [ ] Code is cleaner and more maintainable
- [ ] No hard-coded version dependencies

---

## 📚 Additional Resources

- FFmpeg Documentation: https://ffmpeg.org/documentation.html
- FFmpeg 8.0 Release Notes: https://github.com/FFmpeg/FFmpeg/releases/tag/n8.0
- Python shutil Documentation: https://docs.python.org/3/library/shutil.html

---

## 🤝 Questions?

Refer to the specific analysis documents for detailed explanations:
- **Why?** → [TEST_FAILURE_ANALYSIS.md](./TEST_FAILURE_ANALYSIS.md)
- **How?** → [RECOMMENDED_FIXES.md](./RECOMMENDED_FIXES.md)
- **What?** → [DETAILED_COMPARISON.md](./DETAILED_COMPARISON.md)

